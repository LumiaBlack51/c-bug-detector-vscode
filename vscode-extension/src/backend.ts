import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';

export interface BugReport {
    line_number: number;
    error_type: string;
    severity: string;
    message: string;
    suggestion: string;
    code_snippet: string;
    module_name: string;
}

export interface AnalysisResult {
    file_path: string;
    reports: BugReport[];
    success: boolean;
    error?: string;
}

export class BugDetectorBackend {
    private config: vscode.WorkspaceConfiguration;

    constructor() {
        this.config = vscode.workspace.getConfiguration('c-bug-detector');
    }

    public updateConfiguration(): void {
        this.config = vscode.workspace.getConfiguration('c-bug-detector');
    }

    public async analyzeFile(filePath: string): Promise<AnalysisResult> {
        try {
            const pythonPath = this.config.get<string>('pythonPath', 'python');
            const backendPath = this.config.get<string>('backendPath', '../main.py');
            
            // 构建完整的后端路径
            const fullBackendPath = path.resolve(__dirname, backendPath);
            
            if (!fs.existsSync(fullBackendPath)) {
                throw new Error(`后端检测器不存在: ${fullBackendPath}`);
            }

            // 构建命令参数
            const args = [
                fullBackendPath,
                filePath,
                '-f', 'json'
            ];

            // 添加模块启用/禁用参数
            const enabledModules = this.getEnabledModules();
            if (enabledModules.length > 0) {
                args.push('--enable', ...enabledModules);
            }

            return new Promise<AnalysisResult>((resolve, reject) => {
                const process = spawn(pythonPath, args, {
                    cwd: path.dirname(fullBackendPath)
                });

                let stdout = '';
                let stderr = '';

                process.stdout.on('data', (data) => {
                    stdout += data.toString();
                });

                process.stderr.on('data', (data) => {
                    stderr += data.toString();
                });

                process.on('close', (code) => {
                    if (code === 0) {
                        try {
                            const reports: BugReport[] = JSON.parse(stdout);
                            resolve({
                                file_path: filePath,
                                reports: reports,
                                success: true
                            });
                        } catch (parseError) {
                            reject(new Error(`解析结果失败: ${parseError}`));
                        }
                    } else {
                        reject(new Error(`检测器执行失败 (代码: ${code}): ${stderr}`));
                    }
                });

                process.on('error', (error) => {
                    reject(new Error(`启动检测器失败: ${error.message}`));
                });
            });

        } catch (error) {
            return {
                file_path: filePath,
                reports: [],
                success: false,
                error: error instanceof Error ? error.message : String(error)
            };
        }
    }

    public async analyzeWorkspace(): Promise<AnalysisResult[]> {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            throw new Error('没有打开的工作区');
        }

        const results: AnalysisResult[] = [];
        
        for (const folder of workspaceFolders) {
            const cFiles = await this.findCFiles(folder.uri.fsPath);
            
            for (const filePath of cFiles) {
                const result = await this.analyzeFile(filePath);
                results.push(result);
            }
        }

        return results;
    }

    private async findCFiles(rootPath: string): Promise<string[]> {
        const cFiles: string[] = [];
        
        const findFiles = async (dirPath: string): Promise<void> => {
            try {
                const entries = await fs.promises.readdir(dirPath, { withFileTypes: true });
                
                for (const entry of entries) {
                    const fullPath = path.join(dirPath, entry.name);
                    
                    if (entry.isDirectory()) {
                        // 跳过常见的忽略目录
                        if (!['node_modules', '.git', '.vscode', 'out', 'build'].includes(entry.name)) {
                            await findFiles(fullPath);
                        }
                    } else if (entry.isFile() && entry.name.endsWith('.c')) {
                        cFiles.push(fullPath);
                    }
                }
            } catch (error) {
                console.error(`读取目录失败 ${dirPath}:`, error);
            }
        };

        await findFiles(rootPath);
        return cFiles;
    }

    private getEnabledModules(): string[] {
        const modules: string[] = [];
        
        if (this.config.get<boolean>('enableMemorySafety', true)) {
            modules.push('memory_safety');
        }
        if (this.config.get<boolean>('enableVariableState', true)) {
            modules.push('variable_state');
        }
        if (this.config.get<boolean>('enableStandardLibrary', true)) {
            modules.push('standard_library');
        }
        if (this.config.get<boolean>('enableNumericControlFlow', true)) {
            modules.push('numeric_control_flow');
        }

        return modules;
    }

    public dispose(): void {
        // 清理资源
    }
}

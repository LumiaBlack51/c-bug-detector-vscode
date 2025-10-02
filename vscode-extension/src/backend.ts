import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';
import { BugReport, AnalysisResult } from './cDetector';

export { BugReport, AnalysisResult };

export class BugDetectorBackend {
    private config: vscode.WorkspaceConfiguration;
    private pythonPath: string;
    private backendPath: string;

    constructor() {
        this.config = vscode.workspace.getConfiguration('c-bug-detector');
        this.pythonPath = this.config.get('pythonPath', 'python');
        
        // 获取插件后端路径
        const extensionPath = vscode.extensions.getExtension('c-bug-detector.c-bug-detector')?.extensionPath || '';
        this.backendPath = path.join(extensionPath, '..', 'core', 'main.py');
    }

    public updateConfiguration(): void {
        this.config = vscode.workspace.getConfiguration('c-bug-detector');
        this.pythonPath = this.config.get('pythonPath', 'python');
    }

    public async analyzeFile(filePath: string): Promise<AnalysisResult> {
        try {
            // 检查文件是否存在
            if (!fs.existsSync(filePath)) {
                return {
                    file_path: filePath,
                    reports: [],
                    success: false,
                    error: `文件不存在: ${filePath}`
                };
            }

            // 检查文件扩展名
            const ext = path.extname(filePath).toLowerCase();
            if (ext !== '.c' && ext !== '.h') {
                return {
                    file_path: filePath,
                    reports: [],
                    success: false,
                    error: `不支持的文件类型: ${ext}`
                };
            }

            // 调用Python后端
            const result = await this.callPythonBackend(filePath);
            return result;
        } catch (error) {
            return {
                file_path: filePath,
                reports: [],
                success: false,
                error: `检测器执行失败: ${error}`
            };
        }
    }

    public async analyzeWorkspace(): Promise<AnalysisResult[]> {
        try {
            if (!vscode.workspace.workspaceFolders) {
                return [{
                    file_path: 'workspace',
                    reports: [],
                    success: false,
                    error: '没有打开的工作区'
                }];
            }

            const results: AnalysisResult[] = [];
            
            for (const folder of vscode.workspace.workspaceFolders) {
                const folderResults = await this.analyzeDirectory(folder.uri.fsPath);
                results.push(...folderResults);
            }

            return results;
        } catch (error) {
            return [{
                file_path: 'workspace',
                reports: [],
                success: false,
                error: `工作区分析失败: ${error}`
            }];
        }
    }

    private async analyzeDirectory(directoryPath: string): Promise<AnalysisResult[]> {
        try {
            const results: AnalysisResult[] = [];
            
            // 检查目录是否存在
            if (!fs.existsSync(directoryPath)) {
                return [{
                    file_path: directoryPath,
                    reports: [],
                    success: false,
                    error: `目录不存在: ${directoryPath}`
                }];
            }

            // 递归查找C文件
            const cFiles = await this.findCFiles(directoryPath);
            
            // 分析每个文件
            for (const filePath of cFiles) {
                const result = await this.analyzeFile(filePath);
                results.push(result);
            }

            return results;
        } catch (error) {
            return [{
                file_path: directoryPath,
                reports: [],
                success: false,
                error: `检测器执行失败: ${error}`
            }];
        }
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
                    } else if (entry.isFile() && (entry.name.endsWith('.c') || entry.name.endsWith('.h'))) {
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

    private async callPythonBackend(filePath: string): Promise<AnalysisResult> {
        return new Promise((resolve, reject) => {
            // 检查后端文件是否存在
            if (!fs.existsSync(this.backendPath)) {
                resolve({
                    file_path: filePath,
                    reports: [],
                    success: false,
                    error: `Python后端文件不存在: ${this.backendPath}`
                });
                return;
            }

            const python = spawn(this.pythonPath, [this.backendPath, filePath, '--format', 'json'], {
                cwd: path.dirname(this.backendPath)
            });

            let stdout = '';
            let stderr = '';

            python.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            python.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            python.on('close', (code) => {
                if (code !== 0) {
                    resolve({
                        file_path: filePath,
                        reports: [],
                        success: false,
                        error: `Python后端执行失败 (exit code ${code}): ${stderr}`
                    });
                    return;
                }

                try {
                    // 解析JSON输出
                    const jsonOutput = this.extractJsonFromOutput(stdout);
                    if (!jsonOutput) {
                        resolve({
                            file_path: filePath,
                            reports: [],
                            success: false,
                            error: `无法解析Python后端输出: ${stdout}`
                        });
                        return;
                    }

                    const reports = JSON.parse(jsonOutput);
                    resolve({
                        file_path: filePath,
                        reports: reports,
                        success: true
                    });
                } catch (error) {
                    resolve({
                        file_path: filePath,
                        reports: [],
                        success: false,
                        error: `解析检测结果失败: ${error}`
                    });
                }
            });

            python.on('error', (error) => {
                resolve({
                    file_path: filePath,
                    reports: [],
                    success: false,
                    error: `启动Python后端失败: ${error.message}`
                });
            });
        });
    }

    private extractJsonFromOutput(output: string): string | null {
        // 查找JSON数组的开始和结束
        const startIndex = output.indexOf('[');
        const endIndex = output.lastIndexOf(']');
        
        if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
            return output.substring(startIndex, endIndex + 1);
        }
        
        return null;
    }

    public dispose(): void {
        // 清理资源
    }
}
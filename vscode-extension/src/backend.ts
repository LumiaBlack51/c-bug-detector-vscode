import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';

// 定义接口
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
    private pythonPath: string;
    private backendPath: string;

    constructor() {
        this.config = vscode.workspace.getConfiguration('c-bug-detector');
        this.pythonPath = this.config.get('pythonPath', 'python');
        
        // 获取插件后端路径
        const extension = vscode.extensions.getExtension('c-bug-detector.c-bug-detector');
        let extensionPath = extension?.extensionPath || '';
        
        // 如果无法获取扩展路径，尝试其他方法
        if (!extensionPath) {
            // 尝试从当前文件路径推断
            const currentDir = __dirname;
            extensionPath = path.join(currentDir, '..', '..');
        }
        
        this.backendPath = path.join(extensionPath, 'core', 'main.py');
        
        // 调试信息
        console.log(`插件路径: ${extensionPath}`);
        console.log(`后端路径: ${this.backendPath}`);
        console.log(`后端文件存在: ${fs.existsSync(this.backendPath)}`);
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
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (!workspaceFolders) {
                return [];
            }

            const results: AnalysisResult[] = [];
            for (const folder of workspaceFolders) {
                const cFiles = await this.findCFiles(folder.uri.fsPath);
                for (const file of cFiles) {
                    const result = await this.analyzeFile(file);
                    results.push(result);
                }
            }

            return results;
        } catch (error) {
            return [{
                file_path: '',
                reports: [],
                success: false,
                error: `工作区分析失败: ${error}`
            }];
        }
    }

    private async findCFiles(rootPath: string): Promise<string[]> {
        const cFiles: string[] = [];
        
        const searchDir = (dir: string) => {
            const files = fs.readdirSync(dir);
            for (const file of files) {
                const fullPath = path.join(dir, file);
                const stat = fs.statSync(fullPath);
                
                if (stat.isDirectory()) {
                    // 跳过一些常见的目录
                    if (!['node_modules', '.git', 'build', 'dist'].includes(file)) {
                        searchDir(fullPath);
                    }
                } else if (file.endsWith('.c') || file.endsWith('.h')) {
                    cFiles.push(fullPath);
                }
            }
        };

        try {
            searchDir(rootPath);
        } catch (error) {
            console.error(`搜索C文件时出错: ${error}`);
        }

        return cFiles;
    }

    private async callPythonBackend(filePath: string): Promise<AnalysisResult> {
        return new Promise((resolve) => {
            // 检查后端文件是否存在
            if (!fs.existsSync(this.backendPath)) {
                console.error(`Python后端文件不存在: ${this.backendPath}`);
                console.error(`插件路径: ${vscode.extensions.getExtension('c-bug-detector.c-bug-detector')?.extensionPath}`);
                console.error(`当前工作目录: ${process.cwd()}`);
                
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
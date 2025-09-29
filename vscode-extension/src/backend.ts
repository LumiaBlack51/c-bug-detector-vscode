import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';
import { CDetector, BugReport, AnalysisResult } from './cDetector';

export { BugReport, AnalysisResult };

export class BugDetectorBackend {
    private config: vscode.WorkspaceConfiguration;
    private detector: CDetector;

    constructor() {
        this.config = vscode.workspace.getConfiguration('c-bug-detector');
        this.detector = new CDetector();
    }

    public updateConfiguration(): void {
        this.config = vscode.workspace.getConfiguration('c-bug-detector');
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

            // 使用Python后端检测器
            const result = await this.analyzeWithPythonBackend(filePath);
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

    private async analyzeWithPythonBackend(filePath: string): Promise<AnalysisResult> {
        return new Promise((resolve) => {
            try {
                // 获取Python路径和后端路径
                const pythonPath = this.config.get('pythonPath', 'python');
                const backendPath = this.config.get('backendPath', 'backend/main.py');
                
                // 构建后端脚本的完整路径
                const extensionPath = path.dirname(__filename);
                const fullBackendPath = path.join(extensionPath, '..', backendPath);
                
                console.log(`[Backend] 使用Python路径: ${pythonPath}`);
                console.log(`[Backend] 使用后端路径: ${fullBackendPath}`);
                console.log(`[Backend] 分析文件: ${filePath}`);
                
                // 调用Python后端
                const pythonProcess = spawn(pythonPath, [fullBackendPath, filePath], {
                    cwd: path.dirname(fullBackendPath)
                });
                
                let stdout = '';
                let stderr = '';
                
                pythonProcess.stdout.on('data', (data) => {
                    stdout += data.toString();
                });
                
                pythonProcess.stderr.on('data', (data) => {
                    stderr += data.toString();
                });
                
                pythonProcess.on('close', (code) => {
                    console.log(`[Backend] Python进程退出，代码: ${code}`);
                    console.log(`[Backend] 标准输出: ${stdout}`);
                    if (stderr) {
                        console.log(`[Backend] 错误输出: ${stderr}`);
                    }
                    
                    if (code === 0) {
                        // 解析Python后端的输出
                        const reports = this.parsePythonOutput(stdout);
                        resolve({
                            file_path: filePath,
                            reports: reports,
                            success: true
                        });
                    } else {
                        resolve({
                            file_path: filePath,
                            reports: [],
                            success: false,
                            error: `Python后端执行失败: ${stderr || stdout}`
                        });
                    }
                });
                
                pythonProcess.on('error', (error) => {
                    console.error(`[Backend] Python进程错误: ${error}`);
                    resolve({
                        file_path: filePath,
                        reports: [],
                        success: false,
                        error: `无法启动Python后端: ${error.message}`
                    });
                });
                
            } catch (error) {
                console.error(`[Backend] 分析文件时出错: ${error}`);
                resolve({
                    file_path: filePath,
                    reports: [],
                    success: false,
                    error: `分析失败: ${error}`
                });
            }
        });
    }
    
    private parsePythonOutput(output: string): BugReport[] {
        const reports: BugReport[] = [];
        
        try {
            // 解析Python后端的文本输出
            const lines = output.split('\n');
            let currentReport: Partial<BugReport> | null = null;
            
            for (const line of lines) {
                if (line.includes('[检测]') && line.includes('检测到问题')) {
                    // 开始新的报告
                    if (currentReport) {
                        reports.push(currentReport as BugReport);
                    }
                    currentReport = {
                        module_name: this.extractModuleName(line)
                    };
                } else if (currentReport && line.includes('[位置]')) {
                    const match = line.match(/第\s*(\d+)\s*行/);
                    if (match) {
                        currentReport.line_number = parseInt(match[1]);
                    }
                } else if (currentReport && line.includes('[警告]')) {
                    const match = line.match(/类型：([^-]+)\s*-\s*(.+)/);
                    if (match) {
                        currentReport.error_type = match[1].trim();
                        currentReport.severity = match[2].trim();
                    }
                } else if (currentReport && line.includes('[问题]')) {
                    currentReport.message = line.replace('[问题]', '').trim();
                } else if (currentReport && line.includes('[建议]')) {
                    currentReport.suggestion = line.replace('[建议]', '').trim();
                    currentReport.code_snippet = '';
                }
            }
            
            // 添加最后一个报告
            if (currentReport) {
                reports.push(currentReport as BugReport);
            }
            
        } catch (error) {
            console.error(`[Backend] 解析Python输出时出错: ${error}`);
        }
        
        return reports;
    }
    
    private extractModuleName(line: string): string {
        const match = line.match(/\[检测\]\s*([^检测到问题]+)/);
        return match ? match[1].trim() : '未知模块';
    }

    public dispose(): void {
        // 清理资源
    }
}
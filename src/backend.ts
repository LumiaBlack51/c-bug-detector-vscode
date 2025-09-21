import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
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

            // 使用TypeScript检测器
            const result = this.detector.analyzeFile(filePath);
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

    public dispose(): void {
        // 清理资源
    }
}
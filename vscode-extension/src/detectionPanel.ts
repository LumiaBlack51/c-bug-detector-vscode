import * as vscode from 'vscode';
import { BugDetectorBackend, AnalysisResult } from './backend';
import { ResultsProvider } from './resultsProvider';

export class DetectionPanel {
    private panel: vscode.WebviewPanel | undefined;
    private backend: BugDetectorBackend;
    private resultsProvider: ResultsProvider;

    constructor(
        private context: vscode.ExtensionContext,
        backend: BugDetectorBackend,
        resultsProvider: ResultsProvider
    ) {
        this.backend = backend;
        this.resultsProvider = resultsProvider;
    }

    public show(): void {
        if (this.panel) {
            this.panel.reveal(vscode.ViewColumn.One);
            return;
        }

        this.panel = vscode.window.createWebviewPanel(
            'c-bug-detector',
            'C Bug Detector',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        this.panel.webview.html = this.getWebviewContent();

        this.panel.onDidDispose(() => {
            this.panel = undefined;
        });

        this.panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.command) {
                    case 'analyzeFile':
                        await this.handleAnalyzeFile(message.filePath);
                        break;
                case 'analyzeWorkspace':
                    await this.handleAnalyzeWorkspace();
                    break;
                case 'analyzeAllCFiles':
                    await this.handleAnalyzeAllCFiles();
                    break;
                    case 'clearResults':
                        this.resultsProvider.clearResults();
                        this.updateWebview();
                        break;
                }
            },
            undefined,
            this.context.subscriptions
        );
    }

    public async analyzeFile(document: vscode.TextDocument): Promise<void> {
        const result = await this.backend.analyzeFile(document.fileName);
        this.resultsProvider.addResult(result);
        
        if (result.success) {
            const message = result.reports.length > 0 
                ? `检测完成！发现 ${result.reports.length} 个问题`
                : '检测完成！没有发现任何问题';
            vscode.window.showInformationMessage(message);
        } else {
            vscode.window.showErrorMessage(`检测失败: ${result.error}`);
        }

        this.updateWebview();
    }

    public async analyzeWorkspace(): Promise<void> {
        const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
        statusBarItem.text = "$(loading~spin) 正在分析工作区...";
        statusBarItem.show();

        try {
            const results = await this.backend.analyzeWorkspace();
            this.resultsProvider.updateResults(results);

            const totalIssues = results.reduce((sum, result) => sum + (result.success ? result.reports.length : 0), 0);
            const totalFiles = results.length;

            vscode.window.showInformationMessage(
                `工作区分析完成！检查了 ${totalFiles} 个文件，发现 ${totalIssues} 个问题`
            );

            this.updateWebview();
        } catch (error) {
            vscode.window.showErrorMessage(`工作区分析失败: ${error}`);
        } finally {
            statusBarItem.hide();
            statusBarItem.dispose();
        }
    }

    private async handleAnalyzeFile(filePath: string): Promise<void> {
        const result = await this.backend.analyzeFile(filePath);
        this.resultsProvider.addResult(result);
        this.updateWebview();
    }

    private async handleAnalyzeWorkspace(): Promise<void> {
        await this.analyzeWorkspace();
    }

    private async handleAnalyzeAllCFiles(): Promise<void> {
        if (!vscode.workspace.workspaceFolders) {
            vscode.window.showWarningMessage('请先打开一个工作区');
            return;
        }

        try {
            const results = await this.backend.analyzeWorkspace();
            this.resultsProvider.updateResults(results);
            
            const totalIssues = results.reduce((sum, result) => sum + (result.success ? result.reports.length : 0), 0);
            const totalFiles = results.length;
            
            vscode.window.showInformationMessage(
                `批量分析完成！检查了 ${totalFiles} 个C文件，发现 ${totalIssues} 个问题`
            );
            
            this.updateWebview();
        } catch (error) {
            vscode.window.showErrorMessage(`批量分析失败: ${error}`);
        }
    }

    private updateWebview(): void {
        if (this.panel) {
            this.panel.webview.postMessage({
                command: 'updateResults',
                results: this.getResultsForWebview()
            });
        }
    }

    private getResultsForWebview(): any[] {
        const results: any[] = [];
        
        for (const [filePath, result] of (this.resultsProvider as any).results) {
            const fileName = filePath.split(/[\\/]/).pop() || filePath;
            results.push({
                fileName,
                filePath,
                success: result.success,
                error: result.error,
                reports: result.reports || []
            });
        }
        
        return results;
    }

    private getWebviewContent(): string {
        return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>C Bug Detector</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            margin: 0;
            padding: 20px;
        }
        
        .header {
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        
        .title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        button {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        
        button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        
        button:disabled {
            background-color: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
            cursor: not-allowed;
        }
        
        .results {
            margin-top: 20px;
        }
        
        .file-result {
            margin-bottom: 20px;
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .file-header {
            background-color: var(--vscode-panel-background);
            padding: 10px;
            font-weight: bold;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        
        .file-content {
            padding: 10px;
        }
        
        .bug-item {
            margin-bottom: 10px;
            padding: 8px;
            border-left: 3px solid var(--vscode-charts-red);
            background-color: var(--vscode-textCodeBlock-background);
        }
        
        .bug-item.warning {
            border-left-color: var(--vscode-charts-yellow);
        }
        
        .bug-item.info {
            border-left-color: var(--vscode-charts-blue);
        }
        
        .bug-line {
            font-weight: bold;
            margin-bottom: 4px;
        }
        
        .bug-message {
            margin-bottom: 4px;
        }
        
        .bug-suggestion {
            font-style: italic;
            color: var(--vscode-descriptionForeground);
        }
        
        .bug-module {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-top: 4px;
        }
        
        .no-results {
            text-align: center;
            color: var(--vscode-descriptionForeground);
            margin-top: 40px;
        }
        
        .error {
            color: var(--vscode-errorForeground);
            background-color: var(--vscode-inputValidation-errorBackground);
            border: 1px solid var(--vscode-inputValidation-errorBorder);
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">🔍 C语言Bug检测器</div>
        <div class="buttons">
            <button onclick="analyzeCurrentFile()">分析当前文件</button>
            <button onclick="analyzeWorkspace()">分析工作区</button>
            <button onclick="analyzeAllCFiles()">一键检测所有C文件</button>
            <button onclick="clearResults()">清除结果</button>
        </div>
    </div>
    
    <div id="results" class="results">
        <div class="no-results">点击上方按钮开始检测</div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        
        function analyzeCurrentFile() {
            vscode.postMessage({
                command: 'analyzeFile',
                filePath: ''
            });
        }
        
        function analyzeWorkspace() {
            vscode.postMessage({
                command: 'analyzeWorkspace'
            });
        }
        
        function analyzeAllCFiles() {
            vscode.postMessage({
                command: 'analyzeAllCFiles'
            });
        }
        
        function clearResults() {
            vscode.postMessage({
                command: 'clearResults'
            });
        }
        
        function updateResults(results) {
            const resultsDiv = document.getElementById('results');
            
            if (results.length === 0) {
                resultsDiv.innerHTML = '<div class="no-results">没有检测结果</div>';
                return;
            }
            
            let html = '';
            
            for (const result of results) {
                html += \`<div class="file-result">
                    <div class="file-header">📁 \${result.fileName}</div>
                    <div class="file-content">\`;
                
                if (!result.success) {
                    html += \`<div class="error">检测失败: \${result.error}</div>\`;
                } else if (result.reports.length === 0) {
                    html += '<div class="no-results">✅ 没有发现任何问题</div>';
                } else {
                    for (const report of result.reports) {
                        const severityClass = report.severity.toLowerCase();
                        html += \`<div class="bug-item \${severityClass}">
                            <div class="bug-line">第 \${report.line_number} 行</div>
                            <div class="bug-message">\${report.message}</div>
                            <div class="bug-suggestion">💡 \${report.suggestion}</div>
                            <div class="bug-module">🔧 \${report.module_name}</div>
                        </div>\`;
                    }
                }
                
                html += '</div></div>';
            }
            
            resultsDiv.innerHTML = html;
        }
        
        // 监听来自扩展的消息
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.command) {
                case 'updateResults':
                    updateResults(message.results);
                    break;
            }
        });
    </script>
</body>
</html>`;
    }

    public dispose(): void {
        if (this.panel) {
            this.panel.dispose();
        }
    }
}

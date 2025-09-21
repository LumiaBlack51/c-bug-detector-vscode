import * as vscode from 'vscode';
import { BugReport, AnalysisResult } from './backend';

export class ResultsProvider implements vscode.TreeDataProvider<BugItem>, vscode.Disposable {
    private _onDidChangeTreeData: vscode.EventEmitter<BugItem | undefined | null | void> = new vscode.EventEmitter<BugItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<BugItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private results: Map<string, AnalysisResult> = new Map();
    private diagnosticCollection?: vscode.DiagnosticCollection;

    constructor() {
        // 设置上下文
        vscode.commands.executeCommand('setContext', 'c-bug-detector.hasResults', false);
    }

    public setDiagnosticCollection(collection: vscode.DiagnosticCollection): void {
        this.diagnosticCollection = collection;
    }

    public updateResults(results: AnalysisResult[]): void {
        this.results.clear();
        
        for (const result of results) {
            this.results.set(result.file_path, result);
        }

        this.updateDiagnostics();
        this.updateContext();
        this._onDidChangeTreeData.fire();
    }

    public addResult(result: AnalysisResult): void {
        this.results.set(result.file_path, result);
        this.updateDiagnostics();
        this.updateContext();
        this._onDidChangeTreeData.fire();
    }

    public clearResults(): void {
        this.results.clear();
        if (this.diagnosticCollection) {
            this.diagnosticCollection.clear();
        }
        this.updateContext();
        this._onDidChangeTreeData.fire();
    }

    private updateDiagnostics(): void {
        if (!this.diagnosticCollection) {
            return;
        }

        this.diagnosticCollection.clear();

        for (const [filePath, result] of this.results) {
            if (!result.success || result.reports.length === 0) {
                continue;
            }

            const uri = vscode.Uri.file(filePath);
            const diagnostics: vscode.Diagnostic[] = [];

            for (const report of result.reports) {
                const range = new vscode.Range(
                    report.line_number - 1, 0,
                    report.line_number - 1, Number.MAX_VALUE
                );

                const severity = this.getDiagnosticSeverity(report.severity);
                const diagnostic = new vscode.Diagnostic(
                    range,
                    `${report.module_name}: ${report.message}`,
                    severity
                );

                diagnostic.source = 'C Bug Detector';
                diagnostic.code = report.error_type;
                diagnostic.relatedInformation = [
                    new vscode.DiagnosticRelatedInformation(
                        new vscode.Location(uri, range),
                        `建议: ${report.suggestion}`
                    )
                ];

                diagnostics.push(diagnostic);
            }

            if (diagnostics.length > 0) {
                this.diagnosticCollection.set(uri, diagnostics);
            }
        }
    }

    private getDiagnosticSeverity(severity: string): vscode.DiagnosticSeverity {
        switch (severity.toLowerCase()) {
            case 'error':
                return vscode.DiagnosticSeverity.Error;
            case 'warning':
                return vscode.DiagnosticSeverity.Warning;
            case 'info':
                return vscode.DiagnosticSeverity.Information;
            default:
                return vscode.DiagnosticSeverity.Warning;
        }
    }

    private updateContext(): void {
        const hasResults = this.results.size > 0;
        vscode.commands.executeCommand('setContext', 'c-bug-detector.hasResults', hasResults);
    }

    public getTreeItem(element: BugItem): vscode.TreeItem {
        return element;
    }

    public dispose(): void {
        this._onDidChangeTreeData.dispose();
    }

    public getChildren(element?: BugItem): Thenable<BugItem[]> {
        if (!element) {
            // 根级别：显示文件
            const fileItems: BugItem[] = [];
            
            for (const [filePath, result] of this.results) {
                const fileName = filePath.split(/[\\/]/).pop() || filePath;
                const bugCount = result.success ? result.reports.length : 0;
                
                const fileItem = new BugItem(
                    fileName,
                    vscode.TreeItemCollapsibleState.Collapsed,
                    'file',
                    filePath
                );
                
                fileItem.description = `${bugCount} 个问题`;
                fileItem.tooltip = filePath;
                
                fileItems.push(fileItem);
            }
            
            return Promise.resolve(fileItems);
        } else if (element.type === 'file') {
            // 文件级别：显示问题
            const result = this.results.get(element.filePath!);
            if (!result || !result.success) {
                return Promise.resolve([]);
            }

            const bugItems: BugItem[] = [];
            
            for (const report of result.reports) {
                const bugItem = new BugItem(
                    `第${report.line_number}行: ${report.message}`,
                    vscode.TreeItemCollapsibleState.None,
                    'bug',
                    element.filePath,
                    report
                );
                
                bugItem.description = report.module_name;
                bugItem.tooltip = report.suggestion;
                
                // 设置图标
                switch (report.severity.toLowerCase()) {
                    case 'error':
                        bugItem.iconPath = new vscode.ThemeIcon('error');
                        break;
                    case 'warning':
                        bugItem.iconPath = new vscode.ThemeIcon('warning');
                        break;
                    case 'info':
                        bugItem.iconPath = new vscode.ThemeIcon('info');
                        break;
                    default:
                        bugItem.iconPath = new vscode.ThemeIcon('alert');
                }
                
                bugItems.push(bugItem);
            }
            
            return Promise.resolve(bugItems);
        }
        
        return Promise.resolve([]);
    }
}

export class BugItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly type: 'file' | 'bug',
        public readonly filePath?: string,
        public readonly report?: BugReport
    ) {
        super(label, collapsibleState);
        
        if (type === 'file') {
            this.contextValue = 'c-bug-detector-file';
        } else if (type === 'bug') {
            this.contextValue = 'c-bug-detector-bug';
            this.command = {
                command: 'vscode.open',
                title: '跳转到问题',
                arguments: [
                    vscode.Uri.file(filePath!),
                    {
                        selection: new vscode.Range(
                            report!.line_number - 1, 0,
                            report!.line_number - 1, Number.MAX_VALUE
                        )
                    }
                ]
            };
        }
    }
}

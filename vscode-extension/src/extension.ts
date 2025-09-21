import * as vscode from 'vscode';
import { BugDetectorBackend } from './backend';
import { ResultsProvider } from './resultsProvider';
import { DetectionPanel } from './detectionPanel';

export function activate(context: vscode.ExtensionContext) {
    console.log('C Bug Detector extension is now active!');

    // 初始化后端
    const backend = new BugDetectorBackend();
    const resultsProvider = new ResultsProvider();
    const detectionPanel = new DetectionPanel(context, backend, resultsProvider);

    // 注册命令
    const analyzeFileCommand = vscode.commands.registerCommand('c-bug-detector.analyzeFile', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('请先打开一个C文件');
            return;
        }

        if (!editor.document.fileName.endsWith('.c')) {
            vscode.window.showWarningMessage('当前文件不是C文件');
            return;
        }

        await detectionPanel.analyzeFile(editor.document);
    });

    const analyzeWorkspaceCommand = vscode.commands.registerCommand('c-bug-detector.analyzeWorkspace', async () => {
        await detectionPanel.analyzeWorkspace();
    });

    const analyzeAllCFilesCommand = vscode.commands.registerCommand('c-bug-detector.analyzeAllCFiles', async () => {
        if (!vscode.workspace.workspaceFolders) {
            vscode.window.showWarningMessage('请先打开一个工作区');
            return;
        }

        try {
            const results = await backend.analyzeWorkspace();
            resultsProvider.updateResults(results);
            
            const totalIssues = results.reduce((sum, result) => sum + (result.success ? result.reports.length : 0), 0);
            const totalFiles = results.length;
            
            vscode.window.showInformationMessage(
                `批量分析完成！检查了 ${totalFiles} 个C文件，发现 ${totalIssues} 个问题`
            );
        } catch (error) {
            vscode.window.showErrorMessage(`批量分析失败: ${error}`);
        }
    });

    const showPanelCommand = vscode.commands.registerCommand('c-bug-detector.showPanel', () => {
        detectionPanel.show();
    });

    const clearResultsCommand = vscode.commands.registerCommand('c-bug-detector.clearResults', () => {
        resultsProvider.clearResults();
        vscode.window.showInformationMessage('检测结果已清除');
    });

    // 注册视图
    const resultsTreeView = vscode.window.createTreeView('c-bug-detector-results', {
        treeDataProvider: resultsProvider,
        showCollapseAll: true
    });

    // 注册诊断集合
    const diagnosticCollection = vscode.languages.createDiagnosticCollection('c-bug-detector');

    // 监听配置变化
    const configChangeListener = vscode.workspace.onDidChangeConfiguration(e => {
        if (e.affectsConfiguration('c-bug-detector')) {
            backend.updateConfiguration();
        }
    });

    // 监听文档保存
    const saveListener = vscode.workspace.onDidSaveTextDocument(async (document) => {
        if (document.fileName.endsWith('.c')) {
            const config = vscode.workspace.getConfiguration('c-bug-detector');
            if (config.get('autoAnalyzeOnSave', false)) {
                await detectionPanel.analyzeFile(document);
            }
        }
    });

    // 注册到上下文
    context.subscriptions.push(
        analyzeFileCommand,
        analyzeWorkspaceCommand,
        analyzeAllCFilesCommand,
        showPanelCommand,
        clearResultsCommand,
        resultsTreeView,
        diagnosticCollection,
        configChangeListener,
        saveListener,
        backend,
        resultsProvider,
        detectionPanel
    );

    // 设置诊断集合到结果提供者
    resultsProvider.setDiagnosticCollection(diagnosticCollection);

    // 显示欢迎信息
    vscode.window.showInformationMessage('C Bug Detector 已激活！使用 Ctrl+Shift+B 分析当前C文件');
}

export function deactivate() {
    console.log('C Bug Detector extension is now deactivated!');
}

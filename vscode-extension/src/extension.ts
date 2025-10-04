import * as vscode from 'vscode';
import { BugDetectorBackend } from './backend';
import { ResultsProvider } from './resultsProvider';
import { DetectionPanel } from './detectionPanel';
import { ModuleControlProvider } from './moduleControlProvider';

export function activate(context: vscode.ExtensionContext) {
    console.log('C Bug Detector extension is now active!');

    // 初始化后端
    const backend = new BugDetectorBackend();
    const resultsProvider = new ResultsProvider();
    const moduleControlProvider = new ModuleControlProvider();
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

    // 模块切换命令
    const toggleMemorySafetyCommand = vscode.commands.registerCommand('c-bug-detector.toggleMemorySafety', () => {
        const config = vscode.workspace.getConfiguration('c-bug-detector');
        const currentValue = config.get('enableMemorySafety', true);
        config.update('enableMemorySafety', !currentValue, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage(`内存安全卫士模块已${!currentValue ? '启用' : '禁用'}`);
    });

    const toggleVariableStateCommand = vscode.commands.registerCommand('c-bug-detector.toggleVariableState', () => {
        const config = vscode.workspace.getConfiguration('c-bug-detector');
        const currentValue = config.get('enableVariableState', true);
        config.update('enableVariableState', !currentValue, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage(`变量状态监察官模块已${!currentValue ? '启用' : '禁用'}`);
    });

    const toggleStandardLibraryCommand = vscode.commands.registerCommand('c-bug-detector.toggleStandardLibrary', () => {
        const config = vscode.workspace.getConfiguration('c-bug-detector');
        const currentValue = config.get('enableStandardLibrary', true);
        config.update('enableStandardLibrary', !currentValue, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage(`标准库使用助手模块已${!currentValue ? '启用' : '禁用'}`);
    });

    const toggleNumericControlFlowCommand = vscode.commands.registerCommand('c-bug-detector.toggleNumericControlFlow', () => {
        const config = vscode.workspace.getConfiguration('c-bug-detector');
        const currentValue = config.get('enableNumericControlFlow', true);
        config.update('enableNumericControlFlow', !currentValue, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage(`数值与控制流分析器模块已${!currentValue ? '启用' : '禁用'}`);
    });

    // 注册视图
    const resultsTreeView = vscode.window.createTreeView('c-bug-detector-results', {
        treeDataProvider: resultsProvider,
        showCollapseAll: true
    });

    const moduleControlTreeView = vscode.window.createTreeView('c-bug-detector-controls', {
        treeDataProvider: moduleControlProvider,
        showCollapseAll: false
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
        toggleMemorySafetyCommand,
        toggleVariableStateCommand,
        toggleStandardLibraryCommand,
        toggleNumericControlFlowCommand,
        resultsTreeView,
        moduleControlTreeView,
        diagnosticCollection,
        configChangeListener,
        saveListener,
        backend,
        resultsProvider,
        moduleControlProvider,
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

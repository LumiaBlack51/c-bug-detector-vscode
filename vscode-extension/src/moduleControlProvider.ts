import * as vscode from 'vscode';

export class ModuleControlProvider implements vscode.TreeDataProvider<ModuleControlItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ModuleControlItem | undefined | null | void> = new vscode.EventEmitter<ModuleControlItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ModuleControlItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor() {
        // 监听配置变化
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('c-bug-detector')) {
                this._onDidChangeTreeData.fire();
            }
        });
    }

    getTreeItem(element: ModuleControlItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ModuleControlItem): Thenable<ModuleControlItem[]> {
        if (!element) {
            // 返回根级别的模块控制项
            return Promise.resolve(this.getModuleControls());
        }
        return Promise.resolve([]);
    }

    dispose() {
        this._onDidChangeTreeData.dispose();
    }

    private getModuleControls(): ModuleControlItem[] {
        const config = vscode.workspace.getConfiguration('c-bug-detector');
        
        return [
            new ModuleControlItem(
                '🛡️ 内存安全卫士',
                'enableMemorySafety',
                config.get('enableMemorySafety', true),
                'c-bug-detector.toggleMemorySafety',
                '检测内存泄漏、野指针、空指针解引用等问题'
            ),
            new ModuleControlItem(
                '📊 变量状态监察官',
                'enableVariableState',
                config.get('enableVariableState', true),
                'c-bug-detector.toggleVariableState',
                '检测未初始化变量、作用域问题等'
            ),
            new ModuleControlItem(
                '📚 标准库使用助手',
                'enableStandardLibrary',
                config.get('enableStandardLibrary', true),
                'c-bug-detector.toggleStandardLibrary',
                '检测头文件缺失、printf/scanf参数不匹配等'
            ),
            new ModuleControlItem(
                '🔢 数值与控制流分析器',
                'enableNumericControlFlow',
                config.get('enableNumericControlFlow', true),
                'c-bug-detector.toggleNumericControlFlow',
                '检测类型溢出、死循环等问题'
            )
        ];
    }
}

class ModuleControlItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly configKey: string,
        public readonly enabled: boolean,
        public readonly commandName: string,
        public readonly description: string
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);
        
        this.tooltip = `${this.label}\n${this.description}\n\n点击切换模块状态`;
        this.description = this.enabled ? '已启用' : '已禁用';
        
        // 设置图标
        this.iconPath = new vscode.ThemeIcon(
            this.enabled ? 'check' : 'x',
            new vscode.ThemeColor(this.enabled ? 'charts.green' : 'charts.red')
        );
        
        // 设置命令
        this.command = {
            title: `切换${this.label}`,
            command: this.commandName,
            arguments: [this.configKey]
        };
        
        // 设置上下文值
        this.contextValue = this.enabled ? 'moduleEnabled' : 'moduleDisabled';
    }
}

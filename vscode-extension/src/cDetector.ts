import * as vscode from 'vscode';

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

interface VariableState {
    name: string;
    type: string; // 'int', 'char', 'pointer', etc.
    initialized: boolean;
    value: string | null; // 当前值，如 'NULL', '0', 'malloc_result', etc.
    declaredAt: number; // 声明行号
    lastAssignedAt: number; // 最后赋值行号
    scope: number; // 作用域层级
}

export class CDetector {
    private patterns: { [key: string]: RegExp } = {};
    private variableStates: Map<string, VariableState> = new Map();
    private scopeLevel: number = 0;

    constructor() {
        this.initializePatterns();
    }

    /**
     * 移除行中的注释，返回纯代码部分
     * @param line 原始代码行
     * @returns 移除注释后的代码行
     */
    private removeComments(line: string): string {
        let result = line;
        
        // 处理单行注释 //
        const singleLineCommentIndex = result.indexOf('//');
        if (singleLineCommentIndex !== -1) {
            result = result.substring(0, singleLineCommentIndex);
        }
        
        // 处理多行注释 /* */
        // 注意：这里只处理单行内的多行注释，跨行注释需要更复杂的处理
        const multiLineCommentRegex = /\/\*.*?\*\//g;
        result = result.replace(multiLineCommentRegex, '');
        
        return result.trim();
    }

    /**
     * 移除多行注释（跨行处理）
     * @param lines 代码行数组
     * @returns 移除多行注释后的代码行数组
     */
    private removeMultiLineComments(lines: string[]): string[] {
        const result: string[] = [];
        let inMultiLineComment = false;
        
        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];
            
            if (inMultiLineComment) {
                // 在多行注释中，查找结束标记 */
                const endIndex = line.indexOf('*/');
                if (endIndex !== -1) {
                    // 找到结束标记，移除注释部分
                    line = line.substring(endIndex + 2);
                    inMultiLineComment = false;
                } else {
                    // 整行都是注释，跳过
                    continue;
                }
            }
            
            // 查找多行注释开始标记 /*
            const startIndex = line.indexOf('/*');
            if (startIndex !== -1) {
                // 检查是否在同一行结束
                const endIndex = line.indexOf('*/', startIndex);
                if (endIndex !== -1) {
                    // 同一行内结束，移除注释部分
                    line = line.substring(0, startIndex) + line.substring(endIndex + 2);
                } else {
                    // 跨行注释开始，移除开始部分
                    line = line.substring(0, startIndex);
                    inMultiLineComment = true;
                }
            }
            
            // 移除单行注释
            line = this.removeComments(line);
            
            // 只保留非空行
            if (line.trim().length > 0) {
                result.push(line);
            }
        }
        
        return result;
    }

    private initializePatterns(): void {
        // 函数定义（支持汉字变量名）
        this.patterns['function_definition'] = /^\s*(\w+)\s+([\w\u4e00-\u9fff]+)\s*\([^)]*\)\s*\{/;
        
        // 变量声明（支持汉字变量名）
        this.patterns['variable_declaration'] = /^\s*(int|char|float|double|long|short|unsigned|signed|void)\s+([\w\u4e00-\u9fff]+)/;
        
        // 函数调用（支持汉字变量名）
        this.patterns['function_call'] = /([\w\u4e00-\u9fff]+)\s*\(/;
        
        // malloc/calloc/realloc（支持汉字变量名）
        this.patterns['memory_allocation'] = /([\w\u4e00-\u9fff]+)\s*=\s*(malloc|calloc|realloc)\s*\(/;
        
        // free调用
        this.patterns['memory_free'] = /free\s*\(/;
        
        // printf
        this.patterns['printf'] = /printf\s*\(/;
        
        // scanf
        this.patterns['scanf'] = /scanf\s*\(/;
        
        // while循环
        this.patterns['while_loop'] = /while\s*\(/;
        
        // for循环
        this.patterns['for_loop'] = /for\s*\(/;
        
        // 赋值语句（支持汉字变量名）
        this.patterns['assignment'] = /([\w\u4e00-\u9fff]+)\s*=\s*(.+)/;
        
        // 指针解引用（支持汉字变量名）
        this.patterns['pointer_dereference'] = /\*([\w\u4e00-\u9fff]+)/;
        
        // 取地址（支持汉字变量名）
        this.patterns['address_of'] = /&([\w\u4e00-\u9fff]+)/;
    }

    public analyzeFile(filePath: string): AnalysisResult {
        try {
            const content = this.readFileContent(filePath);
            const originalLines = content.split('\n');
            
            // 移除注释，获取纯代码行
            const cleanLines = this.removeMultiLineComments(originalLines);
            
            const reports: BugReport[] = [];

            // 运行所有检测模块（使用原始行号进行报告）
            reports.push(...this.detectMemorySafety(originalLines, filePath));
            reports.push(...this.detectVariableState(originalLines, filePath));
            reports.push(...this.detectStandardLibrary(originalLines, filePath));
            reports.push(...this.detectNumericControlFlow(originalLines, filePath));

            return {
                file_path: filePath,
                reports: reports,
                success: true
            };
        } catch (error) {
            return {
                file_path: filePath,
                reports: [],
                success: false,
                error: `分析失败: ${error}`
            };
        }
    }

    private readFileContent(filePath: string): string {
        try {
            const fs = require('fs');
            return fs.readFileSync(filePath, 'utf8');
        } catch (error) {
            throw new Error(`无法读取文件: ${filePath}`);
        }
    }

    private detectMemorySafety(lines: string[], filePath: string): BugReport[] {
        const reports: BugReport[] = [];
        this.variableStates.clear();
        this.scopeLevel = 0;

        for (let i = 0; i < lines.length; i++) {
            const originalLine = lines[i];
            const lineNum = i + 1;
            
            // 移除注释，获取纯代码
            const line = this.removeComments(originalLine);
            
            // 跳过空行
            if (line.trim().length === 0) {
                continue;
            }

            // 更新作用域层级
            this.updateScopeLevel(line);

            // 处理变量声明和赋值
            this.processVariableDeclarations(line, lineNum);
            this.processVariableAssignments(line, lineNum);

            // 检测指针解引用
            this.detectPointerDereference(line, lineNum, reports);

            // 检测内存分配和释放
            this.processMemoryOperations(line, lineNum);
        }

        // 检测内存泄漏
        this.detectMemoryLeaks(reports, lines);

        return reports;
    }

    private updateScopeLevel(line: string): void {
        // 检测大括号层级变化
        const openBraces = (line.match(/\{/g) || []).length;
        const closeBraces = (line.match(/\}/g) || []).length;
        
        this.scopeLevel += openBraces;
        this.scopeLevel -= closeBraces;
        
        // 当作用域结束时，清理该作用域的变量
        if (closeBraces > 0) {
            this.cleanupScopeVariables();
        }
    }

    private processVariableDeclarations(line: string, lineNum: number): void {
        // 检测变量声明：int x, char* ptr, struct Point* p, etc.（支持汉字变量名）
        const declPatterns = [
            /^\s*(int|char|float|double|long|short|unsigned|signed|void)\s+([\w\u4e00-\u9fff]+)/,
            /^\s*(int|char|float|double|long|short|unsigned|signed|void)\s*\*\s*([\w\u4e00-\u9fff]+)/,
            /^\s*([\w\u4e00-\u9fff]+)\s*\*\s*([\w\u4e00-\u9fff]+)/,
            /^\s*struct\s+([\w\u4e00-\u9fff]+)\s*\*\s*([\w\u4e00-\u9fff]+)/,  // struct Point* p
            /^\s*struct\s+([\w\u4e00-\u9fff]+)\s+([\w\u4e00-\u9fff]+)/        // struct Point p
        ];

        for (const pattern of declPatterns) {
            const match = line.match(pattern);
            if (match) {
                let varName: string;
                let varType: string;
                let isPointer: boolean;
                
                if (pattern.source.includes('struct')) {
                    // 结构体声明处理
                    varName = match[2];
                    varType = `struct ${match[1]}`;
                    isPointer = line.includes('*');
                } else {
                    // 普通变量声明处理
                    varName = match[2] || match[1];
                    varType = match[1];
                    isPointer = line.includes('*');
                }
                
                // 检查是否初始化
                const isInitialized = line.includes('=');
                let initialValue = null;
                
                if (isInitialized) {
                    const assignMatch = line.match(/=\s*(.+?)(?:;|,|$)/);
                    if (assignMatch) {
                        initialValue = assignMatch[1].trim();
                    }
                }

                this.variableStates.set(varName, {
                    name: varName,
                    type: isPointer ? 'pointer' : varType,
                    initialized: isInitialized,
                    value: initialValue,
                    declaredAt: lineNum,
                    lastAssignedAt: isInitialized ? lineNum : 0,
                    scope: this.scopeLevel
                });
            }
        }
    }

    private processVariableAssignments(line: string, lineNum: number): void {
        // 检测赋值语句：x = value, ptr = malloc(...), ptr1 = ptr2, etc.（支持汉字变量名）
        const assignPattern = /([\w\u4e00-\u9fff]+)\s*=\s*(.+?)(?:;|,|$)/;
        const match = line.match(assignPattern);
        
        if (match) {
            const varName = match[1];
            const value = match[2].trim();
            
            if (this.variableStates.has(varName)) {
                const varState = this.variableStates.get(varName)!;
                varState.initialized = true;
                varState.value = value;
                varState.lastAssignedAt = lineNum;
                
                // 处理指针赋值传播
                this.handlePointerAssignmentPropagation(varName, value, lineNum);
            }
        }
    }

    private handlePointerAssignmentPropagation(targetVar: string, value: string, lineNum: number): void {
        // 检测指针赋值：ptr1 = ptr2
        const pointerAssignMatch = value.match(/^(\w+)$/);
        if (pointerAssignMatch) {
            const sourceVar = pointerAssignMatch[1];
            const sourceState = this.variableStates.get(sourceVar);
            const targetState = this.variableStates.get(targetVar);
            
            if (sourceState && targetState && 
                sourceState.type === 'pointer' && targetState.type === 'pointer') {
                // 指针赋值传播：目标指针继承源指针的状态
                targetState.initialized = sourceState.initialized;
                targetState.value = sourceState.value;
                targetState.lastAssignedAt = lineNum;
                
                // 如果源指针是野指针或空指针，目标指针也变成相同状态
                if (sourceState.value === 'NULL' || !sourceState.initialized) {
                    targetState.value = sourceState.value;
                }
            }
        }
    }

    private detectPointerDereference(line: string, lineNum: number, reports: BugReport[]): void {
        // 检测指针解引用：*ptr, ptr->field, ptr[index], etc.（支持汉字变量名）
        const derefPatterns = [
            /\*([\w\u4e00-\u9fff]+)/,  // *ptr
            /([\w\u4e00-\u9fff]+)->/,  // ptr->field (结构体指针)
            /([\w\u4e00-\u9fff]+)\[/   // ptr[index] (数组指针)
        ];

        for (const pattern of derefPatterns) {
            const match = line.match(pattern);
            if (match) {
                const varName = match[1];
                const varState = this.variableStates.get(varName);
                
                if (varState && varState.type === 'pointer') {
                    // 检查指针是否为空或未初始化
                    if (varState.value === 'NULL' || !varState.initialized) {
                        let errorType = '空指针解引用';
                        let message = `指针 ${varName} 可能为空，但被解引用`;
                        
                        // 区分野指针和空指针
                        if (!varState.initialized) {
                            errorType = '野指针解引用';
                            message = `指针 ${varName} 未初始化，但被解引用`;
                        }
                        
                        reports.push({
                            line_number: lineNum,
                            error_type: errorType,
                            severity: 'Error',
                            message: message,
                            suggestion: '在使用指针前检查是否为NULL或进行初始化',
                            code_snippet: line.trim(),
                            module_name: 'memory_safety'
                        });
                    }
                }
            }
        }
    }

    private processMemoryOperations(line: string, lineNum: number): void {
        // 检测malloc/calloc/realloc
        const allocMatch = line.match(/(\w+)\s*=\s*(malloc|calloc|realloc)\s*\(/);
        if (allocMatch) {
            const varName = allocMatch[1];
            if (this.variableStates.has(varName)) {
                const varState = this.variableStates.get(varName)!;
                varState.initialized = true;
                varState.value = 'malloc_result';
                varState.lastAssignedAt = lineNum;
            }
        }

        // 检测free调用
        const freeMatch = line.match(/free\s*\(\s*(\w+)/);
        if (freeMatch) {
            const varName = freeMatch[1];
            if (this.variableStates.has(varName)) {
                const varState = this.variableStates.get(varName)!;
                varState.value = 'freed';
                varState.lastAssignedAt = lineNum;
            }
        }

        // 检测指针赋值为NULL
        const nullAssignMatch = line.match(/(\w+)\s*=\s*NULL/);
        if (nullAssignMatch) {
            const varName = nullAssignMatch[1];
            if (this.variableStates.has(varName)) {
                const varState = this.variableStates.get(varName)!;
                varState.value = 'NULL';
                varState.lastAssignedAt = lineNum;
            }
        }
    }

    private detectMemoryLeaks(reports: BugReport[], lines: string[]): void {
        // 检测内存泄漏：malloc但未free的变量
        for (const [varName, varState] of this.variableStates) {
            if (varState.type === 'pointer' && 
                varState.value === 'malloc_result' && 
                varState.initialized) {
                
                // 检查是否有return语句包含该变量
                let hasReturn = false;
                for (let i = varState.lastAssignedAt; i < lines.length; i++) {
                    if (lines[i].includes('return') && lines[i].includes(varName)) {
                        hasReturn = true;
                        break;
                    }
                }
                
                if (!hasReturn) {
                    reports.push({
                        line_number: varState.lastAssignedAt,
                        error_type: '内存泄漏',
                        severity: 'Warning',
                        message: `变量 ${varName} 分配了内存但未释放`,
                        suggestion: '在适当位置调用free()释放内存或return该变量',
                        code_snippet: lines[varState.lastAssignedAt - 1].trim(),
                        module_name: 'memory_safety'
                    });
                }
            }
        }
    }

    private cleanupScopeVariables(): void {
        // 清理当前作用域的变量
        for (const [varName, varState] of this.variableStates) {
            if (varState.scope > this.scopeLevel) {
                this.variableStates.delete(varName);
            }
        }
    }

    private detectVariableState(lines: string[], filePath: string): BugReport[] {
        const reports: BugReport[] = [];
        const variables: { [key: string]: { declared: number, initialized: boolean, used: number[], inStruct: boolean, inFunction: boolean } } = {};
        let inStructDefinition = false;
        let inFunctionDefinition = false;
        let braceLevel = 0;

        for (let i = 0; i < lines.length; i++) {
            const originalLine = lines[i];
            const lineNum = i + 1;
            
            // 移除注释，获取纯代码
            const line = this.removeComments(originalLine);
            
            // 跳过空行
            if (line.trim().length === 0) {
                continue;
            }

            // 检测函数定义开始
            if (this.isFunctionDefinition(line)) {
                inFunctionDefinition = true;
            }

            // 检测结构体定义开始
            if (line.includes('struct') && line.includes('{')) {
                inStructDefinition = true;
            }

            // 检测大括号层级
            braceLevel += (line.match(/\{/g) || []).length;
            braceLevel -= (line.match(/\}/g) || []).length;

            // 检测结构体定义结束
            if (inStructDefinition && braceLevel === 0 && line.includes('}')) {
                inStructDefinition = false;
            }

            // 检测函数定义结束（当大括号层级回到函数定义前的层级时）
            if (inFunctionDefinition && braceLevel === 0 && line.includes('}')) {
                inFunctionDefinition = false;
            }

            // 检测变量声明（排除函数定义中的参数）
            const declMatch = line.match(this.patterns['variable_declaration']);
            if (declMatch && !this.isFunctionDefinition(line)) {
                const varName = declMatch[2];
                const isInitialized = line.includes('=');
                variables[varName] = {
                    declared: lineNum,
                    initialized: isInitialized,
                    used: [],
                    inStruct: inStructDefinition,
                    inFunction: inFunctionDefinition
                };
            }

            // 检测变量使用（排除函数定义中的使用）
            for (const varName of Object.keys(variables)) {
                if (line.includes(varName) && 
                    !line.includes('=') && 
                    !line.includes('int ') && 
                    !line.includes('char ') &&
                    !this.isFunctionDefinition(line) &&
                    !this.isFunctionCall(line, varName)) {
                    variables[varName].used.push(lineNum);
                }
            }
        }

        // 检测未初始化变量使用（排除结构体定义和函数定义内的变量）
        for (const [varName, info] of Object.entries(variables)) {
            if (!info.initialized && info.used.length > 0 && !info.inStruct && !info.inFunction) {
                for (const useLine of info.used) {
                    reports.push({
                        line_number: useLine,
                        error_type: '未初始化变量',
                        severity: 'Warning',
                        message: `变量 ${varName} 在使用前未初始化`,
                        suggestion: '在使用变量前为其赋值',
                        code_snippet: lines[useLine - 1].trim(),
                        module_name: 'variable_state'
                    });
                }
            }
        }

        return reports;
    }

    private detectStandardLibrary(lines: string[], filePath: string): BugReport[] {
        const reports: BugReport[] = [];
        const includes: Set<string> = new Set();

        // 检测头文件包含
        for (let i = 0; i < lines.length; i++) {
            const originalLine = lines[i];
            const lineNum = i + 1;
            
            // 移除注释，获取纯代码
            const line = this.removeComments(originalLine);
            
            // 跳过空行
            if (line.trim().length === 0) {
                continue;
            }

            if (line.includes('#include')) {
                const includeMatch = line.match(/#include\s*[<"]([^>"]+)[>"]/);
                if (includeMatch) {
                    includes.add(includeMatch[1]);
                }
            }

            // 检测printf使用
            if (line.match(this.patterns['printf']) && !includes.has('stdio.h')) {
                reports.push({
                    line_number: lineNum,
                    error_type: '缺失头文件',
                    severity: 'Error',
                    message: '使用printf但未包含stdio.h',
                    suggestion: '添加 #include <stdio.h>',
                    code_snippet: line.trim(),
                    module_name: 'standard_library'
                });
            }

            // 检测scanf使用
            if (line.match(this.patterns['scanf'])) {
                if (!includes.has('stdio.h')) {
                    reports.push({
                        line_number: lineNum,
                        error_type: '缺失头文件',
                        severity: 'Error',
                        message: '使用scanf但未包含stdio.h',
                        suggestion: '添加 #include <stdio.h>',
                        code_snippet: line.trim(),
                        module_name: 'standard_library'
                    });
                }

                // 检测scanf缺少&（只对非指针变量）
                if (!line.includes('&') && line.includes('%')) {
                    // 检查是否是字符串输入（不需要&）
                    const isStringInput = line.includes('"%s"') || line.includes("'%s'");
                    if (!isStringInput) {
                        reports.push({
                            line_number: lineNum,
                            error_type: 'scanf参数错误',
                            severity: 'Warning',
                            message: 'scanf可能缺少&操作符',
                            suggestion: '检查scanf参数是否需要&操作符',
                            code_snippet: line.trim(),
                            module_name: 'standard_library'
                        });
                    }
                }
            }
        }

        return reports;
    }

    private detectNumericControlFlow(lines: string[], filePath: string): BugReport[] {
        const reports: BugReport[] = [];

        for (let i = 0; i < lines.length; i++) {
            const originalLine = lines[i];
            const lineNum = i + 1;
            
            // 移除注释，获取纯代码
            const line = this.removeComments(originalLine);
            
            // 跳过空行
            if (line.trim().length === 0) {
                continue;
            }

            // 检测类型溢出
            const overflowMatch = line.match(/(char|short)\s+(\w+)\s*=\s*(\d+)/);
            if (overflowMatch) {
                const type = overflowMatch[1];
                const value = parseInt(overflowMatch[3]);
                
                if (type === 'char' && (value > 127 || value < -128)) {
                    reports.push({
                        line_number: lineNum,
                        error_type: '类型溢出',
                        severity: 'Warning',
                        message: `char类型溢出: ${value}`,
                        suggestion: '使用int类型或检查值范围',
                        code_snippet: line.trim(),
                        module_name: 'numeric_control_flow'
                    });
                }
            }

            // 检测死循环
            if (line.match(/while\s*\(\s*1\s*\)/) && !line.includes('break')) {
                reports.push({
                    line_number: lineNum,
                    error_type: '死循环',
                    severity: 'Warning',
                    message: '检测到可能的死循环',
                    suggestion: '添加break语句或修改循环条件',
                    code_snippet: line.trim(),
                    module_name: 'numeric_control_flow'
                });
            }
        }

        return reports;
    }

    private isFunctionParameter(line: string): boolean {
        // 检测是否是函数参数传递
        // 例如: func(NULL), func(ptr), func(&var)
        const functionCallPattern = /\w+\s*\([^)]*NULL[^)]*\)/;
        return functionCallPattern.test(line);
    }

    private isFunctionDefinition(line: string): boolean {
        // 检测函数定义：有返回类型、函数名、参数列表和大括号
        // 例如: int func(int x) { 或 void func() {
        const functionDefPattern = /^\s*(\w+\s+)*\w+\s+\w+\s*\([^)]*\)\s*\{/;
        return functionDefPattern.test(line);
    }

    private isFunctionCall(line: string, varName: string): boolean {
        // 检测是否是函数调用中的变量使用
        // 例如: func(varName) 或 func(ptr, varName)
        const functionCallPattern = new RegExp(`\\w+\\s*\\([^)]*\\b${varName}\\b[^)]*\\)`);
        return functionCallPattern.test(line);
    }
}

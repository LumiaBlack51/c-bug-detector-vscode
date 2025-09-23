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
        
        // 变量声明（支持汉字变量名、static关键字、指针类型，排除函数定义）
        this.patterns['variable_declaration'] = /^\s*(static\s+)?(const\s+)?(int|char|float|double|long|short|unsigned|signed|void|bool)\s*(\*)?\s*([\w\u4e00-\u9fff]+)\s*[;=]/;
        
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
                
                // 跳过结构体成员声明
                if (this.isStructMemberDeclaration(line)) {
                    continue;
                }
                
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
    
    private isStructMemberDeclaration(line: string): boolean {
        // 检查是否是结构体成员声明
        return line.match(/^\s*(int|char|float|double|long|short|unsigned|signed|void)\s*\*\s*\w+\s*;/) !== null;
    }

    private processMemoryOperations(line: string, lineNum: number): void {
        // 检测malloc/calloc/realloc - 支持声明和赋值在同一行
        const allocPatterns = [
            /(\w+)\s*=\s*(malloc|calloc|realloc)\s*\(/,  // ptr = malloc(...)
            /^\s*(int|char|float|double|long|short|unsigned|signed|void)\s*\*\s*(\w+)\s*=\s*(malloc|calloc|realloc)\s*\(/,  // int *ptr = malloc(...)
            /^\s*(\w+)\s*\*\s*(\w+)\s*=\s*(malloc|calloc|realloc)\s*\(/,  // struct Data *ptr = malloc(...)
            /(\w+)\[(\d+)\]\s*=\s*(malloc|calloc|realloc)\s*\(/,  // array[i] = malloc(...)
            /(\w+)->(\w+)\s*=\s*(malloc|calloc|realloc)\s*\(/  // struct->member = malloc(...)
        ];
        
        for (const pattern of allocPatterns) {
            const match = line.match(pattern);
            if (match) {
                let varName: string;
                
                if (pattern.source.includes('\\*')) {
                    // 声明和赋值在同一行
                    varName = match[2];
                } else if (pattern.source.includes('\\[')) {
                    // 数组元素赋值
                    varName = `${match[1]}[${match[2]}]`;
                } else if (pattern.source.includes('->')) {
                    // 结构体成员赋值
                    varName = `${match[1]}->${match[2]}`;
                } else {
                    // 只有赋值
                    varName = match[1];
                }
                
                // 如果变量不存在，创建一个新的状态
                if (!this.variableStates.has(varName)) {
                    this.variableStates.set(varName, {
                        name: varName,
                        type: 'pointer',
                        initialized: false,
                        value: null,
                        declaredAt: lineNum,
                        lastAssignedAt: 0,
                        scope: this.scopeLevel
                    });
                }
                
                const varState = this.variableStates.get(varName)!;
                varState.initialized = true;
                varState.value = 'malloc_result';
                varState.lastAssignedAt = lineNum;
                varState.type = 'pointer';
            }
        }

        // 检测free调用 - 支持更多模式
        const freePatterns = [
            /free\s*\(\s*(\w+)/,  // free(ptr)
            /free\s*\(\s*(\w+)\[(\d+)\]/,  // free(array[i])
            /free\s*\(\s*(\w+)->(\w+)/  // free(struct->member)
        ];
        
        for (const pattern of freePatterns) {
            const match = line.match(pattern);
            if (match) {
                let varName: string;
                
                if (pattern.source.includes('\\[')) {
                    // 数组元素释放
                    varName = `${match[1]}[${match[2]}]`;
                } else if (pattern.source.includes('->')) {
                    // 结构体成员释放
                    varName = `${match[1]}->${match[2]}`;
                } else {
                    // 普通变量释放
                    varName = match[1];
                }
                
                if (this.variableStates.has(varName)) {
                    const varState = this.variableStates.get(varName)!;
                    varState.value = 'freed';
                    varState.lastAssignedAt = lineNum;
                }
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
                
                // 检查是否有free调用
                let hasFree = false;
                let hasReturn = false;
                
                for (let i = varState.lastAssignedAt; i < lines.length; i++) {
                    const line = lines[i];
                    
                    // 检查free调用 - 支持更多模式
                    if (this.isFreeCall(line, varName)) {
                        hasFree = true;
                        break;
                    }
                    
                    // 检查return语句
                    if (line.includes('return') && line.includes(varName)) {
                        hasReturn = true;
                        break;
                    }
                }
                
                if (!hasFree && !hasReturn) {
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
    
    private isFreeCall(line: string, varName: string): boolean {
        // 检查是否是free调用，支持多种模式
        const freePatterns = [
            new RegExp(`free\\s*\\(\\s*${varName}\\s*\\)`),  // free(varName)
            new RegExp(`free\\s*\\(\\s*${varName}\\[\\d+\\]\\s*\\)`),  // free(varName[i])
            new RegExp(`free\\s*\\(\\s*${varName}->\\w+\\s*\\)`)  // free(varName->member)
        ];
        
        for (const pattern of freePatterns) {
            if (pattern.test(line)) {
                return true;
            }
        }
        
        return false;
    }

    private cleanupScopeVariables(): void {
        // 改进的作用域清理逻辑
        // 只清理比当前作用域层级更高的变量，但保留所有已分配内存的变量用于内存泄漏检测
        if (this.scopeLevel > 0) {
            for (const [varName, varState] of this.variableStates) {
                // 如果变量作用域更高且不是内存分配变量，则清理
                if (varState.scope > this.scopeLevel && varState.value !== 'malloc_result') {
                    this.variableStates.delete(varName);
                }
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
                const varName = declMatch[5]; // 第5个捕获组是变量名
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
                // 检查变量是否在行中被使用
                const varUsed = this.isVariableUsed(line, varName);
                if (varUsed && 
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

    private isVariableUsed(line: string, varName: string): boolean {
        // 检查变量是否在行中被使用
        // 排除变量声明、赋值语句中的变量名
        
        // 如果行中包含变量名
        if (!line.includes(varName)) {
            return false;
        }
        
        // 排除变量声明
        if (line.match(new RegExp(`^\\s*(static\\s+)?(const\\s+)?(int|char|float|double|long|short|unsigned|signed|void|bool)\\s*(\\*)?\\s*${varName}\\s*[;=]`))) {
            return false;
        }
        
        // 排除赋值语句中的变量名（左侧）
        if (line.match(new RegExp(`^\\s*${varName}\\s*=`))) {
            return false;
        }
        
        // 排除函数参数声明
        if (line.match(new RegExp(`\\([^)]*\\b${varName}\\b[^)]*\\)`))) {
            return false;
        }
        
        // 排除函数调用中的变量名（作为函数名）
        if (line.match(new RegExp(`^\\s*${varName}\\s*\\(`))) {
            return false;
        }
        
        // 其他情况认为是变量使用
        return true;
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
            this.detectDeadLoops(line, lineNum, reports, lines);
        }

        return reports;
    }

    private detectDeadLoops(line: string, lineNum: number, reports: BugReport[], lines: string[]): void {
        // 新的死循环检测逻辑：通过模拟执行循环代码来判断
        
        // 1. 检测for循环
        const forMatch = line.match(/for\s*\(\s*([^;]*);\s*([^;]*);\s*([^)]*)\)/);
        if (forMatch) {
            const init = forMatch[1].trim();
            const condition = forMatch[2].trim();
            const increment = forMatch[3].trim();
            
            // 检查是否是明显的死循环
            if (condition === '' || condition === '1' || condition === 'true') {
                // 检查循环体内是否有break或return
                if (!this.hasExitStatement(lines, lineNum, 20)) {
                    reports.push({
                        line_number: lineNum,
                        error_type: '死循环',
                        severity: 'Warning',
                        message: '检测到for循环死循环',
                        suggestion: '添加break语句或return语句',
                        code_snippet: line.trim(),
                        module_name: 'numeric_control_flow'
                    });
                }
            } else {
                // 模拟执行循环，检查是否会在合理次数内退出
                if (this.simulateLoopExecution(init, condition, increment, lines, lineNum)) {
                    reports.push({
                        line_number: lineNum,
                        error_type: '死循环',
                        severity: 'Warning',
                        message: '通过模拟执行检测到死循环',
                        suggestion: '检查循环条件和增量',
                        code_snippet: line.trim(),
                        module_name: 'numeric_control_flow'
                    });
                }
            }
        }
        
        // 2. 检测while循环
        const whileMatch = line.match(/while\s*\(\s*([^)]+)\s*\)/);
        if (whileMatch) {
            const condition = whileMatch[1].trim();
            
            // 检查是否是明显的死循环
            if (condition === '1' || condition === 'true') {
                // 检查循环体内是否有break或return
                if (!this.hasExitStatement(lines, lineNum, 20)) {
                    reports.push({
                        line_number: lineNum,
                        error_type: '死循环',
                        severity: 'Warning',
                        message: '检测到while(1)死循环',
                        suggestion: '添加break语句或return语句',
                        code_snippet: line.trim(),
                        module_name: 'numeric_control_flow'
                    });
                }
            } else {
                // 模拟执行循环，检查是否会在合理次数内退出
                if (this.simulateWhileLoop(condition, lines, lineNum)) {
                    reports.push({
                        line_number: lineNum,
                        error_type: '死循环',
                        severity: 'Warning',
                        message: '通过模拟执行检测到while循环死循环',
                        suggestion: '检查循环条件和循环体内的变量修改',
                        code_snippet: line.trim(),
                        module_name: 'numeric_control_flow'
                    });
                }
            }
        }
        
        // 3. 检测do-while循环
        const doWhileMatch = line.match(/do\s*\{/);
        if (doWhileMatch) {
            // 查找对应的while条件
            let whileLineNum = lineNum;
            let braceCount = 0;
            let foundWhile = false;
            
            for (let i = lineNum; i < Math.min(lineNum + 50, lines.length); i++) {
                const currentLine = lines[i];
                
                // 计算大括号数量
                for (const char of currentLine) {
                    if (char === '{') braceCount++;
                    if (char === '}') braceCount--;
                }
                
                // 如果大括号平衡，说明找到了while条件
                if (braceCount === 0 && currentLine.includes('while')) {
                    whileLineNum = i;
                    foundWhile = true;
                    break;
                }
            }
            
            if (foundWhile) {
                const whileConditionMatch = lines[whileLineNum].match(/while\s*\(\s*([^)]+)\s*\)/);
                if (whileConditionMatch) {
                    const condition = whileConditionMatch[1].trim();
                    
                    // 检查是否是明显的死循环
                    if (condition === '1' || condition === 'true') {
                        // 检查循环体内是否有break或return
                        if (!this.hasExitStatement(lines, lineNum, 20)) {
                            reports.push({
                                line_number: lineNum,
                                error_type: '死循环',
                                severity: 'Warning',
                                message: '检测到do-while循环死循环',
                                suggestion: '添加break语句或return语句',
                                code_snippet: line.trim(),
                                module_name: 'numeric_control_flow'
                            });
                        }
                    } else {
                        // 模拟执行循环，检查是否会在合理次数内退出
                        if (this.simulateWhileLoop(condition, lines, lineNum)) {
                            reports.push({
                                line_number: lineNum,
                                error_type: '死循环',
                                severity: 'Warning',
                                message: '通过模拟执行检测到do-while循环死循环',
                                suggestion: '检查循环条件和循环体内的变量修改',
                                code_snippet: line.trim(),
                                module_name: 'numeric_control_flow'
                            });
                        }
                    }
                }
            }
        }
    }
    
    private hasExitStatement(lines: string[], startLine: number, maxLines: number): boolean {
        // 检查循环体内是否有break或return语句
        for (let i = startLine; i < Math.min(startLine + maxLines, lines.length); i++) {
            const line = lines[i];
            if (line.includes('break') || line.includes('return')) {
                return true;
            }
            if (line.includes('}')) {
                break;
            }
        }
        return false;
    }
    
    private simulateLoopExecution(init: string, condition: string, increment: string, lines: string[], lineNum: number): boolean {
        // 模拟执行for循环，最多执行100000次
        const maxIterations = 100000;
        
        try {
            // 解析初始化语句
            const initValue = this.parseInitialization(init);
            if (initValue === null) return false;
            
            // 解析条件语句
            const conditionExpr = this.parseCondition(condition);
            if (conditionExpr === null) return false;
            
            // 解析增量语句
            const incrementExpr = this.parseIncrement(increment);
            if (incrementExpr === null) return false;
            
            // 检查是否有break或return（简化检查）
            if (this.hasExitStatement(lines, lineNum, 20)) {
                return false; // 有退出语句，不是死循环
            }
            
            // 分析跳出条件是否可达
            if (this.isExitConditionUnreachable(initValue.value, conditionExpr, incrementExpr)) {
                return true; // 跳出条件不可达，是死循环
            }
            
            // 模拟执行
            let currentValue = initValue.value;
            let iterations = 0;
            
            while (iterations < maxIterations) {
                // 检查条件
                if (!this.evaluateCondition(currentValue, conditionExpr)) {
                    return false; // 循环会退出，不是死循环
                }
                
                // 执行增量
                currentValue = this.applyIncrement(currentValue, incrementExpr);
                iterations++;
            }
            
            return true; // 执行了maxIterations次仍未退出，是死循环
            
        } catch (error) {
            // 解析失败，使用简单的启发式方法
            return this.simpleDeadLoopCheck(init, condition, increment);
        }
    }
    
    private simulateWhileLoop(condition: string, lines: string[], lineNum: number): boolean {
        // 模拟执行while循环，最多执行100000次
        const maxIterations = 100000;
        
        try {
            // 解析条件语句
            const conditionExpr = this.parseCondition(condition);
            if (conditionExpr === null) return false;
            
            // 检查是否有break或return
            if (this.hasExitStatement(lines, lineNum, 20)) {
                return false;
            }
            
            // 简化的模拟：如果条件总是为真且没有退出机制，就是死循环
            if (condition === '1' || condition === 'true') {
                return true;
            }
            
            // 分析循环体内的变量修改情况
            const loopBodyAnalysis = this.analyzeLoopBody(lines, lineNum, conditionExpr.variable);
            
            // 如果循环变量在循环体内从未被修改，且条件总是为真，则是死循环
            if (!loopBodyAnalysis.hasVariableModification && this.isConditionAlwaysTrue(conditionExpr)) {
                return true;
            }
            
            // 如果循环变量被赋值为自己，且没有其他修改，则是死循环
            if (loopBodyAnalysis.hasSelfAssignment && !loopBodyAnalysis.hasOtherModification) {
                return true;
            }
            
            // 如果循环变量依赖于外部变量，且外部变量从未被修改，则是死循环
            if (loopBodyAnalysis.dependsOnExternalVariable && !loopBodyAnalysis.hasExternalModification) {
                return true;
            }
            
            return false;
            
        } catch (error) {
            return false;
        }
    }
    
    private analyzeLoopBody(lines: string[], startLine: number, variableName: string): {
        hasVariableModification: boolean,
        hasSelfAssignment: boolean,
        hasOtherModification: boolean,
        dependsOnExternalVariable: boolean,
        hasExternalModification: boolean
    } {
        let hasVariableModification = false;
        let hasSelfAssignment = false;
        let hasOtherModification = false;
        let dependsOnExternalVariable = false;
        let hasExternalModification = false;
        
        // 分析循环体（最多20行）
        for (let i = startLine; i < Math.min(startLine + 20, lines.length); i++) {
            const line = lines[i];
            
            // 如果遇到结束大括号，停止分析
            if (line.includes('}')) {
                break;
            }
            
            // 检查变量修改
            if (line.includes(`${variableName} =`)) {
                hasVariableModification = true;
                
                // 检查是否是自赋值
                if (line.includes(`${variableName} = ${variableName}`)) {
                    hasSelfAssignment = true;
                } else {
                    hasOtherModification = true;
                }
            }
            
            // 检查递增递减
            if (line.includes(`${variableName}++`) || line.includes(`${variableName}--`) ||
                line.includes(`${variableName} +=`) || line.includes(`${variableName} -=`)) {
                hasVariableModification = true;
                hasOtherModification = true;
            }
            
            // 检查是否依赖外部变量
            if (line.includes('=') && !line.includes(variableName)) {
                // 检查是否有其他变量的赋值
                const otherVarMatch = line.match(/(\w+)\s*=/);
                if (otherVarMatch && otherVarMatch[1] !== variableName) {
                    dependsOnExternalVariable = true;
                    hasExternalModification = true;
                }
            }
        }
        
        return {
            hasVariableModification,
            hasSelfAssignment,
            hasOtherModification,
            dependsOnExternalVariable,
            hasExternalModification
        };
    }
    
    private isConditionAlwaysTrue(condition: { variable: string, operator: string, value: number }): boolean {
        // 判断条件是否总是为真
        const operator = condition.operator;
        const value = condition.value;
        
        // 一些明显总是为真的条件
        if (operator === '>=' && value <= 0) return true;
        if (operator === '>' && value < 0) return true;
        if (operator === '!=' && value === 0) return true;
        
        return false;
    }
    
    private parseInitialization(init: string): { value: number } | null {
        // 解析初始化语句，如 "int i = 10" 或 "i = 10"
        const match = init.match(/(\w+)\s*=\s*(\d+)/);
        if (match) {
            return { value: parseInt(match[2]) };
        }
        return null;
    }
    
    private parseCondition(condition: string): { variable: string, operator: string, value: number } | null {
        // 解析条件语句，如 "i < 10" 或 "i >= 10"
        const match = condition.match(/(\w+)\s*([><=!]+)\s*(\d+)/);
        if (match) {
            return {
                variable: match[1],
                operator: match[2],
                value: parseInt(match[3])
            };
        }
        return null;
    }
    
    private parseIncrement(increment: string): { variable: string, operation: string, value: number } | null {
        // 解析增量语句，如 "i++" 或 "i += 3"
        const match = increment.match(/(\w+)\s*([+-])\s*=\s*(\d+)/);
        if (match) {
            return {
                variable: match[1],
                operation: match[2],
                value: parseInt(match[3])
            };
        }
        
        // 处理 i++ 或 i--
        const simpleMatch = increment.match(/(\w+)\s*([+-])\s*([+-])/);
        if (simpleMatch) {
            return {
                variable: simpleMatch[1],
                operation: simpleMatch[2],
                value: 1
            };
        }
        
        return null;
    }
    
    private evaluateCondition(currentValue: number, condition: { variable: string, operator: string, value: number }): boolean {
        // 评估条件表达式
        switch (condition.operator) {
            case '<': return currentValue < condition.value;
            case '>': return currentValue > condition.value;
            case '<=': return currentValue <= condition.value;
            case '>=': return currentValue >= condition.value;
            case '==': return currentValue === condition.value;
            case '!=': return currentValue !== condition.value;
            default: return true;
        }
    }
    
    private applyIncrement(currentValue: number, increment: { variable: string, operation: string, value: number }): number {
        // 应用增量操作
        if (increment.operation === '+') {
            return currentValue + increment.value;
        } else {
            return currentValue - increment.value;
        }
    }
    
    private simpleDeadLoopCheck(init: string, condition: string, increment: string): boolean {
        // 简化的死循环检查，用于解析失败的情况
        const initMatch = init.match(/(\w+)\s*=\s*(\d+)/);
        const conditionMatch = condition.match(/(\w+)\s*([><=!]+)\s*(\d+)/);
        const incrementMatch = increment.match(/(\w+)\s*([+-])\s*=\s*(\d+)/);
        
        if (initMatch && conditionMatch && incrementMatch) {
            const initValue = parseInt(initMatch[2]);
            const operator = conditionMatch[2];
            const conditionValue = parseInt(conditionMatch[3]);
            const incOp = incrementMatch[2];
            const incValue = parseInt(incrementMatch[3]);
            
            return this.isDeadLoopCondition(initValue, operator, conditionValue, incOp, incValue);
        }
        
        return false;
    }
    
    private isExitConditionUnreachable(initValue: number, condition: { variable: string, operator: string, value: number }, increment: { variable: string, operation: string, value: number }): boolean {
        // 分析跳出条件是否可达
        // 跳出条件：当条件为false时循环退出
        
        const operator = condition.operator;
        const conditionValue = condition.value;
        const incOp = increment.operation;
        const incValue = increment.value;
        
        // 1. 步长过大检测：i == 10, i += 3
        if (operator === '==' && incOp === '+') {
            // 检查是否能达到目标值
            if (initValue < conditionValue) {
                // 计算需要多少次迭代才能达到目标值
                const stepsNeeded = conditionValue - initValue;
                if (stepsNeeded % incValue !== 0) {
                    return true; // 步长过大，永远达不到目标值
                }
            } else if (initValue > conditionValue) {
                // 初始值已经大于目标值，且还在增加
                return true; // 永远达不到目标值
            }
        }
        
        // 2. 循环条件错误检测
        if (operator === '>=' && incOp === '+') {
            // 例如: i >= 10, i++ - 如果i从10开始，永远不会小于10
            return initValue >= conditionValue;
        }
        
        if (operator === '<' && incOp === '-') {
            // 例如: i < 10, i-- - 如果i从0开始，永远不会大于等于10
            return initValue < conditionValue;
        }
        
        if (operator === '>' && incOp === '-') {
            // 例如: i > 10, i-- - 如果i从0开始，永远不会大于10
            return initValue <= conditionValue;
        }
        
        if (operator === '<=' && incOp === '+') {
            // 例如: i <= 10, i++ - 如果i从10开始，永远不会小于等于10
            return initValue > conditionValue;
        }
        
        // 3. 浮点数精度问题检测
        if (operator === '!=' && incOp === '+') {
            // 例如: f != 1.0f, f += 0.1f - 浮点数精度问题
            return true; // 浮点数比较通常有问题
        }
        
        return false;
    }
    
    private isDeadLoopCondition(initValue: number, operator: string, conditionValue: number, incOp: string, incValue: number): boolean {
        // 简化的死循环检测逻辑
        // 这里只检测一些明显的情况
        
        if (operator === '>=' && incOp === '+') {
            // 例如: i >= 10, i++ - 如果i从10开始，永远不会小于10
            return initValue >= conditionValue;
        }
        
        if (operator === '<' && incOp === '-') {
            // 例如: i < 10, i-- - 如果i从0开始，永远不会大于等于10
            return initValue < conditionValue;
        }
        
        if (operator === '==' && incOp === '+') {
            // 例如: i == 10, i += 3 - 如果i从0开始，会跳过10
            return initValue < conditionValue && (conditionValue - initValue) % incValue !== 0;
        }
        
        return false;
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

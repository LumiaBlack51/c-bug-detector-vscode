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

export class CDetector {
    private patterns: { [key: string]: RegExp } = {};

    constructor() {
        this.initializePatterns();
    }

    private initializePatterns(): void {
        // 函数定义
        this.patterns['function_definition'] = /^\s*(\w+)\s+(\w+)\s*\([^)]*\)\s*\{/;
        
        // 变量声明
        this.patterns['variable_declaration'] = /^\s*(int|char|float|double|long|short|unsigned|signed|void)\s+(\w+)/;
        
        // 函数调用
        this.patterns['function_call'] = /(\w+)\s*\(/;
        
        // malloc/calloc/realloc
        this.patterns['memory_allocation'] = /(\w+)\s*=\s*(malloc|calloc|realloc)\s*\(/;
        
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
        
        // 赋值语句
        this.patterns['assignment'] = /(\w+)\s*=\s*(.+)/;
        
        // 指针解引用
        this.patterns['pointer_dereference'] = /\*(\w+)/;
        
        // 取地址
        this.patterns['address_of'] = /&(\w+)/;
    }

    public analyzeFile(filePath: string): AnalysisResult {
        try {
            const content = this.readFileContent(filePath);
            const lines = content.split('\n');
            const reports: BugReport[] = [];

            // 运行所有检测模块
            reports.push(...this.detectMemorySafety(lines, filePath));
            reports.push(...this.detectVariableState(lines, filePath));
            reports.push(...this.detectStandardLibrary(lines, filePath));
            reports.push(...this.detectNumericControlFlow(lines, filePath));

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
        const allocations: { [key: string]: number } = {};
        const frees: Set<string> = new Set();

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const lineNum = i + 1;

            // 检测内存分配
            const allocMatch = line.match(this.patterns['memory_allocation']);
            if (allocMatch) {
                const varName = allocMatch[1];
                allocations[varName] = lineNum;
            }

            // 检测free调用
            const freeMatch = line.match(this.patterns['memory_free']);
            if (freeMatch) {
                // 简单检测：如果free后面有变量名
                const varMatch = line.match(/free\s*\(\s*(\w+)/);
                if (varMatch) {
                    frees.add(varMatch[1]);
                }
            }

            // 检测空指针解引用（排除函数参数传递）
            if (line.includes('*') && line.includes('NULL') && !this.isFunctionParameter(line)) {
                reports.push({
                    line_number: lineNum,
                    error_type: '空指针解引用',
                    severity: 'Error',
                    message: '检测到可能的空指针解引用',
                    suggestion: '在使用指针前检查是否为NULL',
                    code_snippet: line.trim(),
                    module_name: 'memory_safety'
                });
            }
        }

        // 检测内存泄漏
        for (const [varName, lineNum] of Object.entries(allocations)) {
            if (!frees.has(varName)) {
                reports.push({
                    line_number: lineNum,
                    error_type: '内存泄漏',
                    severity: 'Warning',
                    message: `变量 ${varName} 分配了内存但未释放`,
                    suggestion: '在适当位置调用free()释放内存',
                    code_snippet: lines[lineNum - 1].trim(),
                    module_name: 'memory_safety'
                });
            }
        }

        return reports;
    }

    private detectVariableState(lines: string[], filePath: string): BugReport[] {
        const reports: BugReport[] = [];
        const variables: { [key: string]: { declared: number, initialized: boolean, used: number[], inStruct: boolean } } = {};
        let inStructDefinition = false;
        let braceLevel = 0;

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const lineNum = i + 1;

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

            // 检测变量声明
            const declMatch = line.match(this.patterns['variable_declaration']);
            if (declMatch) {
                const varName = declMatch[2];
                const isInitialized = line.includes('=');
                variables[varName] = {
                    declared: lineNum,
                    initialized: isInitialized,
                    used: [],
                    inStruct: inStructDefinition
                };
            }

            // 检测变量使用
            for (const varName of Object.keys(variables)) {
                if (line.includes(varName) && !line.includes('=') && !line.includes('int ') && !line.includes('char ')) {
                    variables[varName].used.push(lineNum);
                }
            }
        }

        // 检测未初始化变量使用（排除结构体定义内的变量）
        for (const [varName, info] of Object.entries(variables)) {
            if (!info.initialized && info.used.length > 0 && !info.inStruct) {
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
            const line = lines[i];
            const lineNum = i + 1;

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

                // 检测scanf缺少&
                if (!line.includes('&') && line.includes('%')) {
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

        return reports;
    }

    private detectNumericControlFlow(lines: string[], filePath: string): BugReport[] {
        const reports: BugReport[] = [];

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const lineNum = i + 1;

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
}

const fs = require('fs');
const path = require('path');

// 复制Python后端文件到插件目录
function copyBackendFiles() {
    const sourceDir = path.resolve(__dirname, '../../');
    const targetDir = path.resolve(__dirname, '../backend');
    
    // 创建backend目录
    if (!fs.existsSync(targetDir)) {
        fs.mkdirSync(targetDir, { recursive: true });
    }
    
    // 需要复制的文件列表（从core目录）
    const filesToCopy = [
        'core/main.py',
        'core/requirements.txt',
        'core/modules/memory_safety.py',
        'core/modules/variable_state.py',
        'core/modules/standard_library.py',
        'core/modules/numeric_control_flow.py',
        'core/modules/__init__.py',
        'core/utils/error_reporter.py',
        'core/utils/code_parser.py',
        'core/utils/__init__.py'
    ];
    
    // 复制文件
    filesToCopy.forEach(file => {
        const sourcePath = path.join(sourceDir, file);
        const targetPath = path.join(targetDir, file);
        
        if (fs.existsSync(sourcePath)) {
            // 创建目标目录
            const targetDirPath = path.dirname(targetPath);
            if (!fs.existsSync(targetDirPath)) {
                fs.mkdirSync(targetDirPath, { recursive: true });
            }
            
            // 复制文件
            fs.copyFileSync(sourcePath, targetPath);
            console.log(`复制: ${file}`);
        } else {
            console.warn(`文件不存在: ${sourcePath}`);
        }
    });
    
    console.log('后端文件复制完成！');
}

// 执行复制
copyBackendFiles();

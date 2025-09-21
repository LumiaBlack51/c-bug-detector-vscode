#!/bin/bash

# GitHub仓库设置脚本
# 用于初始化GitHub仓库并创建第一个release

echo "🚀 设置GitHub仓库..."

# 检查是否已配置远程仓库
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ 远程仓库已配置: $(git remote get-url origin)"
else
    echo "❌ 请先配置远程仓库:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/c-bug-detector.git"
    echo "   git push -u origin master"
    exit 1
fi

# 推送代码到GitHub
echo "📤 推送代码到GitHub..."
git push -u origin master

# 创建第一个release标签
echo "🏷️  创建release标签..."
git tag -a v1.0.0 -m "Release v1.0.0: Initial release with VS Code extension and command-line tool"
git push origin v1.0.0

echo "✅ GitHub仓库设置完成！"
echo ""
echo "📋 下一步操作:"
echo "1. 访问 https://github.com/YOUR_USERNAME/c-bug-detector"
echo "2. 检查GitHub Actions是否自动构建了VSIX文件"
echo "3. 在Releases页面下载生成的VSIX文件"
echo "4. 分享给用户使用"
echo ""
echo "🎉 项目已成功上传到GitHub！"

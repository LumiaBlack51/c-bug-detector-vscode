# GitHub仓库设置脚本 (PowerShell版本)
# 用于初始化GitHub仓库并创建第一个release

Write-Host "🚀 设置GitHub仓库..." -ForegroundColor Green

# 检查是否已配置远程仓库
try {
    $originUrl = git remote get-url origin 2>$null
    if ($originUrl) {
        Write-Host "✅ 远程仓库已配置: $originUrl" -ForegroundColor Green
    } else {
        throw "No remote configured"
    }
} catch {
    Write-Host "❌ 请先配置远程仓库:" -ForegroundColor Red
    Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/c-bug-detector.git" -ForegroundColor Yellow
    Write-Host "   git push -u origin master" -ForegroundColor Yellow
    exit 1
}

# 推送代码到GitHub
Write-Host "📤 推送代码到GitHub..." -ForegroundColor Blue
git push -u origin master

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 推送失败，请检查网络连接和权限" -ForegroundColor Red
    exit 1
}

# 创建第一个release标签
Write-Host "🏷️  创建release标签..." -ForegroundColor Blue
git tag -a v1.0.0 -m "Release v1.0.0: Initial release with VS Code extension and command-line tool"
git push origin v1.0.0

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 标签推送失败" -ForegroundColor Red
    exit 1
}

Write-Host "✅ GitHub仓库设置完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📋 下一步操作:" -ForegroundColor Cyan
Write-Host "1. 访问 https://github.com/YOUR_USERNAME/c-bug-detector" -ForegroundColor Yellow
Write-Host "2. 检查GitHub Actions是否自动构建了VSIX文件" -ForegroundColor Yellow
Write-Host "3. 在Releases页面下载生成的VSIX文件" -ForegroundColor Yellow
Write-Host "4. 分享给用户使用" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎉 项目已成功上传到GitHub！" -ForegroundColor Green

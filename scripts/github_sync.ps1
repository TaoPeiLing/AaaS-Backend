# GitHub同步脚本 - 适用于国内网络环境
# 作者：AI Assistant
# 用途：解决国内网络访问GitHub的问题

param(
    [string]$Method = "direct",
    [string]$Token = "your_github_token_here",
    [string]$Repo = "https://github.com/TaoPeiLing/AaaS-Backend.git"
)

Write-Host "=== GitHub同步脚本 ===" -ForegroundColor Green
Write-Host "当前方法: $Method" -ForegroundColor Yellow

switch ($Method) {
    "direct" {
        Write-Host "尝试直接连接GitHub..." -ForegroundColor Blue
        
        # 设置认证
        $env:GIT_ASKPASS = "echo"
        $env:GIT_USERNAME = "TaoPeiLing"
        $env:GIT_PASSWORD = $Token
        
        # 使用token认证的URL
        $authUrl = $Repo -replace "https://", "https://${Token}@"
        
        try {
            git remote set-url origin $authUrl
            git push -u origin main
            Write-Host "✅ 直接推送成功！" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ 直接连接失败: $_" -ForegroundColor Red
            Write-Host "建议尝试其他方法" -ForegroundColor Yellow
        }
    }
    
    "proxy" {
        Write-Host "使用代理连接GitHub..." -ForegroundColor Blue
        Write-Host "请确保您已经配置了HTTP代理" -ForegroundColor Yellow
        
        # 常见代理端口
        $proxyPorts = @("7890", "1080", "8080", "10809")
        
        foreach ($port in $proxyPorts) {
            Write-Host "尝试代理端口: $port" -ForegroundColor Cyan
            
            try {
                git config --global http.proxy "http://127.0.0.1:$port"
                git config --global https.proxy "http://127.0.0.1:$port"
                
                $authUrl = $Repo -replace "https://", "https://${Token}@"
                git remote set-url origin $authUrl
                git push -u origin main
                
                Write-Host "✅ 通过代理端口 $port 推送成功！" -ForegroundColor Green
                return
            }
            catch {
                Write-Host "代理端口 $port 失败" -ForegroundColor Red
                continue
            }
        }
        
        Write-Host "❌ 所有代理端口都失败了" -ForegroundColor Red
    }
    
    "bundle" {
        Write-Host "创建Git Bundle文件..." -ForegroundColor Blue
        
        $bundleFile = "aaas-project.bundle"
        git bundle create $bundleFile main
        
        Write-Host "✅ 已创建 $bundleFile" -ForegroundColor Green
        Write-Host "您可以：" -ForegroundColor Yellow
        Write-Host "1. 将bundle文件传输到有良好网络的环境" -ForegroundColor White
        Write-Host "2. 在那里解包并推送到GitHub" -ForegroundColor White
        Write-Host "3. 解包命令: git clone $bundleFile aaas-temp" -ForegroundColor Gray
    }
    
    default {
        Write-Host "❌ 未知方法: $Method" -ForegroundColor Red
        Write-Host "可用方法: direct, proxy, bundle" -ForegroundColor Yellow
    }
}

Write-Host "`n=== 其他建议 ===" -ForegroundColor Green
Write-Host "1. 使用VPN或代理服务" -ForegroundColor White
Write-Host "2. 使用GitHub Desktop客户端" -ForegroundColor White
Write-Host "3. 使用Gitee等国内代码托管平台作为中转" -ForegroundColor White
Write-Host "4. 在云服务器上操作（如阿里云、腾讯云）" -ForegroundColor White
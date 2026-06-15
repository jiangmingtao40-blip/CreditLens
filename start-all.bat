@echo off
chcp 65001 >nul
echo ========================================
echo   征信报告AI服务 - 一键启动
echo ========================================
echo.

:: 启动Python AI服务
echo [1/3] 启动AI服务 (端口8081)...
start "AI-Service" cmd /k "cd /d %~dp0ai-service && python server_simple.py"

:: 等待2秒
timeout /t 2 /nobreak >nul

:: 启动Java业务服务
echo [2/3] 启动业务服务 (端口20510)...
start "Java-Service" cmd /k "java -jar %~dp0crmeb_java\crmeb\crmeb-front\target\Crmeb-front.jar --spring.profiles.active=dev"

:: 等待2秒
timeout /t 2 /nobreak >nul

:: 启动uni-app前端
echo [3/3] 启动前端服务 (端口5173)...
start "UniApp-Frontend" cmd /k "cd /d %~dp0credit-app && npm run dev:h5"

echo.
echo ========================================
echo   所有服务已启动！
echo ========================================
echo   AI服务:     http://localhost:8081
echo   前端服务:   http://localhost:5173
echo   业务服务:   http://localhost:20510
echo ========================================
echo.
echo 按任意键关闭此窗口...
pause >nul

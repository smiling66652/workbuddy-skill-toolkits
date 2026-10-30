@echo off
chcp 936 >nul
setlocal
set "PKGNAME={PKGNAME}"
set "SRC=%~dp0payload"
set "DEST=%USERPROFILE%\.workbuddy\skills\%PKGNAME%"

echo ============================================================
echo   %PKGNAME%  -  离线安装
echo ============================================================
echo   安装到：%DEST%
echo.

if not exist "%SRC%\SKILL.md" (
    echo [错误] 找不到 payload\SKILL.md
    echo        请确认已完整解压本压缩包，且 install.bat 与 payload 在同一层。
    echo.
    pause
    exit /b 1
)

rem ---------- 1/5 定位 Node ----------
set "NODE="
"%SystemRoot%\System32\where.exe" node >nul 2>nul
if not errorlevel 1 set "NODE=node"

if not defined NODE if exist "%USERPROFILE%\.workbuddy\binaries\node\versions" (
    for /f "delims=" %%v in ('dir /b /ad /o-n "%USERPROFILE%\.workbuddy\binaries\node\versions" 2^>nul') do (
        if not defined NODE if exist "%USERPROFILE%\.workbuddy\binaries\node\versions\%%v\node.exe" set "NODE=%USERPROFILE%\.workbuddy\binaries\node\versions\%%v\node.exe"
    )
)
if defined NODE goto :node_found
echo [1/5] Node  : 未找到
{NODE_MISSING_NOTE}
goto :node_done
:node_found
echo [1/5] Node  : %NODE%
:node_done

rem ---------- 2/5 备份旧版 ----------
if not exist "%DEST%" goto :no_backup
set "BAK=%DEST%_backup_%RANDOM%"
echo [2/5] 备份  : 检测到旧版，先移到 %BAK%
move "%DEST%" "%BAK%" >nul 2>nul
if exist "%DEST%" (
    echo        [失败] 旧版目录被占用，无法备份。
    echo        请完全退出 WorkBuddy（右下角托盘也退）后重新运行本脚本。
    echo.
    pause
    exit /b 1
)
echo        完成
goto :backup_done
:no_backup
echo [2/5] 备份  : 无旧版，跳过
:backup_done

rem ---------- 3/5 复制 ----------
echo [3/5] 复制  : 正在安装...
if not exist "%USERPROFILE%\.workbuddy\skills" mkdir "%USERPROFILE%\.workbuddy\skills" >nul 2>nul
xcopy "%SRC%" "%DEST%\" /E /I /H /Y /Q >nul
if not exist "%DEST%\SKILL.md" (
    echo        [失败] 复制后未找到 SKILL.md，安装未完成。
    echo.
    pause
    exit /b 1
)
echo        完成

rem ---------- 4/5 依赖检查 ----------
if not exist "%DEST%\node_modules" goto :no_deps
echo [4/5] 依赖  : 已随包携带 node_modules，无需联网
goto :deps_done
:no_deps
echo [4/5] 依赖  : 本包无 node_modules（若运行报缺模块，请自行 npm install）
:deps_done

rem ---------- 5/5 自检 ----------
echo [5/5] 自检  : 核对已安装文件数
set "N=0"
for /f %%c in ('dir /b /s /a-d "%DEST%" ^| "%SystemRoot%\System32\find.exe" /c /v ""') do set "N=%%c"
echo        已安装 %N% 个文件
if "%N%"=="0" (
    echo        [失败] 一个文件都没复制成功，请检查权限或杀毒软件拦截。
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   安装完成：%PKGNAME%
echo   重启 WorkBuddy 后即可使用（或新开一个会话）
echo ============================================================
echo.
pause

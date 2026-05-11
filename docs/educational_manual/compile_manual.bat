@echo off
REM File version: 1.0; date: 2026-05-11
setlocal
cd /d "%~dp0"

where lualatex >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    call :add_miktex_from_registry HKCU\Software\MiKTeX.org\MiKTeX\2.9\Core
)

where lualatex >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    call :add_miktex_from_registry HKLM\Software\MiKTeX.org\MiKTeX\2.9\Core
)

where lualatex >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    if exist "%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\lualatex.exe" (
        set "PATH=%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64;%PATH%"
    )
)

where lualatex >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo lualatex was not found. Install MiKTeX or add its miktex\bin\x64 folder to PATH.
    exit /b 1
)

where latexmk >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    latexmk -pdf -lualatex -interaction=nonstopmode -file-line-error manual.tex
    if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
    goto :done
)

echo latexmk was not found. Falling back to lualatex/biber/makeindex.
where biber >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo biber was not found. Install it with MiKTeX Console.
    exit /b 1
)

where makeindex >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo makeindex was not found. Install it with MiKTeX Console.
    exit /b 1
)

lualatex -interaction=nonstopmode -file-line-error manual.tex
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
biber manual
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
makeindex manual
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
lualatex -interaction=nonstopmode -file-line-error manual.tex
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
lualatex -interaction=nonstopmode -file-line-error manual.tex
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

:done
echo Manual build finished.
endlocal
exit /b 0

:add_miktex_from_registry
for /f "tokens=2,*" %%A in ('reg query "%~1" /v UserInstall 2^>nul ^| find "UserInstall"') do (
    if exist "%%B\miktex\bin\x64\lualatex.exe" (
        set "PATH=%%B\miktex\bin\x64;%PATH%"
    )
)
exit /b 0

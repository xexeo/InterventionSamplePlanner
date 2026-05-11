@echo off
REM File version: 2.0; date: 2026-05-11
setlocal
cd /d "%~dp0"

if /I "%~1"=="clean" goto :clean
if /I "%~1"=="clean-all" goto :clean_all

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

:clean
where latexmk >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    latexmk -c manual.tex
)
call :delete_generated
echo Auxiliary files cleaned. Source files and PDF were kept.
endlocal
exit /b 0

:clean_all
where latexmk >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    latexmk -CA manual.tex
)
call :delete_generated
if exist "manual.pdf" del /f /q "manual.pdf"
echo Generated files cleaned. Only source files were kept.
endlocal
exit /b 0

:add_miktex_from_registry
for /f "tokens=2,*" %%A in ('reg query "%~1" /v UserInstall 2^>nul ^| find "UserInstall"') do (
    if exist "%%B\miktex\bin\x64\lualatex.exe" (
        set "PATH=%%B\miktex\bin\x64;%PATH%"
    )
)
exit /b 0

:delete_generated
powershell -NoProfile -Command "$files = @('manual.aux','manual.bbl','manual.bcf','manual.blg','manual.fdb_latexmk','manual.fls','manual.idx','manual.ilg','manual.ind','manual.log','manual.out','manual.run.xml','manual.synctex.gz','manual.toc','manual.lof','manual.lot','manual.nav','manual.snm','manual.vrb','manual.xdv'); Get-ChildItem -LiteralPath '.' -File | Where-Object { $_.Name -in $files } | Remove-Item -Force -ErrorAction SilentlyContinue"
exit /b 0

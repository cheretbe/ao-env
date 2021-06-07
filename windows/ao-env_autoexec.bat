@ECHO OFF

IF /I "%~1"=="--verbose" ECHO.  Running '%~f0'

WHERE /Q ~.bat
IF %ERRORLEVEL% == 0 GOTO :skip_add_to_path

IF /I "%~1"=="--verbose" ECHO.  Adding '%~dp0bin' to PATH
:: If PATH already ends with a ";" don't add an extra one
IF "%PATH:~-1%"==";" (
  SET "PATH=%PATH%%~dp0bin"
) ELSE (
  SET "PATH=%PATH%;%~dp0bin"
)

:skip_add_to_path

IF EXIST "%~dp0local\ao-env_set_vars.bat" CALL "%~dp0local\ao-env_set_vars.bat"

IF "%ProgramFiles(x86)%"=="" (
  "%~dp0clink\clink_x86.exe" inject
) ELSE (
  "%~dp0clink\clink_x64.exe" inject
)

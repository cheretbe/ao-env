@ECHO OFF

IF "%AO_ENV_INITIALIZED%"=="1" EXIT /B 0
SET AO_ENV_INITIALIZED=1

IF "%ProgramFiles(x86)%"=="" (
  SET AO_ENV_PYTHON_PATH=%~dp0python\x86
) ELSE (
  SET AO_ENV_PYTHON_PATH=%~dp0python\x64
)

:: There is no point in checking ao-env_autoexec.bat availability if is in
:: current directory. Change directory temporarily during the check
IF "%CD%\"=="%~dp0" PUSHD "%TEMP%"

WHERE /Q ao-env_autoexec.bat
IF ERRORLEVEL 1 GOTO :add_to_path

FOR /F "TOKENS=*" %%A IN ('WHERE ao-env_autoexec.bat') DO SET aoEnvInstallAutoexecOnPath=%%A
IF "%aoEnvInstallAutoexecOnPath%"=="%~dp0ao-env_autoexec.bat" (
  IF /I "%~1"=="--verbose" ECHO 'ao-env' is already on PATH. Skipping.
  GOTO :skip_add_to_path
)

:add_to_path
IF /I "%~1"=="--verbose" ECHO Adding '%~dp0' to PATH
:: If PATH already ends with a ";" don't add an extra one
IF "%PATH:~-1%"==";" (
  SET "PATH=%PATH%%~dp0"
) ELSE (
  SET "PATH=%PATH%;%~dp0"
)

:skip_add_to_path
POPD

IF NOT EXIST "%~dp0..\variables.cfg" GOTO :skip_variables

FOR /F "EOL=; TOKENS=1,2 DELIMS==" %%A IN ('TYPE "%~dp0..\variables.cfg"') DO (
  SET %%A=%%B
  IF /I "%~1"=="--verbose" ECHO.  %%A=%%B
)

:skip_variables

IF "%ProgramFiles(x86)%"=="" (
  "%~dp0clink\clink_x86.exe" inject --quiet
) ELSE (
  "%~dp0clink\clink_x64.exe" inject --quiet
)
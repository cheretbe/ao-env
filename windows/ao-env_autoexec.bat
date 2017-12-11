@ECHO OFF

:: If PATH already ends with a ";" don't add an extra one
IF "%PATH:~-1%"==";" (
  SET "PATH=%PATH%%~dp0"
) ELSE (
  SET "PATH=%PATH%;%~dp0"
)

IF "%ProgramFiles(x86)%"=="" (
  SET AO_ENV_PYTHON_PATH=%~dp0python\x86
) ELSE (
  SET AO_ENV_PYTHON_PATH=%~dp0python\x64
)
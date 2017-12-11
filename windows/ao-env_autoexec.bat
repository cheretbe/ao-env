@ECHO OFF

:: If PATH already ends with a ";" don't add an extra one
IF "%PATH:~-1%"==";" (
  SET PATH=%PATH%%HOMEDRIVE%%HOMEPATH%\projects\ao-env\windows
) ELSE (
  SET PATH=%PATH%;%HOMEDRIVE%%HOMEPATH%\projects\ao-env\windows
)

IF "%ProgramFiles(x86)%"=="" (
  SET AO_ENV_PYTHON_PATH=%~dp0python\x86
) ELSE (
  SET AO_ENV_PYTHON_PATH=%~dp0python\x64
)
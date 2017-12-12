@ECHO OFF

SET aoEnvInstallDoubleClicked=0
FOR %%x IN (%CMDCMDLINE%) DO IF /I "%%~x"=="/C" SET aoEnvInstallDoubleClicked=1


ECHO Adding AutoRun entry
reg.exe ADD "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d "%~dp0windows\ao-env_autoexec.bat" /f

WHERE /Q ao-env_autoexec.bat
IF ERRORLEVEL 1 GOTO :add_to_path

FOR /F "TOKENS=*" %%A IN ('WHERE ao-env_autoexec.bat') DO SET aoEnvInstallAutoexecOnPath=%%A
IF "%aoEnvInstallAutoexecOnPath%"=="%~dp0windows\ao-env_autoexec.bat" (
  ECHO 'ao-env' is already on PATH. Skipping adding.
  GOTO :skip_add_to_path
)

:add_to_path
ECHO Adding '%~dp0windows' to PATH
:: If PATH already ends with a ";" don't add an extra one
IF "%PATH:~-1%"==";" (
  SET "PATH=%PATH%%~dp0windows"
) ELSE (
  SET "PATH=%PATH%;%~dp0windows"
)

:skip_add_to_path

IF %aoEnvInstallDoubleClicked%==1 (
  ECHO.
  ECHO ==== Press any key to close this window ====
  PAUSE >NUL
)
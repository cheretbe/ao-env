@ECHO OFF

SET aoEnvInstallDoubleClicked=0
FOR %%x IN (%CMDCMDLINE%) DO IF /I "%%~x"=="/C" SET aoEnvInstallDoubleClicked=1


ECHO Adding AutoRun entry
reg.exe ADD "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d "%~dp0windows\ao-env_autoexec.bat" /f

CALL "%~dp0windows\ao-env_autoexec.bat" --verbose

IF %aoEnvInstallDoubleClicked%==1 (
  ECHO.
  ECHO ==== Press any key to close this window ====
  PAUSE >NUL
)
@ECHO OFF

SET aoEnvInstallDoubleClicked=0
FOR %%x IN (%CMDCMDLINE%) DO IF /I "%%~x"=="/C" SET aoEnvInstallDoubleClicked=1

powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0windows/install.ps1" %*

::CALL "%~dp0windows\ao-env_autoexec.bat" --verbose

IF %aoEnvInstallDoubleClicked%==1 (
  ECHO.
  ECHO ==== Press any key to close this window ====
  PAUSE >NUL
)
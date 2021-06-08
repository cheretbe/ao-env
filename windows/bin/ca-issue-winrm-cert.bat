@ECHO OFF

SETLOCAL
IF "%ProgramFiles(x86)%"=="" (SET CPUArch=x86) ELSE (SET CPUArch=x64)
"%~dp0..\python\%CPUArch%\python.exe" "%~dp0..\..\bin\lib\ca-check-root.py" %*
IF ERRORLEVEL 1 EXIT /B 1
"%~dp0..\python\%CPUArch%\python.exe" "%~dp0..\..\bin\lib\ca-issue-winrm-cert.py" %*
ENDLOCAL

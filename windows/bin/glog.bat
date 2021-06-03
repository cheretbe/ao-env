@ECHO OFF

SETLOCAL
IF "%ProgramFiles(x86)%"=="" (SET CPUArch=x86) ELSE (SET CPUArch=x64)
"%~dp0..\python\%CPUArch%\python.exe" "%~dp0..\..\bin\glog" %*
ENDLOCAL

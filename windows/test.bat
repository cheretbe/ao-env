@ECHO OFF
IF "%ProgramFiles(x86)%" == "" (
  "%~dp0python\x86\python.exe" "%~dp0..\bin\test.py"
) ELSE (
  "%~dp0python\x64\python.exe" "%~dp0..\bin\test.py"
)

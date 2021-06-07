```batch
:: Command processor autorun value
:: Query
reg query "HKCU\Software\Microsoft\Command Processor" /v AutoRun

:: Delete without confirmation
reg delete "HKCU\Software\Microsoft\Command Processor" /v AutoRun /f
```

```batch
:: Command processor autorun value
:: Query
reg query "HKCU\Software\Microsoft\Command Processor" /v AutoRun

:: Delete without confirmation
reg delete "HKCU\Software\Microsoft\Command Processor" /v AutoRun /f
```

OpenSSL for Windows
* Download exe from https://slproweb.com/products/Win32OpenSSL.html
* Run the exe (e.g. ``Win32OpenSSL_Light-1_1_1k.exe` for x86)
* It will prompt for download of missing VC redistributable (will open default browser)
* Download WiX Toolset from https://github.com/wixtoolset/wix3/releases
* Extract with ``wix311-binaries\dark.exe -x target_dir vc_redist.x86.exe`
* `vcruntime140.dll` is in ``target_dir\AttachedContainer\packages\vcRuntimeMinimum_x86\cab1.cab`
* Default config locations:
    * `c:\Program Files (x86)\Common Files\SSL\`
    * `c:\Program Files\Common Files\SSL\`

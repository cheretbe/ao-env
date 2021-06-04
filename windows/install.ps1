Set-StrictMode -Version Latest
$ErrorActionPreference = [System.Management.Automation.ActionPreference]::Stop

$script:scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$autoexecPath = Join-Path -Path $script:scriptDir -ChildPath "ao-env_autoexec.bat"

$existingValue = Get-ItemProperty -Path "HKCU:\Software\Microsoft\Command Processor" `
  -Name "AutoRun" -ErrorAction SilentlyContinue

# $existingValue = "aaa"
if ($NULL -ne $existingValue) {
  $existingValue = $existingValue.PSObject.Properties.Item("Autorun").Value
  if ($existingValue -ne $autoexecPath) {
    Write-Host ("HKCU\Software\Microsoft\Command Processor\AutoRun: {0}" -f $existingValue)
    Write-Host (("ERROR: command processor autorun value exists and doesn't point " +`
      "to {0}") -f $autoexecPath) -ForegroundColor Red
    exit 1
  } #if
  Write-Host ("Command processor autorun parameter is already set. Skipping")
} else {
  Write-Host ("Setting command processor autorun parameter")
  if (-not(Test-Path -Path "HKCU:\Software\Microsoft\Command Processor"))
    { New-Item -Path "HKCU:\Software\Microsoft\Command Processor" -ItemType Registry -Force | Out-Null }
  New-ItemProperty -Path "HKCU:\Software\Microsoft\Command Processor" `
    -Name "AutoRun" -PropertyType String -Value $autoexecPath -Force | Out-Null
} #if

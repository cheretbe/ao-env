Set-StrictMode -Version Latest
$ErrorActionPreference = [System.Management.Automation.ActionPreference]::Stop

$script:scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function CreateShortcut {
param(
  [string]$shortcutFileName,
  [string]$shortcutTarget,
  [string]$arguments,
  [string]$iconLocation
)
  $wsShell = New-Object -comObject "WScript.Shell"
  $tcShortcut = $wsShell.CreateShortcut($shortcutFileName)
  $tcShortcut.TargetPath = $shortcutTarget
  if ($arguments)
    { $tcShortcut.Arguments = $arguments }
  if ($iconLocation)
    { $tcShortcut.IconLocation = $iconLocation }
  if ($shortcutFileName.contains(".url")) {
    $tcShortcut.Save()
  } else {
    if (Test-Path -Path $tcShortcut.TargetPath) {
      $tcShortcut.Save()
    } else {
      Write-aoWarning ("Cannot create shortcut for '{0}' - target is missing" -f $tcShortcut.TargetPath)
    } #if
  } #if
}


$autoexecPath = Join-Path -Path $script:scriptDir -ChildPath "ao-env_autoexec.bat"
$existingValue = Get-ItemProperty -Path "HKCU:\Software\Microsoft\Command Processor" `
  -Name "AutoRun" -ErrorAction SilentlyContinue
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

$envVarsFile = Join-Path -Path $script:scriptDir -ChildPath "local\ao-env_set_vars.bat"
if (Test-Path -Path $envVarsFile) {
  Write-Host ("'{0}' already exists. Skipping creation" -f $envVarsFile)
} else {
  Write-Host ("Creating '{0}' file using default values" -f $envVarsFile)
  Copy-Item -Path (Join-Path -Path $script:scriptDir -ChildPath "set_vars_template.bat") `
    -Destination $envVarsFile
} #if

$conemuDesktopShortcut = (Join-Path -Path ([Environment]::GetFolderPath("Desktop")) -ChildPath "ConEmu.lnk")
$conemuConfig = Join-Path -Path $script:scriptDir -ChildPath "local\conemu\ConEmu.xml"
if (Test-Path -Path $conemuDesktopShortcut) {
  Write-Host "ConEmu desktop shortcut already exists. Skipping creation"
} else {
  if ([Environment]::Is64BitOperatingSystem) {
    $conemuPath = Join-Path -Path $script:scriptDir -ChildPath "conemu\ConEmu64.exe"
  } else {
    $conemuPath = Join-Path -Path $script:scriptDir -ChildPath "conemu\ConEmu.exe"
  } #if
  Write-Host "Creating ConEmu desktop shortcut"
  CreateShortcut -shortcutFileName $conemuDesktopShortcut `
    -shortcutTarget ('"{0}"' -f $conemuPath) `
    -arguments @("-loadcfgfile", ('"{0}"' -f $conemuConfig))
} #if

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $conemuConfig) | Out-Null
if (Test-Path -Path $conemuConfig) {
  Write-Host ("'{0}' already exists. Skipping creation" -f $conemuConfig)
} else {
  Write-Host ("Creating '{0}' file using default values" -f $conemuConfig)
  Copy-Item -Path (Join-Path -Path $script:scriptDir -ChildPath "ConEmu_config_template.xml") `
    -Destination $conemuConfig
} #if

# Splunk Forwarder Installation Script for Windows
# Run as Administrator on Domain Controller

#Requires -RunAsAdministrator

param(
    [string]$SplunkServer = "192.168.56.106",
    [int]$SplunkPort = 9997,
    [string]$SplunkVersion = "9.1.2",
    [string]$SplunkBuild = "b6b9c8185839"
)

$ErrorActionPreference = "Stop"

# Color output functions
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Success { param($Message) Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

Write-Info "Starting Splunk Universal Forwarder Installation"
Write-Info "Target Indexer: $SplunkServer`:$SplunkPort"

# Check if already installed
$UFPath = "C:\Program Files\SplunkUniversalForwarder"
if (Test-Path $UFPath) {
    Write-Warning "Splunk Universal Forwarder already installed at $UFPath"
    $reinstall = Read-Host "Reinstall? (y/N)"
    if ($reinstall -ne 'y') {
        Write-Info "Skipping installation. Starting configuration..."
    } else {
        Write-Info "Uninstalling existing Universal Forwarder..."
        & "$UFPath\bin\splunk.exe" stop
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/x {A2D8B2E0-8F0C-4C5C-8A1D-7C6E8B5A3D2F} /quiet" -Wait
    }
}

# Download Universal Forwarder
$UFInstaller = "splunkforwarder-$SplunkVersion-$SplunkBuild-x64-release.msi"
$DownloadUrl = "https://download.splunk.com/products/universalforwarder/releases/$SplunkVersion/windows/$UFInstaller"
$DownloadPath = "C:\Temp\$UFInstaller"

if (-not (Test-Path "C:\Temp")) {
    New-Item -ItemType Directory -Path "C:\Temp" -Force | Out-Null
}

if (-not (Test-Path $DownloadPath)) {
    Write-Info "Downloading Splunk Universal Forwarder..."
    try {
        Invoke-WebRequest -Uri $DownloadUrl -OutFile $DownloadPath -UseBasicParsing
        Write-Success "Download complete"
    } catch {
        Write-Error "Failed to download: $_"
        Write-Info "Please manually download from: $DownloadUrl"
        exit 1
    }
} else {
    Write-Info "Installer already downloaded"
}

# Install Universal Forwarder
Write-Info "Installing Splunk Universal Forwarder..."
$InstallArgs = "/i `"$DownloadPath`" AGREETOLICENSE=Yes RECEIVING_INDEXER=`"$SplunkServer`:$SplunkPort`" /quiet /norestart"
$process = Start-Process -FilePath "msiexec.exe" -ArgumentList $InstallArgs -Wait -PassThru

if ($process.ExitCode -ne 0) {
    Write-Error "Installation failed with exit code: $($process.ExitCode)"
    exit 1
}

Write-Success "Installation complete"

# Configure inputs
Write-Info "Configuring inputs..."
$InputsConf = @"
[WinEventLog://Security]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
index = main
renderXml = false

[WinEventLog://System]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
index = main
renderXml = false

[WinEventLog://Application]
disabled = 0
start_from = oldest
current_only = 0
checkpointInterval = 5
index = main
renderXml = false

[default]
host = dc
"@

$InputsPath = "$UFPath\etc\system\local\inputs.conf"
Set-Content -Path $InputsPath -Value $InputsConf -Force
Write-Success "inputs.conf created"

# Configure outputs
$OutputsConf = @"
[tcpout]
defaultGroup = default-autolb-group

[tcpout:default-autolb-group]
server = $SplunkServer`:$SplunkPort

[tcpout-server://$SplunkServer`:$SplunkPort]
"@

$OutputsPath = "$UFPath\etc\system\local\outputs.conf"
Set-Content -Path $OutputsPath -Value $OutputsConf -Force
Write-Success "outputs.conf created"

# Start the forwarder
Write-Info "Starting Splunk Universal Forwarder..."
& "$UFPath\bin\splunk.exe" start

# Enable boot-start
Write-Info "Enabling boot-start..."
& "$UFPath\bin\splunk.exe" enable boot-start

# Verify status
Write-Info "Checking forwarder status..."
& "$UFPath\bin\splunk.exe" status

Write-Success "Splunk Universal Forwarder setup complete!"
Write-Info "Events should begin appearing in Splunk within 5 minutes"
Write-Info "Verify with Splunk search: index=main host=dc | head 10"

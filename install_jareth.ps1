# ==============================================================================
# Jareth_AINV Installation Script for G: Drive
# AlphaEdge AINV MCP Server with Full Windows OS Control
# ==============================================================================

param(
    [string]$Drive = "G:",
    [string]$ProjectName = "AlphaEdge_AINV",
    [switch]$SkipGPUCheck,
    [switch]$SkipLMStudio
)

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Header($text) {
    Write-Host ""
    Write-ColorOutput Cyan "=" * 80
    Write-ColorOutput Cyan $text.PadLeft(40 + ($text.Length / 2)).PadRight(80)
    Write-ColorOutput Cyan "=" * 80
    Write-Host ""
}

function Write-Success($text) {
    Write-ColorOutput Green "✓ $text"
}

function Write-Error($text) {
    Write-ColorOutput Red "✗ $text"
}

function Write-Warning($text) {
    Write-ColorOutput Yellow "⚠ $text"
}

function Write-Info($text) {
    Write-ColorOutput Cyan "ℹ $text"
}

# ==============================================================================
# Main Installation
# ==============================================================================

Write-Header "Jareth_AINV Installation"
Write-Info "Installing to: $Drive\$ProjectName"

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Warning "Not running as Administrator. Some features may require elevation."
    Write-Info "For full OS control, run: Start-Process powershell -Verb RunAs -ArgumentList '-File $PSCommandPath'"
}

# ==============================================================================
# Step 1: Check Prerequisites
# ==============================================================================

Write-Header "Step 1: Checking Prerequisites"

# Check Python version
Write-Info "Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]

        if ($major -ge 3 -and $minor -ge 10) {
            Write-Success "Python $major.$minor found"
        } else {
            Write-Error "Python 3.10+ required, found $major.$minor"
            exit 1
        }
    }
} catch {
    Write-Error "Python not found. Install from: https://www.python.org/downloads/"
    exit 1
}

# Check Git
Write-Info "Checking Git installation..."
try {
    $gitVersion = git --version 2>&1
    Write-Success "Git installed: $gitVersion"
} catch {
    Write-Warning "Git not found. Install from: https://git-scm.com/download/win"
    Write-Info "You can continue without Git, but manual file copy will be needed"
}

# Check NVIDIA GPU (optional)
if (-not $SkipGPUCheck) {
    Write-Info "Checking for NVIDIA GPU..."
    try {
        $nvidiaInfo = nvidia-smi --query-gpu=name --format=csv,noheader 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "NVIDIA GPU detected: $nvidiaInfo"
        } else {
            Write-Warning "NVIDIA GPU not detected"
        }
    } catch {
        Write-Warning "nvidia-smi not found. GPU monitoring will be unavailable"
    }
}

# Check LM Studio (optional)
if (-not $SkipLMStudio) {
    Write-Info "Checking LM Studio..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:1234/v1/models" -TimeoutSec 2 -ErrorAction SilentlyContinue
        Write-Success "LM Studio is running"
    } catch {
        Write-Warning "LM Studio not running at localhost:1234"
        Write-Info "Download from: https://lmstudio.ai/"
    }
}

# ==============================================================================
# Step 2: Create Directory Structure
# ==============================================================================

Write-Header "Step 2: Creating Directory Structure"

$projectPath = "$Drive\$ProjectName"

Write-Info "Creating project directory: $projectPath"

if (Test-Path $projectPath) {
    Write-Warning "Directory already exists: $projectPath"
    $response = Read-Host "Do you want to continue? (Y/N)"
    if ($response -ne "Y" -and $response -ne "y") {
        Write-Info "Installation cancelled"
        exit 0
    }
} else {
    New-Item -ItemType Directory -Path $projectPath -Force | Out-Null
    Write-Success "Created: $projectPath"
}

# Create subdirectories
$subdirs = @("workspace", "logs", "models", "data", "temp")
foreach ($dir in $subdirs) {
    $dirPath = Join-Path $projectPath $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
        Write-Success "Created: $dir\"
    }
}

# ==============================================================================
# Step 3: Clone/Copy Repository
# ==============================================================================

Write-Header "Step 3: Installing Jareth_AINV"

Set-Location $projectPath

Write-Info "Repository source: https://github.com/AKABoyd7/https-github.com-username-MDMA-App.git-MDMA-App"
Write-Info "Branch: claude/alphaedge-mcp-server-011CV477Fds3K8XrtkujexEt"

$cloneChoice = Read-Host "Do you want to clone from Git? (Y/N)"

if ($cloneChoice -eq "Y" -or $cloneChoice -eq "y") {
    try {
        Write-Info "Cloning repository..."
        git clone -b claude/alphaedge-mcp-server-011CV477Fds3K8XrtkujexEt https://github.com/AKABoyd7/https-github.com-username-MDMA-App.git-MDMA-App .
        Write-Success "Repository cloned"
    } catch {
        Write-Error "Failed to clone repository: $_"
        Write-Info "You can manually copy files to: $projectPath"
        exit 1
    }
} else {
    Write-Warning "Skipping Git clone"
    Write-Info "Please manually copy all files to: $projectPath"
    Write-Info "Press Enter when files are copied..."
    Read-Host
}

# ==============================================================================
# Step 4: Create Virtual Environment
# ==============================================================================

Write-Header "Step 4: Creating Python Virtual Environment"

$venvPath = Join-Path $projectPath "venv"

if (Test-Path $venvPath) {
    Write-Warning "Virtual environment already exists"
    $response = Read-Host "Recreate it? (Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        Remove-Item -Recurse -Force $venvPath
    }
}

if (-not (Test-Path $venvPath)) {
    Write-Info "Creating virtual environment..."
    python -m venv $venvPath
    Write-Success "Virtual environment created"
}

# ==============================================================================
# Step 5: Install Dependencies
# ==============================================================================

Write-Header "Step 5: Installing Python Dependencies"

$pipPath = Join-Path $venvPath "Scripts\pip.exe"

Write-Info "Upgrading pip..."
& $pipPath install --upgrade pip

Write-Info "Installing requirements..."
$requirementsPath = Join-Path $projectPath "requirements.txt"

if (Test-Path $requirementsPath) {
    & $pipPath install -r $requirementsPath
    Write-Success "Dependencies installed"
} else {
    Write-Error "requirements.txt not found at: $requirementsPath"
    exit 1
}

# ==============================================================================
# Step 6: Configure Environment
# ==============================================================================

Write-Header "Step 6: Configuring Environment"

$envTemplatePath = Join-Path $projectPath ".env.template"
$envPath = Join-Path $projectPath ".env"

if (Test-Path $envTemplatePath) {
    if (Test-Path $envPath) {
        Write-Warning ".env file already exists"
    } else {
        Copy-Item $envTemplatePath $envPath
        Write-Success "Created .env file from template"
    }

    # Prompt for NVIDIA API key
    Write-Info ""
    Write-Info "Configuration options:"
    Write-Info "1. NVIDIA API Key (optional but recommended)"
    Write-Info "   Get it from: https://build.nvidia.com/"
    Write-Info ""

    $nvidiaKey = Read-Host "Enter NVIDIA API Key (press Enter to skip)"

    if ($nvidiaKey) {
        $envContent = Get-Content $envPath
        $envContent = $envContent -replace 'nvapi-your-key-here', $nvidiaKey
        Set-Content $envPath $envContent
        Write-Success "NVIDIA API key configured"
    }

    # Update paths in .env
    $envContent = Get-Content $envPath
    $envContent = $envContent -replace 'G:\\AlphaEdge_AINV', $projectPath
    Set-Content $envPath $envContent
    Write-Success "Environment paths configured"

} else {
    Write-Warning ".env.template not found, creating basic .env"
    @"
# Jareth_AINV Configuration
NVIDIA_API_KEY=nvapi-your-key-here
LM_STUDIO_URL=http://localhost:1234/v1
PROJECT_ROOT=$projectPath
WORKSPACE_DIR=$projectPath\workspace
SERVER_PORT=8000
DEBUG_MODE=false
"@ | Out-File -FilePath $envPath -Encoding utf8
    Write-Success "Created basic .env file"
}

# ==============================================================================
# Step 7: Configure Claude Desktop
# ==============================================================================

Write-Header "Step 7: Claude Desktop Configuration"

$claudeConfigDir = "$env:APPDATA\Claude"
$claudeConfigPath = Join-Path $claudeConfigDir "claude_desktop_config.json"

Write-Info "Claude Desktop config location: $claudeConfigPath"

$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$serverScript = Join-Path $projectPath "mcp_server\server.py"

$claudeConfig = @{
    mcpServers = @{
        "jareth-ainv" = @{
            command = $pythonExe
            args = @($serverScript)
            env = @{
                NVIDIA_API_KEY = "nvapi-your-key-here"
                LM_STUDIO_URL = "http://localhost:1234/v1"
                PROJECT_ROOT = $projectPath
            }
        }
    }
} | ConvertTo-Json -Depth 10

Write-Info ""
Write-Info "Add this to your Claude Desktop config:"
Write-ColorOutput Yellow $claudeConfig
Write-Info ""

$autoConfig = Read-Host "Automatically update Claude Desktop config? (Y/N)"

if ($autoConfig -eq "Y" -or $autoConfig -eq "y") {
    if (-not (Test-Path $claudeConfigDir)) {
        New-Item -ItemType Directory -Path $claudeConfigDir -Force | Out-Null
    }

    if (Test-Path $claudeConfigPath) {
        $backupPath = "$claudeConfigPath.backup"
        Copy-Item $claudeConfigPath $backupPath
        Write-Info "Backed up existing config to: $backupPath"
    }

    $claudeConfig | Out-File -FilePath $claudeConfigPath -Encoding utf8
    Write-Success "Claude Desktop configured"
} else {
    Write-Info "Please manually update Claude Desktop configuration"
}

# ==============================================================================
# Step 8: Create Shortcuts
# ==============================================================================

Write-Header "Step 8: Creating Shortcuts"

# Create start server script
$startServerScript = @"
@echo off
cd /d "$projectPath\mcp_server"
"$pythonExe" server.py
pause
"@

$startScriptPath = Join-Path $projectPath "START_JARETH_SERVER.bat"
$startServerScript | Out-File -FilePath $startScriptPath -Encoding ascii
Write-Success "Created: START_JARETH_SERVER.bat"

# Create desktop shortcut
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Jareth AINV.lnk"

try {
    $WScriptShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WScriptShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = $startScriptPath
    $Shortcut.WorkingDirectory = $projectPath
    $Shortcut.Description = "Start Jareth_AINV MCP Server"
    $Shortcut.Save()
    Write-Success "Created desktop shortcut"
} catch {
    Write-Warning "Could not create desktop shortcut: $_"
}

# ==============================================================================
# Step 9: Test Installation
# ==============================================================================

Write-Header "Step 9: Testing Installation"

Write-Info "Running basic tests..."

# Test Python imports
$testScript = @"
import sys
sys.path.insert(0, '$projectPath')
try:
    from mcp_server.config import settings
    from mcp_server.server import AlphaEdgeMCPServer
    print('SUCCESS: All imports working')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
"@

$testScriptPath = Join-Path $projectPath "temp\test_install.py"
$testScript | Out-File -FilePath $testScriptPath -Encoding utf8

& $pythonExe $testScriptPath

if ($LASTEXITCODE -eq 0) {
    Write-Success "Installation test passed"
} else {
    Write-Error "Installation test failed"
}

# ==============================================================================
# Installation Complete
# ==============================================================================

Write-Header "Installation Complete!"

Write-Success "Jareth_AINV has been installed successfully!"
Write-Host ""
Write-Info "Installation Summary:"
Write-Info "  Location: $projectPath"
Write-Info "  Python: $pythonExe"
Write-Info "  Server: $serverScript"
Write-Host ""

Write-ColorOutput Green "Next Steps:"
Write-Host "1. Edit .env file if needed: $envPath"
Write-Host "2. Start LM Studio and load models"
Write-Host "3. Run server: Double-click 'START_JARETH_SERVER.bat' or desktop shortcut"
Write-Host "4. Restart Claude Desktop to load MCP server"
Write-Host ""

Write-ColorOutput Cyan "Available Features:"
Write-Host "  ✓ Local AI Models (Llama 3.3, Qwen 2.5, Llama 3.1)"
Write-Host "  ✓ NVIDIA Cloud APIs (Nemotron, Vision Models)"
Write-Host "  ✓ GPU Monitoring (Status, VRAM, Processes)"
Write-Host "  ✓ System Tools (Files, Commands)"
Write-Host "  ✓ Windows Management (Processes, Services, Registry)"
Write-Host "  ✓ Network Management"
Write-Host "  ✓ Full OS Control"
Write-Host ""

Write-ColorOutput Yellow "Documentation:"
Write-Host "  README: $projectPath\README.md"
Write-Host "  Deployment Guide: $projectPath\DEPLOYMENT_GUIDE.md"
Write-Host ""

$startNow = Read-Host "Start Jareth_AINV server now? (Y/N)"

if ($startNow -eq "Y" -or $startNow -eq "y") {
    Write-Info "Starting server..."
    Start-Process -FilePath $startScriptPath
} else {
    Write-Info "You can start the server later by running: $startScriptPath"
}

Write-Host ""
Write-ColorOutput Green "Thank you for installing Jareth_AINV!"
Write-ColorOutput Cyan "Jareth is ready to serve. 🚀"

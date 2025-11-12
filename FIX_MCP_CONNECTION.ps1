# ==============================================================================
# Jareth_AINV MCP Connection Fix Script
# Fixes "could not attach to mcp file system" error in Claude Desktop
# ==============================================================================

param(
    [string]$ProjectPath = "G:\AlphaEdge_AINV"
)

$ErrorActionPreference = "Stop"

# Colors
function Write-ColorOutput($ForegroundColor, $Message) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Header($text) {
    Write-Host ""
    Write-ColorOutput Cyan ("=" * 80)
    Write-ColorOutput Cyan $text.PadLeft(40 + ($text.Length / 2)).PadRight(80)
    Write-ColorOutput Cyan ("=" * 80)
    Write-Host ""
}

function Write-Success($text) { Write-ColorOutput Green "✓ $text" }
function Write-Error-Text($text) { Write-ColorOutput Red "✗ $text" }
function Write-Warning($text) { Write-ColorOutput Yellow "⚠ $text" }
function Write-Info($text) { Write-ColorOutput Cyan "ℹ $text" }

Write-Header "Jareth_AINV MCP Connection Fix"

# ==============================================================================
# Step 1: Stop Everything
# ==============================================================================

Write-Header "Step 1: Stopping All Processes"

Write-Info "Stopping Claude Desktop..."
Get-Process -Name "Claude" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

Write-Info "Stopping Python servers..."
Get-Process -Name "python" -ErrorAction SilentlyContinue |
    Where-Object {$_.Path -like "*AlphaEdge*"} |
    Stop-Process -Force

Start-Sleep -Seconds 2
Write-Success "All processes stopped"

# ==============================================================================
# Step 2: Verify Installation
# ==============================================================================

Write-Header "Step 2: Verifying Installation"

$pythonExe = "$ProjectPath\venv\Scripts\python.exe"
$pipExe = "$ProjectPath\venv\Scripts\pip.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Error-Text "Python not found at: $pythonExe"
    exit 1
}
Write-Success "Python found: $pythonExe"

# ==============================================================================
# Step 3: Install/Verify MCP SDK
# ==============================================================================

Write-Header "Step 3: Verifying MCP SDK"

Write-Info "Checking MCP package..."
$mcpInstalled = & $pythonExe -c "import mcp; print('OK')" 2>&1

if ($mcpInstalled -like "*OK*") {
    Write-Success "MCP SDK already installed"
} else {
    Write-Warning "MCP SDK not found, installing..."

    Write-Info "Installing mcp package..."
    & $pipExe install mcp --upgrade

    if ($LASTEXITCODE -eq 0) {
        Write-Success "MCP SDK installed successfully"
    } else {
        Write-Error-Text "Failed to install MCP SDK"
        exit 1
    }
}

# Verify version
$mcpVersion = & $pythonExe -c "import mcp; print(mcp.__version__)" 2>&1
Write-Success "MCP SDK version: $mcpVersion"

# ==============================================================================
# Step 4: Test Server Import
# ==============================================================================

Write-Header "Step 4: Testing Server Import"

$testScript = @"
import sys
sys.path.insert(0, '$ProjectPath')

try:
    print('[TEST] Importing mcp_server...')
    from mcp_server import get_server, AlphaEdgeMCPServer
    print('[OK] mcp_server imported successfully')

    print('[TEST] Importing MCP SDK...')
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    print('[OK] MCP SDK imported successfully')

    print('[TEST] Creating server instance...')
    server = get_server()
    print(f'[OK] Server created with {len(server.tools)} tools')

    print('[SUCCESS] All imports working!')
    sys.exit(0)

except Exception as e:
    print(f'[ERROR] {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"@

$testFile = "$env:TEMP\test_mcp_import.py"
$testScript | Out-File -FilePath $testFile -Encoding utf8

Write-Info "Running import test..."
& $pythonExe $testFile

if ($LASTEXITCODE -ne 0) {
    Write-Error-Text "Server import test failed"
    Write-Info "Check the error messages above"
    exit 1
}

Write-Success "Server imports working correctly"

# ==============================================================================
# Step 5: Create Proper Launcher Script
# ==============================================================================

Write-Header "Step 5: Creating MCP Launcher"

$launcherScript = @"
"""
MCP Server Launcher for Claude Desktop
This script ensures proper stdio communication with Claude Desktop.
"""
import sys
import os
import asyncio

# Set project root
PROJECT_ROOT = r'$ProjectPath'
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

# Import and run server
try:
    from mcp_server.server import main
    asyncio.run(main())
except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"Server error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
"@

$launcherPath = "$ProjectPath\mcp_launcher.py"
$launcherScript | Out-File -FilePath $launcherPath -Encoding utf8
Write-Success "Created: mcp_launcher.py"

# ==============================================================================
# Step 6: Update Claude Desktop Config
# ==============================================================================

Write-Header "Step 6: Updating Claude Desktop Config"

$claudeConfigDir = "$env:APPDATA\Claude"
$claudeConfigPath = "$claudeConfigDir\claude_desktop_config.json"

# Backup existing config
if (Test-Path $claudeConfigPath) {
    $backupPath = "$claudeConfigPath.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Copy-Item $claudeConfigPath $backupPath
    Write-Info "Backed up existing config to: $(Split-Path $backupPath -Leaf)"
}

# Create new config
$config = @{
    mcpServers = @{
        'jareth-ainv' = @{
            command = $pythonExe
            args = @($launcherPath)
        }
    }
}

$configJson = $config | ConvertTo-Json -Depth 10

# Ensure directory exists
if (-not (Test-Path $claudeConfigDir)) {
    New-Item -ItemType Directory -Path $claudeConfigDir -Force | Out-Null
}

# Write config
$configJson | Out-File -FilePath $claudeConfigPath -Encoding utf8 -Force

Write-Success "Claude Desktop config updated"
Write-Info "Config location: $claudeConfigPath"
Write-Host ""
Write-ColorOutput White $configJson
Write-Host ""

# ==============================================================================
# Step 7: Test Server Startup
# ==============================================================================

Write-Header "Step 7: Testing Server Startup"

Write-Info "Starting server in test mode..."

$testStartupScript = @"
import sys
import os
import asyncio

PROJECT_ROOT = r'$ProjectPath'
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

async def test():
    from mcp_server.server import get_server
    from mcp_server.config import settings

    print('[TEST] Initializing server...')
    server = get_server()

    print(f'[OK] Server Name: {settings.SERVER_NAME}')
    print(f'[OK] Server Version: {settings.SERVER_VERSION}')
    print(f'[OK] Tools Registered: {len(server.tools)}')
    print(f'[OK] LM Studio URL: {settings.LM_STUDIO_URL}')

    # List first 5 tools
    print('[OK] Sample tools:')
    for i, tool_name in enumerate(list(server.tools.keys())[:5], 1):
        print(f'     {i}. {tool_name}')

    print('[SUCCESS] Server startup test passed!')
    return 0

try:
    result = asyncio.run(test())
    sys.exit(result)
except Exception as e:
    print(f'[ERROR] {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"@

$testStartupFile = "$env:TEMP\test_server_startup.py"
$testStartupScript | Out-File -FilePath $testStartupFile -Encoding utf8

& $pythonExe $testStartupFile

if ($LASTEXITCODE -ne 0) {
    Write-Error-Text "Server startup test failed"
    exit 1
}

Write-Success "Server startup test passed!"

# ==============================================================================
# Step 8: Create Manual Server Launcher (Optional)
# ==============================================================================

Write-Header "Step 8: Creating Manual Server Launcher"

$manualLauncher = @"
@echo off
title Jareth_AINV MCP Server (Manual Mode)
echo.
echo ========================================================================
echo   Jareth_AINV MCP Server - Manual Mode
echo ========================================================================
echo.
echo Starting server...
echo.

cd /d "$ProjectPath"
"$pythonExe" mcp_launcher.py

echo.
echo ========================================================================
echo   Server stopped
echo ========================================================================
pause
"@

$manualLauncherPath = "$ProjectPath\START_MANUAL_SERVER.bat"
$manualLauncher | Out-File -FilePath $manualLauncherPath -Encoding ascii
Write-Success "Created: START_MANUAL_SERVER.bat"

# ==============================================================================
# Step 9: Start Claude Desktop
# ==============================================================================

Write-Header "Step 9: Starting Claude Desktop"

Write-Info "Waiting 3 seconds before starting Claude Desktop..."
Start-Sleep -Seconds 3

Write-Info "Starting Claude Desktop..."
try {
    Start-Process "claude" -ErrorAction Stop
    Write-Success "Claude Desktop started"
} catch {
    Write-Warning "Could not auto-start Claude Desktop"
    Write-Info "Please start Claude Desktop manually"
}

Write-Info "Waiting 10 seconds for Claude Desktop to initialize..."
Start-Sleep -Seconds 10

# ==============================================================================
# Complete
# ==============================================================================

Write-Header "Fix Complete!"

Write-Success "All steps completed successfully!"
Write-Host ""

Write-ColorOutput Green "╔══════════════════════════════════════════════════════════════════════════╗"
Write-ColorOutput Green "║                         SETUP COMPLETE!                                  ║"
Write-ColorOutput Green "╚══════════════════════════════════════════════════════════════════════════╝"
Write-Host ""

Write-ColorOutput Cyan "What to do now:"
Write-Host "  1. Claude Desktop should now be running"
Write-Host "  2. Look for MCP server indicator (🔌 icon in bottom-left)"
Write-Host "  3. It should show 'jareth-ainv' as connected"
Write-Host ""

Write-ColorOutput Cyan "Test commands to try in Claude Desktop:"
Write-ColorOutput White '  • "What tools do you have?"'
Write-ColorOutput White '  • "List all processes by memory usage"'
Write-ColorOutput White '  • "Check my GPU status"'
Write-ColorOutput White '  • "Show system information"'
Write-Host ""

Write-ColorOutput Cyan "If you see '✗ Connection Error':"
Write-Host "  1. Check Claude Desktop logs:"
Write-ColorOutput Yellow "     Get-ChildItem `"$env:APPDATA\Claude\logs`" -Filter *.log | Sort-Object LastWriteTime -Desc | Select-Object -First 1 | Get-Content -Tail 50"
Write-Host "  2. Try manual server test:"
Write-ColorOutput Yellow "     $ProjectPath\START_MANUAL_SERVER.bat"
Write-Host ""

Write-ColorOutput Green "Files created:"
Write-Host "  • $launcherPath"
Write-Host "  • $manualLauncherPath"
Write-Host "  • $claudeConfigPath"
Write-Host ""

Write-ColorOutput Cyan "Support:"
Write-Host "  • Config file: $claudeConfigPath"
Write-Host "  • Server logs: $ProjectPath\mcp_server.log"
Write-Host "  • Project root: $ProjectPath"
Write-Host ""

Write-ColorOutput Green "Jareth_AINV is ready to serve! 🚀"
Write-Host ""

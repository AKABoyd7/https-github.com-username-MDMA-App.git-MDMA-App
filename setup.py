"""
Setup script for AlphaEdge AINV MCP Server.
Automates installation and configuration on Windows.
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def check_python_version():
    """Check if Python version is 3.10+."""
    print_info("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error(f"Python 3.10+ required, found {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_nvidia_gpu():
    """Check if NVIDIA GPU is available."""
    print_info("Checking for NVIDIA GPU...")
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Parse GPU name from output
            lines = result.stdout.split('\n')
            for line in lines:
                if "NVIDIA" in line and "|" in line:
                    print_success(f"Found NVIDIA GPU")
                    return True
        print_warning("nvidia-smi command failed")
        return False
    except Exception as e:
        print_warning(f"Could not detect NVIDIA GPU: {e}")
        return False


def create_virtual_environment(project_root):
    """Create Python virtual environment."""
    print_info("Creating virtual environment...")
    venv_path = project_root / "venv"

    if venv_path.exists():
        print_warning("Virtual environment already exists")
        response = input("Recreate it? (y/N): ").lower()
        if response == 'y':
            shutil.rmtree(venv_path)
        else:
            print_info("Keeping existing virtual environment")
            return True

    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True
        )
        print_success("Virtual environment created")
        return True
    except Exception as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False


def install_dependencies(project_root):
    """Install Python dependencies."""
    print_info("Installing dependencies...")

    # Determine pip path
    if os.name == 'nt':
        pip_path = project_root / "venv" / "Scripts" / "pip.exe"
    else:
        pip_path = project_root / "venv" / "bin" / "pip"

    requirements_file = project_root / "requirements.txt"

    if not requirements_file.exists():
        print_error("requirements.txt not found")
        return False

    try:
        # Upgrade pip first
        subprocess.run(
            [str(pip_path), "install", "--upgrade", "pip"],
            check=True
        )

        # Install requirements
        subprocess.run(
            [str(pip_path), "install", "-r", str(requirements_file)],
            check=True
        )
        print_success("Dependencies installed")
        return True
    except Exception as e:
        print_error(f"Failed to install dependencies: {e}")
        return False


def setup_environment_file(project_root):
    """Setup .env file from template."""
    print_info("Setting up environment file...")

    env_template = project_root / ".env.template"
    env_file = project_root / ".env"

    if env_file.exists():
        print_warning(".env file already exists")
        response = input("Overwrite it? (y/N): ").lower()
        if response != 'y':
            print_info("Keeping existing .env file")
            return True

    if not env_template.exists():
        print_error(".env.template not found")
        return False

    try:
        shutil.copy2(env_template, env_file)
        print_success(".env file created")

        # Prompt for NVIDIA API key
        print_info("\nConfiguration:")
        nvidia_key = input("Enter your NVIDIA API key (press Enter to skip): ").strip()

        if nvidia_key:
            # Update .env file
            with open(env_file, 'r') as f:
                content = f.read()

            content = content.replace('nvapi-your-key-here', nvidia_key)

            with open(env_file, 'w') as f:
                f.write(content)

            print_success("NVIDIA API key configured")
        else:
            print_warning("NVIDIA API key not configured - you can add it later in .env")

        return True
    except Exception as e:
        print_error(f"Failed to setup environment file: {e}")
        return False


def create_directories(project_root):
    """Create necessary directories."""
    print_info("Creating directories...")

    directories = [
        project_root / "workspace",
        project_root / "logs",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    print_success("Directories created")
    return True


def setup_claude_config():
    """Setup Claude Desktop configuration."""
    print_info("Setting up Claude Desktop configuration...")

    print_warning("\nClaude Desktop Configuration:")
    print("To use this MCP server with Claude Desktop, add the following to your")
    print("Claude Desktop configuration file:\n")

    if os.name == 'nt':
        config_path = Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
        python_path = "G:\\AlphaEdge_AINV\\venv\\Scripts\\python.exe"
        server_path = "G:\\AlphaEdge_AINV\\mcp_server\\server.py"
    else:
        config_path = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
        python_path = "G:\\AlphaEdge_AINV\\venv\\Scripts\\python.exe"
        server_path = "G:\\AlphaEdge_AINV\\mcp_server\\server.py"

    print(f"Configuration file location: {config_path}\n")

    config = f"""{{
  "mcpServers": {{
    "alphaedge-ainv": {{
      "command": "{python_path}",
      "args": ["{server_path}"],
      "env": {{
        "NVIDIA_API_KEY": "your-nvidia-api-key-here",
        "LM_STUDIO_URL": "http://localhost:1234/v1"
      }}
    }}
  }}
}}"""

    print(config)
    print()

    return True


def main():
    """Main setup function."""
    print_header("AlphaEdge AINV MCP Server Setup")

    # Determine project root
    if os.name == 'nt':
        project_root = Path("G:/AlphaEdge_AINV")
    else:
        project_root = Path(__file__).parent.resolve()

    print_info(f"Project root: {project_root}")

    # Check Python version
    if not check_python_version():
        return 1

    # Check for NVIDIA GPU
    has_gpu = check_nvidia_gpu()
    if not has_gpu:
        print_warning("NVIDIA GPU not detected - GPU monitoring tools may not work")
        response = input("Continue anyway? (Y/n): ").lower()
        if response == 'n':
            return 1

    # Create virtual environment
    if not create_virtual_environment(project_root):
        return 1

    # Install dependencies
    if not install_dependencies(project_root):
        return 1

    # Setup environment file
    if not setup_environment_file(project_root):
        return 1

    # Create directories
    if not create_directories(project_root):
        return 1

    # Setup Claude Desktop config
    setup_claude_config()

    # Final instructions
    print_header("Setup Complete!")

    print_success("AlphaEdge AINV MCP Server is ready to use!\n")

    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print("1. Edit .env file with your NVIDIA API key (if needed)")
    print("2. Start LM Studio and load your models")
    print("3. Configure Claude Desktop (see configuration above)")
    print("4. Run the server:")

    if os.name == 'nt':
        print(f"   {Colors.OKCYAN}cd {project_root}\\mcp_server{Colors.ENDC}")
        print(f"   {Colors.OKCYAN}..\\venv\\Scripts\\python.exe server.py{Colors.ENDC}")
    else:
        print(f"   {Colors.OKCYAN}cd mcp_server{Colors.ENDC}")
        print(f"   {Colors.OKCYAN}python server.py{Colors.ENDC}")

    print()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Setup interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)

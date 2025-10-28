#!/usr/bin/env python3
"""
Cross-platform launcher for Employee Offboarding Tool
Automatically handles setup and execution
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path


class Colors:
    """ANSI color codes"""
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

    @classmethod
    def disable(cls):
        """Disable colors for Windows or non-TTY"""
        cls.BLUE = ''
        cls.GREEN = ''
        cls.YELLOW = ''
        cls.RED = ''
        cls.CYAN = ''
        cls.NC = ''


# Disable colors on Windows if not supported
if platform.system() == 'Windows' and not os.environ.get('ANSICON'):
    try:
        import colorama
        colorama.init()
    except ImportError:
        Colors.disable()


def print_header():
    """Print application header"""
    print(f"\n{Colors.CYAN}{'=' * 70}")
    print(f"  Employee Offboarding Tool - Automated Launcher")
    print(f"{'=' * 70}{Colors.NC}\n")


def print_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ{Colors.NC} {message}")


def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.NC} {message}")


def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.NC} {message}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗{Colors.NC} {message}")


def check_python_version():
    """Check if Python version meets requirements"""
    print_info("Checking Python version...")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print_error(f"Python 3.7 or higher is required (found {version_str})")
        return False

    print_success(f"Python {version_str} meets requirements")
    return True


def check_pip():
    """Check if pip is available"""
    print_info("Checking pip installation...")

    try:
        import pip
        print_success("pip is available")
        return True
    except ImportError:
        print_error("pip is not available")
        print_info("Installing pip...")
        try:
            subprocess.check_call([sys.executable, '-m', 'ensurepip', '--default-pip'])
            print_success("pip installed successfully")
            return True
        except subprocess.CalledProcessError:
            print_error("Failed to install pip")
            return False


def setup_virtual_environment():
    """Create and setup virtual environment"""
    venv_path = Path('venv')

    if venv_path.exists():
        print_warning("Virtual environment already exists")
        response = input("Do you want to recreate it? (y/N): ").strip().lower()
        if response == 'y':
            print_info("Removing existing virtual environment...")
            shutil.rmtree(venv_path)
        else:
            print_info("Using existing virtual environment")
            return True

    print_info("Creating virtual environment...")
    try:
        subprocess.check_call([sys.executable, '-m', 'venv', 'venv'])
        print_success("Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False


def get_venv_python():
    """Get path to Python executable in virtual environment"""
    if platform.system() == 'Windows':
        return str(Path('venv') / 'Scripts' / 'python.exe')
    else:
        return str(Path('venv') / 'bin' / 'python')


def get_venv_pip():
    """Get path to pip executable in virtual environment"""
    if platform.system() == 'Windows':
        return str(Path('venv') / 'Scripts' / 'pip.exe')
    else:
        return str(Path('venv') / 'bin' / 'pip')


def install_dependencies():
    """Install required dependencies"""
    print_info("Installing dependencies...")

    requirements_file = Path('requirements.txt')
    if not requirements_file.exists():
        print_error("requirements.txt not found!")
        return False

    venv_pip = get_venv_pip()

    # Upgrade pip
    print_info("Upgrading pip...")
    try:
        subprocess.check_call(
            [venv_pip, 'install', '--upgrade', 'pip'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        print_warning("Failed to upgrade pip, continuing anyway...")

    # Install requirements
    print_info("Installing Python packages (this may take a minute)...")
    try:
        subprocess.check_call(
            [venv_pip, 'install', '-r', 'requirements.txt'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print_success("All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        print_info("Try running: pip install -r requirements.txt")
        return False


def check_credentials():
    """Check for Google API credentials"""
    print_info("Checking for Google API credentials...")

    creds_file = Path('credentials.json')
    if creds_file.exists():
        print_success("Found credentials.json")
        return True

    print_warning("credentials.json not found")
    print("\nYou need OAuth2 credentials from Google Cloud Console.\n")
    print("Quick setup:")
    print("1. Visit: https://console.cloud.google.com/apis/credentials")
    print("2. Create OAuth client ID (Desktop app)")
    print("3. Download the JSON file")
    print("4. Save it as 'credentials.json' in this directory\n")

    input("Press Enter when credentials.json is ready (or Ctrl+C to exit)...")

    if creds_file.exists():
        print_success("Found credentials.json")
        return True

    print_error("credentials.json still not found!")
    print_info("The application will prompt you to provide credentials interactively\n")

    response = input("Continue anyway? (y/N): ").strip().lower()
    return response == 'y'


def run_application():
    """Run the main application"""
    print_info("Starting Employee Offboarding Tool...\n")

    venv_python = get_venv_python()

    try:
        exit_code = subprocess.call([venv_python, 'main.py'])

        print()
        if exit_code == 0:
            print_success("Application completed successfully")
        else:
            print_warning(f"Application exited with code {exit_code}")

        return exit_code
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Operation cancelled by user{Colors.NC}")
        return 130
    except Exception as e:
        print_error(f"Failed to run application: {e}")
        return 1


def main():
    """Main launcher function"""
    print_header()

    # Check Python version
    if not check_python_version():
        return 1

    # Check pip
    if not check_pip():
        return 1

    print()
    print_info("Starting setup process...\n")

    # Setup virtual environment
    if not setup_virtual_environment():
        return 1

    # Install dependencies
    if not install_dependencies():
        return 1

    print()

    # Check credentials
    if not check_credentials():
        return 1

    print()
    print_success("Setup complete! Starting application...\n")

    # Run application
    return run_application()


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Operation cancelled by user{Colors.NC}")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

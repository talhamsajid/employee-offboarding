#!/bin/bash

# Employee Offboarding Tool - Automated Setup and Run Script
# This script handles everything from setup to execution

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo -e "${CYAN}"
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  Employee Offboarding Tool - Automated Setup & Run"
    echo "═══════════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

# Check if Python is installed
check_python() {
    print_info "Checking Python installation..."

    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Found Python $PYTHON_VERSION"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        print_success "Found Python $PYTHON_VERSION"
    else
        print_error "Python is not installed!"
        print_info "Please install Python 3.7 or higher from https://www.python.org/"
        exit 1
    fi

    # Check Python version
    PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info[0])')
    PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info[1])')

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
        print_error "Python 3.7 or higher is required (found $PYTHON_VERSION)"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_info "Checking pip installation..."

    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
        print_success "Found pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
        print_success "Found pip"
    else
        print_error "pip is not installed!"
        print_info "Installing pip..."
        $PYTHON_CMD -m ensurepip --default-pip
        PIP_CMD="pip"
    fi
}

# Create virtual environment
setup_venv() {
    print_info "Setting up virtual environment..."

    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " recreate
        if [[ $recreate =~ ^[Yy]$ ]]; then
            print_info "Removing existing virtual environment..."
            rm -rf venv
        else
            print_info "Using existing virtual environment"
            return
        fi
    fi

    print_info "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."

    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
    else
        print_error "Could not find virtual environment activation script"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies..."

    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi

    # Upgrade pip first
    print_info "Upgrading pip..."
    pip install --upgrade pip > /dev/null 2>&1

    # Install requirements
    print_info "Installing Python packages (this may take a minute)..."
    pip install -r requirements.txt > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        print_success "All dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        print_info "Try running: pip install -r requirements.txt"
        exit 1
    fi
}

# Check credentials
check_credentials() {
    print_info "Checking for Google API credentials..."

    if [ -f "credentials.json" ]; then
        print_success "Found credentials.json"
        return 0
    else
        print_warning "credentials.json not found"
        echo ""
        echo "You need OAuth2 credentials from Google Cloud Console."
        echo ""
        echo "Quick setup:"
        echo "1. Visit: https://console.cloud.google.com/apis/credentials"
        echo "2. Create OAuth client ID (Desktop app)"
        echo "3. Download the JSON file"
        echo "4. Save it as 'credentials.json' in this directory"
        echo ""
        read -p "Press Enter when credentials.json is ready (or Ctrl+C to exit)..."

        if [ -f "credentials.json" ]; then
            print_success "Found credentials.json"
            return 0
        else
            print_error "credentials.json still not found!"
            print_info "The application will prompt you to provide credentials interactively"
            echo ""
            read -p "Continue anyway? (y/N): " continue_anyway
            if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    fi
}

# Run the application
run_application() {
    print_info "Starting Employee Offboarding Tool..."
    echo ""

    python main.py

    EXIT_CODE=$?

    echo ""
    if [ $EXIT_CODE -eq 0 ]; then
        print_success "Application completed successfully"
    else
        print_warning "Application exited with code $EXIT_CODE"
    fi

    return $EXIT_CODE
}

# Cleanup function
cleanup() {
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate 2>/dev/null || true
    fi
}

# Main execution
main() {
    # Set trap to cleanup on exit
    trap cleanup EXIT

    print_header

    # Check prerequisites
    check_python
    check_pip

    echo ""
    print_info "Starting setup process..."
    echo ""

    # Setup virtual environment
    setup_venv
    activate_venv

    # Install dependencies
    install_dependencies

    echo ""

    # Check credentials
    check_credentials

    echo ""
    print_success "Setup complete! Starting application..."
    echo ""
    sleep 1

    # Run the application
    run_application
}

# Check if script is being sourced or executed
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

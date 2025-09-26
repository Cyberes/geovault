#!/bin/bash

# Frontend Watch and Build Script
# This script watches the frontend source files for changes and rebuilds automatically

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_DIR="/home/dpanzer/Nextcloud/Documents/Tech/Code/geoserver/src/geo-frontend"
WATCH_DIRS=("src" "public" "index.html" "vite.config.js" "tailwind.config.js" "postcss.config.js")
BUILD_COMMAND="npm run build"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Function to build the frontend
build_frontend() {
    print_status "Building frontend..."
    cd "$FRONTEND_DIR"
    
    if npm run build; then
        print_success "Frontend build completed successfully!"
    else
        print_error "Frontend build failed!"
        return 1
    fi
}

# Function to check if inotify-tools is installed
check_dependencies() {
    if ! command -v inotifywait &> /dev/null; then
        print_error "inotifywait is not installed. Please install inotify-tools:"
        print_error "  Ubuntu/Debian: sudo apt-get install inotify-tools"
        print_error "  CentOS/RHEL: sudo yum install inotify-tools"
        print_error "  Fedora: sudo dnf install inotify-tools"
        exit 1
    fi
}

# Function to check if npm is available
check_npm() {
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed or not in PATH"
        exit 1
    fi
}

# Function to check if node_modules exists
check_node_modules() {
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        print_warning "node_modules not found. Installing dependencies..."
        cd "$FRONTEND_DIR"
        npm install
        print_success "Dependencies installed successfully!"
    fi
}

# Main function
main() {
    print_status "Starting frontend watch script..."
    
    # Check dependencies
    check_dependencies
    check_npm
    check_node_modules
    
    # Change to frontend directory
    cd "$FRONTEND_DIR"
    
    # Initial build
    print_status "Performing initial build..."
    build_frontend
    
    # Create watch paths
    WATCH_PATHS=""
    for dir in "${WATCH_DIRS[@]}"; do
        if [ -e "$FRONTEND_DIR/$dir" ]; then
            WATCH_PATHS="$WATCH_PATHS $FRONTEND_DIR/$dir"
        else
            print_warning "Watch path $dir does not exist, skipping..."
        fi
    done
    
    if [ -z "$WATCH_PATHS" ]; then
        print_error "No valid watch paths found!"
        exit 1
    fi
    
    print_status "Watching for changes in: $WATCH_PATHS"
    print_status "Press Ctrl+C to stop watching"
    echo
    
    # Watch for changes
    inotifywait -m -r -e modify,create,delete,move \
        --format '%w%f %e' \
        $WATCH_PATHS | while read file event; do
        
        # Skip certain files/directories
        if [[ "$file" =~ (node_modules|\.git|dist|\.cache) ]]; then
            continue
        fi
        
        print_status "File changed: $file ($event)"
        
        # Small delay to avoid multiple builds for rapid changes
        sleep 0.5
        
        # Build the frontend
        if build_frontend; then
            print_success "Rebuild completed for: $file"
        else
            print_error "Rebuild failed for: $file"
        fi
        
        echo "---"
    done
}

# Handle Ctrl+C gracefully
trap 'print_status "Stopping watch script..."; exit 0' INT

# Run main function
main "$@"

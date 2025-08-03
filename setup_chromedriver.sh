#!/bin/bash

echo "======================================"
echo "ChromeDriver Setup Script"
echo "======================================"

# Detect OS and architecture
OS=$(uname -s)
ARCH=$(uname -m)

echo "Detected OS: $OS"
echo "Detected Architecture: $ARCH"

# Function to get Chrome version
get_chrome_version() {
    if [[ "$OS" == "Darwin" ]]; then
        if [ -d "/Applications/Google Chrome.app" ]; then
            CHROME_VERSION=$("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        else
            echo "Google Chrome not found in Applications folder"
            return 1
        fi
    elif [[ "$OS" == "Linux" ]]; then
        if command -v google-chrome &> /dev/null; then
            CHROME_VERSION=$(google-chrome --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        elif command -v chromium &> /dev/null; then
            CHROME_VERSION=$(chromium --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        else
            echo "Chrome/Chromium not found"
            return 1
        fi
    else
        echo "Unsupported OS: $OS"
        return 1
    fi
    
    echo "Chrome version: $CHROME_VERSION"
    return 0
}

# Function to download ChromeDriver
download_chromedriver() {
    local version=$1
    local download_url=""
    local zip_file="chromedriver.zip"
    
    # Determine platform string
    if [[ "$OS" == "Darwin" ]]; then
        if [[ "$ARCH" == "x86_64" ]]; then
            PLATFORM="mac-x64"
        else
            PLATFORM="mac-arm64"
        fi
    elif [[ "$OS" == "Linux" ]]; then
        PLATFORM="linux64"
    else
        echo "Unsupported platform"
        return 1
    fi
    
    # Construct download URL
    download_url="https://storage.googleapis.com/chrome-for-testing-public/${version}/${PLATFORM}/chromedriver-${PLATFORM}.zip"
    
    echo "Downloading ChromeDriver from: $download_url"
    
    # Download
    if command -v wget &> /dev/null; then
        wget -O "$zip_file" "$download_url"
    elif command -v curl &> /dev/null; then
        curl -L -o "$zip_file" "$download_url"
    else
        echo "Neither wget nor curl found. Please install one of them."
        return 1
    fi
    
    # Extract
    if [ -f "$zip_file" ]; then
        unzip -o "$zip_file"
        
        # Move to current directory
        if [ -d "chromedriver-${PLATFORM}" ]; then
            mv "chromedriver-${PLATFORM}/chromedriver" ./chromedriver
            rm -rf "chromedriver-${PLATFORM}"
        fi
        
        # Make executable
        chmod +x ./chromedriver
        
        # Clean up
        rm "$zip_file"
        
        echo "✅ ChromeDriver downloaded successfully!"
        ./chromedriver --version
        
        return 0
    else
        echo "Failed to download ChromeDriver"
        return 1
    fi
}

# Main logic
if get_chrome_version; then
    echo ""
    echo "Downloading matching ChromeDriver..."
    download_chromedriver "$CHROME_VERSION"
else
    echo ""
    echo "❌ Could not detect Chrome version."
    echo "Please install Google Chrome first."
    echo ""
    echo "For macOS: Download from https://www.google.com/chrome/"
    echo "For Linux: sudo apt-get install google-chrome-stable"
    exit 1
fi
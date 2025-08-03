#!/bin/bash

set -e

echo "======================================"
echo "Bilibili Video Tracker Installation"
echo "======================================"

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python $PYTHON_VERSION"

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Checking Chrome installation..."
CHROME_FOUND=false
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [ -d "/Applications/Google Chrome.app" ]; then
        CHROME_VERSION=$("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        echo "Found Chrome version: $CHROME_VERSION"
        CHROME_FOUND=true
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v google-chrome &> /dev/null; then
        CHROME_VERSION=$(google-chrome --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        echo "Found Chrome version: $CHROME_VERSION"
        CHROME_FOUND=true
    elif command -v chromium &> /dev/null; then
        CHROME_VERSION=$(chromium --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        echo "Found Chromium version: $CHROME_VERSION"
        CHROME_FOUND=true
    fi
fi

if [ "$CHROME_FOUND" = false ]; then
    echo "Warning: Chrome/Chromium not found. Please install Google Chrome or Chromium."
    echo "The application will attempt to use the default ChromeDriver."
fi

echo "Creating data directory..."
mkdir -p data

echo "Setting up ChromeDriver..."
if [ -x "./setup_chromedriver.sh" ]; then
    ./setup_chromedriver.sh
else
    echo "ChromeDriver setup script not found or not executable"
fi

echo "Creating run script..."
cat > run.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
streamlit run app.py
EOF

chmod +x run.sh

echo "Creating update script..."
cat > update_videos.py << 'EOF'
#!/usr/bin/env python3
import json
import os
import sys
from bili_spider.updater import update_all_users

if __name__ == '__main__':
    if os.path.exists('data/following.json'):
        with open('data/following.json', 'r', encoding='utf-8') as f:
            following_users = json.load(f)
        
        if following_users:
            print("Starting video update for all following users...")
            update_all_users(following_users)
            print("Update completed!")
        else:
            print("No users in following list.")
    else:
        print("No following.json file found. Please add users through the web interface first.")
EOF

chmod +x update_videos.py

echo ""
echo "======================================"
echo "Installation completed successfully!"
echo "======================================"
echo ""
echo "To run the application:"
echo "  ./run.sh"
echo ""
echo "Or manually:"
echo "  source venv/bin/activate"
echo "  streamlit run app.py"
echo ""
echo "To update videos via command line:"
echo "  source venv/bin/activate"
echo "  python update_videos.py"
echo ""
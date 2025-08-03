#!/bin/bash

echo "======================================"
echo "Bilibili Video Tracker Starter"
echo "======================================"

# Detect OS
OS=$(uname -s)
ARCH=$(uname -m)

echo "Detected OS: $OS ($ARCH)"

# Function to check if Docker is running
check_docker() {
    if command -v docker &> /dev/null && docker info &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to run with Docker
run_docker() {
    echo "Running with Docker..."
    
    # Use slim version for faster builds
    if [ -f "docker-compose.slim.yml" ]; then
        echo "Using slim Docker configuration for faster startup..."
        docker-compose -f docker-compose.slim.yml up -d
    else
        docker-compose up -d
    fi
    
    echo ""
    echo "✅ Application started!"
    echo "🌐 Access at: http://localhost:8501"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
}

# Function to run locally
run_local() {
    echo "Running locally..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Virtual environment not found. Running install script..."
        ./install.sh
    fi
    
    # Activate virtual environment and run
    source venv/bin/activate
    
    echo ""
    echo "✅ Starting Streamlit application..."
    echo "🌐 Will open at: http://localhost:8501"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    
    streamlit run app.py
}

# Main logic
echo ""
echo "Select running method:"
echo "1) Docker (recommended for production)"
echo "2) Local Python (recommended for development)"
echo "3) Auto-detect"
echo ""

read -p "Enter your choice (1-3) [default: 3]: " choice
choice=${choice:-3}

case $choice in
    1)
        if check_docker; then
            run_docker
        else
            echo "❌ Docker is not running or not installed."
            echo "Please install Docker Desktop and start it."
            exit 1
        fi
        ;;
    2)
        run_local
        ;;
    3)
        # Auto-detect
        if check_docker; then
            echo "Docker detected. Using Docker..."
            run_docker
        else
            echo "Docker not detected. Using local Python..."
            run_local
        fi
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
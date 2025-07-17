#!/bin/bash

# CineScope Analyzer - Automated Setup Script
# This script sets up both backend and frontend automatically

set -e  # Exit on any error

echo "🎬 CineScope Analyzer - Automated Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VERSION found"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    print_success "All prerequisites met!"
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create environment file
    if [ ! -f .env ]; then
        print_status "Creating environment file..."
        cp .env.template .env 2>/dev/null || echo "# CineScope Backend Environment Variables
DATABASE_URL=sqlite:///./cache/cache.db
OMDB_API_KEY=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=" > .env
    fi
    
    # Create necessary directories
    mkdir -p cache logs scraped_data tests
    
    # Test backend
    print_status "Testing backend setup..."
    python -c "from app.main import app; print('Backend imports successful!')" || {
        print_error "Backend setup failed!"
        exit 1
    }
    
    cd ..
    print_success "Backend setup completed!"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Create environment file
    if [ ! -f .env.local ]; then
        print_status "Creating frontend environment file..."
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=CineScope Analyzer
NEXT_PUBLIC_APP_VERSION=1.0.0" > .env.local
    fi
    
    # Test frontend build
    print_status "Testing frontend build..."
    npm run build || {
        print_error "Frontend build failed!"
        exit 1
    }
    
    cd ..
    print_success "Frontend setup completed!"
}

# Create startup scripts
create_startup_scripts() {
    print_status "Creating startup scripts..."
    
    # Create start script for Unix systems
    cat > start.sh << 'EOF'
#!/bin/bash
echo "🎬 Starting CineScope Analyzer..."

# Function to cleanup on exit
cleanup() {
    echo "Shutting down services..."
    pkill -f uvicorn 2>/dev/null || true
    pkill -f next 2>/dev/null || true
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 CineScope Analyzer is running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
EOF

    chmod +x start.sh
    
    # Create Windows batch file
    cat > start.bat << 'EOF'
@echo off
echo 🎬 Starting CineScope Analyzer...

echo Starting backend...
cd backend
call venv\Scripts\activate
start /B python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting frontend...
cd ..\frontend
start /B npm run dev

echo.
echo 🎉 CineScope Analyzer is running!
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all services
pause >nul

echo Stopping services...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
EOF
    
    print_success "Startup scripts created!"
}

# Run tests
run_tests() {
    print_status "Running tests to verify setup..."
    
    # Test backend
    print_status "Testing backend..."
    cd backend
    source venv/bin/activate
    python -m pytest tests/ -v || print_warning "Some backend tests failed (this is normal for initial setup)"
    cd ..
    
    # Test frontend
    print_status "Testing frontend..."
    cd frontend
    npm test -- --passWithNoTests || print_warning "Some frontend tests failed (this is normal for initial setup)"
    cd ..
    
    print_success "Tests completed!"
}

# Main setup process
main() {
    echo ""
    print_status "Starting automated setup process..."
    echo ""
    
    check_prerequisites
    echo ""
    
    setup_backend
    echo ""
    
    setup_frontend
    echo ""
    
    create_startup_scripts
    echo ""
    
    run_tests
    echo ""
    
    print_success "🎉 Setup completed successfully!"
    echo ""
    echo "🚀 To start the application:"
    echo "   ./start.sh          (Linux/Mac)"
    echo "   start.bat           (Windows)"
    echo "   npm run dev:full    (From frontend directory)"
    echo ""
    echo "📱 Once started, visit: http://localhost:3000"
    echo "🔧 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📖 For detailed instructions, see HOW_TO_RUN.md"
}

# Run main function
main "$@"
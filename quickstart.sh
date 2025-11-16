#!/bin/bash

# Quick Start Script for Enterprise AI Workflows
# This script helps you get started quickly with any project

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Enterprise AI Workflows - Quick Start                 ║"
echo "║     Free & Open-Source Implementation                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print colored output
print_success() {
    echo "✅ $1"
}

print_error() {
    echo "❌ $1"
}

print_info() {
    echo "ℹ️  $1"
}

print_warning() {
    echo "⚠️  $1"
}

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check Docker (optional)
if command_exists docker; then
    DOCKER_VERSION=$(docker --version)
    print_success "Docker found: $DOCKER_VERSION"
    DOCKER_AVAILABLE=true
else
    print_warning "Docker not found. You can still run Projects 1 and 3."
    print_info "Install Docker Desktop for Project 2: https://www.docker.com/products/docker-desktop/"
    DOCKER_AVAILABLE=false
fi

# Check Docker Compose (optional)
if command_exists docker-compose; then
    print_success "Docker Compose found"
elif command_exists docker && docker compose version >/dev/null 2>&1; then
    print_success "Docker Compose (plugin) found"
else
    if [ "$DOCKER_AVAILABLE" = true ]; then
        print_warning "Docker Compose not found"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Select a project to set up:"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "1) Project 1: Rapid Insights Workflow"
echo "   └─ Simulates: Snowflake Cortex AI"
echo "   └─ Time: ~5 minutes"
echo "   └─ Requires: Python only"
echo ""
echo "2) Project 2: Enterprise MLOps Pipeline"
echo "   └─ Simulates: Azure ML, Dataiku"
echo "   └─ Time: ~15 minutes"
echo "   └─ Requires: Docker"
echo ""
echo "3) Project 3: Document Q&A System"
echo "   └─ Simulates: Azure OpenAI + Cognitive Search"
echo "   └─ Time: ~10 minutes"
echo "   └─ Requires: Python only"
echo ""
echo "4) Install all projects"
echo ""
echo "5) Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        print_info "Setting up Project 1: Rapid Insights Workflow"
        echo ""
        
        cd project1-rapid-insights
        
        # Create virtual environment
        print_info "Creating virtual environment..."
        python3 -m venv venv
        
        print_info "Activating virtual environment..."
        source venv/bin/activate
        
        print_info "Upgrading pip..."
        pip install --upgrade pip -q
        
        print_info "Installing dependencies..."
        pip install -r requirements.txt -q
        
        print_success "Project 1 installed successfully!"
        echo ""
        echo "To run the application:"
        echo "  cd project1-rapid-insights"
        echo "  source venv/bin/activate"
        echo "  streamlit run app.py"
        echo ""
        
        # Ask if they want to run now
        read -p "Would you like to run it now? (y/n): " run_now
        if [[ $run_now == "y" || $run_now == "Y" ]]; then
            print_info "Starting Streamlit app..."
            streamlit run app.py
        fi
        ;;
        
    2)
        echo ""
        print_info "Setting up Project 2: Enterprise MLOps Pipeline"
        echo ""
        
        if [ "$DOCKER_AVAILABLE" = false ]; then
            print_error "Docker is required for Project 2"
            print_info "Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
            exit 1
        fi
        
        cd project2-mlops-pipeline
        
        print_info "Pulling Docker images (this may take a while)..."
        docker-compose pull
        
        print_info "Starting services..."
        docker-compose up -d
        
        print_success "Project 2 services started!"
        echo ""
        echo "Services available at:"
        echo "  📊 MLflow UI:    http://localhost:5000"
        echo "  📓 Jupyter Lab:  http://localhost:8888"
        echo "  🚀 API Docs:     http://localhost:8000/docs"
        echo ""
        echo "To use:"
        echo "  1. Open Jupyter at http://localhost:8888"
        echo "  2. Open notebook: 01_customer_churn_mlops.ipynb"
        echo "  3. Run all cells to train models"
        echo "  4. View experiments in MLflow UI"
        echo ""
        echo "To stop services:"
        echo "  docker-compose down"
        echo ""
        ;;
        
    3)
        echo ""
        print_info "Setting up Project 3: Document Q&A System"
        echo ""
        
        cd project3-document-qa
        
        # Create virtual environment
        print_info "Creating virtual environment..."
        python3 -m venv venv
        
        print_info "Activating virtual environment..."
        source venv/bin/activate
        
        print_info "Upgrading pip..."
        pip install --upgrade pip -q
        
        print_info "Installing dependencies (may take a while)..."
        print_warning "First run will download models (~500MB)"
        pip install -r requirements.txt -q
        
        print_success "Project 3 installed successfully!"
        echo ""
        echo "To run the application:"
        echo "  cd project3-document-qa"
        echo "  source venv/bin/activate"
        echo "  python app.py"
        echo ""
        
        # Ask if they want to run now
        read -p "Would you like to run it now? (y/n): " run_now
        if [[ $run_now == "y" || $run_now == "Y" ]]; then
            print_info "Starting application (downloading models on first run)..."
            python app.py
        fi
        ;;
        
    4)
        echo ""
        print_info "Installing all projects..."
        echo ""
        
        # Create main virtual environment
        print_info "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        
        pip install --upgrade pip -q
        
        # Install Project 1
        print_info "Installing Project 1..."
        pip install -r project1-rapid-insights/requirements.txt -q
        print_success "Project 1 installed"
        
        # Install Project 2 dependencies (optional)
        print_info "Installing Project 2 Python dependencies..."
        pip install -r project2-mlops-pipeline/deployment/requirements.txt -q
        print_success "Project 2 dependencies installed"
        
        if [ "$DOCKER_AVAILABLE" = true ]; then
            print_info "Pulling Docker images for Project 2..."
            cd project2-mlops-pipeline
            docker-compose pull
            cd ..
            print_success "Project 2 Docker images ready"
        fi
        
        # Install Project 3
        print_info "Installing Project 3..."
        pip install -r project3-document-qa/requirements.txt -q
        print_success "Project 3 installed"
        
        echo ""
        print_success "All projects installed successfully!"
        echo ""
        echo "To run each project:"
        echo ""
        echo "Project 1:"
        echo "  cd project1-rapid-insights && streamlit run app.py"
        echo ""
        echo "Project 2:"
        echo "  cd project2-mlops-pipeline && docker-compose up -d"
        echo ""
        echo "Project 3:"
        echo "  cd project3-document-qa && python app.py"
        echo ""
        ;;
        
    5)
        echo ""
        print_info "Exiting. Visit the docs/ folder for detailed setup instructions."
        exit 0
        ;;
        
    *)
        print_error "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
print_info "Need help? Check out:"
echo "  📖 docs/setup-guide.md - Detailed setup instructions"
echo "  🎤 docs/interview-prep.md - Interview preparation guide"
echo ""

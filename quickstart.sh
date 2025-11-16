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

# Helper: Check if a TCP port is listening and print a friendly status line
print_port_status() {
    local port=$1
    local label=$2
    local url=$3
    if command_exists lsof && lsof -nP -i :"$port" >/dev/null 2>&1; then
        print_success "$label is RUNNING → $url"
    else
        print_warning "$label is NOT running"
    fi
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

# Resolve Docker CLI even if not on PATH (macOS Docker Desktop)
DOCKER_BIN=""
COMPOSE_CMD=""
DOCKER_AVAILABLE=false

# Preferred: docker in PATH
if command_exists docker; then
    DOCKER_BIN="$(command -v docker)"
fi

# Fallback: Docker Desktop app bundle
if [ -z "$DOCKER_BIN" ] && [ -x "/Applications/Docker.app/Contents/Resources/bin/docker" ]; then
    DOCKER_BIN="/Applications/Docker.app/Contents/Resources/bin/docker"
fi

# Final check and report
if [ -n "$DOCKER_BIN" ]; then
    DOCKER_VERSION=$($DOCKER_BIN --version 2>/dev/null || true)
    if [ -n "$DOCKER_VERSION" ]; then
        print_success "Docker found: $DOCKER_VERSION"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker CLI detected at $DOCKER_BIN but not responding"
    fi
else
    print_warning "Docker not found in PATH or Applications. You can still run Projects 1 and 3."
    print_info "Install/Launch Docker Desktop for Project 2: https://www.docker.com/products/docker-desktop/"
fi

# Determine Compose command
if [ "$DOCKER_AVAILABLE" = true ] && $DOCKER_BIN compose version >/dev/null 2>&1; then
    print_success "Docker Compose (plugin) found"
    COMPOSE_CMD="$DOCKER_BIN compose"
elif command_exists docker-compose; then
    print_success "docker-compose found"
    COMPOSE_CMD="$(command -v docker-compose)"
elif [ -x "/Applications/Docker.app/Contents/Resources/bin/docker-compose" ]; then
    print_success "docker-compose (from Docker.app) found"
    COMPOSE_CMD="/Applications/Docker.app/Contents/Resources/bin/docker-compose"
else
    if [ "$DOCKER_AVAILABLE" = true ]; then
        print_warning "Docker Compose not found — Project 2 may not start."
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
echo "5) Show status of running services"
echo ""
echo "6) Start all projects together"
echo ""
echo "7) Exit"
echo ""

read -p "Enter your choice (1-7): " choice

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
        
        if [ -z "$COMPOSE_CMD" ]; then
            print_error "Docker Compose is required but was not found."
            print_info "If using Docker Desktop on macOS, try: /Applications/Docker.app/Contents/Resources/bin/docker compose version"
            exit 1
        fi

        print_info "Pulling Docker images (this may take a while)..."
        $COMPOSE_CMD pull
        
        print_info "Starting services..."
        $COMPOSE_CMD up -d
        
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
        print_info "Checking service status..."
        echo ""
        # Project 1 - Streamlit
        print_port_status 8501 "Project 1 (Streamlit)" "http://localhost:8501"
        
        # Project 3 - Gradio
        print_port_status 7860 "Project 3 (Gradio)" "http://localhost:7860"
        
        # Project 2 - Docker services
        if [ "$DOCKER_AVAILABLE" = true ]; then
            print_port_status 5000 "MLflow UI" "http://localhost:5000"
            print_port_status 8888 "Jupyter Lab" "http://localhost:8888"
            print_port_status 8000 "Model API (FastAPI)" "http://localhost:8000/docs"
            echo ""
            print_info "Docker containers (if any):"
            # Prefer docker compose plugin if available
            if command_exists docker; then
                docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || true
            fi
        else
            print_warning "Docker not available → Project 2 cannot run yet"
        fi
        echo ""
        print_info "Tip: Use './quickstart.sh' again to start a project."
        ;;

        6)
                echo ""
                print_info "Starting all projects together…"
                echo ""
        
                # 1) Start Project 2 (Docker) if available
                if [ "$DOCKER_AVAILABLE" = true ] && [ -n "$COMPOSE_CMD" ]; then
                        (
                            cd project2-mlops-pipeline && \
                            print_info "[Project 2] Pulling images…" && $COMPOSE_CMD pull && \
                            print_info "[Project 2] Starting services…" && $COMPOSE_CMD up -d
                        ) || print_warning "[Project 2] Could not start Docker services"
                else
                        print_warning "[Project 2] Skipped — Docker/Compose not detected"
                fi
        
                # 2) Start Project 1 (Streamlit) in background
                (
                    cd project1-rapid-insights && \
                    print_info "[Project 1] Ensuring virtual environment…" && \
                    [ -d venv ] || python3 -m venv venv && \
                    . venv/bin/activate && \
                    print_info "[Project 1] Installing dependencies (this may take a bit)…" && \
                    pip install --upgrade pip -q && \
                    pip install -r requirements.txt -q || \
                    { print_warning "[Project 1] Requirements install failed — installing core deps"; pip install streamlit pandas numpy plotly textblob -q; } && \
                    print_info "[Project 1] Launching Streamlit on :8501…" && \
                    nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > /tmp/project1.log 2>&1 &
                ) || print_warning "[Project 1] Failed to start"
        
                # 3) Start Project 3 (Gradio) in background
                (
                    cd project3-document-qa && \
                    print_info "[Project 3] Ensuring virtual environment…" && \
                    [ -d venv ] || python3 -m venv venv && \
                    . venv/bin/activate && \
                    print_info "[Project 3] Installing dependencies (models may download on first run)…" && \
                    pip install --upgrade pip -q && \
                    pip install -r requirements.txt -q && \
                    print_info "[Project 3] Launching Gradio on :7860…" && \
                    nohup python app.py > /tmp/project3.log 2>&1 &
                ) || print_warning "[Project 3] Failed to start"
        
                # Show status and open URLs
                echo ""
                print_info "Checking status…"
                print_port_status 8501 "Project 1 (Streamlit)" "http://localhost:8501"
                print_port_status 7860 "Project 3 (Gradio)" "http://localhost:7860"
                if [ "$DOCKER_AVAILABLE" = true ]; then
                        print_port_status 5000 "MLflow UI" "http://localhost:5000"
                        print_port_status 8888 "Jupyter Lab" "http://localhost:8888"
                        print_port_status 8000 "Model API (FastAPI)" "http://localhost:8000/docs"
                fi
        
                if command_exists open; then
                        open http://localhost:8501 >/dev/null 2>&1 || true
                        open http://localhost:7860 >/dev/null 2>&1 || true
                        [ "$DOCKER_AVAILABLE" = true ] && open http://localhost:5000 >/dev/null 2>&1 || true
                        [ "$DOCKER_AVAILABLE" = true ] && open http://localhost:8888 >/dev/null 2>&1 || true
                        [ "$DOCKER_AVAILABLE" = true ] && open http://localhost:8000/docs >/dev/null 2>&1 || true
                fi
        
                echo ""
                print_info "Logs: /tmp/project1.log, /tmp/project3.log (Docker logs via: $COMPOSE_CMD logs -f)"
                ;;

        7)
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

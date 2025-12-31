.PHONY: test test-unit test-integration test-local test-aws lint format clean install benchmark help

# Default target
.DEFAULT_GOAL := help

test: test-unit test-integration  ## Run all tests

test-unit:  ## Run unit tests only
	pytest tests/unit/ -v -m "not integration and not aws"

test-integration:  ## Run integration tests (requires Docker services)
	@echo "Starting Docker Compose services..."
	docker-compose up -d || true
	@echo "Waiting for services to be ready..."
	sleep 30
	pytest tests/integration/ -v -m "integration and not aws"
	@echo "Stopping Docker Compose services..."
	docker-compose down -v || true

test-local:  ## Run local tests (Docker Compose stack)
	bash scripts/run_local_tests.sh

test-aws:  ## Run AWS integration tests (requires AWS credentials)
	bash scripts/run_aws_tests.sh

benchmark:  ## Run performance benchmarks
	bash scripts/performance_benchmark.sh

lint:  ## Check code quality
	@echo "Running flake8..."
	flake8 .
	@echo "Running black check..."
	black --check .
	@echo "Running isort check..."
	isort --check-only .
	@echo "Running mypy..."
	mypy kafka_streams/ healthcare_data/ || true

format:  ## Format code with black and isort
	@echo "Formatting with black..."
	black .
	@echo "Sorting imports with isort..."
	isort .

clean:  ## Clean up artifacts and caches
	@echo "Cleaning Python cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	@echo "Cleaning test artifacts..."
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .mypy_cache
	@echo "Stopping Docker services..."
	docker-compose down -v || true

install:  ## Install dependencies
	@echo "Installing production dependencies..."
	pip install kafka-python requests
	@echo "Installing test dependencies..."
	pip install pytest pytest-cov pytest-mock flake8 black isort mypy

install-dev:  ## Install all dependencies including dev tools
	$(MAKE) install
	pip install ipython jupyter

docker-up:  ## Start Docker Compose services
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	sleep 30

docker-down:  ## Stop Docker Compose services
	docker-compose down -v

docker-logs:  ## View Docker Compose logs
	docker-compose logs -f

security-scan:  ## Run security scan
	bash scripts/security_scan.sh

data-validation:  ## Run data validation checks
	bash scripts/data_validation.sh

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

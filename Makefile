.PHONY: install dev build test docker-up docker-down clean

install:
	@echo "Installing dependencies..."
	@pip install -r backend/requirements.txt
	@npm install --prefix frontend

dev:
	@echo "Starting development environment..."
	@./scripts/dev.sh

build:
	@echo "Building frontend..."
	@npm run build --prefix frontend
	@echo "Building Docker images..."
	@docker-compose build

test:
	@echo "Running tests..."
	@pytest backend/tests
	@npm test --prefix frontend

docker-up:
	@echo "Starting Docker containers..."
	@docker-compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	@docker-compose down

clean:
	@echo "Cleaning up..."
	@rm -rf backend/__pycache__ frontend/node_modules frontend/dist
	@docker-compose down --volumes --remove-orphans
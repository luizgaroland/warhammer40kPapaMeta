# Makefile
# Common Docker operations for Warhammer Meta Analysis Platform

.PHONY: help up down restart build logs clean init-db test-scraper shell-scraper shell-db status backup-db restore-db

# Default target - show help
help:
	@echo "Warhammer Meta Analysis Platform - Docker Commands"
	@echo "=================================================="
	@echo ""
	@echo "Setup & Infrastructure:"
	@echo "  make init           - Initial setup (create dirs, copy env, build)"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make build          - Build/rebuild all containers"
	@echo "  make clean          - Remove containers, volumes, and data"
	@echo ""
	@echo "Database Operations:"
	@echo "  make init-db        - Initialize database with schema"
	@echo "  make shell-db       - Open PostgreSQL shell"
	@echo "  make backup-db      - Backup database"
	@echo "  make restore-db     - Restore database from backup"
	@echo ""
	@echo "Scraper Operations:"
	@echo "  make test-scraper   - Run scraper tests"
	@echo "  make shell-scraper  - Open shell in scraper container"
	@echo "  make scrape-faction - Scrape a single faction (FACTION=name)"
	@echo ""
	@echo "Monitoring:"
	@echo "  make logs           - View all service logs"
	@echo "  make logs-scraper   - View scraper logs only"
	@echo "  make status         - Show container status"
	@echo "  make redis-cli      - Open Redis CLI"
	@echo ""
	@echo "Development:"
	@echo "  make dev            - Start services and tail logs"
	@echo "  make test           - Run all tests"

# =====================================================
# Setup & Infrastructure
# =====================================================

# Initial setup - create directories and build containers
init:
	@echo "========================================="
	@echo "Initializing Warhammer Meta Analysis Platform"
	@echo "========================================="
	@echo ""
	@echo "Creating directory structure..."
	@mkdir -p database/init database/backups
	@mkdir -p services/wahapedia-scraper/src/scrapers
	@mkdir -p services/wahapedia-scraper/src/publishers
	@mkdir -p services/wahapedia-scraper/src/utils
	@mkdir -p services/wahapedia-scraper/tests
	@mkdir -p services/laravel
	@mkdir -p logs/scraper logs/laravel
	@echo "✓ Directories created"
	@echo ""
	@echo "Creating Python package structure..."
	@touch services/wahapedia-scraper/src/__init__.py
	@touch services/wahapedia-scraper/src/scrapers/__init__.py
	@touch services/wahapedia-scraper/src/publishers/__init__.py
	@touch services/wahapedia-scraper/src/utils/__init__.py
	@touch services/wahapedia-scraper/tests/__init__.py
	@echo "✓ Python packages initialized"
	@echo ""
	@echo "Setting up environment file..."
	@if [ ! -f .env ]; then \
		echo "Creating .env from template..."; \
		if [ -f .env.example ]; then \
			cp .env.example .env; \
		else \
			echo "# Database Configuration" > .env; \
			echo "POSTGRES_DB=warhammer_meta" >> .env; \
			echo "POSTGRES_USER=warhammer_user" >> .env; \
			echo "POSTGRES_PASSWORD=warhammer_secret_2024" >> .env; \
			echo "POSTGRES_PORT=5432" >> .env; \
			echo "" >> .env; \
			echo "# Redis Configuration" >> .env; \
			echo "REDIS_PORT=6379" >> .env; \
			echo "" >> .env; \
			echo "# Scraper Configuration" >> .env; \
			echo "SCRAPER_ENV=development" >> .env; \
			echo "SCRAPER_LOG_LEVEL=INFO" >> .env; \
			echo "WAHAPEDIA_BASE_URL=https://wahapedia.ru" >> .env; \
			echo "RATE_LIMIT_DELAY=2" >> .env; \
		fi; \
		echo "✓ Environment file created"; \
	else \
		echo "✓ Environment file already exists"; \
	fi
	@echo ""
	@echo "Building Docker containers..."
	@docker-compose build
	@echo "✓ Containers built successfully"
	@echo ""
	@echo "========================================="
	@echo "✓ Setup complete! Run 'make up' to start services."
	@echo "========================================="

# Start all services
up:
	@echo "Starting services..."
	@docker-compose up -d
	@sleep 3
	@echo "✓ Services started"
	@echo ""
	@make status

# Stop all services
down:
	@echo "Stopping services..."
	@docker-compose down
	@echo "✓ Services stopped"

# Restart all services
restart:
	@echo "Restarting services..."
	@docker-compose restart
	@sleep 3
	@echo "✓ Services restarted"
	@make status

# Build/rebuild containers
build:
	@echo "Building containers..."
	@docker-compose build --no-cache
	@echo "✓ Build complete"

# Clean everything (WARNING: destructive)
clean:
	@echo "⚠️  WARNING: This will delete all containers, volumes, and data!"
	@read -p "Are you sure you want to continue? (y/N) " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "Cleaning up..."; \
		docker-compose down -v; \
		rm -rf logs/*; \
		echo "✓ Cleanup complete"; \
	else \
		echo "Cleanup cancelled"; \
	fi

# =====================================================
# Database Operations
# =====================================================

# Initialize database with schema
init-db:
	@echo "Initializing database..."
	@if [ -f database/init/schema.sql ]; then \
		docker exec -i warhammer_postgres psql -U warhammer_user -d warhammer_meta < database/init/schema.sql && \
		echo "✓ Database initialized successfully"; \
	else \
		echo "❌ Error: database/init/schema.sql not found"; \
		echo "Please add your SQL schema file to database/init/schema.sql"; \
		exit 1; \
	fi

# Open PostgreSQL shell
shell-db:
	@echo "Connecting to PostgreSQL..."
	@docker exec -it warhammer_postgres psql -U warhammer_user -d warhammer_meta

# Backup database
backup-db:
	@echo "Creating database backup..."
	@BACKUP_FILE="backup_$$(date +%Y%m%d_%H%M%S).sql" && \
	docker exec warhammer_postgres pg_dump -U warhammer_user warhammer_meta > database/backups/$$BACKUP_FILE && \
	echo "✓ Backup saved to database/backups/$$BACKUP_FILE"

# Restore database from backup
restore-db:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make restore-db FILE=backup_file.sql"; \
		exit 1; \
	fi
	@if [ ! -f "database/backups/$(FILE)" ]; then \
		echo "❌ Error: Backup file database/backups/$(FILE) not found"; \
		exit 1; \
	fi
	@echo "Restoring database from $(FILE)..."
	@docker exec -i warhammer_postgres psql -U warhammer_user -d warhammer_meta < database/backups/$(FILE)
	@echo "✓ Database restored successfully"

# =====================================================
# Scraper Operations
# =====================================================

# Test scraper connections
test-scraper:
	@echo "Testing scraper connections..."
	@docker exec warhammer_wahapedia_scraper python -c " \
		import sys; \
		print('Testing database connection...'); \
		try: \
			from sqlalchemy import create_engine; \
			engine = create_engine('postgresql://warhammer_user:warhammer_secret_2024@postgres:5432/warhammer_meta'); \
			conn = engine.connect(); \
			conn.close(); \
			print('✓ Database connection successful'); \
		except Exception as e: \
			print(f'❌ Database connection failed: {e}'); \
			sys.exit(1); \
		print(''); \
		print('Testing Redis connection...'); \
		try: \
			import redis; \
			r = redis.Redis(host='redis', port=6379, db=0); \
			r.ping(); \
			print('✓ Redis connection successful'); \
		except Exception as e: \
			print(f'❌ Redis connection failed: {e}'); \
			sys.exit(1); \
		print(''); \
		print('✓ All connections successful!'); \
	"

# Open shell in scraper container
shell-scraper:
	@echo "Opening scraper shell..."
	@docker exec -it warhammer_wahapedia_scraper /bin/bash

# Scrape a specific faction
scrape-faction:
	@if [ -z "$(FACTION)" ]; then \
		echo "Usage: make scrape-faction FACTION=faction_name"; \
		echo "Example: make scrape-faction FACTION=space_marines"; \
		exit 1; \
	fi
	@echo "Scraping faction: $(FACTION)"
	@docker exec warhammer_wahapedia_scraper python -m src.scrapers.wahapedia --faction $(FACTION)

# =====================================================
# Monitoring
# =====================================================

# View all logs
logs:
	@docker-compose logs -f --tail=100

# View scraper logs only
logs-scraper:
	@docker-compose logs -f --tail=100 wahapedia-scraper

# Show container status
status:
	@echo "Container Status:"
	@echo "-----------------"
	@docker-compose ps
	@echo ""
	@echo "Service Health:"
	@echo "---------------"
	@docker ps --filter "name=warhammer_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Open Redis CLI
redis-cli:
	@echo "Connecting to Redis..."
	@docker exec -it warhammer_redis redis-cli

# =====================================================
# Development Shortcuts
# =====================================================

# Start services and tail logs (development mode)
dev:
	@make up
	@make logs

# Run all tests
test:
	@echo "Running tests..."
	@make test-scraper
	@echo "✓ All tests passed"

# Quick restart for development
dev-restart:
	@docker-compose restart wahapedia-scraper
	@echo "✓ Scraper restarted"
	@docker-compose logs -f --tail=50 wahapedia-scraper

# =====================================================
# Docker Management
# =====================================================

# Show Docker disk usage
disk-usage:
	@echo "Docker Disk Usage:"
	@docker system df

# Prune unused Docker resources
prune:
	@echo "Pruning unused Docker resources..."
	@docker system prune -f
	@echo "✓ Prune complete"

# =====================================================
# Production Commands
# =====================================================

# Start in production mode
prod:
	@echo "Starting in production mode..."
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✓ Production services started"

# =====================================================
# Utility Functions
# =====================================================

# Check if all required files exist
check-files:
	@echo "Checking required files..."
	@[ -f docker-compose.yml ] && echo "✓ docker-compose.yml" || echo "❌ docker-compose.yml missing"
	@[ -f .env ] && echo "✓ .env" || echo "❌ .env missing"
	@[ -f services/wahapedia-scraper/Dockerfile ] && echo "✓ Scraper Dockerfile" || echo "❌ Scraper Dockerfile missing"
	@[ -f database/init/schema.sql ] && echo "✓ Database schema" || echo "❌ Database schema missing"
	@[ -f Makefile ] && echo "✓ Makefile" || echo "❌ Makefile missing"

# Show environment variables
show-env:
	@echo "Current Environment Variables:"
	@echo "------------------------------"
	@cat .env | grep -v '^#' | grep -v '^$$'

# Show ports in use
show-ports:
	@echo "Ports Configuration:"
	@echo "-------------------"
	@echo "PostgreSQL: 5432"
	@echo "Redis: 6379"
	@echo "pgAdmin: 5050"
	@echo "Redis Commander: 8081"

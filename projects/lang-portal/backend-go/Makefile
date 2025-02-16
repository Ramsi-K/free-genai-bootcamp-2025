.PHONY: build init seed run clean verify-db serve help

# Set environment variables for CGO
export CGO_ENABLED=1

# Windows-specific settings
ifeq ($(OS),Windows_NT)
    # Check for different shells
    ifeq ($(SHELL),/bin/bash)
        # Git Bash
        export PATH := /c/msys64/mingw64/bin:$(PATH)
        export CC := gcc
    else ifeq ($(SHELL),/usr/bin/bash)
        # MSYS2
        export PATH := /mingw64/bin:$(PATH)
        export CC := gcc
    else
        # CMD/PowerShell
        export PATH := C:\msys64\mingw64\bin;$(PATH)
        export CC := gcc
    endif
endif

# Ensure bin directory exists
bin:
	mkdir -p bin

# Build the database CLI tool with CGO enabled
build-db: bin
	go build -tags sqlite_fts5 -o bin/db cmd/db/main.go

# Build the server with CGO enabled
build-server: bin
	go build -tags sqlite_fts5 -o bin/server cmd/server/main.go

# Build all binaries
build: build-db build-server

# Initialize database
init: build-db
	./bin/db -init

# Seed database with data
seed: build-db
	./bin/db -seed

# Run the server
run: build-server
	./bin/server

# Clean build artifacts
clean:
	rm -rf bin/
	rm -rf instance/

# Install dependencies
deps:
	go mod tidy
	go mod download

# Verify GCC installation
verify-gcc:
	@echo "Checking GCC installation..."
	@gcc --version || (echo "GCC not found. Please install MSYS2 and run: pacman -S mingw-w64-x86_64-gcc" && exit 1)

# Full setup with GCC verification
setup: clean verify-gcc deps build init seed 

# Verify database contents
verify-db: build-db
	./bin/db -verify

# Run API server
serve: build-server
	./bin/server

# Show help
help:
	@echo "Available commands:"
	@echo "  make setup      - Full setup: install deps, build, init db, and seed"
	@echo "  make init      - Initialize database"
	@echo "  make seed      - Seed database with data"
	@echo "  make verify-db - Verify database contents"
	@echo "  make serve     - Start the API server"
	@echo "  make clean     - Remove build artifacts" 
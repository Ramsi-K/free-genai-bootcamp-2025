.PHONY: build init seed run clean

# Ensure bin directory exists
bin:
	mkdir -p bin

# Build the database CLI tool
build-db: bin
	go build -o bin/db cmd/db/main.go

# Build the server
build-server: bin
	go build -o bin/server cmd/server/main.go

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

# Full setup: install deps, build, init db, and seed
setup: deps build init seed 
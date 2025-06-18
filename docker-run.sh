#!/bin/bash

# Ranch Fire Alert Docker Runner
# This script helps you run the application with SQLite database

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Ranch Fire Alert Docker Runner${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to show usage
show_usage() {
    print_header
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start      - Start the application with SQLite database"
    echo "  stop       - Stop all containers"
    echo "  clean      - Stop and remove all containers and volumes"
    echo "  logs       - Show logs from running containers"
    echo "  status     - Show status of containers"
    echo "  backup     - Create database backup"
    echo "  restore    - Restore database from backup"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start       # Start the application"
    echo "  $0 stop        # Stop all containers"
    echo "  $0 logs        # View logs"
    echo ""
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to start the application
start_application() {
    print_status "Starting Ranch Fire Alert with SQLite database..."
    
    # Check if containers are already running
    if docker compose ps | grep -q "Up"; then
        print_warning "Containers are already running. Stopping first..."
        docker compose down
    fi
    
    # Start containers
    docker compose up -d
    
    print_status "Waiting for services to start..."
    sleep 5
    
    # Check if services are healthy
    if docker compose ps | grep -q "Up"; then
        print_status "✅ Ranch Fire Alert is running with SQLite!"
        print_status "🌐 Access the application at: http://localhost:8088"
        print_status "📊 Admin interface: http://localhost:8088/admin"
        print_status "📝 View logs: $0 logs"
    else
        print_error "❌ Failed to start services. Check logs with: $0 logs"
        exit 1
    fi
}

# Function to stop containers
stop_containers() {
    print_status "Stopping all containers..."
    docker compose down
    print_status "✅ All containers stopped."
}

# Function to clean everything
clean_containers() {
    print_warning "This will remove ALL containers and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning all containers and volumes..."
        docker compose down -v
        print_status "✅ All containers and volumes removed."
    else
        print_status "Clean operation cancelled."
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing logs from running containers..."
    if docker compose ps | grep -q "Up"; then
        docker compose logs -f
    else
        print_warning "No containers are currently running."
    fi
}

# Function to show status
show_status() {
    print_status "Container status:"
    echo ""
    docker compose ps
}

# Function to create backup
create_backup() {
    print_status "Creating database backup..."
    if docker compose ps | grep -q "Up"; then
        docker compose exec web python -c "
import os
import sys
sys.path.append('/app')
from app import create_backup
create_backup()
print('Backup created successfully!')
"
    else
        print_warning "No containers are currently running."
    fi
}

# Function to restore backup
restore_backup() {
    print_warning "This will overwrite the current database. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Restoring database from backup..."
        if docker compose ps | grep -q "Up"; then
            docker compose exec web python -c "
import os
import sys
sys.path.append('/app')
from app import restore_backup
restore_backup()
print('Backup restored successfully!')
"
        else
            print_warning "No containers are currently running."
        fi
    else
        print_status "Restore operation cancelled."
    fi
}

# Main script logic
main() {
    check_docker
    
    case "${1:-help}" in
        start)
            start_application
            ;;
        stop)
            stop_containers
            ;;
        clean)
            clean_containers
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        backup)
            create_backup
            ;;
        restore)
            restore_backup
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 
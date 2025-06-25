#!/bin/bash

# Docker management commands for CambioML Backend

case "$1" in
    "start")
        echo "🚀 Starting CambioML Backend services..."
        docker-compose up -d
        echo "✅ Services started!"
        echo "   Frontend: http://localhost:8000/static/index.html"
        echo "   API Docs: http://localhost:8000/docs"
        ;;
    
    "stop")
        echo "🛑 Stopping CambioML Backend services..."
        docker-compose down
        echo "✅ Services stopped!"
        ;;
    
    "restart")
        echo "🔄 Restarting CambioML Backend services..."
        docker-compose down
        docker-compose up -d
        echo "✅ Services restarted!"
        ;;
    
    "logs")
        echo "📋 Showing logs..."
        docker-compose logs -f
        ;;
    
    "status")
        echo "📊 Service status:"
        docker-compose ps
        ;;
    
    "build")
        echo "🏗️  Building services..."
        docker-compose build --no-cache
        echo "✅ Build completed!"
        ;;
    
    "clean")
        echo "🧹 Cleaning up Docker resources..."
        docker-compose down -v
        docker system prune -f
        echo "✅ Cleanup completed!"
        ;;
    
    "backup")
        echo "💾 Creating database backup..."
        mkdir -p backups
        docker-compose exec postgres pg_dump -U cambioml cambioml > backups/backup_$(date +%Y%m%d_%H%M%S).sql
        echo "✅ Backup created in backups/ directory"
        ;;
    
    "restore")
        if [ -z "$2" ]; then
            echo "❌ Please provide backup file: $0 restore <backup_file>"
            exit 1
        fi
        echo "🔄 Restoring database from $2..."
        docker-compose exec -T postgres psql -U cambioml -d cambioml < "$2"
        echo "✅ Database restored!"
        ;;
    
    *)
        echo "CambioML Backend Docker Management"
        echo "=================================="
        echo "Usage: $0 {start|stop|restart|logs|status|build|clean|backup|restore}"
        echo ""
        echo "Commands:"
        echo "  start    - Start all services"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - Show service logs"
        echo "  status   - Show service status"
        echo "  build    - Build services"
        echo "  clean    - Clean up Docker resources"
        echo "  backup   - Create database backup"
        echo "  restore  - Restore database from backup"
        ;;
esac

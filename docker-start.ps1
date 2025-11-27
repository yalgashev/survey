# Quick Docker Start Script
# Run this script to start the application in Docker

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Student-Professor Evaluation System" -ForegroundColor Cyan
Write-Host "Docker Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found or not running." -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

# Check if Docker Compose is available
try {
    $composeVersion = docker-compose --version
    Write-Host "✓ Found: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Compose not found." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building and Starting Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Build and start services
docker-compose up --build -d

Write-Host ""
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Application: http://localhost:8000" -ForegroundColor Green
Write-Host "Admin Panel: http://localhost:8000/admin-panel/login/" -ForegroundColor Green
Write-Host ""
Write-Host "To create a superuser account, run:" -ForegroundColor Yellow
Write-Host "  docker-compose exec web python manage.py createsuperuser" -ForegroundColor Cyan
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop services:" -ForegroundColor Yellow
Write-Host "  docker-compose down" -ForegroundColor Cyan
Write-Host ""

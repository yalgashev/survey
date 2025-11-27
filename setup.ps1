# Quick Setup Script for Windows PowerShell
# This script will help you set up the entire project

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Student-Professor Evaluation System" -ForegroundColor Cyan
Write-Host "Quick Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8+." -ForegroundColor Red
    exit 1
}

# Check PostgreSQL
Write-Host "`nChecking PostgreSQL..." -ForegroundColor Yellow
try {
    $pgVersion = psql --version
    Write-Host "✓ Found: $pgVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ PostgreSQL not found. Please install PostgreSQL 12+." -ForegroundColor Red
    Write-Host "Download from: https://www.postgresql.org/download/" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Step 1: Creating Virtual Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (Test-Path "venv") {
    Write-Host "Virtual environment already exists." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created." -ForegroundColor Green
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Step 2: Activating Virtual Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

& "venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated." -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Step 3: Installing Dependencies" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

pip install -r requirements.txt
Write-Host "✓ Dependencies installed." -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Step 4: Database Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "IMPORTANT: Before proceeding, please:" -ForegroundColor Yellow
Write-Host "1. Create PostgreSQL database: survey_db" -ForegroundColor Yellow
Write-Host "2. Update config/settings.py with your PostgreSQL credentials" -ForegroundColor Yellow
Write-Host ""
$continue = Read-Host "Have you completed the above? (y/n)"

if ($continue -ne "y") {
    Write-Host "`nSetup paused. Please complete the database setup and run this script again." -ForegroundColor Yellow
    exit 0
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Step 5: Running Migrations" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

python manage.py makemigrations
python manage.py migrate
Write-Host "✓ Database migrations completed." -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Step 6: Creating Superuser" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "Please create an admin account:" -ForegroundColor Yellow
python manage.py createsuperuser

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Step 7: Loading Sample Data (Optional)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$loadSample = Read-Host "Would you like to load sample data? (y/n)"

if ($loadSample -eq "y") {
    python setup_sample_data.py
    Write-Host "✓ Sample data loaded." -ForegroundColor Green
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the development server, run:" -ForegroundColor Yellow
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Then visit:" -ForegroundColor Yellow
Write-Host "  Public Survey: http://localhost:8000" -ForegroundColor White
Write-Host "  Admin Panel:   http://localhost:8000/admin" -ForegroundColor White
Write-Host "  Edit Section:  http://localhost:8000/edit/" -ForegroundColor White
Write-Host ""
Write-Host "Happy evaluating! 🎓" -ForegroundColor Green

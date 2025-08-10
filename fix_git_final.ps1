#!/usr/bin/env powershell
# Complete Git Repository Fix Script

Write-Host "🔧 Starting complete git repository cleanup..." -ForegroundColor Green

# Navigate to repository root
Set-Location "c:\Users\Acer\Downloads\CineScopeAnalyzer"

# 1. Abort any ongoing merge
Write-Host "📋 Aborting any ongoing merge..." -ForegroundColor Yellow
git merge --abort 2>$null

# 2. Reset to clean state
Write-Host "🔄 Resetting to clean state..." -ForegroundColor Yellow
git reset --hard HEAD

# 3. Clean untracked files
Write-Host "🧹 Cleaning untracked files..." -ForegroundColor Yellow
git clean -fd

# 4. Check current status
Write-Host "📊 Current git status:" -ForegroundColor Cyan
git status

# 5. Force push the cleaned state
Write-Host "🚀 Force pushing cleaned repository..." -ForegroundColor Green
git push origin main --force

Write-Host "✅ Git repository cleanup complete!" -ForegroundColor Green
Write-Host "🎯 Repository should now be clean and pushable." -ForegroundColor Green

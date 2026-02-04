# ============================================
# Security Cleanup Script
# ============================================
# This script removes sensitive files from git tracking
# while keeping them in your local directory

# Remove secrets.toml from git tracking (but keep local file)
Write-Host "Removing .streamlit/secrets.toml from git tracking..." -ForegroundColor Yellow
git rm --cached .streamlit/secrets.toml

# Remove CSV files from git tracking
Write-Host "Removing CSV files from git tracking..." -ForegroundColor Yellow
git rm --cached *.csv 2>$null

Write-Host "`n✅ Sensitive files removed from git tracking!" -ForegroundColor Green
Write-Host "ℹ️  Your local files are still safe and won't be deleted." -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor White
Write-Host "1. Review changes: git status" -ForegroundColor Gray
Write-Host "2. Commit the changes: git commit -m 'chore: remove sensitive files from tracking'" -ForegroundColor Gray
Write-Host "3. Push to remote: git push" -ForegroundColor Gray

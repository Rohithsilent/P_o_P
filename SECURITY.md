# 🔒 Security Guide - API Key Protection

## ⚠️ CRITICAL: Files Currently Tracked by Git

The following sensitive files are **currently being tracked** by git and need to be removed:

1. `.streamlit/secrets.toml` - Contains YouTube API key
2. `9R3X0JoCLyU.csv` - Contains scraped YouTube comment data

## 🛡️ How to Remove Sensitive Files from Git

### Option 1: Use the Cleanup Script (Recommended)
```powershell
.\remove_sensitive_files.ps1
```

### Option 2: Manual Removal
```bash
# Remove secrets.toml from git (keeps local file)
git rm --cached .streamlit/secrets.toml

# Remove all CSV files from git
git rm --cached *.csv

# Commit the changes
git commit -m "chore: remove sensitive files from git tracking"

# Push to remote
git push
```

## ✅ Protected Files

Your `.gitignore` now protects:

### API Keys & Secrets
- `.env` - Gemini API key
- `.streamlit/secrets.toml` - YouTube API key
- `*.env` files
- `*.key` files
- `secrets/` directory

### Data Files
- `*.csv` - Comment data exports
- `*.json` - JSON data files
- `*.db`, `*.sqlite` - Database files

### Development Files
- `__pycache__/`, `*.pyc` - Python cache
- `.vscode/`, `.idea/` - IDE configs
- `*.log` - Log files
- `node_modules/` - Node packages (if added)

## 📋 Pre-Commit Checklist

Before every commit, verify:

```bash
# Check what files will be committed
git status

# Verify sensitive files are ignored
git check-ignore -v .env .streamlit/secrets.toml

# Review actual changes
git diff
```

## 🔐 Example Files Provided

Safe template files you CAN commit:
- `.env.example` - Template for environment variables
- `.streamlit/secrets.toml.example` - Template for Streamlit secrets

## 🚨 What to Do If You Accidentally Commit Keys

1. **Immediately revoke the exposed API keys**
   - Gemini: https://aistudio.google.com/app/apikey
   - YouTube: https://console.cloud.google.com/apis/credentials

2. **Remove from git history**
   ```bash
   # Use BFG Repo-Cleaner or git filter-branch
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```

3. **Generate new API keys**

4. **Force push** (⚠️ dangerous - coordinate with team)
   ```bash
   git push --force --all
   ```

## 📚 Additional Resources

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [Google Cloud: Best practices for API keys](https://cloud.google.com/docs/authentication/api-keys)
- [OWASP: Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

## ✅ Verification Commands

```bash
# List all files tracked by git
git ls-files

# Check if sensitive files are tracked
git ls-files | findstr /i ".env secrets.toml .csv"

# Should return nothing if properly configured!
```

---

**Remember**: Once a secret is committed to git, assume it's compromised. Always rotate keys immediately!

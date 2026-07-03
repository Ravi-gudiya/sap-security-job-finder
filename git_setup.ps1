# git_setup.ps1
# Helper script to initialize git and prepare repository for pushing to GitHub

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   Naukri Bot GitHub Setup Assistant" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Check if git is installed
$gitCheck = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCheck) {
    Write-Host "[!] Git is not installed on this system. Please download and install Git from: https://git-scm.com/" -ForegroundColor Red
    Exit
}

# 1. Initialize git if not already initialized
if (-not (Test-Path ".git")) {
    Write-Host "[*] Initializing local git repository..." -ForegroundColor Yellow
    git init
} else {
    Write-Host "[+] Local git repository already initialized." -ForegroundColor Green
}

# 2. Add files
Write-Host "[*] Staging files for commit..." -ForegroundColor Yellow
git add .

# 3. Create initial commit
Write-Host "[*] Creating initial commit..." -ForegroundColor Yellow
# Check if there is anything to commit
$status = git status --porcelain
if ($status) {
    git commit -m "Initial commit of Naukri Bot"
    Write-Host "[+] Successfully created initial commit!" -ForegroundColor Green
} else {
    Write-Host "[+] Nothing to commit, local state matches Git repository." -ForegroundColor Green
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "            NEXT STEPS ON GITHUB" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "1. Open your browser and go to: https://github.com/new"
Write-Host "2. Create a NEW repository:" -ForegroundColor Yellow
Write-Host "   - Repository name: sap-security-job-finder"
Write-Host "   - Public/Private: Choose PRIVATE (Crucial! Do not make it public)" -ForegroundColor Red
Write-Host "   - Do NOT add a README, gitignore, or license."
Write-Host "3. Once created, copy the URL of your repository."
Write-Host "4. In this terminal, run the following commands (replace URL with yours):" -ForegroundColor Yellow
Write-Host "   git remote add origin <PASTE_YOUR_GITHUB_PRIVATE_REPO_URL>"
Write-Host "   git branch -M main"
Write-Host "   git push -u origin main"
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Important GitHub Actions Configuration:" -ForegroundColor Yellow
Write-Host "   In your GitHub repository web page:"
Write-Host "   - Go to Settings -> Actions -> General"
Write-Host "   - Scroll down to 'Workflow permissions'"
Write-Host "   - Select 'Read and write permissions'" -ForegroundColor Green
Write-Host "   - Click 'Save'"
Write-Host "=============================================" -ForegroundColor Cyan

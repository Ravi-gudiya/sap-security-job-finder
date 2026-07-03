# Naukri Auto-Apply & Profile Auto-Updater Bot

This bot automates the process of updating your Naukri profile (to make it look active to recruiters) and auto-applying to SAP Security jobs.

## Features
1. **Auto Profile Updater**: Edits your Resume Headline slightly (toggles a period at the end) and saves it. This updates the "Last updated" date on your profile, boosting search visibility. If a `resume.pdf` exists in the folder, it will also re-upload it.
2. **Auto Job Applier**: Searches for "SAP Security" jobs (or any other custom search keyword) and applies to direct-apply job posts automatically, up to a custom limit.
3. **Session Persistence**: Reuses your logged-in session cookies/data using Playwright persistent contexts, avoiding CAPTCHAs, OTPs, and email checks on subsequent runs.
4. **Daily Scheduling**: Runs automatically twice a day (8:30 AM and 5:30 PM) using Windows Task Scheduler.

---

## Setup Instructions

### Step 1: Install Dependencies
If you haven't already, make sure you have Python installed, then set up the virtual environment:
```cmd
python -m venv venv
venv\Scripts\activate
pip install playwright
playwright install chromium
```

### Step 2: Perform One-Time Manual Login
Run the setup script to log in to your Naukri account. This opens a visible browser window:
```cmd
venv\Scripts\activate
python naukri_bot.py --setup
```
1. In the opened browser window, log in to Naukri.com using your credentials (solve any OTP, email verification, or CAPTCHA).
2. Go to your dashboard or profile page.
3. Return to the command prompt/terminal, and press **Enter** to save the session.
4. The browser will close, and your login state will be saved in the `naukri_profile` folder.

### Step 3: Verify the Bot Works
To test both profile update and job application in visible (headed) mode, run:
```cmd
python naukri_bot.py --run --headed --limit 2
```
This will run the profile update, then search for "SAP Security" jobs and apply to up to 2 of them. You can check the logs in `naukri_bot.log`.

### Step 4: Schedule the Bot (Choose Local OR GitHub Actions)

#### Option A: Run on GitHub Actions (Recommended - Runs when Laptop is Off)
1. Initialize git and commit your files locally:
   ```powershell
   powershell -ExecutionPolicy Bypass -File git_setup.ps1
   ```
2. Go to [GitHub](https://github.com/new) and create a new **PRIVATE** repository. Name it `sap-security-job-finder`.
3. Add the GitHub remote and push your files:
   ```cmd
   git remote add origin https://github.com/YOUR_USERNAME/sap-security-job-finder.git
   git branch -M main
   git push -u origin main
   ```
4. **Enable Actions Permissions**:
   - In your GitHub repo, go to **Settings** ➔ **Actions** ➔ **General**.
   - Under **Workflow permissions**, select **"Read and write permissions"** (required so the workflow can save updated session cookies).
   - Click **Save**.
5. The workflow is scheduled to run at **8:30 AM IST** (3:00 AM UTC) and **5:30 PM IST** (12:00 PM UTC) daily. You can also run it manually by going to the **Actions** tab on GitHub, selecting **Naukri Auto Update & Apply**, and clicking **Run workflow**.

#### Option B: Run on local Windows Task Scheduler (Runs only when Laptop is On)
If you prefer not to use GitHub, you can schedule it on your local system:
1. Open PowerShell.
2. Navigate to this directory.
3. Run the local scheduling script:
   ```powershell
   powershell -ExecutionPolicy Bypass -File schedule_task.ps1
   ```

---

## Configuration & Usage Details

### Command-Line Arguments
You can run the bot with specific options using the virtual environment python:
* `--setup`: Run interactive login setup.
* `--update-profile`: Run the profile update process only.
* `--apply-jobs`: Search and apply for jobs only.
* `--run`: Run both profile update and job application.
* `--query "SAP Security"`: Change the job search query (default is "SAP Security").
* `--limit 5`: Maximum number of applications per run (default is 5).
* `--headless`: Run the browser in headless mode (default is headed-minimized).

### Logs
* **Local runs**: Written to `naukri_bot.log` in this directory.
* **GitHub Action runs**: Outputted directly in the run execution step logs under the **Actions** tab of your GitHub repository.


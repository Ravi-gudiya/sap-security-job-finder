#!/usr/bin/env python3
import os
import sys
import time
import argparse
import datetime
import urllib.parse
from playwright.sync_api import sync_playwright

SESSION_DIR = os.path.join(os.path.dirname(__file__), "naukri_profile")
LOG_FILE = os.path.join(os.path.dirname(__file__), "naukri_bot.log")

def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted_message + "\n")
    except Exception as e:
        print(f"Failed to write to log file: {e}")

def login_setup():
    log_message("[*] Starting browser for one-time manual login...")
    if not os.path.exists(SESSION_DIR):
        os.makedirs(SESSION_DIR)
        
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto("https://www.naukri.com/nlogin/login")
        
        log_message("[!] PLEASE LOG IN MANUALLY IN THE OPENED BROWSER WINDOW.")
        log_message("[!] Enter your credentials, solve any OTP or Captcha required.")
        log_message("[!] Once you successfully log in and see your dashboard, return here.")
        
        input("\n>>> Press ENTER key in this terminal window AFTER you have successfully logged in... ")
        
        # Verify login by attempting to load the profile page
        log_message("[*] Verifying login state...")
        page.goto("https://www.naukri.com/mnjuser/profile")
        page.wait_for_timeout(3000)
        
        if "nlogin" in page.url:
            log_message("[!] Warning: It seems you are not logged in. Redirected to login page.")
        else:
            log_message("[+] Login verified successfully!")
            
        browser.close()
        
    log_message("[+] Session setup completed and browser context saved.")

def update_profile(headless=True):
    log_message("[*] Initiating Naukri profile auto-update...")
    if not os.path.exists(SESSION_DIR):
        log_message("[!] Error: Session directory not found. Please run with '--setup' first.")
        return False
        
    success = False
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=SESSION_DIR,
                headless=headless,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                args=["--disable-blink-features=AutomationControlled", "--start-minimized"]
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            log_message("[*] Navigating to profile page...")
            page.goto("https://www.naukri.com/mnjuser/profile")
            page.wait_for_timeout(5000)
            
            if "nlogin" in page.url:
                log_message("[!] Error: Session expired or not logged in. Please run with '--setup' to re-authenticate.")
                browser.close()
                return False
                
            # Locate the edit button for Resume Headline
            log_message("[*] Locating Resume Headline edit icon...")
            edit_btn = None
            selectors = [
                "xpath=//div[contains(@class, 'resumeHeadline')]//span[contains(text(), 'edit') or contains(@class, 'edit') or contains(@class, 'icon')]",
                "xpath=//*[@id='lazyResumeHead']//span[contains(text(), 'edit') or contains(@class, 'edit')]",
                "css=div.resumeHeadline span.edit",
                "css=#lazyResumeHead span.edit"
            ]
            
            for selector in selectors:
                try:
                    locator = page.locator(selector)
                    if locator.first.is_visible(timeout=2000):
                        edit_btn = locator.first
                        log_message(f"[+] Found edit button using selector: {selector}")
                        break
                except Exception:
                    continue
                    
            if not edit_btn:
                log_message("[*] Direct selector failed. Attempting to click parent wrapper container...")
                try:
                    # Look for parent wrapper containing text Resume Headline
                    page.get_by_text("Resume headline").locator("xpath=..").locator("span.edit").click(timeout=3000)
                    edit_btn = "clicked"
                except Exception as e:
                    log_message(f"[!] Fallback locator failed: {e}")
                    
            if edit_btn and edit_btn != "clicked":
                edit_btn.click()
                page.wait_for_timeout(2000)
                
            log_message("[*] Locating Resume Headline textarea...")
            textarea_selector = "#resumeHeadlineTxt"
            page.wait_for_selector(textarea_selector, timeout=5000)
            textarea = page.locator(textarea_selector)
            
            current_headline = textarea.input_value()
            log_message(f"[*] Current Resume Headline: '{current_headline}'")
            
            # Modify slightly (toggle a trailing dot)
            if current_headline.endswith("."):
                new_headline = current_headline[:-1].strip()
            else:
                new_headline = current_headline.strip() + "."
                
            log_message(f"[*] Updating Resume Headline to: '{new_headline}'")
            textarea.fill(new_headline)
            page.wait_for_timeout(1000)
            
            log_message("[*] Saving profile changes...")
            save_selectors = [
                "xpath=//button[@type='submit' and text()='Save']",
                "xpath=//button[contains(text(), 'Save')]",
                "css=button.btn-dark-ot",
                "xpath=//div[contains(@class, 'resumeHeadline')]//button"
            ]
            
            saved = False
            for selector in save_selectors:
                try:
                    btn = page.locator(selector)
                    if btn.first.is_visible(timeout=2000):
                        btn.first.click()
                        saved = True
                        log_message(f"[+] Clicked Save button using selector: {selector}")
                        break
                except Exception:
                    continue
                    
            if not saved:
                log_message("[!] Save selectors failed. Attempting to submit via Enter...")
                textarea.press("Enter")
                page.wait_for_timeout(2000)
                
            page.wait_for_timeout(4000)
            log_message("[+] Profile update completed successfully!")
            success = True
            
            # Optional Resume Upload
            resume_path = os.path.join(os.path.dirname(__file__), "resume.pdf")
            if os.path.exists(resume_path):
                log_message("[*] Local 'resume.pdf' found. Attempting to upload to profile...")
                file_input = page.locator("input[type='file']")
                if file_input.count() > 0:
                    file_input.first.set_input_files(resume_path)
                    log_message("[+] Resume PDF uploaded successfully!")
                    page.wait_for_timeout(5000)
                else:
                    log_message("[!] No file input field found for resume upload.")
                    
        except Exception as e:
            log_message(f"[!] Error updating profile: {e}")
            try:
                screenshot_path = os.path.join(os.path.dirname(__file__), f"error_profile_{int(time.time())}.png")
                page.screenshot(path=screenshot_path)
                log_message(f"[!] Saved error screenshot to: {screenshot_path}")
            except Exception as ex:
                log_message(f"[!] Failed to save screenshot: {ex}")
        finally:
            try:
                browser.close()
            except Exception:
                pass
            
    return success

def apply_jobs(query="SAP Security", limit=5, headless=True):
    log_message(f"[*] Initiating auto-apply for '{query}' (Limit: {limit} jobs)...")
    if not os.path.exists(SESSION_DIR):
        log_message("[!] Error: Session directory not found. Please run with '--setup' first.")
        return 0
        
    applied_count = 0
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=SESSION_DIR,
                headless=headless,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                args=["--disable-blink-features=AutomationControlled", "--start-minimized"]
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.naukri.com/{encoded_query.replace('%20', '-')}-jobs?k={encoded_query}"
            log_message(f"[*] Navigating to search URL: {search_url}")
            page.goto(search_url)
            page.wait_for_timeout(6000)
            
            log_message("[*] Waiting for job listings to load...")
            job_cards_selector = "div.srp-job-tuple, div[data-job-id], article"
            try:
                page.wait_for_selector(job_cards_selector, timeout=12000)
            except Exception:
                log_message("[!] Timeout waiting for job cards. Trying generic links...")
                
            card_elements = page.locator("div.srp-job-tuple, div[data-job-id]").all()
            log_message(f"[*] Found {len(card_elements)} job listings on the page.")
            
            job_urls = []
            for card in card_elements:
                try:
                    title_link = card.locator("a.title")
                    if title_link.count() > 0:
                        href = title_link.first.get_attribute("href")
                        if href and href.startswith("http"):
                            job_urls.append(href)
                except Exception:
                    continue
                    
            if not job_urls:
                # Fallback: Find all links to job listings
                links = page.locator("a").all()
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        if href and "/job-listings-" in href and href not in job_urls:
                            job_urls.append(href)
                    except Exception:
                        continue
            
            log_message(f"[+] Collected {len(job_urls)} job details URLs.")
            
            for index, url in enumerate(job_urls):
                if applied_count >= limit:
                    log_message(f"[*] Reached application limit of {limit} for this run. Stopping.")
                    break
                    
                log_message(f"[*] [{index+1}/{len(job_urls)}] Inspecting job page: {url}")
                job_page = browser.new_page()
                try:
                    job_page.goto(url, timeout=20000)
                    job_page.wait_for_timeout(4000)
                    
                    page_text = job_page.content().lower()
                    if "already applied" in page_text or "applied" in page_text:
                        log_message("[-] Already applied. Skipping.")
                        job_page.close()
                        continue
                        
                    # Check for external company site redirects
                    company_site_selectors = [
                        "xpath=//button[contains(text(), 'Apply on company') or contains(text(), 'Company site')]",
                        "xpath=//a[contains(text(), 'Apply on company') or contains(text(), 'Company site')]"
                    ]
                    
                    is_company_site = False
                    for selector in company_site_selectors:
                        try:
                            if job_page.locator(selector).first.is_visible(timeout=1000):
                                is_company_site = True
                                break
                        except Exception:
                            continue
                            
                    if is_company_site:
                        log_message("[-] Job requires application on third-party company site. Skipping.")
                        job_page.close()
                        continue
                        
                    # Locate direct Apply buttons
                    apply_selectors = [
                        "xpath=//button[text()='Apply' or text()='Easy Apply' or contains(text(), 'Quick Apply')]",
                        "css=button.apply-button",
                        "xpath=//button[contains(@class, 'apply')]"
                    ]
                    
                    apply_btn = None
                    for selector in apply_selectors:
                        try:
                            locator = job_page.locator(selector)
                            if locator.first.is_visible(timeout=2000):
                                apply_btn = locator.first
                                break
                        except Exception:
                            continue
                            
                    if apply_btn:
                        log_message("[*] Clicking Apply button...")
                        apply_btn.click()
                        job_page.wait_for_timeout(5000)
                        
                        # Verify if a questionnaire or registration page was triggered
                        new_content = job_page.content().lower()
                        if "questionnaire" in new_content or "survey" in new_content or "answer" in new_content:
                            log_message("[!] Warning: Application page loaded custom questions. Skipping to prevent invalid submit.")
                        else:
                            log_message("[+] Successfully applied to job!")
                            applied_count += 1
                    else:
                        log_message("[-] Apply button not found or could not interact.")
                        
                except Exception as e:
                    log_message(f"[!] Error processing job details page: {e}")
                finally:
                    try:
                        job_page.close()
                    except Exception:
                        pass
                    job_page.wait_for_timeout(1000)
                    
        except Exception as e:
            log_message(f"[!] Error during job apply flow: {e}")
            try:
                screenshot_path = os.path.join(os.path.dirname(__file__), f"error_apply_{int(time.time())}.png")
                page.screenshot(path=screenshot_path)
                log_message(f"[!] Saved error screenshot to: {screenshot_path}")
            except Exception as ex:
                log_message(f"[!] Failed to save screenshot: {ex}")
        finally:
            try:
                browser.close()
            except Exception:
                pass
            
    log_message(f"[+] Completed run. Successfully applied to {applied_count} jobs.")
    return applied_count

def main():
    parser = argparse.ArgumentParser(description="Naukri Automation Bot")
    parser.add_argument("--setup", action="store_true", help="Run browser in headed mode to login manually")
    parser.add_argument("--update-profile", action="store_true", help="Auto-update the Naukri profile headline")
    parser.add_argument("--apply-jobs", action="store_true", help="Search and auto-apply for SAP Security jobs")
    parser.add_argument("--query", type=str, default="SAP Security", help="Job search query")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of job applications per run")
    parser.add_argument("--run", action="store_true", help="Run both profile update and job application")
    parser.add_argument("--headless", action="store_true", help="Run the browser in headless mode (warning: may get Access Denied)")
    args = parser.parse_args()
    
    if not (args.setup or args.update_profile or args.apply_jobs or args.run):
        parser.print_help()
        sys.exit(1)
        
    if args.setup:
        login_setup()
        sys.exit(0)
        
    # Default to headed mode (headless=False) because headless is blocked by Naukri
    headless = args.headless
    
    if args.run or args.update_profile:
        update_profile(headless=headless)
        
    if args.run or args.apply_jobs:
        apply_jobs(query=args.query, limit=args.limit, headless=headless)

if __name__ == "__main__":
    main()

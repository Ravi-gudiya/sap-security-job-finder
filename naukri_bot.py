#!/usr/bin/env python3
import os
import sys
import time
import argparse
import datetime
import urllib.parse
from playwright.sync_api import sync_playwright

STATE_FILE = os.path.join(os.path.dirname(__file__), "naukri_state.json")
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
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
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
            context.storage_state(path=STATE_FILE)
            log_message(f"[+] Session state saved to: {STATE_FILE}")
            
        browser.close()
        
    log_message("[+] Session setup completed.")

def update_profile(headless=True):
    log_message("[*] Initiating Naukri profile auto-update...")
    if not os.path.exists(STATE_FILE):
        log_message("[!] Error: Session state file not found. Please run with '--setup' first.")
        return False
        
    success = False
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(
                storage_state=STATE_FILE,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()
            
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
            context.storage_state(path=STATE_FILE)
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

def send_external_job_email(job_url, company_url):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    recipient = "gudiyaravi02@gmail.com"
    sender_email = os.environ.get("EMAIL_USER")
    sender_password = os.environ.get("EMAIL_PASS")
    
    if not sender_email or not sender_password:
        log_message(f"[!] Warning: Email credentials (EMAIL_USER / EMAIL_PASS) not set in Environment. Cannot send email.")
        log_message(f"    Company Careers Link: {company_url or 'Please check Naukri Job Link'}")
        log_message(f"    Naukri Job Link: {job_url}")
        return False
        
    log_message(f"[*] Preparing to send email notification to {recipient}...")
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = "Naukri Bot: External Career Portal Job Link"
        
        body = f"""Hello,

The Naukri automation bot has found an SAP Security job listing that requires applying directly on the company's career portal:

- Naukri Job Link: {job_url}
- Company Application Link: {company_url or 'See Naukri page'}

Please click the link above to submit your application manually.

Best regards,
Your Naukri Automation Bot"""

        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()
        log_message(f"[+] Email successfully sent to {recipient}!")
        return True
    except Exception as e:
        log_message(f"[!] Error sending email: {e}")
        return False

def handle_questionnaire(job_page):
    log_message("[*] Checking for questionnaire / custom questions...")
    fields = job_page.locator("input[type='text'], input[type='number'], input[type='tel'], textarea, select, input[type='radio'], input[type='checkbox']").all()
    if not fields:
        return False
        
    log_message(f"[*] Found {len(fields)} form fields. Attempting to answer...")
    handled_radios = set()
    
    for field in fields:
        try:
            if not field.is_visible() or not field.is_enabled():
                continue
                
            field_type = field.get_attribute("type")
            field_name = field.get_attribute("name")
            
            if field_type == "radio":
                if field_name in handled_radios:
                    continue
            
            question_text = field.evaluate("""
                el => {
                    if (el.id) {
                        let label = document.querySelector(`label[for="${el.id}"]`);
                        if (label && label.innerText.trim()) return label.innerText.trim();
                    }
                    let container = el.closest('.question, .field, .row, .container, .form-group, li, tr, .tuple');
                    if (container) {
                        let lbl = container.querySelector('label, .label, .q-text, .question-text, span');
                        if (lbl && lbl.innerText.trim()) return lbl.innerText.trim();
                        return container.innerText.trim();
                    }
                    return '';
                }
            """)
            
            if not question_text:
                continue
                
            q_lower = question_text.lower()
            log_message(f"  Field Label/Question: '{question_text.strip()}'")
            
            answer = None
            if "experience" in q_lower or "year" in q_lower:
                answer = "3" if field_type == "number" else "2.6 Years"
            elif "notice" in q_lower:
                answer = "Immediate"
            elif "expected" in q_lower and ("ctc" in q_lower or "salary" in q_lower or "lpa" in q_lower):
                answer = "9,00,000" if field_type != "number" else "900000"
            elif "current" in q_lower and ("ctc" in q_lower or "salary" in q_lower or "lpa" in q_lower):
                answer = "6,00,000" if field_type != "number" else "600000"
            elif "location" in q_lower or "city" in q_lower:
                if field_type in ["radio", "checkbox"]:
                    answer = "PreferredCity"
                else:
                    answer = "Bhubaneswar, Hyderabad, Bangalore, Chennai, Mysore"
            elif "sap" in q_lower or "security" in q_lower or "grc" in q_lower:
                answer = "Yes" if field_type in ["radio", "checkbox"] else "2.6 Years"
            elif "relocate" in q_lower or "ready" in q_lower:
                answer = "Yes"
                
            if not answer:
                if "yes" in q_lower or "no" in q_lower:
                    answer = "Yes"
                else:
                    answer = "Yes" if field_type in ["radio", "checkbox"] else "Immediate"
            
            if field_type in ["radio", "checkbox"]:
                value = (field.get_attribute("value") or "").lower()
                label_text = field.evaluate("""
                    el => {
                        let label = el.nextElementSibling || el.previousElementSibling;
                        if (label) return label.innerText.trim().toLowerCase();
                        return '';
                    }
                """)
                
                # Check for preferred locations
                preferred_cities = ["hyderabad", "bangalore", "bengaluru", "chennai", "mysore", "bhubaneswar", "any", "relocate"]
                is_preferred_city = any(city in label_text or city in value for city in preferred_cities)
                
                if answer == "PreferredCity":
                    if is_preferred_city:
                        field.click()
                        log_message(f"    Selected Preferred Location: '{label_text or value}'")
                    continue
                
                if answer.lower() == "yes":
                    if (value and ("yes" in value or "true" in value or "1" == value)) or "yes" in label_text or is_preferred_city:
                        field.click()
                        if field_type == "radio":
                            handled_radios.add(field_name)
                        log_message(f"    Selected Radio/Checkbox Option: Yes/Preferred")
                elif answer.lower() == "no":
                    if (value and ("no" in value or "false" in value or "0" == value)) or "no" in label_text:
                        field.click()
                        if field_type == "radio":
                            handled_radios.add(field_name)
                        log_message(f"    Selected Radio/Checkbox Option: No")
                else:
                    field.click()
                    if field_type == "radio":
                        handled_radios.add(field_name)
                    log_message(f"    Clicked default Radio/Checkbox Option")
                    
            elif field.evaluate("el => el.tagName") == "SELECT":
                options = field.locator("option").all()
                selected = False
                for opt in options:
                    opt_text = opt.inner_text().lower()
                    opt_val = opt.get_attribute("value")
                    if answer.lower() in opt_text or (opt_val and answer.lower() in opt_val.lower()):
                        field.select_option(value=opt_val)
                        selected = True
                        log_message(f"    Selected Dropdown Option: '{opt.inner_text().strip()}'")
                        break
                if not selected and len(options) > 1:
                    field.select_option(index=1)
                    log_message(f"    Selected default Dropdown Option: '{options[1].inner_text().strip()}'")
            else:
                field.fill(answer)
                log_message(f"    Filled Text Value: '{answer}'")
                
        except Exception as e:
            log_message(f"    [!] Error filling field: {e}")
            
    submit_selectors = [
        "button:has-text('Submit')",
        "button:has-text('Save')",
        "button:has-text('Confirm')",
        "input[type='submit']",
        "xpath=//button[contains(text(), 'Submit') or contains(text(), 'Save') or contains(text(), 'Apply')]"
    ]
    
    for selector in submit_selectors:
        try:
            btn = job_page.locator(selector)
            if btn.first.is_visible(timeout=2000):
                btn.first.click()
                log_message("[+] Clicked Submit/Save button in Questionnaire.")
                job_page.wait_for_timeout(4000)
                return True
        except Exception:
            continue
            
    return False

def apply_jobs(query="SAP Security", limit=5, headless=True):
    log_message(f"[*] Initiating auto-apply for '{query}' (Limit: {limit} jobs)...")
    if not os.path.exists(STATE_FILE):
        log_message("[!] Error: Session state file not found. Please run with '--setup' first.")
        return 0
        
    applied_count = 0
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(
                storage_state=STATE_FILE,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()
            
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
                job_page = context.new_page()
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
                    external_url = None
                    for selector in company_site_selectors:
                        try:
                            locator = job_page.locator(selector)
                            if locator.first.is_visible(timeout=1000):
                                is_company_site = True
                                tag_name = locator.first.evaluate("el => el.tagName.toLowerCase()")
                                if tag_name == "a":
                                    external_url = locator.first.get_attribute("href")
                                break
                        except Exception:
                            continue
                            
                    if is_company_site:
                        log_message("[-] Job requires application on third-party company site. Emailing link and skipping.")
                        send_external_job_email(url, external_url)
                        job_page.close()
                        continue
                        
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
                        if "questionnaire" in new_content or "survey" in new_content or "answer" in new_content or job_page.locator("input[type='text'], textarea, select").count() > 0:
                            log_message("[*] Questionnaire detected. Attempting to answer questions...")
                            success = handle_questionnaire(job_page)
                            if success:
                                log_message("[+] Successfully filled and submitted questionnaire!")
                                applied_count += 1
                            else:
                                log_message("[!] Failed to complete questionnaire automatically.")
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
                    page.wait_for_timeout(1000)
                    
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
                context.storage_state(path=STATE_FILE)
            except Exception as se:
                log_message(f"[!] Failed to save storage state: {se}")
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

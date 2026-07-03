import os
from playwright.sync_api import sync_playwright

SESSION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "naukri_profile"))

def main():
    print(f"[*] SESSION_DIR: {SESSION_DIR}")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        try:
            url = "https://www.naukri.com/job-listings-sap-security-consultant-immediate-to-30-days-alike-thoughts-pune-chennai-mumbai-all-areas-6-to-11-years-300626008343"
            print(f"[*] Navigating to: {url}")
            page.goto(url)
            page.wait_for_timeout(8000)
            
            print(f"[+] Current Page URL: {page.url}")
            print(f"[*] Current Page Title: {page.title()}")
            
            # Let's search for elements containing "Apply"
            print("\n--- Searching for 'Apply' elements ---")
            elements = page.evaluate("""
                () => {
                    let results = [];
                    // Search all buttons, anchors, divs, spans
                    let allElems = document.querySelectorAll('button, a, span, div');
                    for (let el of allElems) {
                        let text = el.innerText ? el.innerText.trim() : '';
                        if (text === 'Apply' || text === 'Apply on company' || text === 'Easy Apply') {
                            results.push({
                                tagName: el.tagName,
                                id: el.id,
                                className: el.className,
                                text: text,
                                outerHTML: el.outerHTML.substring(0, 200),
                                isVisible: el.offsetWidth > 0 && el.offsetHeight > 0
                            });
                        }
                    }
                    return results;
                }
            """)
            
            for idx, el in enumerate(elements):
                print(f"[{idx+1}] Tag: {el['tagName']}, ID: {el['id']}, Class: {el['className']}")
                print(f"    Text: {el['text']}")
                print(f"    HTML: {el['outerHTML']}")
                print(f"    Visible: {el['isVisible']}")
                print("-" * 40)
                
            page.screenshot(path="dump_apply_screenshot.png")
            print("[+] Saved screenshot to: dump_apply_screenshot.png")
            
        except Exception as e:
            print(f"[!] Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()

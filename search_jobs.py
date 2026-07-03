#!/usr/bin/env python3
import json
import os
import sys
import urllib.parse
import urllib.request
import re
from html.parser import HTMLParser

class GoogleSearchParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.recording = False
        self.current_href = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs_dict = dict(attrs)
            href = attrs_dict.get('href', '')
            # Google search links usually start with /url?q=
            if href.startswith('/url?q='):
                clean_url = href.split('/url?q=')[1].split('&')[0]
                clean_url = urllib.parse.unquote(clean_url)
                if 'sap' in clean_url.lower() or 'job' in clean_url.lower():
                    self.current_href = clean_url
                    self.recording = True

    def handle_endtag(self, tag):
        if tag == 'a':
            self.recording = False
            self.current_href = None

    def handle_data(self, data):
        if self.recording and self.current_href:
            title = data.strip()
            if len(title) > 5 and self.current_href not in [x['url'] for x in self.links]:
                self.links.append({
                    "title": title,
                    "url": self.current_href
                })

def search_sap_jobs(location, experience_years=None):
    print(f"[*] Searching for SAP Security jobs in: {location}...")
    query = f"\"SAP Security\" jobs in {location}"
    if experience_years:
        query += f" \"{experience_years} years\""
    
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}&num=20"
    
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[!] Error fetching search results: {e}")
        return []

    parser = GoogleSearchParser()
    parser.feed(html)
    
    # Process and filter results
    jobs = []
    import datetime
    today = datetime.date.today().isoformat()
    
    for item in parser.links:
        title = item['title']
        item_url = item['url']
        
        # Clean title (google sometimes leaves trailing dots or garbage)
        title = re.sub(r'\s+', ' ', title).strip()
        if not title or len(title) < 10 or 'google' in item_url:
            continue
            
        # Deduce company from URL or title
        company = "Unknown Company"
        domain = urllib.parse.urlparse(item_url).netloc
        if 'linkedin.com' in domain:
            company = "LinkedIn Job Posting"
        elif 'indeed.com' in domain:
            company = "Indeed Job Posting"
        elif 'glassdoor.com' in domain:
            company = "Glassdoor Job Posting"
        elif 'accenture.com' in domain:
            company = "Accenture"
        elif 'deloitte.com' in domain:
            company = "Deloitte"
        elif 'ey.com' in domain:
            company = "EY"
        elif 'pwc.com' in domain:
            company = "PwC"
        elif 'sap.com' in domain:
            company = "SAP"
        else:
            # Try to parse company name from domain
            parts = domain.split('.')
            if len(parts) >= 2:
                company = parts[-2].capitalize()
        
        # Determine job details
        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "experience_years": int(experience_years) if experience_years else 5,
            "url": item_url,
            "posted_date": today,
            "type": "Full-time",
            "skills": ["SAP Security", "GRC", "Authorization"]
        })
        
    return jobs

def update_database(new_jobs):
    db_path = os.path.join(os.path.dirname(__file__), 'jobs_database.json')
    if not os.path.exists(db_path):
        existing_jobs = []
    else:
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                existing_jobs = json.load(f)
        except Exception:
            existing_jobs = []
            
    # Simple deduplication based on URL
    existing_urls = {job['url'] for job in existing_jobs}
    added_count = 0
    for job in new_jobs:
        if job['url'] not in existing_urls:
            existing_jobs.insert(0, job)
            existing_urls.add(job['url'])
            added_count += 1
            
    if added_count > 0:
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(existing_jobs, f, indent=2)
        
        # Write to jobs_data.js as well
        js_path = os.path.join(os.path.dirname(__file__), 'jobs_data.js')
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write("const JOBS_DATABASE = ")
            json.dump(existing_jobs, f, indent=2)
            f.write(";\n")
            
        print(f"[+] Successfully added {added_count} new jobs to database files!")
    else:
        print("[*] No new unique jobs found to add to database.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python search_jobs.py <Location> [Experience Years]")
        print("Example: python search_jobs.py India 5")
        sys.exit(1)
        
    location = sys.argv[1]
    experience_years = sys.argv[2] if len(sys.argv) > 2 else None
    
    new_jobs = search_sap_jobs(location, experience_years)
    
    if new_jobs:
        print(f"\nFound {len(new_jobs)} jobs:")
        for idx, job in enumerate(new_jobs, 1):
            print(f"{idx}. {job['title']} at {job['company']} ({job['location']})")
            print(f"   Apply: {job['url']}\n")
        
        # Ask to save
        update_database(new_jobs)
    else:
        print("[*] No jobs found or search limits reached.")

if __name__ == '__main__':
    main()

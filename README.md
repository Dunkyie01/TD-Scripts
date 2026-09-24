
WARNING: Legal & Ethical Usage
- This script scrapes ONLY from authorized educational sources
- Always respect robots.txt and website Terms of Service
- Do not use scraped data for commercial purposes
- Ensure compliance with your jurisdiction's laws
- This is for educational/personal use only

WARNING: Rate Limiting
- The script includes delays between requests (time.sleep)
- Do not remove these delays - they prevent server overload
- Aggressive scraping may result in IP bans

TIPS:
1. Always verify robots.txt before scraping (this script does it automatically)
2. Use API endpoints when available (StackOverflow uses official API)
3. Add User-Agent headers for transparency
4. Monitor your output to catch errors early
5. Save data incrementally to prevent loss on failure
6. Keep logs of what you scraped and when
7. Test on small datasets first before full runs

"""
DATA SOURCES:
All sources are authorized for educational scraping:

1. OWASP - https://owasp.org/www-community/attacks/SQL_Injection
   Purpose: Security education, explicitly allows scraping
   
2. StackOverflow API - https://api.stackexchange.com/2.3/search/advanced
   Purpose: Official API, no ToS violation
   
3. PyPI - https://pypi.org/project/
   Purpose: Official Python package index
   In current version (v0.1) only outputs URL's cannot be used unless reinputed

"""
OUTPUT:
1. The Output file should always be in plain text for conversion, any other data format as of v0.1 will be processed as plain text - this can yield some STRANGE results.
   
"""

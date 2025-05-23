from playwright.sync_api import sync_playwright
import pandas as pd
import time
import logging
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ReraPlaywrightScraper:
    def __init__(self):
        self.url = "https://rera.odisha.gov.in/projects/project-list"
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def setup(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,  # Set to True for production
                slow_mo=50  # Add small delays between actions
            )
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            self.page = self.context.new_page()
            self.page.set_default_timeout(30000)  # 30 seconds timeout
            logger.info("Browser setup completed")
            return True
        except Exception as e:
            logger.error(f"Error setting up browser: {str(e)}")
            return False

    def cleanup(self):
        """Clean up Playwright resources"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    def wait_and_click(self, selector: str, timeout: int = 30000) -> bool:
        """Wait for an element and click it"""
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            self.page.click(selector)
            return True
        except Exception as e:
            logger.error(f"Error clicking element {selector}: {str(e)}")
            return False

    def extract_text(self, selector: str, timeout: int = 5000) -> str:
        """Extract text from an element"""
        try:
            element = self.page.wait_for_selector(selector, timeout=timeout)
            if element:
                return element.text_content().strip()
        except Exception:
            pass
        return "N/A"

    def get_project_details(self) -> Optional[Dict[str, str]]:
        """Extract details from the current project page"""
        try:
            # Wait for page load
            self.page.wait_for_load_state('networkidle')
            time.sleep(2)

            # Extract main details
            project_data = {
                'RERA Regd. No.': 'N/A',
                'Project Name': 'N/A',
                'Promoter Name': 'N/A',
                'Address of the Promoter': 'N/A',
                'GST No.': 'N/A'
            }

            # Try different selectors for each field
            selectors = {
                'RERA Regd. No.': [
                    'text="RERA Regd. No." >> xpath=following-sibling::*',
                    'td:has-text("RERA Regd. No.") + td',
                    'div:has-text("RERA Regd. No.") + div'
                ],
                'Project Name': [
                    'text="Project Name" >> xpath=following-sibling::*',
                    'td:has-text("Project Name") + td',
                    'div:has-text("Project Name") + div'
                ]
            }

            # Extract main tab details
            for field, selector_list in selectors.items():
                for selector in selector_list:
                    try:
                        value = self.extract_text(selector)
                        if value != "N/A":
                            project_data[field] = value
                            break
                    except Exception:
                        continue

            # Click Promoter Details tab
            promoter_tab_selectors = [
                'a:has-text("Promoter Details")',
                'text=Promoter Details'
            ]

            for selector in promoter_tab_selectors:
                try:
                    if self.wait_and_click(selector):
                        time.sleep(2)  # Wait for content to load
                        
                        # Extract promoter details
                        promoter_selectors = {
                            'Promoter Name': [
                                'td:has-text("Company Name") + td',
                                'text="Company Name" >> xpath=following-sibling::*'
                            ],
                            'Address of the Promoter': [
                                'td:has-text("Registered Office Address") + td',
                                'text="Registered Office Address" >> xpath=following-sibling::*'
                            ],
                            'GST No.': [
                                'td:has-text("GST No.") + td',
                                'text="GST No." >> xpath=following-sibling::*'
                            ]
                        }

                        for field, selector_list in promoter_selectors.items():
                            for selector in selector_list:
                                try:
                                    value = self.extract_text(selector)
                                    if value != "N/A":
                                        project_data[field] = value
                                        break
                                except Exception:
                                    continue
                        break
                except Exception:
                    continue

            return project_data

        except Exception as e:
            logger.error(f"Error extracting project details: {str(e)}")
            return None

    def scrape_projects(self, num_projects: int = 6) -> bool:
        """Main scraping function"""
        try:
            if not self.setup():
                return False

            print("\n=== Starting the scraping process ===")
            
            # Navigate to the main page
            print("\nOpening the RERA website...")
            self.page.goto(self.url)
            self.page.wait_for_load_state('networkidle')
            time.sleep(3)
            print("✓ Website loaded successfully")

            all_projects = []
            projects_scraped = 0

            # Wait for the project list to be visible
            print("\nWaiting for project list to load...")
            self.page.wait_for_selector('a:has-text("View Details")', timeout=10000)
            print("✓ Project list loaded")
            
            # Get all View Details buttons on current page
            buttons = self.page.query_selector_all('a:has-text("View Details")')
            if not buttons:
                logger.error("No View Details buttons found")
                print("❌ No projects found on the page")
                return False

            print(f"\nFound {len(buttons)} projects on the page")
            print(f"Will scrape the first {num_projects} projects\n")

            # Process only the first num_projects buttons
            for i in range(min(len(buttons), num_projects)):
                try:
                    print(f"\n--- Processing Project #{i+1} ---")
                    
                    # Re-query the buttons to avoid stale references
                    buttons = self.page.query_selector_all('a:has-text("View Details")')
                    if not buttons or i >= len(buttons):
                        print("❌ Could not find project buttons")
                        break
                        
                    # Click the i-th button
                    print(f"Opening details for Project #{i+1}...")
                    buttons[i].click()
                    self.page.wait_for_load_state('networkidle')
                    time.sleep(2)
                    print("✓ Project details page opened")

                    # Extract project details
                    print("Scraping project details...")
                    project_data = self.get_project_details()
                    if project_data:
                        all_projects.append(project_data)
                        projects_scraped += 1
                        print(f"✓ Successfully scraped Project #{i+1}")
                        print(f"  RERA No: {project_data.get('RERA Regd. No.', 'N/A')}")
                        print(f"  Project Name: {project_data.get('Project Name', 'N/A')}")
                        print(f"  Promoter: {project_data.get('Promoter Name', 'N/A')}")

                        # Save progress
                        print(f"Saving Project #{i+1} data to CSV...")
                        df = pd.DataFrame(all_projects)
                        df.to_csv('rera_projects.csv', index=False)
                        print("✓ Data saved successfully")

                    # Go back to the list page
                    print("Returning to project list...")
                    self.page.go_back()
                    self.page.wait_for_load_state('networkidle')
                    time.sleep(2)
                    print("✓ Back on project list page")

                except Exception as e:
                    print(f"\n❌ Error processing Project #{i+1}: {str(e)}")
                    # Try to recover by going back to the list page
                    try:
                        print("Attempting to recover...")
                        self.page.go_back()
                        self.page.wait_for_load_state('networkidle')
                        time.sleep(2)
                        print("✓ Successfully recovered")
                    except:
                        print("❌ Recovery failed, reloading page...")
                        self.page.reload()
                        time.sleep(2)
                    continue

            print("\n=== Scraping process completed ===")
            print(f"Total projects scraped: {projects_scraped}")
            print("All data has been saved to rera_projects.csv")
            return True

        except Exception as e:
            print(f"\n❌ Fatal error in scraping process: {str(e)}")
            return False

        finally:
            print("\nCleaning up and closing browser...")
            self.cleanup()
            print("✓ Cleanup completed")

if __name__ == "__main__":
    scraper = ReraPlaywrightScraper()
    scraper.scrape_projects() 
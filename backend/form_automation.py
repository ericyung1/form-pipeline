"""
Playwright form automation for Army recruitment form.
Fills out the form with student data.
"""
import asyncio
from typing import Dict, Optional
from playwright.async_api import async_playwright, Page, Browser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Form selectors (discovered via inspection - same for all URLs)
SELECTORS = {
    'email': 'input[id*="email" i]',
    'first_name': 'input[id*="first" i]',
    'last_name': 'input[id*="last" i]',
    'phone': 'input[id*="phone" i]',
    'dob': 'input[id*="dob" i]',
    'zip_code': 'input[id*="zip" i]',
    'consent_checkbox_1': '#checkbox-3863ad55eb-1-input',
    'consent_checkbox_2': '#checkbox-3863ad55eb-2-input',
    'submit_button': 'button.form-submit'
}


class FormAutomation:
    """Handles automated form filling using Playwright."""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def start(self):
        """Initialize Playwright and browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        logger.info("Browser launched successfully")
    
    async def stop(self):
        """Close browser and Playwright."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")
    
    async def fill_form(
        self,
        url: str,
        student_data: Dict[str, str],
        submit: bool = False,
        max_retries: int = 3
    ) -> Dict[str, any]:
        """
        Fill out the form with student data.
        
        Args:
            url: Target form URL
            student_data: Dictionary with student information
            submit: Whether to actually submit the form (False for testing)
            max_retries: Number of retries on failure
        
        Returns:
            Dictionary with status and message
        """
        context = None
        for attempt in range(max_retries):
            try:
                if context:
                    await context.close()
                context = await self.browser.new_context()
                page = await context.new_page()
                
                # Navigate to form
                logger.info(f"Navigating to: {url}")
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Fill email
                logger.info(f"Filling email: {student_data['Email Address']}")
                await page.fill(SELECTORS['email'], student_data['Email Address'])
                
                # Fill first name
                logger.info(f"Filling first name: {student_data['First Name']}")
                await page.fill(SELECTORS['first_name'], student_data['First Name'])
                
                # Fill last name
                logger.info(f"Filling last name: {student_data['Last Name']}")
                await page.fill(SELECTORS['last_name'], student_data['Last Name'])
                
                # Fill phone
                logger.info(f"Filling phone: {student_data['Phone']}")
                await page.fill(SELECTORS['phone'], student_data['Phone'])
                
                # Fill date of birth
                logger.info(f"Filling DOB: {student_data['Date of Birth']}")
                await page.fill(SELECTORS['dob'], student_data['Date of Birth'])
                
                # Fill ZIP code
                logger.info(f"Filling ZIP: {student_data['Zip Code']}")
                await page.fill(SELECTORS['zip_code'], student_data['Zip Code'])
                
                # Wait a bit for form to process
                await asyncio.sleep(1)
                
                # Try to check consent checkboxes (optional - may need manual adjustment)
                logger.info("Attempting to check consent checkboxes...")
                try:
                    # Try finding checkboxes with more flexible selectors
                    checkboxes = await page.query_selector_all('input[type="checkbox"]')
                    logger.info(f"Found {len(checkboxes)} checkboxes on page")
                    
                    # Check the last two checkboxes (usually the consent ones)
                    if len(checkboxes) >= 2:
                        for i, checkbox in enumerate(checkboxes[-2:], 1):
                            try:
                                await checkbox.scroll_into_view_if_needed()
                                await checkbox.check(timeout=2000)
                                logger.info(f"✓ Checked consent checkbox {i}")
                            except:
                                logger.warning(f"Could not check checkbox {i}")
                    else:
                        logger.warning(f"Not enough checkboxes found (need 2, found {len(checkboxes)})")
                except Exception as e:
                    logger.warning(f"Checkbox checking failed: {str(e)} - continuing anyway")
                
                # Optional: Submit the form
                if submit:
                    logger.info("⚠️  SUBMITTING FORM!")
                    await page.click(SELECTORS['submit_button'])
                    await page.wait_for_load_state("networkidle", timeout=10000)
                    logger.info("✓ Form submitted successfully")
                else:
                    logger.info("✓ Form filled (NOT submitted - testing mode)")
                
                # Success! Close context and return
                result = {
                    'success': True,
                    'message': 'Form submitted' if submit else 'Form filled successfully (not submitted)',
                    'student': f"{student_data['First Name']} {student_data['Last Name']}"
                }
                
                try:
                    await context.close()
                except:
                    pass
                
                return result
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying... ({attempt + 2}/{max_retries})")
                    await asyncio.sleep(2)  # Wait before retry
                else:
                    return {
                        'success': False,
                        'message': f'Failed after {max_retries} attempts: {str(e)}',
                        'student': f"{student_data.get('First Name', 'Unknown')} {student_data.get('Last Name', 'Unknown')}"
                    }
            
            finally:
                if context:
                    try:
                        await context.close()
                    except:
                        pass
        
        return {
            'success': False,
            'message': 'Unknown error',
            'student': 'Unknown'
        }


# Test function
async def test_automation():
    """Test the automation with sample data."""
    test_data = {
        'Email Address': 'test@example.com',
        'First Name': 'John',
        'Last Name': 'Doe',
        'Phone': '5555551234',
        'Date of Birth': '01/15/1995',
        'Zip Code': '12345'
    }
    
    automation = FormAutomation()
    
    try:
        await automation.start()
        
        # Test WITHOUT submitting
        result = await automation.fill_form(
            url="https://www.goarmy.com/info?iom=CKXG-XX_LAP_Exhibit_2897052_C04_NA_ROTC",
            student_data=test_data,
            submit=False  # DO NOT SUBMIT during testing
        )
        
        print("\n" + "="*60)
        print("TEST RESULT:")
        print("="*60)
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        print(f"Student: {result['student']}")
        print("="*60 + "\n")
        
    finally:
        await automation.stop()


if __name__ == "__main__":
    print("\n🚀 Testing Form Automation (WITHOUT SUBMITTING)\n")
    asyncio.run(test_automation())


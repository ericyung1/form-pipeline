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
        self.context = None  # Reuse same context across students
        self.page = None
    
    async def start(self):
        """Initialize Playwright and browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        # Create a single context and page to reuse across all students
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        logger.info("Browser launched successfully")
    
    async def stop(self):
        """Close browser and Playwright."""
        if self.page:
            try:
                await self.page.close()
            except:
                pass
            self.page = None
        if self.context:
            try:
                await self.context.close()
            except:
                pass
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
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
        for attempt in range(max_retries):
            try:
                # Check if browser is still connected
                if not self.browser or not self.browser.is_connected():
                    raise Exception("Browser is not connected")

                # Check if page exists (should have been created in start())
                if not self.page:
                    raise Exception("Page not initialized")
                
                # Navigate to form (reusing the same page for all students)
                logger.info(f"Navigating to: {url}")
                await self.page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Fill email
                logger.info(f"Filling email: {student_data['Email Address']}")
                await self.page.fill(SELECTORS['email'], student_data['Email Address'])
                
                # Fill first name
                logger.info(f"Filling first name: {student_data['First Name']}")
                await self.page.fill(SELECTORS['first_name'], student_data['First Name'])
                
                # Fill last name
                logger.info(f"Filling last name: {student_data['Last Name']}")
                await self.page.fill(SELECTORS['last_name'], student_data['Last Name'])
                
                # Fill phone
                logger.info(f"Filling phone: {student_data['Phone']}")
                await self.page.fill(SELECTORS['phone'], student_data['Phone'])
                
                # Fill date of birth
                logger.info(f"Filling DOB: {student_data['Date of Birth']}")
                await self.page.fill(SELECTORS['dob'], student_data['Date of Birth'])
                
                # Fill ZIP code
                logger.info(f"Filling ZIP: {student_data['Zip Code']}")
                await self.page.fill(SELECTORS['zip_code'], student_data['Zip Code'])
                
                # Check consent checkboxes - DIRECTLY using known selectors (no searching!)
                logger.info("Checking consent checkboxes...")
                try:
                    # Use JavaScript to directly click the exact checkboxes we need
                    checkbox_result = await self.page.evaluate(f'''() => {{
                        const checkbox1 = document.querySelector('{SELECTORS['consent_checkbox_1']}');
                        const checkbox2 = document.querySelector('{SELECTORS['consent_checkbox_2']}');
                        let results = [];
                        
                        if (checkbox1) {{
                            if (!checkbox1.checked) {{
                                checkbox1.click();
                            }}
                            results.push({{id: 1, checked: checkbox1.checked}});
                        }}
                        
                        if (checkbox2) {{
                            if (!checkbox2.checked) {{
                                checkbox2.click();
                            }}
                            results.push({{id: 2, checked: checkbox2.checked}});
                        }}
                        
                        return results;
                    }}''')
                    
                    for result in checkbox_result:
                        logger.info(f"✓ Consent checkbox {result['id']} checked: {result['checked']}")
                    
                except Exception as e:
                    logger.warning(f"Checkbox checking failed: {str(e)} - continuing anyway")
                
                # Optional: Submit the form
                if submit:
                    logger.info("⚠️  SUBMITTING FORM!")
                    await self.page.click(SELECTORS['submit_button'])
                    await self.page.wait_for_load_state("networkidle", timeout=10000)
                    logger.info("✓ Form submitted successfully")
                else:
                    logger.info("✓ Form filled (NOT submitted - testing mode)")
                
                # Success! Return result (page will be reused for next student)
                return {
                    'success': True,
                    'message': 'Form submitted' if submit else 'Form filled successfully (not submitted)',
                    'student': f"{student_data['First Name']} {student_data['Last Name']}"
                }
                
            except Exception as e:
                error_msg = str(e) if str(e) else "Unknown error"
                logger.error(f"Attempt {attempt + 1} failed: {error_msg}")
                
                # If it's a browser connection issue, try to recreate page
                if "browser" in error_msg.lower() or "target closed" in error_msg.lower():
                    logger.warning("Browser/page issue detected, recreating page...")
                    try:
                        if self.page:
                            try:
                                await self.page.close()
                            except:
                                pass
                        if self.context:
                            try:
                                await self.context.close()
                            except:
                                pass
                        # Recreate context and page
                        self.context = await self.browser.new_context()
                        self.page = await self.context.new_page()
                        logger.info("Page recreated successfully")
                    except Exception as recreate_error:
                        logger.error(f"Failed to recreate page: {recreate_error}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying... ({attempt + 2}/{max_retries})")
                    await asyncio.sleep(1)  # Short delay before retry
                else:
                    return {
                        'success': False,
                        'message': f'Failed after {max_retries} attempts: {error_msg}',
                        'student': f"{student_data.get('First Name', 'Unknown')} {student_data.get('Last Name', 'Unknown')}"
                    }
        
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


"""
Form inspection script to identify selectors for the Army form.
This is a ONE-TIME script to find all the required field selectors.
"""
import asyncio
from playwright.async_api import async_playwright

TARGET_URL = "https://www.goarmy.com/info?iom=CKXG-XX_LAP_Exhibit_2897052_C04_NA_ROTC"

async def inspect_form():
    """Inspect the form and identify all required field selectors."""
    print(f"\n{'='*60}")
    print("INSPECTING FORM STRUCTURE")
    print(f"{'='*60}\n")
    print(f"Target URL: {TARGET_URL}\n")
    
    async with async_playwright() as p:
        # Launch browser in headless mode
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to the form
            print(f"Navigating to: {TARGET_URL}")
            await page.goto(TARGET_URL, wait_until="networkidle", timeout=30000)
            
            print("\n" + "="*60)
            print("SEARCHING FOR FORM FIELDS...")
            print("="*60 + "\n")
            
            # Common selector patterns to try
            field_patterns = {
                "Email": [
                    'input[type="email"]',
                    'input[name*="email" i]',
                    'input[id*="email" i]',
                    '#email',
                ],
                "First Name": [
                    'input[name*="first" i]',
                    'input[name*="fname" i]',
                    'input[id*="first" i]',
                    '#firstName',
                    '#first-name',
                ],
                "Last Name": [
                    'input[name*="last" i]',
                    'input[name*="lname" i]',
                    'input[id*="last" i]',
                    '#lastName',
                    '#last-name',
                ],
                "Phone": [
                    'input[type="tel"]',
                    'input[name*="phone" i]',
                    'input[id*="phone" i]',
                    '#phone',
                ],
                "Date of Birth": [
                    'input[type="date"]',
                    'input[name*="birth" i]',
                    'input[name*="dob" i]',
                    'input[id*="birth" i]',
                    'input[id*="date" i]',
                    'input[placeholder*="date" i]',
                    'input[placeholder*="birth" i]',
                    'input[placeholder*="mm" i]',
                    '#dateOfBirth',
                    '#dob',
                ],
                "ZIP Code": [
                    'input[name*="zip" i]',
                    'input[name*="postal" i]',
                    'input[id*="zip" i]',
                    '#zipCode',
                    '#zip',
                ],
            }
            
            found_selectors = {}
            
            # Find each field
            for field_name, patterns in field_patterns.items():
                print(f"Looking for: {field_name}...")
                for pattern in patterns:
                    element = await page.query_selector(pattern)
                    if element:
                        # Get attributes to identify it better
                        attrs = await element.evaluate('''el => ({
                            id: el.id,
                            name: el.name,
                            type: el.type,
                            placeholder: el.placeholder
                        })''')
                        found_selectors[field_name] = {
                            'selector': pattern,
                            'attributes': attrs
                        }
                        print(f"  ✓ Found: {pattern}")
                        print(f"    Attributes: {attrs}")
                        break
                
                if field_name not in found_selectors:
                    print(f"  ✗ NOT FOUND")
            
            # Look for checkboxes
            print("\nLooking for consent checkboxes...")
            checkboxes = await page.query_selector_all('input[type="checkbox"]')
            print(f"  Found {len(checkboxes)} checkbox(es)")
            
            for i, checkbox in enumerate(checkboxes, 1):
                attrs = await checkbox.evaluate('''el => ({
                    id: el.id,
                    name: el.name,
                    value: el.value,
                    ariaLabel: el.getAttribute('aria-label')
                })''')
                print(f"  Checkbox {i}: {attrs}")
            
            # Look for submit button
            print("\nLooking for submit button...")
            
            # Search for all buttons
            all_buttons = await page.query_selector_all('button, input[type="submit"], a[role="button"]')
            print(f"  Found {len(all_buttons)} button(s) total")
            
            submit_button = None
            for i, button in enumerate(all_buttons, 1):
                try:
                    text = await button.inner_text()
                    text = text.strip().lower()
                    
                    if 'get more information' in text or 'submit' in text.lower():
                        attrs = await button.evaluate('''el => ({
                            id: el.id,
                            type: el.type,
                            className: el.className,
                            tagName: el.tagName
                        })''')
                        full_text = await button.inner_text()
                        print(f"  Button {i}: '{full_text.strip()}'")
                        print(f"    Attributes: {attrs}")
                        
                        if 'get more information' in text:
                            submit_button = attrs
                            print(f"    ✓ THIS IS THE SUBMIT BUTTON!")
                except:
                    pass
            
            print("\n" + "="*60)
            print("INSPECTION COMPLETE")
            print("="*60 + "\n")
            print("Found selectors:")
            for field, data in found_selectors.items():
                print(f"  {field}: {data['selector']}")
            
        except Exception as e:
            print(f"\n❌ Error during inspection: {e}")
        
        finally:
            await browser.close()
            print("\nBrowser closed.")


if __name__ == "__main__":
    asyncio.run(inspect_form())


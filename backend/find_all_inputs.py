"""
Find ALL input fields on the page to locate Date of Birth
"""
import asyncio
from playwright.async_api import async_playwright

TARGET_URL = "https://www.goarmy.com/info?iom=CKXG-XX_LAP_Exhibit_2897052_C04_NA_ROTC"

async def find_all_inputs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print(f"Navigating to: {TARGET_URL}\n")
            await page.goto(TARGET_URL, wait_until="networkidle", timeout=30000)
            
            # Find ALL input elements
            all_inputs = await page.query_selector_all('input')
            print(f"Found {len(all_inputs)} input elements total\n")
            print("="*80)
            
            for i, input_elem in enumerate(all_inputs, 1):
                attrs = await input_elem.evaluate('''el => ({
                    id: el.id,
                    name: el.name,
                    type: el.type,
                    placeholder: el.placeholder,
                    value: el.value,
                    className: el.className,
                    ariaLabel: el.getAttribute('aria-label')
                })''')
                
                # Get the label text if there is one
                label_text = await input_elem.evaluate('''el => {
                    const label = el.closest('label') || document.querySelector(`label[for="${el.id}"]`);
                    return label ? label.textContent.trim() : '';
                }''')
                
                print(f"Input {i}:")
                print(f"  ID: {attrs['id']}")
                print(f"  Type: {attrs['type']}")
                print(f"  Placeholder: {attrs['placeholder']}")
                print(f"  Name: {attrs['name']}")
                print(f"  Class: {attrs['className']}")
                print(f"  Label: {label_text}")
                if attrs['ariaLabel']:
                    print(f"  Aria-Label: {attrs['ariaLabel']}")
                print()
                
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(find_all_inputs())


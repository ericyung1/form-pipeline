# Form Selectors Documentation

## Target Form
https://www.goarmy.com/info?iom=CKXG-XX_LAP_Exhibit_2897052_C04_NA_ROTC

**Note**: All URLs with this form share the same HTML structure. These selectors work for ANY URL with the same form.

## Discovered Selectors (One-Time Inspection)

### Required Fields
```javascript
{
  'email': 'input[id*="email" i]',           // → #ebrc-3863ad55eb__ebrc-emailAddress
  'first_name': 'input[id*="first" i]',      // → #ebrc-3863ad55eb__ebrc-firstName
  'last_name': 'input[id*="last" i]',        // → #ebrc-3863ad55eb__ebrc-lastName
  'phone': 'input[id*="phone" i]',           // → #ebrc-3863ad55eb__ebrc-phoneNumber
  'dob': 'input[id*="dob" i]',               // → #ebrc-3863ad55eb__ebrc-dob
  'zip_code': 'input[id*="zip" i]',          // → #ebrc-3863ad55eb__ebrc-addressZip
}
```

### Consent Checkboxes
```javascript
{
  'consent_checkbox_1': '#checkbox-3863ad55eb-1-input',
  'consent_checkbox_2': '#checkbox-3863ad55eb-2-input'
}
```

**Note**: Checkboxes may require manual adjustment. Current implementation tries all checkboxes on page.

### Submit Button
```javascript
{
  'submit_button': 'button.form-submit'  // Text: "GET MORE INFORMATION"
}
```

## Tested ✓

### Working Fields:
- ✅ Email Address
- ✅ First Name
- ✅ Last Name
- ✅ Phone Number (10 digits)
- ✅ Date of Birth (MM/DD/YYYY format)
- ✅ ZIP Code (5 digits)

### Checkboxes:
- ✅ Consent checkboxes working (using JavaScript click)

### Submit Button:
- ❌ NOT tested (intentionally - manual testing required)

## Data Format

Input data should match cleaned spreadsheet format:
```python
{
    'Email Address': 'test@example.com',
    'First Name': 'John',
    'Last Name': 'Doe',
    'Phone': '5555551234',           # 10 digits, no formatting
    'Date of Birth': '01/15/1995',   # MM/DD/YYYY
    'Zip Code': '12345'              # 5 digits
}
```

## Usage

```python
from form_automation import FormAutomation

automation = FormAutomation()
await automation.start()

result = await automation.fill_form(
    url="https://www.goarmy.com/info?iom=...",
    student_data=student_data,
    submit=False  # Set to True when ready to actually submit
)

await automation.stop()
```

## Testing Instructions

1. Test form filling WITHOUT submission:
```bash
python form_automation.py
```

2. Verify all fields are filled correctly

3. When ready, manually test submission OR set `submit=True` in code

## Retry Logic

- Automatic retry on network errors: 3 attempts
- 2-second delay between retries
- Continues if checkboxes fail (non-critical)


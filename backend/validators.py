"""
Data validation and cleaning functions for student spreadsheet processing.
"""
import re
from datetime import datetime
from typing import Tuple, Optional


# Required headers in exact order
REQUIRED_HEADERS = [
    "Email Address",
    "First Name", 
    "Last Name",
    "Phone",
    "Date of Birth",
    "Zip Code"
]


def validate_headers(headers: list) -> Tuple[bool, Optional[str]]:
    """
    Validate that spreadsheet headers match required format exactly.
    
    Args:
        headers: List of header strings from spreadsheet
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(headers) < len(REQUIRED_HEADERS):
        return False, f"Missing headers. Expected: {', '.join(REQUIRED_HEADERS)}"
    
    # Check first 6 headers match exactly (ignore extra columns)
    for i, required_header in enumerate(REQUIRED_HEADERS):
        if i >= len(headers) or headers[i] != required_header:
            actual = headers[i] if i < len(headers) else "missing"
            return False, f"Header mismatch at position {i+1}. Expected '{required_header}', got '{actual}'"
    
    return True, None


def clean_phone(phone: str) -> Tuple[str, str, str]:
    """
    Extract digits from phone number and validate.
    
    Args:
        phone: Phone number string (may include formatting)
    
    Returns:
        Tuple of (cleaned_value, status, note)
        - cleaned_value: 10-digit string or original value if invalid
        - status: 'ok', 'fixed', or 'skipped'
        - note: Description of action taken
    """
    if not phone or not str(phone).strip():
        return "", "skipped", "Phone number is empty"
    
    original = str(phone).strip()
    
    # Extract only digits
    digits = re.sub(r'\D', '', original)
    
    if len(digits) == 10:
        if digits == original:
            return digits, "ok", ""
        else:
            return digits, "fixed", f"Phone formatted: {original} → {digits}"
    else:
        return original, "skipped", f"Phone must be 10 digits, got {len(digits)}"


def clean_zip_code(zip_code: str) -> Tuple[str, str, str]:
    """
    Extract first 5 digits from ZIP code.
    
    Args:
        zip_code: ZIP code string (may be 5 or 9 digit format)
    
    Returns:
        Tuple of (cleaned_value, status, note)
    """
    if not zip_code or not str(zip_code).strip():
        return "", "skipped", "ZIP code is empty"
    
    original = str(zip_code).strip()
    
    # Extract only digits
    digits = re.sub(r'\D', '', original)
    
    if len(digits) >= 5:
        zip_5 = digits[:5]
        if zip_5 == original:
            return zip_5, "ok", ""
        else:
            return zip_5, "fixed", f"ZIP code formatted: {original} → {zip_5}"
    else:
        return original, "skipped", f"ZIP code must be 5 digits, got {len(digits)}"


def clean_name(name: str, field_name: str = "Name") -> Tuple[str, str, str]:
    """
    Validate name contains only allowed characters.
    
    Args:
        name: Name string
        field_name: Field name for error messages
    
    Returns:
        Tuple of (cleaned_value, status, note)
    """
    if not name or not str(name).strip():
        return "", "skipped", f"{field_name} is empty"
    
    cleaned = str(name).strip()
    
    # Allow letters, spaces, hyphens, apostrophes
    # Including accented characters
    name_pattern = r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$"
    
    if re.match(name_pattern, cleaned):
        return cleaned, "ok", ""
    else:
        return cleaned, "skipped", f"{field_name} contains invalid characters"


def clean_email(email: str) -> Tuple[str, str, str]:
    """
    Validate email format.
    
    Args:
        email: Email address string
    
    Returns:
        Tuple of (cleaned_value, status, note)
    """
    if not email or not str(email).strip():
        return "", "skipped", "Email is empty"
    
    cleaned = str(email).strip().lower()
    
    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(email_pattern, cleaned):
        return cleaned, "ok", ""
    else:
        return cleaned, "skipped", "Invalid email format"


def clean_date_of_birth(dob: str) -> Tuple[str, str, str]:
    """
    Clean and validate date of birth.
    Pad to MM/DD/YYYY format and validate year range.
    
    Args:
        dob: Date of birth string
    
    Returns:
        Tuple of (cleaned_value, status, note)
    """
    if not dob or not str(dob).strip():
        return "", "skipped", "Date of birth is empty"
    
    original = str(dob).strip()
    
    try:
        # Try to parse various date formats
        date_obj = None
        for fmt in ['%m/%d/%Y', '%m/%d/%y', '%-m/%-d/%Y', '%-m/%-d/%y', '%m-%d-%Y', '%m-%d-%y']:
            try:
                date_obj = datetime.strptime(original, fmt)
                break
            except ValueError:
                continue
        
        # If none of the formats worked, try manual parsing
        if not date_obj:
            # Try splitting by / or -
            parts = re.split(r'[/-]', original)
            if len(parts) == 3:
                month, day, year = parts
                month = int(month)
                day = int(day)
                year = int(year)
                
                # Handle 2-digit years
                if year < 100:
                    if year <= 50:
                        year += 2000
                    else:
                        year += 1900
                
                date_obj = datetime(year, month, day)
            else:
                return original, "skipped", "Invalid date format"
        
        year = date_obj.year
        current_year = datetime.now().year
        
        # Check if year is in future or current year -> auto-correct to junior age
        if year >= current_year:
            corrected_year = current_year - 16
            date_obj = datetime(corrected_year, date_obj.month, date_obj.day)
            formatted = date_obj.strftime('%m/%d/%Y')
            return formatted, "fixed", f"DOB year corrected: {original} → {formatted} (future year adjusted to age 16)"
        
        # Check if year is too old
        if year < 1950:
            return original, "skipped", f"DOB year {year} is before 1950"
        
        if year > current_year + 1:
            return original, "skipped", f"DOB year {year} is too far in future"
        
        # Format to MM/DD/YYYY
        formatted = date_obj.strftime('%m/%d/%Y')
        
        if formatted == original:
            return formatted, "ok", ""
        else:
            return formatted, "fixed", f"DOB formatted: {original} → {formatted}"
    
    except (ValueError, TypeError) as e:
        return original, "skipped", f"Invalid date format: {str(e)}"


def detect_duplicate(row_data: dict, existing_rows: list) -> bool:
    """
    Check if a row is a duplicate based on email or name+DOB combination.
    
    Args:
        row_data: Dictionary with student data
        existing_rows: List of previously processed rows
    
    Returns:
        True if duplicate, False otherwise
    """
    email = row_data.get('Email Address', '').lower().strip()
    first_name = row_data.get('First Name', '').lower().strip()
    last_name = row_data.get('Last Name', '').lower().strip()
    dob = row_data.get('Date of Birth', '').strip()
    
    for existing in existing_rows:
        # Check email match
        if email and email == existing.get('Email Address', '').lower().strip():
            return True
        
        # Check name + DOB match
        existing_first = existing.get('First Name', '').lower().strip()
        existing_last = existing.get('Last Name', '').lower().strip()
        existing_dob = existing.get('Date of Birth', '').strip()
        
        if (first_name and last_name and dob and
            first_name == existing_first and
            last_name == existing_last and
            dob == existing_dob):
            return True
    
    return False


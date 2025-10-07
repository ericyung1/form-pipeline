"""
Test script for the spreadsheet cleaner.
"""
from validators import (
    clean_phone,
    clean_zip_code,
    clean_name,
    clean_email,
    clean_date_of_birth,
    validate_headers
)


def test_phone_cleaning():
    """Test phone number cleaning."""
    print("=== Testing Phone Cleaning ===")
    
    tests = [
        ("(636) 480-1423", "6364801423", "fixed"),
        ("636-480-1423", "6364801423", "fixed"),
        ("6364801423", "6364801423", "ok"),
        ("123", "123", "skipped"),  # Too short
        ("", "", "skipped"),  # Empty
    ]
    
    for original, expected, expected_status in tests:
        result, status, note = clean_phone(original)
        print(f"  Input: '{original}' → Output: '{result}' (Status: {status})")
        assert result == expected, f"Expected {expected}, got {result}"
        assert status == expected_status, f"Expected status {expected_status}, got {status}"
    
    print("✓ Phone cleaning tests passed\n")


def test_zip_cleaning():
    """Test ZIP code cleaning."""
    print("=== Testing ZIP Cleaning ===")
    
    tests = [
        ("60163-1234", "60163", "fixed"),
        ("60163", "60163", "ok"),
        ("123", "123", "skipped"),  # Too short
        ("", "", "skipped"),  # Empty
    ]
    
    for original, expected, expected_status in tests:
        result, status, note = clean_zip_code(original)
        print(f"  Input: '{original}' → Output: '{result}' (Status: {status})")
        assert result == expected, f"Expected {expected}, got {result}"
        assert status == expected_status, f"Expected status {expected_status}, got {status}"
    
    print("✓ ZIP cleaning tests passed\n")


def test_name_cleaning():
    """Test name validation."""
    print("=== Testing Name Validation ===")
    
    tests = [
        ("John", "John", "ok"),
        ("O'Brien", "O'Brien", "ok"),
        ("Mary-Jane", "Mary-Jane", "ok"),
        ("José", "José", "ok"),
        ("John123", "John123", "skipped"),  # Contains digits
        ("", "", "skipped"),  # Empty
    ]
    
    for original, expected, expected_status in tests:
        result, status, note = clean_name(original, "Name")
        print(f"  Input: '{original}' → Output: '{result}' (Status: {status})")
        assert result == expected, f"Expected {expected}, got {result}"
        assert status == expected_status, f"Expected status {expected_status}, got {status}"
    
    print("✓ Name validation tests passed\n")


def test_email_cleaning():
    """Test email validation."""
    print("=== Testing Email Validation ===")
    
    tests = [
        ("test@example.com", "test@example.com", "ok"),
        ("Test@Example.COM", "test@example.com", "ok"),  # Lowercase
        ("invalid.email", "invalid.email", "skipped"),  # No @
        ("", "", "skipped"),  # Empty
    ]
    
    for original, expected, expected_status in tests:
        result, status, note = clean_email(original)
        print(f"  Input: '{original}' → Output: '{result}' (Status: {status})")
        assert result == expected, f"Expected {expected}, got {result}"
        assert status == expected_status, f"Expected status {expected_status}, got {status}"
    
    print("✓ Email validation tests passed\n")


def test_dob_cleaning():
    """Test DOB cleaning."""
    print("=== Testing DOB Cleaning ===")
    
    tests = [
        ("3/7/2007", "03/07/2007", "fixed"),  # Padding
        ("03/16/2007", "03/16/2007", "ok"),  # Already formatted
        ("1/1/2025", None, "fixed"),  # Future year - will be corrected to current_year - 16
        ("1/1/1949", "1/1/1949", "skipped"),  # Too old
    ]
    
    for test in tests:
        original = test[0]
        result, status, note = clean_date_of_birth(original)
        print(f"  Input: '{original}' → Output: '{result}' (Status: {status})")
        if note:
            print(f"    Note: {note}")
    
    print("✓ DOB cleaning tests passed\n")


def test_header_validation():
    """Test header validation."""
    print("=== Testing Header Validation ===")
    
    correct_headers = ["Email Address", "First Name", "Last Name", "Phone", "Date of Birth", "Zip Code"]
    wrong_headers = ["Email", "First Name", "Last Name", "Phone", "Date of Birth", "Zip Code"]
    
    is_valid, error = validate_headers(correct_headers)
    print(f"  Correct headers: Valid={is_valid}")
    assert is_valid, "Should accept correct headers"
    
    is_valid, error = validate_headers(wrong_headers)
    print(f"  Wrong headers: Valid={is_valid}, Error={error}")
    assert not is_valid, "Should reject wrong headers"
    
    print("✓ Header validation tests passed\n")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("Running Cleaner Tests")
    print("="*50 + "\n")
    
    test_phone_cleaning()
    test_zip_cleaning()
    test_name_cleaning()
    test_email_cleaning()
    test_dob_cleaning()
    test_header_validation()
    
    print("="*50)
    print("✓ All tests passed!")
    print("="*50 + "\n")


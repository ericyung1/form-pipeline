"""
Create sample Excel file for testing the cleaner.
"""
from openpyxl import Workbook

# Create workbook
wb = Workbook()
ws = wb.active
ws.title = "Students"

# Add headers
headers = ["Email Address", "First Name", "Last Name", "Phone", "Date of Birth", "Zip Code"]
ws.append(headers)

# Add test data with various scenarios
test_data = [
    # Good data - should be OK
    ["bsavila03@gmail.com", "Brithany", "Avila", "7088828259", "3/16/2007", "60163"],
    
    # Phone with formatting - should be FIXED
    ["tordyeet@gmail.com", "Bennett", "Navarrete", "(708) 616-6634", "9/1/2007", "60104"],
    
    # ZIP with 9 digits - should be FIXED
    ["john.doe@example.com", "John", "Doe", "636-480-1423", "5/15/2006", "60163-1234"],
    
    # DOB needs padding - should be FIXED
    ["jane.smith@example.com", "Jane", "Smith", "3125551234", "3/7/2007", "60201"],
    
    # Future year DOB - should be FIXED (corrected to age 16)
    ["future@example.com", "Future", "Student", "7083334444", "1/1/2025", "60301"],
    
    # Invalid email - should be SKIPPED
    ["invalid.email", "Invalid", "Email", "7085556666", "6/20/2006", "60401"],
    
    # Invalid phone (too short) - should be SKIPPED
    ["short@example.com", "Short", "Phone", "123", "7/25/2006", "60501"],
    
    # Invalid name (contains digits) - should be SKIPPED
    ["digits@example.com", "John123", "Smith", "7085557777", "8/30/2006", "60601"],
    
    # Old DOB (before 1950) - should be SKIPPED
    ["old@example.com", "Too", "Old", "7085558888", "1/1/1949", "60701"],
    
    # Duplicate email - should be SKIPPED
    ["bsavila03@gmail.com", "Different", "Person", "7085559999", "10/10/2006", "60801"],
    
    # Name with apostrophe - should be OK
    ["obrien@example.com", "Michael", "O'Brien", "7085550000", "11/11/2006", "60901"],
    
    # Name with hyphen - should be OK
    ["maryjane@example.com", "Mary-Jane", "Wilson", "7085551111", "12/12/2006", "61001"],
]

# Add data rows
for row in test_data:
    ws.append(row)

# Save file
filename = "sample_students.xlsx"
wb.save(filename)
print(f"✓ Created sample Excel file: {filename}")
print(f"  Total rows: {len(test_data)}")
print(f"  Expected OK: 4")
print(f"  Expected FIXED: 4")
print(f"  Expected SKIPPED: 4 (invalid) + 1 (duplicate) = 5")


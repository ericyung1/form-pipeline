"""
Create sample Excel file with 30 students for testing.
"""
from openpyxl import Workbook
import random

# Create workbook
wb = Workbook()
ws = wb.active
ws.title = "Students"

# Add headers
headers = ["Email Address", "First Name", "Last Name", "Phone", "Date of Birth", "Zip Code"]
ws.append(headers)

# First names pool
first_names = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Barbara", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra"
]

# Last names pool
last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris",
    "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"
]

# Generate 30 students
test_data = []
for i in range(1, 31):
    first_name = first_names[i-1]
    last_name = last_names[i-1]
    
    # Vary the data quality
    if i % 10 == 0:  # Every 10th: formatted phone
        phone = f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"
    elif i % 7 == 0:  # Every 7th: phone with dashes
        phone = f"{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}"
    else:  # Most: clean 10 digits
        phone = f"{random.randint(200,999)}{random.randint(200,999)}{random.randint(1000,9999)}"
    
    # ZIP codes
    if i % 8 == 0:  # Every 8th: 9-digit ZIP
        zip_code = f"{random.randint(10000,99999)}-{random.randint(1000,9999)}"
    else:  # Most: 5-digit ZIP
        zip_code = f"{random.randint(10000,99999)}"
    
    # DOB - all valid ages (16-18 years old)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    year = random.randint(2006, 2008)
    
    # Some with padding needed, some without
    if i % 3 == 0:
        dob = f"{month}/{day}/{year}"  # Needs padding
    else:
        dob = f"{month:02d}/{day:02d}/{year}"  # Already padded
    
    # Email
    email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
    
    test_data.append([email, first_name, last_name, phone, dob, zip_code])

# Add data rows
for row in test_data:
    ws.append(row)

# Save file
filename = "sample_30_students.xlsx"
wb.save(filename)
print(f"✓ Created sample Excel file: {filename}")
print(f"  Total students: {len(test_data)}")
print(f"  All should be valid (OK or Fixed)")
print(f"\nThis file has:")
print(f"  - Mix of formatted and clean phone numbers")
print(f"  - Mix of 5-digit and 9-digit ZIP codes")
print(f"  - Mix of padded and unpadded dates")
print(f"  - All valid data (should result in 30 OK/Fixed)")


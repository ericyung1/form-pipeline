"""
Spreadsheet cleaning and processing logic.
"""
import io
from typing import List, Dict, Any, Tuple
import pandas as pd
from openpyxl import load_workbook, Workbook
from validators import (
    validate_headers,
    clean_phone,
    clean_zip_code,
    clean_name,
    clean_email,
    clean_date_of_birth,
    detect_duplicate,
    REQUIRED_HEADERS
)


class SpreadsheetCleaner:
    """Handles spreadsheet validation, cleaning, and processing."""
    
    def __init__(self):
        self.results = []
        self.summary = {
            "ok": 0,
            "fixed": 0,
            "skipped": 0,
            "total": 0
        }
    
    def process_spreadsheet(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process uploaded spreadsheet file.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
        
        Returns:
            Dictionary with processing results and summary
        """
        try:
            # Load Excel file
            df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
            
            # Validate headers
            headers = df.columns.tolist()
            is_valid, error_msg = validate_headers(headers)
            
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "results": [],
                    "summary": {}
                }
            
            # Process each row
            processed_rows = []
            valid_rows_for_duplicate_check = []
            
            for idx, row in df.iterrows():
                row_num = idx + 2  # Excel rows start at 1, header is row 1
                
                # Skip completely blank rows
                if row.isna().all():
                    continue
                
                # Extract data
                row_data = {
                    "Email Address": str(row.get("Email Address", "")).strip() if pd.notna(row.get("Email Address")) else "",
                    "First Name": str(row.get("First Name", "")).strip() if pd.notna(row.get("First Name")) else "",
                    "Last Name": str(row.get("Last Name", "")).strip() if pd.notna(row.get("Last Name")) else "",
                    "Phone": str(row.get("Phone", "")).strip() if pd.notna(row.get("Phone")) else "",
                    "Date of Birth": str(row.get("Date of Birth", "")).strip() if pd.notna(row.get("Date of Birth")) else "",
                    "Zip Code": str(row.get("Zip Code", "")).strip() if pd.notna(row.get("Zip Code")) else ""
                }
                
                # Clean and validate each field
                cleaned_row = self._clean_row(row_data, row_num, valid_rows_for_duplicate_check)
                processed_rows.append(cleaned_row)
                
                # Track for duplicate detection (only if not already skipped)
                if cleaned_row["status"] != "skipped":
                    valid_rows_for_duplicate_check.append(cleaned_row["data"])
            
            # Generate summary
            self._calculate_summary(processed_rows)
            
            # Generate cleaned Excel file (excluding skipped rows)
            cleaned_file = self._generate_cleaned_file(processed_rows)
            
            return {
                "success": True,
                "results": processed_rows,
                "summary": self.summary,
                "cleaned_file": cleaned_file
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing spreadsheet: {str(e)}",
                "results": [],
                "summary": {}
            }
    
    def _clean_row(self, row_data: Dict[str, str], row_num: int, 
                   existing_rows: List[Dict]) -> Dict[str, Any]:
        """
        Clean and validate a single row.
        
        Args:
            row_data: Raw row data
            row_num: Row number in spreadsheet
            existing_rows: Previously validated rows for duplicate detection
        
        Returns:
            Dictionary with cleaned data, status, and notes
        """
        cleaned_data = {}
        notes = []
        row_status = "ok"
        
        # Clean email
        email, status, note = clean_email(row_data["Email Address"])
        cleaned_data["Email Address"] = email
        if status == "skipped":
            row_status = "skipped"
            notes.append(note)
        elif note:
            notes.append(note)
        
        # Clean first name
        first_name, status, note = clean_name(row_data["First Name"], "First Name")
        cleaned_data["First Name"] = first_name
        if status == "skipped":
            row_status = "skipped"
            notes.append(note)
        elif note:
            notes.append(note)
        
        # Clean last name
        last_name, status, note = clean_name(row_data["Last Name"], "Last Name")
        cleaned_data["Last Name"] = last_name
        if status == "skipped":
            row_status = "skipped"
            notes.append(note)
        elif note:
            notes.append(note)
        
        # Clean phone
        phone, status, note = clean_phone(row_data["Phone"])
        cleaned_data["Phone"] = phone
        if status == "skipped":
            row_status = "skipped"
            notes.append(note)
        elif status == "fixed":
            if row_status != "skipped":
                row_status = "fixed"
            notes.append(note)
        
        # Clean date of birth
        dob, status, note = clean_date_of_birth(row_data["Date of Birth"])
        cleaned_data["Date of Birth"] = dob
        if status == "skipped":
            row_status = "skipped"
            notes.append(note)
        elif status == "fixed":
            if row_status != "skipped":
                row_status = "fixed"
            notes.append(note)
        
        # Clean ZIP code
        zip_code, status, note = clean_zip_code(row_data["Zip Code"])
        cleaned_data["Zip Code"] = zip_code
        if status == "skipped":
            row_status = "skipped"
            notes.append(note)
        elif status == "fixed":
            if row_status != "skipped":
                row_status = "fixed"
            notes.append(note)
        
        # Check for duplicates (only if not already skipped)
        if row_status != "skipped":
            if detect_duplicate(cleaned_data, existing_rows):
                row_status = "skipped"
                notes.append("Duplicate entry detected")
        
        # Combine notes
        combined_notes = "; ".join(notes) if notes else ""
        
        return {
            "row_number": row_num,
            "status": row_status,
            "note": combined_notes,
            "data": cleaned_data
        }
    
    def _calculate_summary(self, processed_rows: List[Dict]) -> None:
        """Calculate summary statistics."""
        self.summary = {
            "ok": sum(1 for r in processed_rows if r["status"] == "ok"),
            "fixed": sum(1 for r in processed_rows if r["status"] == "fixed"),
            "skipped": sum(1 for r in processed_rows if r["status"] == "skipped"),
            "total": len(processed_rows)
        }
    
    def _generate_cleaned_file(self, processed_rows: List[Dict]) -> bytes:
        """
        Generate Excel file with only valid (ok/fixed) rows.
        
        Args:
            processed_rows: List of processed row dictionaries
        
        Returns:
            Excel file as bytes
        """
        # Filter for valid rows only
        valid_rows = [
            r["data"] for r in processed_rows 
            if r["status"] in ["ok", "fixed"]
        ]
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Cleaned Data"
        
        # Write headers
        ws.append(REQUIRED_HEADERS)
        
        # Write data rows
        for row_data in valid_rows:
            ws.append([
                row_data["Email Address"],
                row_data["First Name"],
                row_data["Last Name"],
                row_data["Phone"],
                row_data["Date of Birth"],
                row_data["Zip Code"]
            ])
        
        # Save to bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output.getvalue()


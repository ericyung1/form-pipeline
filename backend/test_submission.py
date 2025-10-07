"""
Test script for submission API endpoints.
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_submission():
    """Test the submission endpoints with sample data."""
    
    print("\n" + "="*60)
    print("TESTING SUBMISSION API")
    print("="*60 + "\n")
    
    # Sample students (only 2 for quick testing)
    students = [
        {
            "row_number": 2,
            "data": {
                "Email Address": "test1@example.com",
                "First Name": "John",
                "Last Name": "Doe",
                "Phone": "5555551234",
                "Date of Birth": "01/15/2000",
                "Zip Code": "12345"
            }
        },
        {
            "row_number": 3,
            "data": {
                "Email Address": "test2@example.com",
                "First Name": "Jane",
                "Last Name": "Smith",
                "Phone": "5555555678",
                "Date of Birth": "03/20/2001",
                "Zip Code": "54321"
            }
        }
    ]
    
    # 1. Test /submit endpoint
    print("1. Starting submission...")
    submit_data = {
        "url": "https://www.goarmy.com/info?iom=CKXG-XX_LAP_Exhibit_2897052_C04_NA_ROTC",
        "students": students
    }
    
    response = requests.post(f"{BASE_URL}/submit", json=submit_data)
    print(f"   Response: {response.json()}\n")
    
    # 2. Monitor status
    print("2. Monitoring status...")
    for i in range(10):  # Monitor for 10 iterations
        time.sleep(2)  # Poll every 2 seconds
        
        response = requests.get(f"{BASE_URL}/status")
        status = response.json()
        
        print(f"   [{i+1}] Status: {status['status']} | "
              f"Progress: {status['completed']}/{status['total']} | "
              f"Failed: {status['failed']} | "
              f"Elapsed: {status['elapsed_seconds']}s")
        
        # Show latest log entries
        if status['log']:
            latest_log = status['log'][-1]
            print(f"       Latest: Row {latest_log['row']} - {latest_log['status']} - {latest_log['student']}")
        
        # Stop monitoring if completed or killed
        if status['status'] in ['completed', 'killed', 'error']:
            print(f"\n   Final Status: {status['status']}")
            break
    
    # 3. Show final summary
    print("\n3. Final Summary:")
    response = requests.get(f"{BASE_URL}/status")
    final_status = response.json()
    
    print(f"   Completed: {final_status['completed']}")
    print(f"   Failed: {final_status['failed']}")
    print(f"   Total Time: {final_status['elapsed_seconds']}s")
    
    if final_status['errors']:
        print(f"\n   Errors:")
        for error in final_status['errors']:
            print(f"   - {error}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")


def test_pause_resume():
    """Test pause and resume functionality."""
    
    print("\n" + "="*60)
    print("TESTING PAUSE/RESUME")
    print("="*60 + "\n")
    
    # Create submission with 3 students
    students = [
        {
            "row_number": i,
            "data": {
                "Email Address": f"test{i}@example.com",
                "First Name": f"Student{i}",
                "Last Name": "Test",
                "Phone": "5555551234",
                "Date of Birth": "01/15/2000",
                "Zip Code": "12345"
            }
        }
        for i in range(1, 4)
    ]
    
    submit_data = {
        "url": "https://www.goarmy.com/info?iom=CKXG-XX_LAP_Exhibit_2897052_C04_NA_ROTC",
        "students": students
    }
    
    # Start submission
    print("1. Starting submission...")
    response = requests.post(f"{BASE_URL}/submit", json=submit_data)
    print(f"   {response.json()}\n")
    
    # Wait a bit
    time.sleep(3)
    
    # Pause
    print("2. Pausing submission...")
    response = requests.post(f"{BASE_URL}/pause")
    print(f"   {response.json()}\n")
    
    # Check status
    response = requests.get(f"{BASE_URL}/status")
    status = response.json()
    print(f"   Status after pause: {status['status']}")
    print(f"   Position: {status['current_position']}/{status['total']}\n")
    
    # Wait
    time.sleep(2)
    
    # Resume
    print("3. Resuming submission...")
    response = requests.post(f"{BASE_URL}/resume")
    print(f"   {response.json()}\n")
    
    # Monitor completion
    for i in range(10):
        time.sleep(2)
        response = requests.get(f"{BASE_URL}/status")
        status = response.json()
        print(f"   [{i+1}] Status: {status['status']} | Progress: {status['completed']}/{status['total']}")
        
        if status['status'] in ['completed', 'killed', 'error']:
            break
    
    print("\n" + "="*60)
    print("PAUSE/RESUME TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Test basic submission
    test_submission()
    
    # Uncomment to test pause/resume
    # time.sleep(5)  # Wait before next test
    # test_pause_resume()


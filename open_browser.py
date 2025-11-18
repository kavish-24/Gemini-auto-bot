"""
Simple script to open Chrome browser with automation profile.
Use this to login to Gemini once, then the main script reuses the session.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import subprocess
import os

def close_chrome_processes():
    """Close all Chrome processes"""
    try:
        print("Checking for running Chrome processes...")
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], 
                      capture_output=True, check=False)
        time.sleep(2)
        print("Chrome processes closed.")
    except Exception as e:
        print(f"Note: {e}")

def main():
    print("="*60)
    print("CHROME BROWSER - AUTOMATION PROFILE")
    print("="*60)
    
    # Close Chrome completely
    close_chrome_processes()
    
    # ChromeDriver path
    CHROMEDRIVER_PATH = r"D:\Gemini_automator\chromedriver.exe"
    
    # Real Chrome profile path
    automation_profile = r"C:\Users\Kavish\AppData\Local\Google\Chrome\User Data"
    
    # Verify the profile folder exists
    if not os.path.exists(automation_profile):
        print(f"❌ Profile path does not exist: {automation_profile}")
        return
    
    print("Opening Chrome with your user profile...")
    print("You should already be logged in to Google.")
    
    service = Service(executable_path=CHROMEDRIVER_PATH)
    options = webdriver.ChromeOptions()
    
    # VERY IMPORTANT: Correct format
    options.add_argument(f"--user-data-dir={automation_profile}")
    options.add_argument("--profile-directory=Profile 3")
   # choose correct profile
    
    # Stabilizers
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Keep browser open after script ends
    options.add_experimental_option("detach", True)
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    # Start chrome
    driver = webdriver.Chrome(service=service, options=options)
    
    # Load Gemini
    print("Opening Gemini...")
    driver.get("https://gemini.google.com")
    
    print("="*60)
    print("Browser opened successfully!")
    print("If Gemini asks you to log in, do it now.")
    print("After login, CLOSE NOTHING — just run the main automation script.")
    print("="*60)
    
    time.sleep(3)

if __name__ == "__main__":
    main()

"""
Connect to already-open Chrome and type in Gemini.
Make sure Chrome is already open with Gemini loaded!
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def main():
    CHROME_DRIVER = r"D:\Gemini_automator\chromedriver.exe"
    
    # Connect to existing Chrome with remote debugging
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    print("Connecting to your open Chrome browser...")
    try:
        driver = webdriver.Chrome(service=Service(CHROME_DRIVER), options=options)
        print("✅ Connected!")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("\nMake sure Chrome is open with this flag:")
        print('chrome.exe --remote-debugging-port=9222')
        return
    
    print(f"Current page: {driver.current_url}")
    
    # Find the input box
    print("\nLooking for Gemini input box...")
    try:
        # Wait for the textarea to appear
        wait = WebDriverWait(driver, 10)
        
        # Common Gemini input selectors
        selectors = [
            "textarea[placeholder*='Enter']",
            "textarea[aria-label*='prompt']",
            "textarea.ql-editor",
            "div[contenteditable='true']",
            "textarea",
        ]
        
        input_box = None
        for selector in selectors:
            try:
                input_box = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Found input box using: {selector}")
                break
            except:
                continue
        
        if not input_box:
            print("❌ Could not find input box")
            print("Please provide the HTML of the input element")
            return
        
        # Type "hi"
        print("Typing 'hi'...")
        input_box.click()
        time.sleep(0.5)
        input_box.send_keys("hi")
        
        print("✅ Typed 'hi' successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import subprocess
import os
import pyperclip

def kill_chrome():
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
    time.sleep(1)

def main():
    print("="*60)
    print("STEP 1: Opening Chrome with remote debugging...")
    print("="*60)
    
    # Kill any existing Chrome
    kill_chrome()
    time.sleep(3)

    CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    PROFILE_PATH = r"C:\Users\Kavish\AppData\Local\Google\Chrome\User Data"
    PROFILE_NAME = "Profile 3"
    
    # Use a separate user data dir for automation to avoid locks
    AUTOMATION_DATA_DIR = r"D:\Gemini_automator\chrome_debug_profile"
    
    # Launch Chrome with remote debugging using automation profile
    chrome_cmd = [
        CHROME_PATH,
        f"--user-data-dir={AUTOMATION_DATA_DIR}",
        "--remote-debugging-port=9222",
        "--start-maximized",
        "https://gemini.google.com"
    ]
    
    print("Starting Chrome with debugging enabled...")
    print("NOTE: You'll need to login to Google manually in this Chrome window.")
    try:
        subprocess.Popen(chrome_cmd, shell=False)
        print("✅ Chrome process started")
    except Exception as e:
        print(f"❌ Failed to start Chrome: {e}")
        return
    
    print("Waiting for Chrome to start and open debugging port...")
    time.sleep(8)
    
    # Verify Chrome is running
    result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq chrome.exe"], 
                          capture_output=True, text=True)
    if "chrome.exe" in result.stdout:
        print("✅ Chrome is running")
    else:
        print("❌ Chrome is not running!")
        return
    
    print("\n" + "="*60)
    print("IMPORTANT: Login to Google in the Chrome window that just opened!")
    print("Then navigate to https://gemini.google.com")
    print("="*60)
    input("\nPress ENTER after you've logged in and are on Gemini page...")
    print()
    
    print("="*60)
    print("STEP 2: Connecting to Chrome...")
    print("="*60)
    
    CHROME_DRIVER = r"D:\Gemini_automator\chromedriver.exe"
    
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(service=Service(CHROME_DRIVER), options=options)
        print("✅ Connected to Chrome!")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    print(f"Current page: {driver.current_url}")
    
    # Wait for user confirmation
    print("\n" + "="*60)
    response = input("Type 'y' when you're ready for me to paste a prompt: ")
    
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Find input box and paste prompt
    print("\nLooking for Gemini input box...")
    try:
        # Try multiple selectors
        selectors = [
            "textarea[placeholder*='Enter']",
            "textarea[aria-label*='prompt']",
            "div[contenteditable='true']",
            "textarea",
        ]
        
        input_box = None
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    input_box = elements[0]
                    print(f"✅ Found input box: {selector}")
                    break
            except:
                continue
        
        if not input_box:
            print("❌ Could not find input box")
            return
        
        # Paste the prompt
        test_prompt = "Hello! This is a test message from automation."
        print(f"\nPasting prompt: {test_prompt}")
        
        input_box.click()
        time.sleep(0.5)
        
        pyperclip.copy(test_prompt)
        input_box.send_keys(Keys.CONTROL, 'v')
        input_box.send_keys(Keys.ENTER)
        
        print("✅ Prompt pasted and sent!")
        print("\nWaiting for Gemini to respond...")
        time.sleep(5)
        
        # Wait for response to complete
        print("Monitoring response...")
        previous_length = 0
        stable_count = 0
        
        for _ in range(60):  # Wait up to 60 seconds
            try:
                # Find response elements
                response_elements = driver.find_elements(By.CSS_SELECTOR, 
                    "div[data-test-id*='conversation-turn'], div.model-response, div[class*='response']")
                
                if response_elements:
                    current_text = response_elements[-1].text
                    current_length = len(current_text)
                    
                    if current_length == previous_length and current_length > 0:
                        stable_count += 1
                        if stable_count >= 3:
                            print("✅ Response complete!")
                            break
                    else:
                        stable_count = 0
                    
                    previous_length = current_length
                    
            except Exception as e:
                pass
            
            time.sleep(1)
        
        # Get the full response
        print("\n" + "="*60)
        print("GEMINI RESPONSE:")
        print("="*60)
        try:
            # Try to click the copy button directly
            print("Looking for copy button...")
            copy_button_selectors = [
                "button[aria-label*='Copy']",
                "button[title*='Copy']",
                "button[data-tooltip*='Copy']",
                "button.copy-button",
                "[class*='copy'][role='button']",
            ]
            
            copy_clicked = False
            for selector in copy_button_selectors:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    if buttons:
                        # Click the last copy button (most recent response)
                        buttons[-1].click()
                        print(f"✅ Clicked copy button using: {selector}")
                        copy_clicked = True
                        time.sleep(0.5)
                        break
                except:
                    continue
            
            if copy_clicked:
                # Get from clipboard
                gemini_response = pyperclip.paste()
                print("\n" + "-"*60)
                print(gemini_response)
                print("-"*60)
                print("\n✅ Response copied from clipboard!")
            else:
                print("⚠️ Copy button not found, trying text extraction...")
                
                # Fallback: try to get text from response container
                selectors = [
                    "div[data-test-id*='conversation-turn']",
                    "div.model-response",
                    "message-content",
                ]
                
                for selector in selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            gemini_response = elements[-1].text.strip()
                            if gemini_response and len(gemini_response) > 10:
                                print("\n" + "-"*60)
                                print(gemini_response)
                                print("-"*60)
                                pyperclip.copy(gemini_response)
                                print("\n✅ Response extracted and copied!")
                                break
                    except:
                        continue
                
        except Exception as e:
            print(f"❌ Error getting response: {e}")
            import traceback
            traceback.print_exc()
        
        print("\nPress Ctrl+C to exit...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()

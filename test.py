from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
service= Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service)
driver.get("https://gemini.google.com")
time.sleep(3)  # Wait for page to load
# Use a more specific selector for the textarea
input_element = driver.find_element(By.CSS_SELECTOR, ".ql-editor[contenteditable='true']")
input_element.send_keys("Hello, Gemini!" + Keys.ENTER)
time.sleep(15)
driver.quit()


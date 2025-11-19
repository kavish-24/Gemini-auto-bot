"""
Complete Selenium Automation Bot for Gemini UI
Automates text matching between segment transcripts and full transcripts
MODIFIED: Skips login wait since Chrome is already logged in
"""

import os
import re
import time
import zipfile
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import List, Tuple, Optional

import pyperclip  # For copying large text to clipboard

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# ===================================================
# UNIVERSAL TRANSCRIPT READER
# ===================================================

def read_txt(path: str) -> str:
    """Read text from .txt file"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_docx(path: str) -> str:
    """Read text from .docx file"""
    try:
        from docx import Document
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    except ImportError:
        raise ImportError("python-docx is required. Install with: pip install python-docx")


def read_odt(path: str) -> str:
    """Read text from .odt file"""
    with zipfile.ZipFile(path, 'r') as z:
        xml_content = z.read("content.xml")
    root = ET.fromstring(xml_content)
    ns = {"text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}
    paragraphs = []
    for p in root.findall(".//text:p", ns):
        collected = ""
        for node in p.iter():
            if node.text:
                collected += node.text
        paragraphs.append(collected.strip())
    return "\n".join(paragraphs)


def load_transcript(path: str) -> str:
    """Universal transcript reader - supports TXT, DOCX, ODT"""
    p = path.lower()
    if p.endswith(".txt"):
        return read_txt(path)
    if p.endswith(".docx"):
        return read_docx(path)
    if p.endswith(".odt"):
        return read_odt(path)
    raise ValueError(f"Unsupported file type: {path}")


# ===================================================
# EXACT MAPPING TABLE - Segment Folder to Cleaned Transcript
# ===================================================

SEGMENT_TO_TRANSCRIPT_MAP = {
    # AUGUST
    "Konkani Prime News_070817": "7 AUG PRIME_non_bold.odt",
    "Konkani Prime News_100817": "10 AUG PRIME_non_bold.odt",
    "Konkani Prime News_150817": "15 AUG PRIME_non_bold.odt",
    "Konkani Prime News_180817": "18 AUG PRIME_non_bold.odt",
    "Konkani Prime News_210817": "21 AUG PRIME_non_bold.odt",
    "Konkani Prime News_260817": "26 AUG PRIME_non_bold.odt",
    "Konkani Prime News_270817": "27 AUG PRIME_non_bold.odt",
    "Konkani Prime News_310817": "31 AUG PRIME_non_bold.odt",
    
    # JULY
    "konkani Prime news_030717": "3 JULY PRIME_non_bold.odt",
    "Konkani Prime news_040717": "4 JULY PRIME_non_bold.odt",
    "Konkani Prime news_060717": "6  JULY PRIME_non_bold.odt",
    "Konkani Prime news_100717": "10JULYPRIME_non_bold.odt",
    "Konkani Prime news_170717": "17 JULY PRIME_non_bold.odt",
    "Konkani Update news_170717": "17 JULY UPDATE_non_bold.odt",
    "Konkani Prime news_250717": "25 JULY PRIME_non_bold.odt",
    "Konkani Prime news_270717": "27 JULY PRIME_non_bold.odt",
    
    # JUNE
    "konkani prime news_01.0617": "1 JUNE PRIME_non_bold.odt",
    "konkani prime news_050617": "5 JUNE PRIME_non_bold.odt",
    "konkani update news_110617": "11 JUNE UPDATE_non_bold.odt",
    "konkani prime news_120617": "12 JUNE PRIME_non_bold.odt",
    "konkani prime news_190617": "19 JUNE PRIME_non_bold.odt",
    "konkani prime news_210617": "21 JUNE PRIME_non_bold.odt",
    "konkani prime news_220617": "22 JUNE PRIME_non_bold.odt",
    "konkani Prime news_260617": "26 JUNE PRIME_non_bold.odt",
    "konkani update news_260617": "26 JUNE UPDATE_non_bold.odt",
    
    # MAY
    "Konk Prime_010517": "1 MAY PRIME_non_bold.odt",
    "Konk Prime News_040517": "4 MAY PRIME_non_bold.odt",
    "Konkani Prime News_080517": "8 MAY PRIME_non_bold.odt",
    "Konk Prime News_110517": "11 MAY PRIME_non_bold.odt",
    "Konkani Prime News_150517": "15 MAY PRIME_non_bold.odt",
    "Konk Prime News_220517": "21 MAY PRIME_non_bold.odt",
    "konkani prime news_250517": "25 MAY PRIME_non_bold.odt",
    
    # OCTOBER
    "2nd Oct 17_Konk Prime News": "2 OCT PRIME_non_bold.odt",
    "6nd Oct 17_Konk Prime News": "6 OCT PRIME_non_bold.odt",
    "9th Oct 17_Konk Prime News": "9 OCT PRIME_non_bold.odt",
    "12th Oct 17_Konk Prime News": "12 OCT PRIME_non_bold.odt",
    "16th Oct 17_Konk Prime News": "16 OCT PRIME_non_bold.odt",
    "19th Oct 17_Konk Prime News": "19 OCT PRIME_non_bold.odt",
    "27th Oct 17_Konk Prime News": "27 OCT PRIME_non_bold.odt",
    "30th Oct 17_Konk Prime News": "30 OCT PRIME_non_bold.odt",
    
    # NOVEMBER
    "03 nov 17_Konk Prime News": "3  NOV  PRIME_non_bold.odt",
    "06 nov 17_Konk Prime News": "6  NOV  PRIME_non_bold.odt",
    "konkani prime 13 nov 17": "13  NOV PRIME_non_bold.odt",
    "konkani prime 15 nov 17": "15 NOV PRIME_non_bold.odt",
    "konkani prime 16 nov 17": "16 NOV PRIME_non_bold.odt",
    "16th Nov 17 _ konkani update 17 nov _audio_only": "16 NOV PRIME_non_bold.odt",
    "konkani prime 20 nov 17": "20 NOV PRIME_non_bold.odt",
    "konkani prime 24 nov 17": "24  NOV PRIME_non_bold.odt",
    "konkani prime 27 nov 17": "27  NOV PRIME_non_bold.odt",
}

# Month folder mapping
MONTH_FOLDER_MAP = {
    "aug": "Augustcleaned",
    "july": "Julycleaned",
    "june": "Junecleaned",
    "may": "Maycleaned",
    "october": "Octobercleaned",
    "november": "Novembercleaned",
}


# ===================================================
# FILE DISCOVERY AND ORGANIZATION
# ===================================================

def find_segment_files(segment_dir: str) -> List[Tuple[str, str]]:
    """
    Find all segment files and return list of (subfolder_path, file_path) tuples
    """
    segment_files = []
    base_path = Path(segment_dir)
    
    for month_folder in base_path.iterdir():
        if not month_folder.is_dir():
            continue
            
        for subfolder in month_folder.iterdir():
            if not subfolder.is_dir():
                continue
                
            for txt_file in subfolder.glob("*.txt"):
                rel_subfolder = str(subfolder.relative_to(base_path))
                segment_files.append((rel_subfolder, str(txt_file)))
    
    return segment_files


def find_corresponding_full_transcript(segment_subfolder: str, cleaned_transcript_dir: str) -> Optional[str]:
    """
    Find the corresponding full transcript file using the exact mapping table.
    """
    segment_folder_name = Path(segment_subfolder).name
    
    transcript_filename = None
    for key, value in SEGMENT_TO_TRANSCRIPT_MAP.items():
        if key.lower() == segment_folder_name.lower():
            transcript_filename = value
            break
    
    if not transcript_filename:
        print(f"  Warning: No mapping found for segment folder: {segment_folder_name}")
        return None
    
    month_folder = Path(segment_subfolder).parent.name.lower()
    month_name = None
    
    for key, value in MONTH_FOLDER_MAP.items():
        if key in month_folder:
            month_name = value
            break
    
    if not month_name:
        month_map = {
            "jan": "january", "feb": "february", "mar": "march", "apr": "april",
            "may": "may", "jun": "june", "jul": "july", "aug": "august",
            "sep": "september", "oct": "october", "nov": "november", "dec": "december"
        }
        for key, value in month_map.items():
            if key in month_folder or value in month_folder:
                month_name = value
                break
    
    if not month_name:
        print(f"  Warning: Could not determine month from {segment_subfolder}")
        return None
    
    month_folder_path = Path(cleaned_transcript_dir) / month_name
    if not month_folder_path.exists():
        print(f"  Warning: Month folder not found: {month_folder_path}")
        return None
    
    transcript_path = month_folder_path / transcript_filename
    
    if transcript_path.exists():
        print(f"  ✓ Matched: {segment_folder_name} -> {transcript_filename}")
        return str(transcript_path)
    else:
        for file in month_folder_path.glob("*"):
            if file.name.lower() == transcript_filename.lower():
                print(f"  ✓ Matched (case-insensitive): {segment_folder_name} -> {file.name}")
                return str(file)
        
        print(f"  ✗ Error: Transcript file not found: {transcript_path}")
        return None


def group_segments_by_subfolder(segment_files: List[Tuple[str, str]]) -> dict:
    """Group segment files by their subfolder"""
    grouped = {}
    for subfolder, file_path in segment_files:
        if subfolder not in grouped:
            grouped[subfolder] = []
        grouped[subfolder].append(file_path)
    return grouped


# ===================================================
# PROMPT GENERATION
# ===================================================

def build_strict_matcher_prompt(segment_files: List[str], full_transcript: str) -> str:
    """
    Build the strict fuzzy-text alignment prompt with character-level similarity.
    """
    prompt_parts = [
        "You are a STRICT fuzzy-text aligner, not a translator.\n\n",
        "Your task:\n",
        "Given a LARGE TRANSCRIPT and multiple SEGMENTS (Whisper outputs),\n",
        "for each segment find the CLOSEST MATCHING PASSAGE from the transcript\n",
        "using CHARACTER-LEVEL similarity (not meaning).\n\n",
        "Rules:\n",
        "• Compare segment text and transcript text as Devanagari strings.\n",
        "• Allow spelling drift, vowel swaps, minor consonant variations.\n",
        "• DO NOT guess missing lines or invent text.\n",
        "• Select only the longest substring with ≥ 60% similarity.\n",
        "• If no substring reaches 60% similarity → SKIP that segment.\n",
        "• NEVER modify the transcript; return the transcript substring EXACTLY.\n",
        "• NEVER output explanations.\n",
        "• NEVER output invented text.\n\n",
        "Similarity method:\n",
        "• Compare substrings of the transcript against the segment.\n",
        "• Score based on longest matching character sequence and overall edit distance.\n",
        "• Choose the top-scoring match ONLY.\n\n",
        "Output:\n",
        "Return ONLY a CSV:\n",
        "file_name, matched_text\n\n",
        "Skip segments with no qualified match.\n",
        "DO NOT output blank rows.\n",
        "DO NOT output commentary.\n\n",
        "BEGIN\n",
        "Segments:\n"
    ]
    
    for segment_file in segment_files:
        file_name = Path(segment_file).stem
        try:
            segment_text = load_transcript(segment_file)
            prompt_parts.append(f"--- {file_name} ---\n")
            prompt_parts.append(f"{segment_text}\n\n")
        except Exception as e:
            print(f"Warning: Could not read segment file {segment_file}: {e}")
            continue
    
    prompt_parts.append("Transcript:\n")
    prompt_parts.append(f"{full_transcript}\n")
    
    return "".join(prompt_parts)


# ===================================================
# SELENIUM AUTOMATION FUNCTIONS
# ===================================================

class GeminiAutomator:
    """Selenium automation class for Gemini UI"""
    
    def __init__(self, chromedriver_path: str = "chromedriver.exe"):
        """Initialize the browser"""
        self.driver = None
        self.chromedriver_path = chromedriver_path
        self.wait = None
    
    def start_browser(self):
        """Start Chrome browser with remote debugging and connect to it"""
        print("🔧 Step 1: Starting Chrome browser...")
        
        # Kill any existing Chrome
        print("   Closing any existing Chrome instances...")
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
        time.sleep(3)
        
        CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        AUTOMATION_DATA_DIR = r"D:\Gemini_automator\chrome_debug_profile"
        
        # Launch Chrome with remote debugging
        chrome_cmd = [
            CHROME_PATH,
            f"--user-data-dir={AUTOMATION_DATA_DIR}",
            "--remote-debugging-port=9222",
            "--start-maximized",
            "https://gemini.google.com"
        ]
        
        print("   Starting Chrome with debugging enabled...")
        try:
            subprocess.Popen(chrome_cmd, shell=False)
            print("   ✓ Chrome process started")
        except Exception as e:
            print(f"   ❌ Failed to start Chrome: {e}")
            raise
        
        print("   Waiting for Chrome to start and open debugging port...")
        time.sleep(8)
        
        # Verify Chrome is running
        result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq chrome.exe"], 
                              capture_output=True, text=True)
        if "chrome.exe" not in result.stdout:
            raise Exception("Chrome failed to start!")
        print("   ✓ Chrome is running")
        
        print("\n🌐 Step 2: Connecting to Chrome...")
        service = Service(executable_path=self.chromedriver_path)
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        try:
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 15)
            print("   ✓ Connected to Chrome!")
        except Exception as e:
            print(f"   ❌ Failed to connect: {e}")
            raise
        
        print(f"   Current page: {self.driver.current_url}")
        
        print("\n⏳ Step 3: Setting up automation...")
        print("   ⚠️  IMPORTANT: Make sure you're logged into Google in the Chrome window!")
        print("   ⚠️  Navigate to https://gemini.google.com if not already there")
        
        # Give 15 seconds for manual setup
        print("\n   ⏱️  You have 15 seconds to setup (login/navigate to Gemini)...")
        for i in range(15, 0, -1):
            print(f"   Starting in {i} seconds...", end='\r')
            time.sleep(1)
        print("\n\n✅ Browser ready! Starting automation...\n")
    
    def find_input_element(self):
        """Find the Gemini input textarea element"""
        print("   🔍 Searching for Gemini input element...")
        try:
            selectors = [
                ".ql-editor[contenteditable='true']",
                "textarea[aria-label*='Enter a prompt']",
                "textarea[placeholder*='Enter a prompt']",
                "[contenteditable='true'][role='textbox']",
                "div[contenteditable='true']"
            ]
            
            for i, selector in enumerate(selectors, 1):
                print(f"      Trying selector {i}/{len(selectors)}: {selector}")
                try:
                    element = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"      ✓ Found input element with selector: {selector}")
                    return element
                except TimeoutException:
                    print(f"      ✗ Selector failed: {selector}")
                    continue
            
            raise NoSuchElementException("Could not find input element")
        except Exception as e:
            print(f"   ❌ Error finding input element: {e}")
            raise
    
    def clear_input_box(self):
        """Clear the input box by selecting all and deleting"""
        try:
            input_element = self.find_input_element()
            input_element.click()
            time.sleep(0.5)
            input_element.send_keys(Keys.CONTROL + "a")
            time.sleep(0.3)
            input_element.send_keys(Keys.DELETE)
            time.sleep(0.5)
        except Exception as e:
            print(f"Warning: Could not clear input box: {e}")
            self.driver.refresh()
            time.sleep(3)
    
    def send_prompt_to_gemini(self, prompt_text: str):
        """
        Paste prompt into Gemini input textbox using pyperclip and press Enter.
        """
        print("\n📤 Step 4: Sending prompt to Gemini...")
        try:
            print("   🧹 Clearing previous input...")
            self.clear_input_box()
            
            print("   🔍 Waiting for input element...")
            input_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ql-editor[contenteditable='true']"))
            )
            print("   ✓ Input element found")
            
            print("   📋 Copying prompt to clipboard...")
            pyperclip.copy(prompt_text)
            print(f"   ✓ Copied {len(prompt_text)} characters to clipboard")
            
            print("   🖱️ Clicking input element to focus...")
            input_element.click()
            time.sleep(1)
            print("   ✓ Input element focused")
            
            print("   📝 Pasting content via Ctrl+V...")
            input_element.send_keys(Keys.CONTROL, 'v')
            print("   ✓ Content pasted")
            
            time.sleep(1)
            
            print("   ⏎ Pressing Enter to submit...")
            input_element.send_keys(Keys.ENTER)
            print("   ✓ Prompt submitted successfully!")
            print("   ⏳ Waiting for Gemini to generate response...")
            
        except Exception as e:
            print(f"   ❌ Error sending prompt: {e}")
            raise
    
    def wait_for_response_complete(self, timeout: int = 300):
        """
        Wait exactly 20 seconds for Gemini response with countdown timer.
        """
        print("   ⏳ Waiting 20 seconds for Gemini response...")
        
        for i in range(20, 0, -1):
            print(f"   ⏱️  {i} seconds remaining...", end='\r')
            time.sleep(1)
        
        print("\n   ✓ Wait complete!                    ")
    
    def read_gemini_output(self) -> str:
        """
        Extract full text from Gemini response area using copy button
        """
        try:
            print("   📋 Scrolling to bottom to ensure full response is visible...")
            
            # Scroll to bottom of the page to ensure complete response is loaded
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)  # Wait for scroll to complete
                print("   ✓ Scrolled to bottom")
            except Exception as e:
                print(f"   ⚠️  Scroll failed: {e}")
            
            print("   📋 Looking for copy button to get response...")
            
            # Try to click the copy button
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
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if buttons:
                        # Scroll the last copy button into view first
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", buttons[-1])
                        time.sleep(0.5)
                        
                        # Click the last copy button (most recent response)
                        buttons[-1].click()
                        print(f"   ✓ Clicked copy button")
                        copy_clicked = True
                        time.sleep(0.5)
                        break
                except:
                    continue
            
            if copy_clicked:
                # Get from clipboard
                response_text = pyperclip.paste()
                print(f"   ✓ Got {len(response_text)} characters from clipboard")
                return response_text.strip()
            else:
                print("   ⚠️  Copy button not found, using text extraction...")
                
                # Fallback: try to get text from response container
                response_selectors = [
                    "div[class*='markdown']",
                    "div[data-markdown]",
                    ".response-text",
                    "[data-testid='response']",
                    "div.model-response-text"
                ]
                
                for selector in response_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            response_text = elements[-1].text
                            if response_text:
                                print(f"   ✓ Extracted {len(response_text)} characters using {selector}")
                                return response_text.strip()
                    except:
                        continue
                
                # Last resort
                try:
                    main_content = self.driver.find_element(By.TAG_NAME, "main")
                    response_text = main_content.text
                    if response_text:
                        print(f"   ✓ Extracted {len(response_text)} characters from main tag")
                        return response_text.strip()
                except:
                    pass
                
                print("   ⚠️  Could not extract response text")
                return ""
            
        except Exception as e:
            print(f"   ❌ Error reading Gemini output: {e}")
            return ""
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()


# ===================================================
# RESPONSE PARSING
# ===================================================

def parse_gemini_response(response_text: str) -> List[Tuple[str, str]]:
    """
    Parse Gemini response to extract file_name and matched_text pairs.
    Handles multiple formats:
    1. --- filename ---,text
    2. filename,text
    """
    matches = []
    
    # Remove the CSV header if present
    response_text = re.sub(r'^file_name\s*,\s*matched_text\s*\n?', '', response_text, flags=re.IGNORECASE)
    
    # Try format 1: --- filename ---,text
    pattern1 = r'---\s*([^-]+?)\s*---\s*,\s*(.+?)(?=\s*---\s*[^-]+?\s*---|$)'
    
    for match in re.finditer(pattern1, response_text, re.MULTILINE | re.DOTALL):
        file_name = match.group(1).strip()
        matched_text = match.group(2).strip()
        
        if file_name and matched_text:
            matches.append((file_name, matched_text))
            print(f"   Parsed (format 1): {file_name} ({len(matched_text)} chars)")
    
    # If no matches with format 1, try format 2: filename,text (CSV style)
    if not matches:
        # Split by newlines and parse each line
        lines = response_text.strip().split('\n')
        for line in lines:
            # Skip empty lines or header
            if not line.strip() or 'file_name' in line.lower():
                continue
            
            # Try to split by comma - filename should be before first comma
            parts = line.split(',', 1)
            if len(parts) == 2:
                file_name = parts[0].strip()
                matched_text = parts[1].strip()
                
                # Make sure filename looks valid (not just random text)
                if file_name and matched_text and len(file_name) < 200:
                    matches.append((file_name, matched_text))
                    print(f"   Parsed (format 2): {file_name} ({len(matched_text)} chars)")
    
    return matches


# ===================================================
# FILE SAVING
# ===================================================

def save_matched_outputs(matches: List[Tuple[str, str]], output_dir: str, segment_subfolder: str):
    """
    Save each matched_text to its own .txt file.
    Handles long filenames by truncating them to fit Windows path limits.
    """
    full_output_dir = Path(output_dir) / segment_subfolder
    full_output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_count = 0
    for file_name, matched_text in matches:
        # Remove invalid characters
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', file_name)
        if not safe_filename.endswith('.txt'):
            safe_filename += '.txt'
        
        # Handle long filenames - Windows has 260 char path limit
        # Reserve space for directory path and .txt extension
        base_path = str(full_output_dir)
        max_filename_length = 255 - len(base_path) - 10  # Extra buffer for safety
        
        if len(safe_filename) > max_filename_length:
            # Truncate filename but keep .txt extension
            name_part = safe_filename[:-4]  # Remove .txt
            truncated_name = name_part[:max_filename_length - 4]  # Leave room for .txt
            safe_filename = truncated_name + '.txt'
            print(f"  ⚠️  Truncated long filename to: {safe_filename[:50]}...")
        
        output_path = full_output_dir / safe_filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(matched_text)
            saved_count += 1
            print(f"  Saved: {safe_filename}")
        except Exception as e:
            print(f"  Error saving {safe_filename}: {e}")
    
    return saved_count


# ===================================================
# MAIN AUTOMATION LOOP
# ===================================================

def main():
    """Main automation loop"""
    
    BASE_DIR = r"D:\Gemini_automator"
    CLEANED_TRANSCRIPT_DIR = os.path.join(BASE_DIR, "Cleaned Transcript")
    SEGMENT_TRANSCRIPT_DIR = os.path.join(BASE_DIR, "Segment transcript")
    OUTPUT_DIR = os.path.join(BASE_DIR, "training")
    CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")
    
    print("="*60)
    print("GEMINI UI AUTOMATION BOT")
    print("="*60)
    print(f"Cleaned Transcript Dir: {CLEANED_TRANSCRIPT_DIR}")
    print(f"Segment Transcript Dir: {SEGMENT_TRANSCRIPT_DIR}")
    print(f"Output Dir: {OUTPUT_DIR}")
    print("="*60)
    
    print("\n🤖 Initializing automator...")
    automator = GeminiAutomator(chromedriver_path=CHROMEDRIVER_PATH)
    print("   ✓ Automator initialized")
    
    try:
        print("\n" + "="*60)
        print("PHASE 1: BROWSER STARTUP")
        print("="*60)
        automator.start_browser()
        
        print("\n" + "="*60)
        print("PHASE 2: FILE DISCOVERY")
        print("="*60)
        print("\n🔍 Discovering segment files...")
        segment_files = find_segment_files(SEGMENT_TRANSCRIPT_DIR)
        print(f"   ✓ Found {len(segment_files)} segment files")
        
        print("\n📁 Grouping segments by subfolder...")
        grouped_segments = group_segments_by_subfolder(segment_files)
        print(f"   ✓ Found {len(grouped_segments)} segment subfolders")
        
        print("\n📋 Subfolders to process:")
        for i, subfolder in enumerate(grouped_segments.keys(), 1):
            print(f"   {i}. {subfolder} ({len(grouped_segments[subfolder])} files)")
        
        print("\n" + "="*60)
        print("PHASE 3: PROCESSING SEGMENTS")
        print("="*60)
        
        processed_count = 0
        for subfolder, segment_file_list in grouped_segments.items():
            processed_count += 1
            print(f"\n{'='*60}")
            print(f"📂 SUBFOLDER {processed_count}/{len(grouped_segments)}: {subfolder}")
            print(f"{'='*60}")
            
            try:
                print("\n🔗 Step 1: Finding corresponding full transcript...")
                full_transcript_path = find_corresponding_full_transcript(
                    subfolder, CLEANED_TRANSCRIPT_DIR
                )
                
                if not full_transcript_path:
                    print("   ❌ Could not find full transcript for this subfolder")
                    print("   ⏭️ Skipping to next subfolder...")
                    continue
                
                print(f"   ✓ Matched transcript: {Path(full_transcript_path).name}")
                
                print("\n📖 Step 2: Loading full transcript...")
                try:
                    full_transcript = load_transcript(full_transcript_path)
                    print(f"   ✓ Loaded {len(full_transcript)} characters")
                except Exception as e:
                    print(f"   ❌ Error loading transcript: {e}")
                    continue
                
                print(f"\n🔨 Step 3: Building prompt for {len(segment_file_list)} segments...")
                prompt = build_strict_matcher_prompt(segment_file_list, full_transcript)
                print(f"   ✓ Prompt built: {len(prompt)} characters")
                
                automator.send_prompt_to_gemini(prompt)
                
                print("\n⏳ Step 5: Waiting for Gemini response to complete...")
                automator.wait_for_response_complete()
                
                print("\n📥 Step 6: Reading Gemini response...")
                response = automator.read_gemini_output()
                
                if not response:
                    print("   ⚠️ Warning: Empty response from Gemini")
                    continue
                
                print(f"   ✓ Response received: {len(response)} characters")
                
                print("\n" + "="*60)
                print("DEBUG - RAW RESPONSE (first 500 chars):")
                print("="*60)
                print(response[:500])
                print("="*60 + "\n")
                
                print("🔍 Step 7: Parsing response...")
                matches = parse_gemini_response(response)
                print(f"   ✓ Found {len(matches)} matches")
                
                if matches:
                    print("\n💾 Step 8: Saving matched outputs...")
                    saved = save_matched_outputs(matches, OUTPUT_DIR, subfolder)
                    print(f"   ✅ Saved {saved} files successfully")
                else:
                    print("   ⚠️ No matches found in response")
                
                print("\n🔄 Step 9: Starting new chat for next prompt...")
                try:
                    # Click "New chat" button to start fresh
                    new_chat_selectors = [
                        "button[aria-label*='New chat']",
                        "button[title*='New chat']",
                        "[aria-label='New chat']",
                        "a[href*='new']",
                    ]
                    
                    new_chat_clicked = False
                    for selector in new_chat_selectors:
                        try:
                            buttons = automator.driver.find_elements(By.CSS_SELECTOR, selector)
                            if buttons:
                                buttons[0].click()
                                print("   ✓ Started new chat")
                                new_chat_clicked = True
                                time.sleep(2)
                                break
                        except:
                            continue
                    
                    if not new_chat_clicked:
                        print("   ⚠️ New chat button not found, clearing input instead")
                        automator.clear_input_box()
                    
                except Exception as e:
                    print(f"   ⚠️ Could not start new chat: {e}")
                    automator.clear_input_box()
                
                time.sleep(2)
                print("   ✓ Ready for next subfolder")
                
            except Exception as e:
                print(f"\n❌ Error processing {subfolder}: {e}")
                import traceback
                traceback.print_exc()
                print("⏭️ Continuing with next subfolder...")
                continue
        
        print(f"\n{'='*60}")
        print("🎉 AUTOMATION COMPLETE!")
        print(f"{'='*60}")
        print(f"✅ Processed {processed_count} subfolders")
        print(f"{'='*60}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Automation interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔒 Closing browser in 5 seconds...")
        time.sleep(5)
        automator.close()
        print("✓ Browser closed")


if __name__ == "__main__":
    main()
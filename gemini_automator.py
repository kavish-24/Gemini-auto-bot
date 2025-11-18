"""
Complete Selenium Automation Bot for Gemini UI
Automates text matching between segment transcripts and full transcripts
"""

import os
import re
import time
import zipfile
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

# This is the exact 1-to-1 mapping provided by the user
SEGMENT_TO_TRANSCRIPT_MAP = {
    # AUGUST
    "Konkani Prime News_070817": "7 AUG PRIME_non_bold.odt",
    "Konkani Prime News_100817": "10  AUG PRIME_non_bold.odt",
    "Konkani Prime News_150817": "15 AUG PRIME_non_bold.odt",
    "Konkani Prime News_180817": "18 AUG PRIME_non_bold.odt",
    "Konkani Prime News_210817": "21 AUG PRIME_non_bold.odt",
    "Konkani Prime News_260817": "26 AUG PRIME_non_bold.odt",
    "Konkani Prime News_270817": "27 AUG PRIME_non_bold.odt",
    "Konkani Prime News_310817": "31  AUG PRIME_non_bold.odt",
    
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
    "Konk Prime News_220517": "21 MAY PRIME_non_bold.odt",  # Note: date mismatch in mapping but using as provided
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
    "16th Nov 17_konkani update 17 nov_audio_only": "16 NOV PRIME_non_bold.odt",
    "konkani prime 20 nov 17": "20 NOV PRIME_non_bold.odt",
    "konkani prime 24 nov 17": "24  NOV PRIME_non_bold.odt",
    "konkani prime 27 nov 17": "27  NOV PRIME_non_bold.odt",
}

# Month folder mapping
MONTH_FOLDER_MAP = {
    "aug": "august",
    "july": "july",
    "june": "june",
    "may": "may",
    "october": "october",
    "november": "november",
}


# ===================================================
# FILE DISCOVERY AND ORGANIZATION
# ===================================================

def find_segment_files(segment_dir: str) -> List[Tuple[str, str]]:
    """
    Find all segment files and return list of (subfolder_path, file_path) tuples
    Example: ("Segment transcript/July/Konkani Prime news_170717", "segment_001.txt")
    """
    segment_files = []
    base_path = Path(segment_dir)
    
    # Walk through all subdirectories
    for month_folder in base_path.iterdir():
        if not month_folder.is_dir():
            continue
            
        for subfolder in month_folder.iterdir():
            if not subfolder.is_dir():
                continue
                
            # Find all .txt files in this subfolder
            for txt_file in subfolder.glob("*.txt"):
                # Get relative path from segment_dir
                rel_subfolder = str(subfolder.relative_to(base_path))
                segment_files.append((rel_subfolder, str(txt_file)))
    
    return segment_files


def find_corresponding_full_transcript(segment_subfolder: str, cleaned_transcript_dir: str) -> Optional[str]:
    """
    Find the corresponding full transcript file using the exact mapping table.
    Uses the provided 1-to-1 mapping for perfect accuracy.
    """
    segment_folder_name = Path(segment_subfolder).name
    
    # Try exact match first (case-insensitive)
    transcript_filename = None
    for key, value in SEGMENT_TO_TRANSCRIPT_MAP.items():
        if key.lower() == segment_folder_name.lower():
            transcript_filename = value
            break
    
    if not transcript_filename:
        print(f"  Warning: No mapping found for segment folder: {segment_folder_name}")
        print(f"  Available mappings: {list(SEGMENT_TO_TRANSCRIPT_MAP.keys())[:5]}...")
        return None
    
    # Extract month from segment subfolder path
    month_folder = Path(segment_subfolder).parent.name.lower()
    month_name = None
    
    # Map month folder to cleaned transcript folder name
    for key, value in MONTH_FOLDER_MAP.items():
        if key in month_folder:
            month_name = value
            break
    
    # Fallback: try to extract month from folder name
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
    
    # Look in the corresponding month folder
    month_folder_path = Path(cleaned_transcript_dir) / f"{month_name}cleaned"
    if not month_folder_path.exists():
        print(f"  Warning: Month folder not found: {month_folder_path}")
        return None
    
    # Find the exact transcript file
    transcript_path = month_folder_path / transcript_filename
    
    if transcript_path.exists():
        print(f"  ✓ Matched: {segment_folder_name} -> {transcript_filename}")
        return str(transcript_path)
    else:
        # Try case-insensitive search
        for file in month_folder_path.glob("*"):
            if file.name.lower() == transcript_filename.lower():
                print(f"  ✓ Matched (case-insensitive): {segment_folder_name} -> {file.name}")
                return str(file)
        
        print(f"  ✗ Error: Transcript file not found: {transcript_path}")
        print(f"  Available files in {month_folder_path}:")
        for f in list(month_folder_path.glob("*"))[:5]:
            print(f"    - {f.name}")
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
    Build the strict matcher prompt exactly as specified.
    Format: segments with file names, then full transcript.
    """
    prompt_parts = [
        "You are a strict text-matcher. Do not guess or compensate.\n\n",
        "Goal:\n",
        "Match each small segment to the exact matching text in the large transcript.\n",
        "If a segment does NOT clearly exist in the transcript, skip it completely — do not guess.\n\n",
        "Output Format:\n",
        "Return ONLY CSV:\n",
        "file_name, matched_text\n\n",
        "Rules:\n",
        "• No explanations.\n",
        "• No commentary.\n",
        "• Only CSV rows with strong matches.\n\n",
        "Segments:\n"
    ]
    
    # Add each segment with its file name
    for segment_file in segment_files:
        file_name = Path(segment_file).stem  # Get filename without extension
        try:
            segment_text = load_transcript(segment_file)
            prompt_parts.append(f"--- {file_name} ---\n")
            prompt_parts.append(f"{segment_text}\n\n")
        except Exception as e:
            print(f"Warning: Could not read segment file {segment_file}: {e}")
            continue
    
    # Add full transcript
    prompt_parts.append("Full Transcript:\n")
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
        """Start Chrome browser and navigate to Gemini"""
        print("Starting Chrome browser...")
        service = Service(executable_path=self.chromedriver_path)
        options = webdriver.ChromeOptions()
        # Keep browser open for manual login
        options.add_experimental_option("detach", True)
        
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 30)
        
        print("Navigating to Gemini...")
        self.driver.get("https://gemini.google.com")
        print("Waiting for page to load...")
        time.sleep(5)  # Wait for page to fully load
        print("Proceeding automatically...")
    
    def find_input_element(self):
        """Find the Gemini input textarea element"""
        try:
            # Try multiple selectors for Gemini input
            selectors = [
                ".ql-editor[contenteditable='true']",
                "textarea[aria-label*='Enter a prompt']",
                "textarea[placeholder*='Enter a prompt']",
                "[contenteditable='true'][role='textbox']",
                "div[contenteditable='true']"
            ]
            
            for selector in selectors:
                try:
                    element = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    return element
                except TimeoutException:
                    continue
            
            raise NoSuchElementException("Could not find input element")
        except Exception as e:
            print(f"Error finding input element: {e}")
            raise
    
    def clear_input_box(self):
        """Clear the input box by selecting all and deleting"""
        try:
            input_element = self.find_input_element()
            input_element.click()
            time.sleep(0.5)
            # Select all and delete
            input_element.send_keys(Keys.CONTROL + "a")
            time.sleep(0.3)
            input_element.send_keys(Keys.DELETE)
            time.sleep(0.5)
        except Exception as e:
            print(f"Warning: Could not clear input box: {e}")
            # Try reloading page as fallback
            self.driver.refresh()
            time.sleep(3)
    
    def send_prompt_to_gemini(self, prompt_text: str):
        """
        Paste prompt into Gemini input textbox using pyperclip and press Enter.
        This method is more reliable for very long prompts.
        """
        try:
            # Clear previous input
            self.clear_input_box()
            
            # Wait for the input element to be present and clickable
            print("Waiting for input element...")
            input_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ql-editor[contenteditable='true']"))
            )
            print("Input element found.")
            
            # Use pyperclip to copy the entire text
            print("Copying prompt to clipboard...")
            pyperclip.copy(prompt_text)
            
            # Click to focus and then paste
            input_element.click()
            time.sleep(1)  # Small delay to ensure focus is established
            
            # Use Ctrl+V to paste the content
            print("Pasting long content via clipboard...")
            input_element.send_keys(Keys.CONTROL, 'v')
            
            # Wait a moment for the paste to register before hitting enter
            time.sleep(1)
            
            # Press Enter to send
            input_element.send_keys(Keys.ENTER)
            print("Prompt submitted. Waiting for response...")
            
        except Exception as e:
            print(f"Error sending prompt: {e}")
            raise
    
    def wait_for_response_complete(self, timeout: int = 300):
        """
        Wait until Gemini response is fully generated.
        Uses response container detection approach from reference code.
        """
        print("Waiting for Gemini response to complete...")
        
        try:
            # Wait for the response to start loading (waiting for response container element)
            # This selector might need adjustment, but it's a better starting point
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".response-container"))
                )
                print("Response container detected. Waiting for response completion...")
            except TimeoutException:
                # Fallback if the element selection is wrong, wait fixed time
                print("Could not find response container, waiting fixed time (30s) for server processing...")
                time.sleep(30)
                return
            
            # Additional wait for response to stabilize
            # Wait for response to stabilize (no changes for 3 seconds)
            last_text = ""
            stable_count = 0
            max_stable = 3  # 3 consecutive checks with no change
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Try to find response element
                    response_element = None
                    response_selectors = [
                        "div[class*='markdown']",
                        "div[data-markdown]",
                        ".response-text",
                        "[data-testid='response']",
                        ".response-container"
                    ]
                    
                    for selector in response_selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                response_element = elements[-1]  # Get most recent
                                break
                        except Exception:
                            continue
                    
                    if response_element:
                        current_text = response_element.text
                        if current_text == last_text and len(current_text) > 0:
                            stable_count += 1
                            if stable_count >= max_stable:
                                print("Response appears complete.")
                                time.sleep(2)  # Extra buffer
                                return
                        else:
                            stable_count = 0
                            last_text = current_text
                    
                    time.sleep(1)
                except Exception:
                    time.sleep(1)
            
            print("Timeout waiting for response, proceeding anyway...")
            # Final wait as fallback
            time.sleep(15)
            
        except Exception as e:
            print(f"Warning: Error waiting for response: {e}")
            # Fallback: wait a fixed time
            print("Using fallback: waiting 30 seconds...")
            time.sleep(30)
    
    def read_gemini_output(self) -> str:
        """
        Extract full text from Gemini response area
        """
        try:
            # Try multiple selectors for response
            response_selectors = [
                "div[class*='markdown']",
                "div[data-markdown]",
                ".response-text",
                "[data-testid='response']",
                "div.model-response-text"
            ]
            
            response_text = ""
            for selector in response_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        # Get the last one (most recent response)
                        response_text = elements[-1].text
                        if response_text:
                            break
                except Exception:
                    continue
            
            # Fallback: try to find any text that looks like a response
            if not response_text:
                try:
                    # Look for the main content area
                    main_content = self.driver.find_element(By.TAG_NAME, "main")
                    response_text = main_content.text
                except Exception:
                    # Last resort: get body text
                    response_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            return response_text.strip()
            
        except Exception as e:
            print(f"Error reading Gemini output: {e}")
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
    Parse Gemini response using regex to extract file_name and matched_text pairs.
    Pattern: --- file_name, matched_text
    """
    matches = []
    
    # Use the exact regex pattern specified
    pattern = r"---\s*(.*?)\s*,(.*)"
    
    # Find all matches
    for match in re.finditer(pattern, response_text, re.MULTILINE | re.DOTALL):
        file_name = match.group(1).strip()
        matched_text = match.group(2).strip()
        
        # Clean up file_name (remove any extra dashes or whitespace)
        file_name = re.sub(r'^---+', '', file_name).strip()
        
        if file_name and matched_text:
            matches.append((file_name, matched_text))
    
    # Alternative pattern: if CSV format without dashes
    if not matches:
        # Try CSV format: file_name, matched_text
        csv_pattern = r"^([^,]+?),\s*(.+)$"
        for line in response_text.split('\n'):
            match = re.match(csv_pattern, line.strip())
            if match:
                file_name = match.group(1).strip()
                matched_text = match.group(2).strip()
                if file_name and matched_text and not file_name.startswith('file_name'):
                    matches.append((file_name, matched_text))
    
    return matches


# ===================================================
# FILE SAVING
# ===================================================

def save_matched_outputs(matches: List[Tuple[str, str]], output_dir: str, segment_subfolder: str):
    """
    Save each matched_text to its own .txt file.
    Filename = file_name from Gemini output.
    """
    # Create output directory structure matching segment subfolder
    full_output_dir = Path(output_dir) / segment_subfolder
    full_output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_count = 0
    for file_name, matched_text in matches:
        # Sanitize filename
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', file_name)
        if not safe_filename.endswith('.txt'):
            safe_filename += '.txt'
        
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
    
    # Configuration
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
    
    # Initialize automation
    automator = GeminiAutomator(chromedriver_path=CHROMEDRIVER_PATH)
    
    try:
        # Start browser and wait for login
        automator.start_browser()
        
        # Find all segment files
        print("\nDiscovering segment files...")
        segment_files = find_segment_files(SEGMENT_TRANSCRIPT_DIR)
        print(f"Found {len(segment_files)} segment files")
        
        # Group by subfolder
        grouped_segments = group_segments_by_subfolder(segment_files)
        print(f"Found {len(grouped_segments)} segment subfolders\n")
        
        # Process each subfolder
        processed_count = 0
        for subfolder, segment_file_list in grouped_segments.items():
            processed_count += 1
            print(f"\n{'='*60}")
            print(f"Processing {processed_count}/{len(grouped_segments)}: {subfolder}")
            print(f"{'='*60}")
            
            try:
                # Find corresponding full transcript
                full_transcript_path = find_corresponding_full_transcript(
                    subfolder, CLEANED_TRANSCRIPT_DIR
                )
                
                if not full_transcript_path:
                    print(f"Warning: Could not find full transcript for {subfolder}")
                    print("Skipping this subfolder...")
                    continue
                
                print(f"Full transcript: {Path(full_transcript_path).name}")
                
                # Load full transcript
                try:
                    full_transcript = load_transcript(full_transcript_path)
                    print(f"Loaded full transcript ({len(full_transcript)} characters)")
                except Exception as e:
                    print(f"Error loading full transcript: {e}")
                    continue
                
                # Build prompt
                print(f"Building prompt for {len(segment_file_list)} segments...")
                prompt = build_strict_matcher_prompt(segment_file_list, full_transcript)
                print(f"Prompt length: {len(prompt)} characters")
                
                # Send to Gemini
                automator.send_prompt_to_gemini(prompt)
                
                # Wait for response
                automator.wait_for_response_complete()
                
                # Read response
                print("Reading Gemini response...")
                response = automator.read_gemini_output()
                
                if not response:
                    print("Warning: Empty response from Gemini")
                    continue
                
                print(f"Response length: {len(response)} characters")
                
                # Parse response
                print("Parsing response...")
                matches = parse_gemini_response(response)
                print(f"Found {len(matches)} matches")
                
                if matches:
                    # Save outputs
                    print("Saving matched outputs...")
                    saved = save_matched_outputs(matches, OUTPUT_DIR, subfolder)
                    print(f"Saved {saved} files")
                else:
                    print("No matches found in response")
                
                # Clear for next iteration
                print("Clearing input for next segment...")
                automator.clear_input_box()
                time.sleep(2)
                
            except Exception as e:
                print(f"Error processing {subfolder}: {e}")
                import traceback
                traceback.print_exc()
                print("Continuing with next subfolder...")
                continue
        
        print(f"\n{'='*60}")
        print("AUTOMATION COMPLETE!")
        print(f"Processed {processed_count} subfolders")
        print(f"{'='*60}")
        
    except KeyboardInterrupt:
        print("\n\nAutomation interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nClosing browser in 5 seconds...")
        time.sleep(5)
        automator.close()


if __name__ == "__main__":
    main()


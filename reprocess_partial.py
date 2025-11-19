"""
Reprocess only partially completed folders.
This script will only process folders that have some but not all files matched.
"""

import os
import re
import time
import zipfile
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import List, Tuple, Optional

import pyperclip

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# Import functions from main script
import sys
sys.path.insert(0, os.path.dirname(__file__))

from gemini_automator import (
    load_transcript,
    find_corresponding_full_transcript,
    build_strict_matcher_prompt,
    parse_gemini_response,
    save_matched_outputs,
    GeminiAutomator,
    SEGMENT_TO_TRANSCRIPT_MAP
)


# Partially processed folders to reprocess
PARTIAL_FOLDERS = [
    "November\\03 nov 17_Konk Prime News",
]


def main():
    BASE_DIR = r"D:\Gemini_automator"
    CLEANED_TRANSCRIPT_DIR = os.path.join(BASE_DIR, "Cleaned Transcript")
    SEGMENT_TRANSCRIPT_DIR = os.path.join(BASE_DIR, "Segment transcript")
    OUTPUT_DIR = os.path.join(BASE_DIR, "training")
    CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")
    
    print("="*60)
    print("REPROCESS PARTIAL FOLDERS")
    print("="*60)
    print(f"Folders to reprocess: {len(PARTIAL_FOLDERS)}")
    print("="*60)
    
    print("\n🤖 Initializing automator...")
    automator = GeminiAutomator(chromedriver_path=CHROMEDRIVER_PATH)
    
    try:
        print("\n" + "="*60)
        print("PHASE 1: BROWSER STARTUP")
        print("="*60)
        automator.start_browser()
        
        print("\n" + "="*60)
        print("PHASE 2: REPROCESSING PARTIAL FOLDERS")
        print("="*60)
        
        processed_count = 0
        
        for subfolder in PARTIAL_FOLDERS:
            processed_count += 1
            print(f"\n{'='*60}")
            print(f"📂 FOLDER {processed_count}/{len(PARTIAL_FOLDERS)}: {subfolder}")
            print(f"{'='*60}")
            
            try:
                # Get all segment files for this subfolder
                segment_dir = Path(SEGMENT_TRANSCRIPT_DIR) / subfolder
                
                if not segment_dir.exists():
                    print(f"   ⚠️  Folder not found: {segment_dir}")
                    continue
                
                segment_files = list(segment_dir.glob("*.txt"))
                print(f"   Found {len(segment_files)} segment files")
                
                if not segment_files:
                    print("   ⚠️  No segment files found, skipping")
                    continue
                
                print("\n🔗 Step 1: Finding corresponding full transcript...")
                full_transcript_path = find_corresponding_full_transcript(
                    subfolder, CLEANED_TRANSCRIPT_DIR
                )
                
                if not full_transcript_path:
                    print("   ❌ Could not find full transcript for this subfolder")
                    continue
                
                print(f"   ✓ Matched transcript: {Path(full_transcript_path).name}")
                
                print("\n📖 Step 2: Loading full transcript...")
                try:
                    full_transcript = load_transcript(full_transcript_path)
                    print(f"   ✓ Loaded {len(full_transcript)} characters")
                except Exception as e:
                    print(f"   ❌ Error loading transcript: {e}")
                    continue
                
                print(f"\n🔨 Step 3: Building prompt for {len(segment_files)} segments...")
                segment_file_paths = [str(f) for f in segment_files]
                prompt = build_strict_matcher_prompt(segment_file_paths, full_transcript)
                print(f"   ✓ Prompt built: {len(prompt)} characters")
                
                automator.send_prompt_to_gemini(prompt)
                
                print("\n⏳ Step 4: Waiting for Gemini response...")
                automator.wait_for_response_complete()
                
                print("\n📥 Step 5: Reading Gemini response...")
                response = automator.read_gemini_output()
                
                if not response:
                    print("   ⚠️ Warning: Empty response from Gemini")
                    continue
                
                print(f"   ✓ Response received: {len(response)} characters")
                
                print("\n🔍 Step 6: Parsing response...")
                matches = parse_gemini_response(response)
                print(f"   ✓ Found {len(matches)} matches")
                
                if matches:
                    print("\n💾 Step 7: Saving matched outputs...")
                    # Delete existing files first
                    output_folder = Path(OUTPUT_DIR) / subfolder
                    if output_folder.exists():
                        for old_file in output_folder.glob("*.txt"):
                            old_file.unlink()
                        print(f"   🗑️  Deleted old files")
                    
                    saved = save_matched_outputs(matches, OUTPUT_DIR, subfolder)
                    print(f"   ✅ Saved {saved} files successfully")
                else:
                    print("   ⚠️ No matches found in response")
                
                print("\n🔄 Step 8: Starting new chat for next prompt...")
                try:
                    new_chat_selectors = [
                        "button[aria-label*='New chat']",
                        "button[title*='New chat']",
                        "[aria-label='New chat']",
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
                        automator.clear_input_box()
                    
                except Exception as e:
                    automator.clear_input_box()
                
                time.sleep(2)
                print("   ✓ Ready for next folder")
                
            except Exception as e:
                print(f"\n❌ Error processing {subfolder}: {e}")
                import traceback
                traceback.print_exc()
                print("⏭️ Continuing with next folder...")
                continue
        
        print(f"\n{'='*60}")
        print("🎉 REPROCESSING COMPLETE!")
        print(f"{'='*60}")
        print(f"✅ Processed {processed_count} folders")
        print(f"{'='*60}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Reprocessing interrupted by user")
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

"""
Get list of not processed and partial folders for reprocessing.
"""

from pathlib import Path
from collections import defaultdict

def count_training_files():
    training_dir = Path(r"D:\Gemini_automator\training_through_bot")
    results = defaultdict(dict)
    
    for month_folder in training_dir.iterdir():
        if not month_folder.is_dir():
            continue
        month_name = month_folder.name
        for subfolder in month_folder.iterdir():
            if not subfolder.is_dir():
                continue
            txt_files = list(subfolder.glob("*.txt"))
            results[month_name][subfolder.name] = len(txt_files)
    
    return results

def count_segment_files():
    segment_dir = Path(r"D:\Gemini_automator\Segment transcript")
    results = defaultdict(dict)
    
    for month_folder in segment_dir.iterdir():
        if not month_folder.is_dir():
            continue
        month_name = month_folder.name
        for subfolder in month_folder.iterdir():
            if not subfolder.is_dir():
                continue
            txt_files = list(subfolder.glob("*.txt"))
            results[month_name][subfolder.name] = len(txt_files)
    
    return results

def main():
    training_counts = count_training_files()
    segment_counts = count_segment_files()
    
    all_months = set(training_counts.keys()) | set(segment_counts.keys())
    
    not_processed = []
    partial = []
    
    for month in sorted(all_months):
        segment_subfolders = set(segment_counts.get(month, {}).keys())
        
        for subfolder in sorted(segment_subfolders):
            segment_count = segment_counts.get(month, {}).get(subfolder, 0)
            training_count = training_counts.get(month, {}).get(subfolder, 0)
            
            if training_count == 0:
                not_processed.append(f"{month}\\{subfolder}")
            elif training_count < segment_count:
                partial.append(f"{month}\\{subfolder}")
    
    print("NOT PROCESSED FOLDERS:")
    print("="*60)
    for folder in not_processed:
        print(f'    "{folder}",')
    
    print(f"\nTotal not processed: {len(not_processed)}")
    
    print("\n\nPARTIAL FOLDERS:")
    print("="*60)
    for folder in partial:
        print(f'    "{folder}",')
    
    print(f"\nTotal partial: {len(partial)}")
    
    print(f"\n\nTOTAL TO REPROCESS: {len(not_processed) + len(partial)}")

if __name__ == "__main__":
    main()

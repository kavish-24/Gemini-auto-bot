"""
Delete files in training folders that don't match the segment naming pattern.
Keeps only files that end with _segment_###.txt
"""

from pathlib import Path
import re

def cleanup_non_segment_files(training_dir: str):
    """
    Delete files that don't match the segment pattern: *_segment_###.txt
    """
    training_path = Path(training_dir)
    
    # Pattern for valid segment files
    segment_pattern = re.compile(r'.*_segment_\d{3}\.txt$')
    
    deleted_count = 0
    kept_count = 0
    deleted_files = []  # Track all deleted files
    
    print("="*80)
    print("CLEANING UP NON-SEGMENT FILES")
    print("="*80)
    print(f"Scanning: {training_dir}")
    print("="*80)
    
    # Walk through all subdirectories
    for month_folder in training_path.iterdir():
        if not month_folder.is_dir():
            continue
        
        print(f"\n📁 {month_folder.name}")
        print("-" * 80)
        
        for subfolder in month_folder.iterdir():
            if not subfolder.is_dir():
                continue
            
            folder_deleted = 0
            folder_kept = 0
            
            # Check all .txt files in this subfolder
            for txt_file in subfolder.glob("*.txt"):
                if segment_pattern.match(txt_file.name):
                    # Valid segment file - keep it
                    folder_kept += 1
                    kept_count += 1
                else:
                    # Non-segment file - delete it
                    relative_path = f"{month_folder.name}/{subfolder.name}/{txt_file.name}"
                    deleted_files.append(relative_path)
                    print(f"  ❌ Deleting: {txt_file.name[:80]}...")
                    txt_file.unlink()
                    folder_deleted += 1
                    deleted_count += 1
            
            if folder_deleted > 0:
                print(f"  📂 {subfolder.name}: Deleted {folder_deleted} files, Kept {folder_kept} files")
    
    print("\n" + "="*80)
    print("CLEANUP SUMMARY")
    print("="*80)
    print(f"✅ Kept (valid segment files):     {kept_count}")
    print(f"❌ Deleted (non-segment files):    {deleted_count}")
    print("="*80)
    
    # Show detailed list of deleted files
    if deleted_files:
        print("\n" + "="*80)
        print("DELETED FILES LIST")
        print("="*80)
        for i, file_path in enumerate(deleted_files, 1):
            print(f"{i:3}. {file_path}")
        print("="*80)
    
    return deleted_files


if __name__ == "__main__":
    training_dir = r"D:\Gemini_automator\training_through_bot"
    
    print("\n⚠️  WARNING: This will permanently delete files that don't match *_segment_###.txt pattern!")
    print(f"Target directory: {training_dir}")
    
    response = input("\nContinue? (yes/no): ").strip().lower()
    
    if response == 'yes':
        cleanup_non_segment_files(training_dir)
        print("\n✅ Cleanup complete!")
    else:
        print("\n❌ Cleanup cancelled.")

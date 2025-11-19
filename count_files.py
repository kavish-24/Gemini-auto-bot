"""
Count and compare files between training output and segment transcript folders.
Shows how many files were processed vs how many segments exist.
"""

from pathlib import Path
from collections import defaultdict

def count_training_files():
    """Count files in training folder organized by month and subfolder"""
    training_dir = Path(r"D:\Gemini_automator\training_through_bot")
    
    results = defaultdict(dict)
    
    for month_folder in training_dir.iterdir():
        if not month_folder.is_dir():
            continue
        
        month_name = month_folder.name
        
        for subfolder in month_folder.iterdir():
            if not subfolder.is_dir():
                continue
            
            # Count .txt files in this subfolder
            txt_files = list(subfolder.glob("*.txt"))
            results[month_name][subfolder.name] = len(txt_files)
    
    return results


def count_segment_files():
    """Count files in segment transcript folder organized by month and subfolder"""
    segment_dir = Path(r"D:\Gemini_automator\Segment transcript")
    
    results = defaultdict(dict)
    
    for month_folder in segment_dir.iterdir():
        if not month_folder.is_dir():
            continue
        
        month_name = month_folder.name
        
        for subfolder in month_folder.iterdir():
            if not subfolder.is_dir():
                continue
            
            # Count .txt files in this subfolder
            txt_files = list(subfolder.glob("*.txt"))
            results[month_name][subfolder.name] = len(txt_files)
    
    return results


def main():
    print("="*80)
    print("FILE COUNT COMPARISON REPORT")
    print("="*80)
    
    print("\n📊 Counting files in training output...")
    training_counts = count_training_files()
    
    print("📊 Counting files in segment transcript...")
    segment_counts = count_segment_files()
    
    print("\n" + "="*80)
    print("DETAILED COMPARISON BY MONTH")
    print("="*80)
    
    total_training = 0
    total_segments = 0
    total_matched = 0
    
    # Get all months from both sources
    all_months = set(training_counts.keys()) | set(segment_counts.keys())
    
    for month in sorted(all_months):
        print(f"\n{'='*80}")
        print(f"📅 {month.upper()}")
        print(f"{'='*80}")
        
        month_training = 0
        month_segments = 0
        month_matched = 0
        
        # Get all subfolders for this month
        training_subfolders = set(training_counts.get(month, {}).keys())
        segment_subfolders = set(segment_counts.get(month, {}).keys())
        all_subfolders = training_subfolders | segment_subfolders
        
        print(f"\n{'Subfolder':<50} {'Segments':<12} {'Training':<12} {'Match %':<10} {'Status'}")
        print("-" * 90)
        
        for subfolder in sorted(all_subfolders):
            segment_count = segment_counts.get(month, {}).get(subfolder, 0)
            training_count = training_counts.get(month, {}).get(subfolder, 0)
            
            month_segments += segment_count
            month_training += training_count
            
            # Calculate match percentage
            if segment_count > 0:
                match_percent = (training_count / segment_count) * 100
                match_str = f"{match_percent:.1f}%"
            else:
                match_str = "N/A"
            
            # Determine status
            if training_count == 0:
                status = "❌ Not processed"
            elif training_count == segment_count:
                status = "✅ Complete"
                month_matched += training_count
            elif training_count < segment_count:
                status = f"⚠️  Partial ({training_count}/{segment_count})"
                month_matched += training_count
            else:
                status = f"⚠️  Extra files"
                month_matched += segment_count
            
            print(f"{subfolder:<50} {segment_count:<12} {training_count:<12} {match_str:<10} {status}")
        
        print("-" * 90)
        
        # Month summary with percentage
        if month_segments > 0:
            month_percent = (month_training / month_segments) * 100
            month_percent_str = f"{month_percent:.1f}%"
        else:
            month_percent_str = "N/A"
        
        print(f"{'MONTH TOTAL':<50} {month_segments:<12} {month_training:<12} {month_percent_str:<10}")
        print(f"Month Completion: {month_matched}/{month_segments} files matched")
        
        total_segments += month_segments
        total_training += month_training
        total_matched += month_matched
    
    print("\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)
    print(f"Total segment files:        {total_segments}")
    print(f"Total training files:       {total_training}")
    print(f"Successfully matched:       {total_matched}")
    print(f"Missing/incomplete:         {total_segments - total_matched}")
    
    if total_segments > 0:
        percentage = (total_matched / total_segments) * 100
        print(f"Completion percentage:      {percentage:.1f}%")
    
    print("="*80)
    
    # Summary by month
    print("\n" + "="*80)
    print("SUMMARY BY MONTH")
    print("="*80)
    print(f"\n{'Month':<20} {'Days/Folders':<15} {'Segments':<12} {'Training':<12} {'Complete'}")
    print("-" * 80)
    
    for month in sorted(all_months):
        training_subfolders = set(training_counts.get(month, {}).keys())
        segment_subfolders = set(segment_counts.get(month, {}).keys())
        
        num_folders = len(segment_subfolders)
        month_segments = sum(segment_counts.get(month, {}).values())
        month_training = sum(training_counts.get(month, {}).values())
        
        if month_segments > 0:
            percent = (month_training / month_segments) * 100
            complete_str = f"{percent:.1f}%"
        else:
            complete_str = "N/A"
        
        print(f"{month:<20} {num_folders:<15} {month_segments:<12} {month_training:<12} {complete_str}")
    
    print("-" * 80)
    print(f"{'TOTAL':<20} {len(set(k for v in segment_counts.values() for k in v.keys())):<15} {total_segments:<12} {total_training:<12} {(total_matched/total_segments*100 if total_segments > 0 else 0):.1f}%")
    print("="*80)
    
    # List incomplete folders
    print("\n" + "="*80)
    print("INCOMPLETE/NOT PROCESSED FOLDERS")
    print("="*80)
    
    incomplete = []
    not_processed = []
    
    for month in sorted(all_months):
        segment_subfolders = set(segment_counts.get(month, {}).keys())
        
        for subfolder in sorted(segment_subfolders):
            segment_count = segment_counts.get(month, {}).get(subfolder, 0)
            training_count = training_counts.get(month, {}).get(subfolder, 0)
            
            if training_count == 0:
                not_processed.append((month, subfolder, segment_count, training_count))
            elif training_count < segment_count:
                incomplete.append((month, subfolder, segment_count, training_count))
    
    if not_processed:
        print(f"\n❌ NOT PROCESSED ({len(not_processed)} folders):")
        print("-" * 80)
        print(f"{'Month':<20} {'Folder':<50} {'Segments'}")
        print("-" * 80)
        for month, folder, seg_count, _ in not_processed:
            print(f"{month:<20} {folder:<50} {seg_count}")
    else:
        print("\n✅ All folders have been processed!")
    
    if incomplete:
        # Filter to show only folders with missing > 1
        high_missing = [(month, folder, seg_count, train_count) for month, folder, seg_count, train_count in incomplete if (seg_count - train_count) > 1]
        
        if high_missing:
            print(f"\n⚠️  PARTIALLY PROCESSED WITH MISSING > 1 ({len(high_missing)} folders):")
            print("-" * 80)
            print(f"{'Month':<20} {'Folder':<50} {'Segments':<12} {'Training':<12} {'Missing'}")
            print("-" * 80)
            for month, folder, seg_count, train_count in high_missing:
                missing = seg_count - train_count
                print(f"{month:<20} {folder:<50} {seg_count:<12} {train_count:<12} {missing}")
        
        print(f"\n⚠️  ALL PARTIALLY PROCESSED ({len(incomplete)} folders):")
        print("-" * 80)
        print(f"{'Month':<20} {'Folder':<50} {'Segments':<12} {'Training':<12} {'Missing'}")
        print("-" * 80)
        for month, folder, seg_count, train_count in incomplete:
            missing = seg_count - train_count
            print(f"{month:<20} {folder:<50} {seg_count:<12} {train_count:<12} {missing}")
    else:
        print("\n✅ All processed folders are complete!")
    
    print("="*80)


if __name__ == "__main__":
    main()

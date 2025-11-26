#!/usr/bin/env python3
"""
KSAS - Star Database Merge Utility

Combina múltiples archivos analyzed_stars.json de diferentes máquinas.
Uso: python merge_databases.py file1.json file2.json file3.json -o merged_output.json
"""

import json
import argparse
import os
from datetime import datetime

def merge_star_databases(files, output_file=None):
    """
    Merge multiple analyzed_stars.json files.
    
    Args:
        files: List of JSON file paths
        output_file: Output file path (default: analyzed_stars_merged.json)
    
    Returns:
        Set of unique TIC IDs
    """
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"analyzed_stars_merged_{timestamp}.json"
    
    all_stars = set()
    stats = {}
    
    print("="*60)
    print("KSAS - Database Merge Utility")
    print("="*60)
    print()
    
    # Load all files
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"⚠️  Warning: File not found: {file_path}")
            continue
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                stars = set(data.get('analyzed', []))
                
                print(f"📁 {os.path.basename(file_path)}")
                print(f"   Stars: {len(stars)}")
                
                # Track stats
                stats[file_path] = len(stars)
                
                # Add to combined set
                before = len(all_stars)
                all_stars.update(stars)
                added = len(all_stars) - before
                
                print(f"   New unique stars added: {added}")
                print()
                
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            print()
    
    # Summary
    print("="*60)
    print("MERGE SUMMARY")
    print("="*60)
    print(f"Files processed: {len(stats)}")
    print(f"Total unique stars: {len(all_stars)}")
    print()
    
    # Calculate overlap
    total_all_files = sum(stats.values())
    duplicates = total_all_files - len(all_stars)
    if duplicates > 0:
        overlap_pct = (duplicates / total_all_files) * 100
        print(f"Duplicates removed: {duplicates} ({overlap_pct:.1f}% overlap)")
    else:
        print("No duplicates found (0% overlap)")
    
    print()
    print(f"💾 Saving to: {output_file}")
    
    # Save merged file
    try:
        with open(output_file, 'w') as f:
            json.dump({
                'analyzed': sorted(list(all_stars)),
                'merged_from': list(stats.keys()),
                'merge_date': datetime.now().isoformat(),
                'total_unique': len(all_stars)
            }, f, indent=2)
        
        print("✅ Merge complete!")
        print()
        print("="*60)
        
        return all_stars
        
    except Exception as e:
        print(f"❌ Error saving merged file: {e}")
        return None

def interactive_mode():
    """Interactive merge mode."""
    print("="*60)
    print("KSAS - Interactive Database Merge")
    print("="*60)
    print()
    print("Enter JSON file paths (one per line)")
    print("Type 'done' when finished")
    print()
    
    files = []
    while True:
        path = input("File path (or 'done'): ").strip()
        if path.lower() == 'done':
            break
        if path and os.path.exists(path):
            files.append(path)
            print(f"  ✓ Added: {path}")
        elif path:
            print(f"  ⚠️  File not found: {path}")
    
    if not files:
        print("\n❌ No files selected. Exiting.")
        return
    
    print()
    output = input("Output file (default: auto-generated): ").strip()
    output = output if output else None
    
    print()
    merge_star_databases(files, output)

def main():
    parser = argparse.ArgumentParser(
        description="Merge multiple KSAS analyzed_stars.json databases"
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='JSON files to merge'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file name (default: analyzed_stars_merged_TIMESTAMP.json)'
    )
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Interactive mode'
    )
    
    args = parser.parse_args()
    
    if args.interactive or not args.files:
        interactive_mode()
    else:
        merge_star_databases(args.files, args.output)

if __name__ == "__main__":
    main()

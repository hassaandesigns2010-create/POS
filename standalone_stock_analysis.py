#!/usr/bin/env python3
"""
Standalone Stock Analysis Tool - Analyzes backup files without database connection
"""

import os
import re
from datetime import datetime
from pathlib import Path

def analyze_backups_only():
    """Analyze backup files without database connection"""
    
    print("=" * 80)
    print("STANDALONE STOCK ANALYSIS - BACKUP FILES ONLY")
    print("=" * 80)
    
    backup_dir = Path("C:/Users/pc/Documents/backups")
    backup_files = sorted(backup_dir.glob("pos_backup_*.sql"))
    
    if not backup_files:
        print("No backup files found!")
        return
    
    print(f"Found {len(backup_files)} backup files")
    print()
    
    backup_analysis = {}
    
    for backup_file in backup_files:
        print(f"Analyzing: {backup_file.name}")
        
        # Extract date from filename
        date_match = re.search(r'(\d{8})_(\d{6})', backup_file.name)
        if date_match:
            date_str = f"{date_match.group(1)} {date_match.group(2)}"
            backup_date = datetime.strptime(date_str, "%Y%m%d %H%M%S")
        else:
            backup_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
        
        try:
            with open(backup_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Count products and stock
            product_count = content.count('COPY public.products')
            
            # Simple stock extraction (basic approach)
            stock_pattern = r'\t(\d+\.?\d*)\t'
            stock_matches = re.findall(stock_pattern, content)
            
            total_stock = 0
            for match in stock_matches[:1000]:  # Limit to avoid memory issues
                try:
                    total_stock += float(match)
                except:
                    pass
            
            backup_analysis[backup_file.name] = {
                'date': backup_date,
                'product_count': product_count,
                'estimated_stock': total_stock,
                'file_size': backup_file.stat().st_size
            }
            
            print(f"  Date: {backup_date}")
            print(f"  Products: ~{product_count}")
            print(f"  Estimated Stock: {total_stock:,.0f}")
            print()
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # Show timeline
    print("BACKUP TIMELINE:")
    print("-" * 50)
    
    for name, data in sorted(backup_analysis.items(), key=lambda x: x[1]['date']):
        print(f"{data['date']}: {name}")
        print(f"  Products: {data['product_count']}, Stock: {data['estimated_stock']:,.0f}")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    analyze_backups_only()

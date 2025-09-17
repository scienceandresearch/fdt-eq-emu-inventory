#!/usr/bin/env python3
"""
Test script for the enhanced EQ inventory monitor
"""

import sys
import os

# Add the directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_inv_monitor import EQInventoryMonitor
    
    print("Testing Enhanced EQ Inventory Monitor...")
    print("="*50)
    
    # Test loading inventory from current directory
    inventory = EQInventoryMonitor()
    
    if inventory.items_df.empty:
        print("❌ No data loaded")
        sys.exit(1)
    
    print("\n✓ Data loaded successfully!")
    
    # Test search functionality
    print("\n🔍 Testing search for 'Earring':")
    results = inventory.search_items("Earring")
    print(f"Found {len(results)} items")
    if not results.empty:
        print(results.head())
    
    print("\n🔍 Testing search for 'Prismatic':")
    results = inventory.search_items("Prismatic")
    print(f"Found {len(results)} items")
    if not results.empty:
        print(results.head())
    
    print("\n📊 Character Info:")
    print(inventory.characters_info)
    
    print("\n✅ All tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()

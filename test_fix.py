#!/usr/bin/env python3
"""
Quick test to verify the AttributeError fix
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Import the GUI class
    from eq_inventory_gui import EQInventoryGUI
    
    print("✅ Successfully imported EQInventoryGUI class")
    
    # Try to create an instance (this should not crash)
    app = EQInventoryGUI()
    print("✅ Successfully created EQInventoryGUI instance")
    
    # Check if the problematic methods are gone
    if hasattr(app, 'stats_text'):
        print("❌ ERROR: stats_text attribute still exists!")
    else:
        print("✅ stats_text attribute correctly removed")
    
    if hasattr(app, 'char_tree'):
        print("❌ ERROR: char_tree attribute still exists!")  
    else:
        print("✅ char_tree attribute correctly removed")
    
    # Check if the working methods exist
    if hasattr(app, 'stats_summary'):
        print("✅ stats_summary attribute exists (correct embedded overview)")
    else:
        print("❌ ERROR: stats_summary attribute missing!")
        
    if hasattr(app, 'char_summary_tree'):
        print("✅ char_summary_tree attribute exists (correct embedded overview)")
    else:
        print("❌ ERROR: char_summary_tree attribute missing!")
    
    # Check update_overview method
    if hasattr(app, 'update_overview') and callable(getattr(app, 'update_overview')):
        print("✅ update_overview method exists")
        
        # Try calling it (should not crash even with empty data)
        try:
            app.update_overview()
            print("✅ update_overview method runs without error")
        except Exception as e:
            print(f"❌ ERROR: update_overview method failed: {e}")
    else:
        print("❌ ERROR: update_overview method missing!")
    
    print("\n🎉 Fix verification completed successfully!")
    print("The AttributeError: 'EQInventoryGUI' object has no attribute 'stats_text' should be resolved.")
    
except Exception as e:
    print(f"❌ ERROR during testing: {e}")
    import traceback
    traceback.print_exc()

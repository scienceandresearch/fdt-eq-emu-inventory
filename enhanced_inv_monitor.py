import pandas as pd
from datetime import datetime
import sys
import os
import glob
import re
from functools import reduce
from pandasgui import show
from typing import Optional, List, Dict
import argparse


class EQInventoryMonitor:
    def __init__(self, data_directory: str = None):
        """
        Initialize the EverQuest inventory monitor.
        
        Args:
            data_directory: Path to directory containing inventory files. 
                          If None, uses current directory.
        """
        if data_directory is None:
            data_directory = os.getcwd()
            
        if not os.path.exists(data_directory):
            raise ValueError(f"Data directory does not exist: {data_directory}")
            
        self.data_dir = data_directory
        self.items_df = self.load_all_inventory_files()
        
        if self.items_df.empty:
            print("Warning: No inventory data found!")
            return
            
        self.characters_info = self.get_character_info()
        print(f"\n{'='*60}")
        print(f"INVENTORY LOADED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"Characters found: {len(self.characters_info)}")
        print(f"Total items loaded: {len(self.items_df):,}")
        print(f"Non-empty items: {len(self.items_df[self.items_df['Name'] != 'Empty']):,}")
        print(f"{'='*60}\n")

    def load_all_inventory_files(self) -> pd.DataFrame:
        """
        Load and process all *-Inventory.txt files from the data directory.
        
        Returns:
            DataFrame containing consolidated inventory data from all characters
        """
        # Look for inventory files in the data directory
        pattern = os.path.join(self.data_dir, "*-Inventory.txt")
        inventory_files = glob.glob(pattern)
        
        if not inventory_files:
            print(f"No *-Inventory.txt files found in {self.data_dir}")
            return pd.DataFrame()
        
        result_list = []
        print(f"Found {len(inventory_files)} inventory files:")

        for file_path in inventory_files:
            try:
                file_name = os.path.basename(file_path)
                modified_epoch = os.path.getmtime(file_path)
                modified_ts = datetime.fromtimestamp(modified_epoch)
                
                # Extract character name from filename (everything before first hyphen)
                match = re.match(r"(.+?)-", file_name)
                if not match:
                    print(f"  ⚠️  Warning: Could not parse character name from {file_name}")
                    continue
                    
                char_name = match.group(1)
                
                # Read inventory file
                df = pd.read_csv(file_path, sep='\t')
                
                # Add metadata columns
                df.insert(0, 'Character', char_name)
                df['UpdatedAt'] = modified_ts
                df['FileName'] = file_name
                
                # Handle shared bank items - mark them as SHARED-BANK character
                df['Character'] = df['Location'].apply(
                    lambda loc: 'SHARED-BANK' if str(loc).startswith('SharedBank') else char_name
                )
                
                # Add derived columns for better searching
                df['ItemType'] = df['Location'].apply(self._categorize_location)
                df['IsEquipped'] = df['Location'].apply(lambda x: not any(word in str(x) for word in ['Slot', 'Bank', 'Bag']))
                df['IsEmpty'] = df['Name'] == 'Empty'
                
                result_list.append(df)
                item_count = len(df)
                non_empty_count = len(df[df['Name'] != 'Empty'])
                print(f"  ✓  {char_name}: {item_count:,} slots ({non_empty_count:,} items)")
                
            except Exception as e:
                print(f"  ❌  Error processing {file_name}: {e}")
                continue
        
        if not result_list:
            return pd.DataFrame()
            
        # Combine all dataframes
        final_df = pd.concat(result_list, axis=0, ignore_index=True)
        
        # Remove duplicates based on all columns except UpdatedAt and FileName
        unique_cols = [col for col in final_df.columns if col not in ['UpdatedAt', 'FileName']]
        initial_count = len(final_df)
        final_df = final_df.drop_duplicates(subset=unique_cols)
        dedup_count = len(final_df)
        
        if initial_count != dedup_count:
            print(f"  ℹ️  Removed {initial_count - dedup_count:,} duplicate entries")
        
        return final_df

    def _categorize_location(self, location: str) -> str:
        """Categorize item location for easier filtering."""
        location = str(location).lower()
        
        if 'bank' in location:
            return 'Bank'
        elif 'bag' in location or 'slot' in location:
            return 'Inventory'
        elif location in ['charm', 'ear', 'head', 'face', 'neck', 'shoulders', 'arms', 'wrist', 
                         'hands', 'finger', 'chest', 'legs', 'feet', 'waist', 'primary', 
                         'secondary', 'range', 'ammo']:
            return 'Equipped'
        else:
            return 'Other'

    def get_character_info(self) -> pd.DataFrame:
        """Get summary information about each character."""
        if self.items_df.empty:
            return pd.DataFrame()
            
        summary = self.items_df.groupby('Character').agg({
            'Name': lambda x: len(x[x != 'Empty']),  # Count non-empty items
            'UpdatedAt': 'max',
            'FileName': 'first'
        }).rename(columns={'Name': 'ItemCount'}).reset_index()
        
        summary['LastUpdated'] = summary['UpdatedAt'].dt.strftime('%Y-%m-%d %H:%M')
        summary = summary.drop('UpdatedAt', axis=1)
        
        return summary.sort_values('ItemCount', ascending=False)

    def search_items(self, search_term: str, character: str = None, 
                    exact_match: bool = False, item_type: str = None) -> pd.DataFrame:
        """
        Search for items across all characters with flexible filtering.
        
        Args:
            search_term: Item name or partial name to search for
            character: Specific character to search (None for all characters)
            exact_match: If True, search for exact name matches only
            item_type: Filter by item type ('Equipped', 'Inventory', 'Bank')
            
        Returns:
            DataFrame containing matching items
        """
        df = self.items_df[self.items_df['IsEmpty'] == False].copy()  # Exclude empty slots
        
        # Filter by search term
        if exact_match:
            df = df[df['Name'].str.lower() == search_term.lower()]
        else:
            df = df[df['Name'].str.contains(search_term, case=False, na=False)]
        
        # Filter by character
        if character:
            df = df[df['Character'].str.lower() == character.lower()]
            
        # Filter by item type
        if item_type:
            df = df[df['ItemType'].str.lower() == item_type.lower()]
        
        return df[['Character', 'Name', 'Location', 'ItemType', 'Count', 'ID']].sort_values(['Character', 'Name'])

    def find_duplicates(self, min_count: int = 2) -> pd.DataFrame:
        """Find items that appear multiple times across characters."""
        item_counts = self.items_df[self.items_df['IsEmpty'] == False].groupby(['Name', 'ID']).agg({
            'Character': 'count',
            'Count': 'sum'
        }).rename(columns={'Character': 'CharacterCount'}).reset_index()
        
        duplicates = item_counts[item_counts['CharacterCount'] >= min_count].sort_values('CharacterCount', ascending=False)
        
        if duplicates.empty:
            return duplicates
            
        # Get details for duplicate items
        result_list = []
        for _, row in duplicates.iterrows():
            item_details = self.items_df[
                (self.items_df['Name'] == row['Name']) & 
                (self.items_df['ID'] == row['ID']) &
                (self.items_df['IsEmpty'] == False)
            ][['Character', 'Name', 'Location', 'Count']].copy()
            item_details['TotalFound'] = row['CharacterCount']
            result_list.append(item_details)
            
        return pd.concat(result_list, ignore_index=True)

    def get_character_summary(self, character_name: str) -> Dict:
        """Get detailed summary for a specific character."""
        char_data = self.items_df[
            (self.items_df['Character'].str.lower() == character_name.lower()) &
            (self.items_df['IsEmpty'] == False)
        ]
        
        if char_data.empty:
            return {'error': f"Character '{character_name}' not found"}
            
        summary = {
            'character': character_name,
            'total_items': len(char_data),
            'equipped_items': len(char_data[char_data['ItemType'] == 'Equipped']),
            'inventory_items': len(char_data[char_data['ItemType'] == 'Inventory']),
            'bank_items': len(char_data[char_data['ItemType'] == 'Bank']),
            'last_updated': char_data['UpdatedAt'].max().strftime('%Y-%m-%d %H:%M'),
            'unique_items': char_data['Name'].nunique()
        }
        
        return summary

    def export_search_results(self, search_results: pd.DataFrame, filename: str = None):
        """Export search results to CSV."""
        if search_results.empty:
            print("No results to export.")
            return
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eq_search_results_{timestamp}.csv"
            
        search_results.to_csv(filename, index=False)
        print(f"✓ Search results exported to {filename}")

    def interactive_search(self):
        """Interactive search interface."""
        print("\n" + "="*60)
        print("🔍 INTERACTIVE ITEM SEARCH")
        print("="*60)
        
        while True:
            print("\nSearch Options:")
            print("1. Search by item name")
            print("2. View character inventory")
            print("3. Find duplicate items")
            print("4. Character summary")
            print("5. Export current results")
            print("0. Back to main menu")
            
            choice = input("\nChoice: ").strip()
            
            if choice == "1":
                search_term = input("Enter item name (partial match): ").strip()
                if not search_term:
                    continue
                    
                character = input("Character name (Enter for all): ").strip() or None
                item_type = input("Item type (Equipped/Inventory/Bank, Enter for all): ").strip() or None
                
                results = self.search_items(search_term, character, item_type=item_type)
                
                if not results.empty:
                    print(f"\n✓ Found {len(results)} items:")
                    print(results.to_string(index=False))
                    self.last_search_results = results
                else:
                    print("❌ No items found.")
                    
            elif choice == "2":
                char_name = input("Enter character name: ").strip()
                char_items = self.items_df[
                    (self.items_df['Character'].str.lower() == char_name.lower()) &
                    (self.items_df['IsEmpty'] == False)
                ][['Name', 'Location', 'ItemType', 'Count']].sort_values(['ItemType', 'Name'])
                
                if not char_items.empty:
                    summary = self.get_character_summary(char_name)
                    print(f"\n📦 {char_name}'s Inventory:")
                    print(f"Total Items: {summary['total_items']} | Equipped: {summary['equipped_items']} | " + 
                          f"Inventory: {summary['inventory_items']} | Bank: {summary['bank_items']}")
                    print("-" * 80)
                    print(char_items.to_string(index=False))
                else:
                    print("❌ Character not found or has no items.")
                    
            elif choice == "3":
                min_count = input("Minimum duplicate count (default 2): ").strip()
                try:
                    min_count = int(min_count) if min_count else 2
                except ValueError:
                    min_count = 2
                    
                duplicates = self.find_duplicates(min_count)
                if not duplicates.empty:
                    print(f"\n🔄 Items appearing {min_count}+ times:")
                    print(duplicates.to_string(index=False))
                    self.last_search_results = duplicates
                else:
                    print("❌ No duplicate items found.")
                    
            elif choice == "4":
                char_name = input("Enter character name: ").strip()
                summary = self.get_character_summary(char_name)
                if 'error' not in summary:
                    print(f"\n📊 Character Summary: {summary['character']}")
                    print(f"  Total Items: {summary['total_items']}")
                    print(f"  Equipped: {summary['equipped_items']}")
                    print(f"  Inventory: {summary['inventory_items']}")  
                    print(f"  Bank: {summary['bank_items']}")
                    print(f"  Unique Items: {summary['unique_items']}")
                    print(f"  Last Updated: {summary['last_updated']}")
                else:
                    print(f"❌ {summary['error']}")
                    
            elif choice == "5":
                if hasattr(self, 'last_search_results') and not self.last_search_results.empty:
                    filename = input("Filename (Enter for auto-generated): ").strip() or None
                    self.export_search_results(self.last_search_results, filename)
                else:
                    print("❌ No search results to export. Run a search first.")
                    
            elif choice == "0":
                break
            else:
                print("❌ Invalid choice.")

    def show_gui(self):
        """Display inventory in PandasGUI."""
        if not self.items_df.empty:
            # Show only non-empty items in GUI for better performance
            display_df = self.items_df[self.items_df['IsEmpty'] == False].copy()
            show(display_df, settings={'block': True})
        else:
            print("No data to display")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='EverQuest Inventory Monitor')
    parser.add_argument('-d', '--directory', help='Directory containing inventory files (default: current directory)')
    parser.add_argument('-g', '--gui', action='store_true', help='Launch GUI immediately')
    parser.add_argument('-s', '--search', help='Search for item by name')
    
    args = parser.parse_args()
    
    try:
        inventory = EQInventoryMonitor(args.directory)
        
        if inventory.items_df.empty:
            print("❌ No inventory data found. Make sure *-Inventory.txt files are in the directory.")
            return
            
        # Show character overview
        print("📋 Character Overview:")
        print(inventory.characters_info.to_string(index=False))
        
        if args.gui:
            inventory.show_gui()
            return
            
        if args.search:
            results = inventory.search_items(args.search)
            if not results.empty:
                print(f"\n🔍 Search results for '{args.search}':")
                print(results.to_string(index=False))
            else:
                print(f"❌ No items found matching '{args.search}'")
            return
        
        # Interactive menu
        while True:
            print(f"\n{'='*60}")
            print("🎮 EVERQUEST INVENTORY MANAGER")
            print("="*60)
            print("1. Interactive Search")
            print("2. View PandasGUI")
            print("3. Show character list")
            print("4. Quick item search")
            print("5. Export all data")
            print("0. Exit")
            
            choice = input("\nChoice: ").strip()
            
            if choice == "1":
                inventory.interactive_search()
            elif choice == "2":
                inventory.show_gui()
            elif choice == "3":
                print("\n📋 Character Overview:")
                print(inventory.characters_info.to_string(index=False))
            elif choice == "4":
                search_term = input("Enter item name: ").strip()
                if search_term:
                    results = inventory.search_items(search_term)
                    if not results.empty:
                        print(results.to_string(index=False))
                    else:
                        print("❌ No items found.")
            elif choice == "5":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"eq_full_inventory_{timestamp}.csv"
                inventory.items_df.to_csv(filename, index=False)
                print(f"✓ Full inventory exported to {filename}")
            elif choice == "0":
                break
            else:
                print("❌ Invalid choice.")
                
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

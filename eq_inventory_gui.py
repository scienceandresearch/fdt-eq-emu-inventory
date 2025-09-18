import pandas as pd
from datetime import datetime
import os
import glob
import re
from functools import reduce
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import threading
from typing import Optional, List, Dict
from signet_of_might_data import SignetOfMightQuest


class EQInventoryGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FDT EQ Emu Inventory Parser")
        self.root.geometry("1400x850")
        self.root.minsize(1200, 650)  # Set minimum window size
        self.root.configure(bg='#2c3e50')
        
        # Data storage
        self.items_df = pd.DataFrame()
        self.last_search_results = pd.DataFrame()
        self.data_dir = ""
        
        # Configure style with enhanced appearance
        style = ttk.Style()
        style.theme_use('clam')
        
        # Enhanced color scheme
        style.configure('Title.TLabel', 
                       font=('Arial', 18, 'bold'), 
                       background='#2c3e50', 
                       foreground='#ecf0f1')
        
        style.configure('Header.TLabel', 
                       font=('Arial', 12, 'bold'), 
                       background='#34495e', 
                       foreground='#ecf0f1')
        
        style.configure('Custom.TFrame', 
                       background='#34495e',
                       relief='raised',
                       borderwidth=1)
        
        # Enhance button appearance
        style.configure('Accent.TButton',
                       font=('Arial', 10, 'bold'),
                       padding=(10, 5))
        
        # Style the notebook tabs
        style.configure('TNotebook.Tab',
                       padding=[15, 8],
                       font=('Arial', 10, 'bold'))
        
        self.create_widgets()
        self.center_window()
        
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main title with enhanced styling
        title_frame = ttk.Frame(self.root, style='Custom.TFrame')
        title_frame.pack(fill='x', padx=10, pady=8)
        
        title_label = ttk.Label(title_frame, text="🎮 FDT EQ Emu Inventory Parser", style='Title.TLabel')
        title_label.pack(pady=8)
        
        # Subtitle
        subtitle_label = ttk.Label(title_frame, text="Find DnK's Tulwar - Advanced inventory search for EverQuest Emulator servers", 
                                  font=('Arial', 10), background='#34495e', foreground='#95a5a6')
        subtitle_label.pack()
        
        # Directory selection with enhanced styling
        dir_frame = ttk.LabelFrame(self.root, text="📁 Inventory Files Location")
        dir_frame.pack(fill='x', padx=10, pady=8)
        
        dir_inner_frame = ttk.Frame(dir_frame)
        dir_inner_frame.pack(fill='x', padx=10, pady=8)
        
        ttk.Label(dir_inner_frame, text="Directory:", font=('Arial', 10, 'bold')).pack(side='left')
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(dir_inner_frame, textvariable=self.dir_var, width=60, font=('Arial', 10))
        self.dir_entry.pack(side='left', padx=8, fill='x', expand=True)
        
        ttk.Button(dir_inner_frame, text="Browse", command=self.browse_directory, 
                  style='Accent.TButton').pack(side='right', padx=5)
        ttk.Button(dir_inner_frame, text="Load Inventory", command=self.load_inventory,
                  style='Accent.TButton').pack(side='right')
        
        # Status bar
        self.status_var = tk.StringVar(value="Select directory and load inventory files...")
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill='x', padx=10, pady=2)
        
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side='left')
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(side='right', padx=10)
        
        # Main content area with notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Search Tab (now includes overview)
        self.create_search_tab()
        
        # Results Tab
        self.create_results_tab()
        
        # Signet of Might Quest Tab
        self.create_signet_quest_tab()
        
        # Set initial directory to current directory and auto-load
        initial_dir = os.getcwd()
        self.dir_var.set(initial_dir)
        
        # Auto-load inventory files from current directory if any exist
        self.auto_load_initial_inventory()
        
    def create_search_tab(self):
        """Create the search interface tab with optimized layout."""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="🏠 Dashboard")
        
        # Main container
        main_container = ttk.Frame(search_frame)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Top row - Search Controls (full width)
        search_controls = ttk.LabelFrame(main_container, text="🔍 Search & Actions")
        search_controls.pack(fill='x', pady=(0,8))
        
        controls_inner = ttk.Frame(search_controls)
        controls_inner.pack(fill='x', padx=8, pady=5)
        
        # Search controls in a single row
        search_row = ttk.Frame(controls_inner)
        search_row.pack(fill='x', pady=2)
        
        # Item search
        ttk.Label(search_row, text="Item:").pack(side='left')
        self.search_term_var = tk.StringVar()
        search_entry = ttk.Entry(search_row, textvariable=self.search_term_var, width=25)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<Return>', lambda e: self.perform_search())
        
        # Character filter
        ttk.Label(search_row, text="Character:").pack(side='left', padx=(15,5))
        self.character_var = tk.StringVar()
        self.character_combo = ttk.Combobox(search_row, textvariable=self.character_var, width=15, state='readonly')
        self.character_combo.pack(side='left', padx=5)
        
        # Item type filter
        ttk.Label(search_row, text="Type:").pack(side='left', padx=(15,5))
        self.item_type_var = tk.StringVar()
        self.item_type_combo = ttk.Combobox(search_row, textvariable=self.item_type_var, width=12, state='readonly')
        self.item_type_combo['values'] = ('All', 'Equipped', 'Inventory', 'Bank')
        self.item_type_combo.set('All')
        self.item_type_combo.pack(side='left', padx=5)
        
        # Exact match checkbox
        self.exact_match_var = tk.BooleanVar()
        ttk.Checkbutton(search_row, text="Exact Match", variable=self.exact_match_var).pack(side='left', padx=(15,5))
        
        # Action buttons row
        actions_row = ttk.Frame(controls_inner)
        actions_row.pack(fill='x', pady=5)
        
        # Left side buttons
        left_buttons = ttk.Frame(actions_row)
        left_buttons.pack(side='left')
        
        ttk.Button(left_buttons, text="🔍 Search", command=self.perform_search).pack(side='left', padx=2)
        ttk.Button(left_buttons, text="🔄 Find Duplicates", command=self.find_duplicates).pack(side='left', padx=2)
        ttk.Button(left_buttons, text="📊 Character Summary", command=self.show_character_summary).pack(side='left', padx=2)
        
        # Right side buttons
        right_buttons = ttk.Frame(actions_row)
        right_buttons.pack(side='right')
        
        ttk.Button(right_buttons, text="💾 Export Results", command=self.export_results).pack(side='left', padx=2)
        ttk.Button(right_buttons, text="🗑️ Clear", command=self.clear_search).pack(side='left', padx=2)
        
        # Bottom section with 3 columns
        bottom_container = ttk.Frame(main_container)
        bottom_container.pack(fill='both', expand=True)
        
        # Left Column - Overview (expanded)
        left_column = ttk.Frame(bottom_container)
        left_column.pack(side='left', fill='both', expand=False, padx=(0,5))
        
        # Statistics (expanded)
        stats_frame = ttk.LabelFrame(left_column, text="📊 Statistics")
        stats_frame.pack(fill='x', pady=(0,5))
        
        self.stats_summary = tk.Text(stats_frame, height=8, width=40, wrap='word', 
                                    font=('Consolas', 9), state='disabled')
        self.stats_summary.pack(fill='both', expand=True, padx=8, pady=5)
        
        # Characters (expanded)
        chars_frame = ttk.LabelFrame(left_column, text="👥 Characters")
        chars_frame.pack(fill='both', expand=True)
        
        char_columns = ('Character', 'Items', 'Updated')
        self.char_summary_tree = ttk.Treeview(chars_frame, columns=char_columns, show='headings')
        
        # Configure columns
        for col in char_columns:
            self.char_summary_tree.heading(col, text=col)
            if col == 'Character':
                self.char_summary_tree.column(col, width=120)
            elif col == 'Items':
                self.char_summary_tree.column(col, width=70)
            else:
                self.char_summary_tree.column(col, width=100)
        
        # Add scrollbar for character list
        char_scrollbar = ttk.Scrollbar(chars_frame, orient='vertical', command=self.char_summary_tree.yview)
        self.char_summary_tree.configure(yscrollcommand=char_scrollbar.set)
        
        self.char_summary_tree.pack(side='left', fill='both', expand=True, padx=8, pady=5)
        char_scrollbar.pack(side='right', fill='y', padx=(0,8), pady=5)
        
        self.char_summary_tree.bind('<Double-1>', self.on_character_summary_double_click)
        
        # Middle Column - Equipment & Weapons
        middle_column = ttk.Frame(bottom_container)
        middle_column.pack(side='left', fill='both', expand=True, padx=5)
        
        # Equipment Slots
        equip_frame = ttk.LabelFrame(middle_column, text="⚔️ Equipment Slots")
        equip_frame.pack(fill='x', pady=(0,5))
        
        equip_inner = ttk.Frame(equip_frame)
        equip_inner.pack(fill='both', expand=True, padx=5, pady=5)
        
        equipment_searches = [
            ("Charm", "Charm"), ("Earrings", "Earring"), ("Head/Helm", "Helm|Head"), ("Face/Mask", "Face|Mask"),
            ("Neck", "Neck|Necklace"), ("Shoulders", "Shoulder|Shawl|Mantle"), ("Arms", "Arms|Bracer|Sleeve"), ("Wrists", "Wrist|Bracer"),
            ("Hands", "Hand|Glove|Gauntlet"), ("Rings", "Ring"), ("Chest", "Chest|Breastplate|Robe|Tunic"), ("Waist", "Waist|Belt|Cord|Sash"),
            ("Legs", "Leg|Pant|Greave|Kilt"), ("Feet", "Feet|Boot|Shoe|Sandal"), ("Primary", "Primary|Sword|Axe|Mace|Hammer"), ("Secondary", "Secondary|Shield|Orb")
        ]
        
        for i, (label, search_term) in enumerate(equipment_searches):
            btn = ttk.Button(equip_inner, text=label, width=11,
                      command=lambda term=search_term: self.quick_search(term))
            btn.grid(row=i//4, column=i%4, padx=1, pady=1, sticky='ew')
        
        for col in range(4):
            equip_inner.grid_columnconfigure(col, weight=1)
        
        # Weapon Types
        weapon_frame = ttk.LabelFrame(middle_column, text="🗡️ Weapon Types")
        weapon_frame.pack(fill='x', pady=5)
        
        weapon_inner = ttk.Frame(weapon_frame)
        weapon_inner.pack(fill='both', expand=True, padx=5, pady=5)
        
        weapon_searches = [
            ("Swords", "Sword"), ("Daggers", "Dagger"), ("Axes", "Axe"), ("Maces", "Mace"),
            ("Staves", "Staff|Stave"), ("Bows", "Bow"), ("Shields", "Shield"), ("Orbs", "Orb")
        ]
        
        for i, (label, search_term) in enumerate(weapon_searches):
            btn = ttk.Button(weapon_inner, text=label, width=11,
                      command=lambda term=search_term: self.quick_search(term))
            btn.grid(row=i//4, column=i%4, padx=1, pady=1, sticky='ew')
        
        for col in range(4):
            weapon_inner.grid_columnconfigure(col, weight=1)
        
        # Additional space utilization - Common Searches
        common_frame = ttk.LabelFrame(middle_column, text="🔍 Common Searches")
        common_frame.pack(fill='both', expand=True, pady=5)
        
        common_inner = ttk.Frame(common_frame)
        common_inner.pack(fill='both', expand=True, padx=5, pady=5)
        
        common_searches = [
            ("Empty Slots", "Empty"), ("All Items", ".*"), ("Bags", "Bag"), ("Food/Drink", "Bread|Water|Food|Drink"),
            ("Spells", "Spell:"), ("Books", "Book"), ("Keys", "Key"), ("Potions", "Potion")
        ]
        
        for i, (label, search_term) in enumerate(common_searches):
            btn = ttk.Button(common_inner, text=label, width=11,
                      command=lambda term=search_term: self.quick_search(term))
            btn.grid(row=i//4, column=i%4, padx=1, pady=1, sticky='ew')
        
        for col in range(4):
            common_inner.grid_columnconfigure(col, weight=1)
        
        # Right Column - Augments & Zeb Weapon
        right_column = ttk.Frame(bottom_container)
        right_column.pack(side='right', fill='both', expand=False, padx=(5,0))
        
        # Augments & Special Items
        special_frame = ttk.LabelFrame(right_column, text="✨ Augments & Special Items")
        special_frame.pack(fill='x', pady=(0,5))
        
        special_inner = ttk.Frame(special_frame)
        special_inner.pack(fill='x', padx=5, pady=5)
        
        special_searches = [
            ("All Augments", "Prismatic|Fragment"),
            ("Prismatic Scales", "Prismatic Scale of"),
            ("Truth Fragments", "Fragment of Truth"),
            ("Armor Fragments", "Armor Fragment"),
            ("Legendary Items", "Legendary"),
            ("Enchanted Items", "Enchanted")
        ]
        
        for i, (label, search_term) in enumerate(special_searches):
            btn = ttk.Button(special_inner, text=label, width=20,
                      command=lambda term=search_term: self.quick_search(term))
            btn.grid(row=i//2, column=i%2, padx=1, pady=1, sticky='ew')
        
        for col in range(2):
            special_inner.grid_columnconfigure(col, weight=1)
        
        # Zeb Weapon Section (expanded)
        zeb_frame = ttk.LabelFrame(right_column, text="🗡️ Zeb Weapon Analysis")
        zeb_frame.pack(fill='both', expand=True)
        
        zeb_inner = ttk.Frame(zeb_frame)
        zeb_inner.pack(fill='both', expand=True, padx=8, pady=5)
        
        # Instructions/info
        info_text = tk.Text(zeb_inner, height=4, wrap='word', font=('Arial', 9), 
                           bg='#f0f0f0', relief='flat', state='disabled')
        info_text.pack(fill='x', pady=(0,5))
        
        info_content = """Zeb Weapon requires 12 different Fragment of Truth types (Legendary) plus Time Phased Quintessence and Vortex of the Past. You can combine 4 Enchanted fragments to make 1 Legendary. "Include equipped" counts fragments in worn gear AND spare gear. (Common on EQ Emu servers)"""
        
        info_text.config(state='normal')
        info_text.insert(1.0, info_content)
        info_text.config(state='disabled')
        
        # Checkbox
        self.include_equipped_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(zeb_inner, text="Include equipped fragments\n(in worn gear AND spare gear augment slots)", 
                       variable=self.include_equipped_var).pack(anchor='w', pady=5)
        
        # Buttons
        zeb_buttons = ttk.Frame(zeb_inner)
        zeb_buttons.pack(fill='x', pady=5)
        
        ttk.Button(zeb_buttons, text="🗡️ Check Zeb Weapon Components", 
                  command=self.check_zeb_weapon_components, width=30).pack(pady=2)
        ttk.Button(zeb_buttons, text="🔍 Debug Fragment Locations", 
                  command=self.debug_fragment_locations, width=30).pack(pady=2)
        
        # Last weapon check results (if available)
        results_label = ttk.Label(zeb_inner, text="Last Check Results:", font=('Arial', 9, 'bold'))
        results_label.pack(anchor='w', pady=(10,2))
        
        self.zeb_results_text = tk.Text(zeb_inner, height=6, wrap='word', font=('Consolas', 8),
                                       bg='#f8f8f8', relief='sunken', state='disabled')
        self.zeb_results_text.pack(fill='both', expand=True)
        
        # Initialize with placeholder text
        self.zeb_results_text.config(state='normal')
        self.zeb_results_text.insert(1.0, "No weapon check performed yet.\nClick 'Check Zeb Weapon Components' to analyze your fragments.")
        self.zeb_results_text.config(state='disabled')
    

    
    def create_results_tab(self):
        """Create the search results tab with embedded search controls."""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📄 Results")
        
        # Search controls at top of results tab
        search_controls = ttk.LabelFrame(results_frame, text="🔍 Refine Search")
        search_controls.pack(fill='x', padx=10, pady=(5,0))
        
        controls_inner = ttk.Frame(search_controls)
        controls_inner.pack(fill='x', padx=8, pady=5)
        
        # Search controls in a single row (same as Dashboard)
        search_row = ttk.Frame(controls_inner)
        search_row.pack(fill='x', pady=2)
        
        # Item search
        ttk.Label(search_row, text="Item:").pack(side='left')
        # Use the same search variables as Dashboard for consistency
        results_search_entry = ttk.Entry(search_row, textvariable=self.search_term_var, width=25)
        results_search_entry.pack(side='left', padx=5)
        results_search_entry.bind('<Return>', lambda e: self.perform_search())
        
        # Character filter
        ttk.Label(search_row, text="Character:").pack(side='left', padx=(15,5))
        results_character_combo = ttk.Combobox(search_row, textvariable=self.character_var, width=15, state='readonly')
        results_character_combo.pack(side='left', padx=5)
        
        # Item type filter
        ttk.Label(search_row, text="Type:").pack(side='left', padx=(15,5))
        results_type_combo = ttk.Combobox(search_row, textvariable=self.item_type_var, width=12, state='readonly')
        results_type_combo['values'] = ('All', 'Equipped', 'Inventory', 'Bank')
        results_type_combo.pack(side='left', padx=5)
        
        # Exact match checkbox
        ttk.Checkbutton(search_row, text="Exact Match", variable=self.exact_match_var).pack(side='left', padx=(15,5))
        
        # Action buttons
        actions_row = ttk.Frame(controls_inner)
        actions_row.pack(fill='x', pady=5)
        
        # Left side buttons
        left_buttons = ttk.Frame(actions_row)
        left_buttons.pack(side='left')
        
        ttk.Button(left_buttons, text="🔍 Search", command=self.perform_search).pack(side='left', padx=2)
        ttk.Button(left_buttons, text="🔄 Find Duplicates", command=self.find_duplicates).pack(side='left', padx=2)
        ttk.Button(left_buttons, text="📊 Character Summary", command=self.show_character_summary).pack(side='left', padx=2)
        
        # Right side buttons
        right_buttons = ttk.Frame(actions_row)
        right_buttons.pack(side='right')
        
        ttk.Button(right_buttons, text="💾 Export Results", command=self.export_results).pack(side='left', padx=2)
        ttk.Button(right_buttons, text="🗑️ Clear", command=self.clear_search).pack(side='left', padx=2)
        ttk.Button(right_buttons, text="🏠 Back to Dashboard", command=lambda: self.notebook.select(0)).pack(side='left', padx=2)
        
        # Store references to combo boxes for updating values
        self.results_character_combo = results_character_combo
        self.results_type_combo = results_type_combo
        
        # Results count
        count_frame = ttk.Frame(results_frame)
        count_frame.pack(fill='x', padx=10, pady=5)
        
        self.results_count_var = tk.StringVar(value="No search performed")
        ttk.Label(count_frame, textvariable=self.results_count_var, font=('Arial', 10, 'bold')).pack(side='left')
        
        # Results treeview
        columns = ('Character', 'Item Name', 'Location', 'Type', 'Count', 'ID')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings')
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            if col == 'Item Name':
                self.results_tree.column(col, width=300)
            elif col == 'Location':
                self.results_tree.column(col, width=200)
            else:
                self.results_tree.column(col, width=100)
        
        results_scrollbar_y = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_tree.yview)
        results_scrollbar_x = ttk.Scrollbar(results_frame, orient='horizontal', command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=results_scrollbar_y.set, xscrollcommand=results_scrollbar_x.set)
        
        self.results_tree.pack(side='left', fill='both', expand=True, padx=(10,0), pady=5)
        results_scrollbar_y.pack(side='right', fill='y', pady=5)
        results_scrollbar_x.pack(side='bottom', fill='x', padx=10)
    
    def on_character_summary_double_click(self, event):
        """Handle double-click on character in summary overview."""
        selection = self.char_summary_tree.selection()
        if selection:
            character = self.char_summary_tree.item(selection[0])['values'][0]
            
            # Search for this character's items
            self.character_var.set(character)
            self.search_term_var.set('')  # Search all items for this character
            self.item_type_var.set('All')
            
            # Get all items for this character
            char_items = self.items_df[
                (self.items_df['Character'] == character) &
                (self.items_df['IsEmpty'] == False)
            ][['Character', 'Name', 'Location', 'ItemType', 'Count', 'ID']].sort_values('Name')
            
            self.display_results(char_items, f"All items for {character}")
    
    def update_overview(self):
        """Update the embedded overview section with current data."""
        if self.items_df.empty:
            return
        
        # Update statistics text
        total_items = len(self.items_df)
        non_empty_items = len(self.items_df[self.items_df['IsEmpty'] == False])
        characters = self.items_df['Character'].nunique()
        equipped_items = len(self.items_df[self.items_df['ItemType'] == 'Equipped'])
        inventory_items = len(self.items_df[self.items_df['ItemType'] == 'Inventory']) 
        bank_items = len(self.items_df[self.items_df['ItemType'] == 'Bank'])
        
        stats_text = f"""Total Characters: {characters}
Total Slots: {total_items:,}
Items (Non-Empty): {non_empty_items:,}
Empty Slots: {total_items - non_empty_items:,}

Equipped: {equipped_items:,}
Inventory: {inventory_items:,}
Bank: {bank_items:,}"""
        
        # Update the stats summary text widget
        self.stats_summary.config(state='normal')
        self.stats_summary.delete(1.0, tk.END)
        self.stats_summary.insert(1.0, stats_text)
        self.stats_summary.config(state='disabled')
        
        # Update character summary tree
        for item in self.char_summary_tree.get_children():
            self.char_summary_tree.delete(item)
        
        char_summary = self.items_df.groupby('Character').agg({
            'Name': lambda x: len(x[x != 'Empty']),
            'UpdatedAt': 'max'
        }).rename(columns={'Name': 'ItemCount'}).reset_index()
        
        for _, row in char_summary.iterrows():
            self.char_summary_tree.insert('', 'end', values=(
                row['Character'],
                f"{row['ItemCount']:,}",
                row['UpdatedAt'].strftime('%Y-%m-%d %H:%M')
            ))
    
    def auto_load_initial_inventory(self):
        """Auto-load inventory files from current directory if any exist."""
        current_dir = os.getcwd()
        pattern = os.path.join(current_dir, "*-Inventory.txt")
        inventory_files = glob.glob(pattern)
        
        if inventory_files:
            self.status_var.set(f"Found {len(inventory_files)} inventory files in current directory. Loading...")
            self.root.update()
            
            # Delay the loading slightly to let the GUI appear first
            self.root.after(500, lambda: self.load_inventory_auto())
        else:
            dir_name = os.path.basename(current_dir) if current_dir else "current directory"
            self.status_var.set(f"No inventory files found in {dir_name}. Use Browse button to select a different directory.")
    
    def load_inventory_auto(self):
        """Auto-load inventory files (called after GUI is displayed)."""
        directory = self.dir_var.get()
        
        # Start loading in background thread
        self.progress.start()
        self.status_var.set("Auto-loading inventory files...")
        self.root.update()
        
        # Set flag to indicate this is an auto-load (less intrusive notifications)
        self._manual_load = False
        
        thread = threading.Thread(target=self._load_inventory_thread, args=(directory,))
        thread.daemon = True
        thread.start()
        
    def browse_directory(self):
        """Browse for directory containing inventory files."""
        directory = filedialog.askdirectory(
            title="Select Directory with Inventory Files",
            initialdir=self.dir_var.get()
        )
        if directory:
            self.dir_var.set(directory)
    
    def load_inventory(self):
        """Load inventory files from selected directory (manual load)."""
        directory = self.dir_var.get()
        if not directory or not os.path.exists(directory):
            messagebox.showerror("Error", "Please select a valid directory")
            return
        
        # Start loading in background thread
        self.progress.start()
        self.status_var.set("Loading inventory files...")
        self.root.update()
        
        # Set flag to show success popup for manual loads
        self._manual_load = True
        
        thread = threading.Thread(target=self._load_inventory_thread, args=(directory,))
        thread.daemon = True
        thread.start()
    
    def _load_inventory_thread(self, directory):
        """Background thread for loading inventory."""
        try:
            self.data_dir = directory
            self.items_df = self.load_inventory_files(directory)
            
            # Update UI in main thread
            self.root.after(0, self._on_inventory_loaded)
            
        except Exception as e:
            self.root.after(0, lambda: self._on_inventory_error(str(e)))
    
    def _on_inventory_loaded(self):
        """Called when inventory loading completes successfully."""
        self.progress.stop()
        
        if self.items_df.empty:
            self.status_var.set("No inventory files found")
            messagebox.showwarning("Warning", "No *-Inventory.txt files found in the selected directory")
            return
        
        total_items = len(self.items_df)
        non_empty_items = len(self.items_df[self.items_df['IsEmpty'] == False])
        characters = self.items_df['Character'].nunique()
        shared_bank_items = len(self.items_df[self.items_df['Character'] == 'SHARED-BANK'])
        
        self.status_var.set(f"Loaded {non_empty_items:,} items from {characters} characters")
        
        # Update character dropdown (both Dashboard and Results tabs)
        char_list = ['All'] + sorted(self.items_df['Character'].unique().tolist())
        self.character_combo['values'] = char_list
        self.character_combo.set('All')
        
        # Update Results tab dropdowns if they exist
        if hasattr(self, 'results_character_combo'):
            self.results_character_combo['values'] = char_list
            self.results_character_combo.set(self.character_var.get())
        if hasattr(self, 'results_type_combo'):
            self.results_type_combo.set(self.item_type_var.get())
        
        # Update overview tab
        self.update_overview()
        
        # Show appropriate message based on load type
        if hasattr(self, '_manual_load') and self._manual_load:
            # Manual load - always show success popup
            success_msg = f"Successfully loaded inventory!\n\nCharacters: {characters}\nTotal items: {non_empty_items:,}"
            if shared_bank_items > 0:
                success_msg += f"\nShared Bank items: {shared_bank_items:,}\n\n✓ Duplicate shared banks automatically removed"
            messagebox.showinfo("Success", success_msg)
        else:
            # Auto-load - only show popup for substantial inventories
            if non_empty_items > 100:
                success_msg = f"Successfully auto-loaded inventory!\n\nCharacters: {characters}\nTotal items: {non_empty_items:,}"
                if shared_bank_items > 0:
                    success_msg += f"\nShared Bank items: {shared_bank_items:,}\n\n✓ Duplicate shared banks automatically removed"
                messagebox.showinfo("Auto-Load Success", success_msg)
    
    def _on_inventory_error(self, error_msg):
        """Called when inventory loading fails."""
        self.progress.stop()
        self.status_var.set("Error loading inventory")
        messagebox.showerror("Error", f"Failed to load inventory:\n{error_msg}")
    
    def load_inventory_files(self, directory):
        """Load all inventory files from directory."""
        pattern = os.path.join(directory, "*-Inventory.txt")
        inventory_files = glob.glob(pattern)
        
        if not inventory_files:
            return pd.DataFrame()
        
        result_list = []
        shared_bank_data = {}  # Track shared bank data to detect duplicates
        
        for file_path in inventory_files:
            try:
                file_name = os.path.basename(file_path)
                modified_epoch = os.path.getmtime(file_path)
                modified_ts = datetime.fromtimestamp(modified_epoch)
                
                # Extract character name
                match = re.match(r"(.+?)-", file_name)
                if not match:
                    continue
                    
                char_name = match.group(1)
                
                # Read file
                df = pd.read_csv(file_path, sep='\t')
                df.insert(0, 'Character', char_name)
                df['UpdatedAt'] = modified_ts
                df['FileName'] = file_name
                
                # Separate shared bank items for duplicate detection
                shared_bank_items = df[df['Location'].str.startswith('SharedBank', na=False)].copy()
                character_items = df[~df['Location'].str.startswith('SharedBank', na=False)].copy()
                
                # Process shared bank duplicate detection
                if not shared_bank_items.empty:
                    # Create a signature for this shared bank based on all items
                    shared_bank_signature = self._create_shared_bank_signature(shared_bank_items)
                    
                    if shared_bank_signature in shared_bank_data:
                        # This shared bank already exists - skip it to avoid duplicates
                        print(f"  Skipping duplicate shared bank from {char_name} (same as {shared_bank_data[shared_bank_signature]['source_char']})")
                    else:
                        # New unique shared bank - add it
                        shared_bank_items['Character'] = 'SHARED-BANK'
                        shared_bank_data[shared_bank_signature] = {
                            'data': shared_bank_items,
                            'source_char': char_name,
                            'updated_at': modified_ts
                        }
                
                # Always add character-specific items
                character_items['Character'] = char_name
                
                # Add derived columns
                for df_part in [character_items]:
                    if not df_part.empty:
                        df_part['ItemType'] = df_part['Location'].apply(self._categorize_location)
                        df_part['IsEquipped'] = df_part['Location'].apply(lambda x: not any(word in str(x) for word in ['Slot', 'Bank', 'Bag']))
                        df_part['IsEmpty'] = df_part['Name'] == 'Empty'
                        result_list.append(df_part)
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        # Add all unique shared banks
        for signature, bank_info in shared_bank_data.items():
            shared_bank_df = bank_info['data']
            shared_bank_df['ItemType'] = shared_bank_df['Location'].apply(self._categorize_location)
            shared_bank_df['IsEquipped'] = shared_bank_df['Location'].apply(lambda x: not any(word in str(x) for word in ['Slot', 'Bank', 'Bag']))
            shared_bank_df['IsEmpty'] = shared_bank_df['Name'] == 'Empty'
            result_list.append(shared_bank_df)
        
        if not result_list:
            return pd.DataFrame()
            
        final_df = pd.concat(result_list, axis=0, ignore_index=True)
        
        # Remove duplicates from character-specific items only (shared bank already deduplicated)
        character_items_df = final_df[final_df['Character'] != 'SHARED-BANK']
        shared_bank_df = final_df[final_df['Character'] == 'SHARED-BANK']
        
        if not character_items_df.empty:
            unique_cols = [col for col in character_items_df.columns if col not in ['UpdatedAt', 'FileName']]
            character_items_df = character_items_df.drop_duplicates(subset=unique_cols)
        
        if not shared_bank_df.empty:
            final_df = pd.concat([character_items_df, shared_bank_df], axis=0, ignore_index=True)
        else:
            final_df = character_items_df
        
        return final_df
    
    def _create_shared_bank_signature(self, shared_bank_df):
        """Create a unique signature for shared bank contents to detect duplicates."""
        # Sort by location and name to ensure consistent ordering
        sorted_items = shared_bank_df.sort_values(['Location', 'Name', 'ID', 'Count'])
        
        # Create signature from non-empty items only (empty slots can vary)
        non_empty_items = sorted_items[sorted_items['Name'] != 'Empty']
        
        if non_empty_items.empty:
            # If shared bank is completely empty, create signature based on structure
            return f"empty_bank_{len(sorted_items)}_slots"
        
        # Create signature from item data (location, name, id, count)
        signature_parts = []
        for _, row in non_empty_items.iterrows():
            signature_parts.append(f"{row['Location']}|{row['Name']}|{row['ID']}|{row['Count']}")
        
        # Hash the signature for efficient comparison
        import hashlib
        signature_string = ":::".join(signature_parts)
        return hashlib.md5(signature_string.encode()).hexdigest()
    
    def _categorize_location(self, location):
        """Categorize item location."""
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
    

    
    def perform_search(self):
        """Perform search based on current filters."""
        if self.items_df.empty:
            messagebox.showwarning("Warning", "No inventory data loaded")
            return
        
        search_term = self.search_term_var.get().strip()
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term")
            return
        
        # Get filter values
        character = self.character_var.get() if self.character_var.get() != 'All' else None
        item_type = self.item_type_var.get() if self.item_type_var.get() != 'All' else None
        exact_match = self.exact_match_var.get()
        
        # Perform search
        results = self.search_items(search_term, character, exact_match, item_type)
        self.display_results(results, f"Search: '{search_term}'")
    
    def search_items(self, search_term, character=None, exact_match=False, item_type=None):
        """Search for items with filters."""
        df = self.items_df[self.items_df['IsEmpty'] == False].copy()
        
        # Handle regex patterns for quick searches
        if '|' in search_term:
            df = df[df['Name'].str.contains(search_term, case=False, na=False, regex=True)]
        elif exact_match:
            df = df[df['Name'].str.lower() == search_term.lower()]
        else:
            df = df[df['Name'].str.contains(search_term, case=False, na=False)]
        
        if character:
            df = df[df['Character'].str.lower() == character.lower()]
            
        if item_type:
            df = df[df['ItemType'].str.lower() == item_type.lower()]
        
        return df[['Character', 'Name', 'Location', 'ItemType', 'Count', 'ID']].sort_values(['Character', 'Name'])
    
    def debug_fragment_locations(self):
        """Debug function to show where fragments are located."""
        if self.items_df.empty:
            messagebox.showwarning("Warning", "No inventory data loaded")
            return
        
        # Find all Fragment of Truth items
        fragment_items = self.items_df[
            (self.items_df['Name'].str.contains('Fragment of Truth', case=False, na=False)) &
            (self.items_df['IsEmpty'] == False)
        ]
        
        if fragment_items.empty:
            messagebox.showinfo("Debug", "No Fragment of Truth items found in inventory")
            return
        
        # Group by location type for analysis
        debug_info = []
        debug_info.append("🔍 FRAGMENT OF TRUTH DEBUG ANALYSIS")
        debug_info.append("=" * 50)
        debug_info.append(f"Total fragments found: {len(fragment_items)}")
        debug_info.append("")
        
        # Categorize locations using the SAME logic as the main analyzer
        def count_slot_levels(location):
            return str(location).count('-Slot')
        
        def is_equipped_location(location):
            """Determine if location represents an equipped augment."""
            location_str = str(location)
            slot_count = location_str.count('-Slot')
            
            if slot_count == 0:
                # No slots = loose item/gear
                return False
            elif slot_count == 1:
                # One slot level - check if it's in a container or worn gear
                if ('General' in location_str or 'Bank' in location_str or 'SharedBank' in location_str):
                    # General1-Slot1 = item in bag = Available
                    return False
                else:
                    # Primary-Slot1 = augment in worn gear = Equipped
                    return True
            else:
                # 2+ slot levels = augment in item = Equipped
                return True
        
        # Add analysis columns
        fragment_items = fragment_items.copy()
        fragment_items['SlotLevel'] = fragment_items['Location'].apply(count_slot_levels)
        fragment_items['IsEquippedLocation'] = fragment_items['Location'].apply(is_equipped_location)
        
        # Available = items in non-equipped locations
        available_items = fragment_items[fragment_items['IsEquippedLocation'] == False]
        
        # Equipped = items in equipped locations
        equipped_items = fragment_items[fragment_items['IsEquippedLocation'] == True]
        
        # Split available items by container type
        available_general = available_items[available_items['Location'].str.contains('General', case=False, na=False)]
        available_bank = available_items[available_items['Location'].str.contains('Bank', case=False, na=False)]
        available_other = available_items[
            ~available_items['Location'].str.contains('General', case=False, na=False) &
            ~available_items['Location'].str.contains('Bank', case=False, na=False)
        ]
        
        # Split equipped items by location (worn vs spare gear)
        equipped_worn = equipped_items[
            ~equipped_items['Location'].str.contains('General', case=False, na=False) &
            ~equipped_items['Location'].str.contains('Bank', case=False, na=False)
        ]
        
        equipped_spare = equipped_items[
            (equipped_items['Location'].str.contains('General', case=False, na=False)) |
            (equipped_items['Location'].str.contains('Bank', case=False, na=False))
        ]
        
        debug_info.append(f"📦 Available in Bags: {len(available_general)}")
        for _, item in available_general.head(10).iterrows():
            debug_info.append(f"  • {item['Character']}: {item['Name']} @ {item['Location']} (Level {item['SlotLevel']})")
        if len(available_general) > 10:
            debug_info.append(f"  ... and {len(available_general) - 10} more")
        
        debug_info.append(f"\n🏦 Available in Bank: {len(available_bank)}")
        for _, item in available_bank.head(10).iterrows():
            debug_info.append(f"  • {item['Character']}: {item['Name']} @ {item['Location']} (Level {item['SlotLevel']})")
        if len(available_bank) > 10:
            debug_info.append(f"  ... and {len(available_bank) - 10} more")
        
        debug_info.append(f"\n⚔️ Equipped in Worn Gear: {len(equipped_worn)}")
        for _, item in equipped_worn.iterrows():
            debug_info.append(f"  • {item['Character']}: {item['Name']} @ {item['Location']} (Level {item['SlotLevel']})")
        
        debug_info.append(f"\n🎒 Equipped in Spare Gear: {len(equipped_spare)}")
        for _, item in equipped_spare.head(10).iterrows():
            debug_info.append(f"  • {item['Character']}: {item['Name']} @ {item['Location']} (Level {item['SlotLevel']})")
        if len(equipped_spare) > 10:
            debug_info.append(f"  ... and {len(equipped_spare) - 10} more")
        
        debug_info.append(f"\n❓ Other Available: {len(available_other)}")
        for _, item in available_other.iterrows():
            debug_info.append(f"  • {item['Character']}: {item['Name']} @ {item['Location']} (Level {item['SlotLevel']})")
        
        # Show unique location patterns
        debug_info.append("\n📍 UNIQUE LOCATION PATTERNS:")
        unique_locations = fragment_items['Location'].unique()
        for loc in sorted(unique_locations):
            count = len(fragment_items[fragment_items['Location'] == loc])
            debug_info.append(f"  • {loc} ({count} items)")
        
        # Show results in popup
        popup = tk.Toplevel(self.root)
        popup.title("Fragment Location Debug")
        popup.geometry("800x600")
        
        text_widget = scrolledtext.ScrolledText(popup, wrap='word', font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget.insert(1.0, "\n".join(debug_info))
        text_widget.configure(state='disabled')
        
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
    
    def check_zeb_weapon_components(self):
        """Check if player has components needed for Zeb Weapon creation."""
        if self.items_df.empty:
            messagebox.showwarning("Warning", "No inventory data loaded")
            return
        
        # Define required components
        required_fragments = [
            "Akhevan Fragment of Truth",
            "Fiery Fragment of Truth", 
            "Gelid Fragment of Truth",
            "Hastened Fragment of Truth",
            "Healing Fragment of Truth",
            "Icy Fragment of Truth",
            "Lethal Fragment of Truth",
            "Magical Fragment of Truth",
            "Replenishing Fragment of Truth",
            "Runic Fragment of Truth",
            "Ssraeshzian Fragment of Truth",
            "Yttrium Fragment of Truth"
        ]
        
        other_components = [
            "Time Phased Quintessence",
            "Vortex of the Past"
        ]
        
        # Check inventory for all components
        include_equipped = self.include_equipped_var.get()
        results = self._analyze_zeb_components(required_fragments, other_components, include_equipped)
        
        # Display results in a new window
        self._show_zeb_weapon_results(results)
    
    def _analyze_zeb_components(self, required_fragments, other_components, include_equipped=False):
        """Analyze inventory for Zeb weapon components."""
        # Get all non-empty items
        all_non_empty_items = self.items_df[self.items_df['IsEmpty'] == False]
        
        # Define what constitutes "available" (not equipped) items
        if not include_equipped:
            # Available = items that are loose in containers (not augmented into any gear)
            # Equipped = items that are augmented into gear (worn OR spare)
            
            # Count the number of "-Slot" occurrences and analyze location pattern
            # Available patterns:
            #   Level 0: Primary, Head, General1 (loose gear/items)
            #   Level 1: General1-Slot1, Bank4-Slot7 (items IN containers)
            # Equipped patterns:
            #   Level 1: Range-Slot1, Primary-Slot2 (augments IN worn gear)
            #   Level 2+: General2-Slot1-Slot2 (augments IN items IN containers)
            
            def count_slot_levels(location):
                return str(location).count('-Slot')
            
            def is_equipped_location(location):
                """Determine if location represents an equipped augment."""
                location_str = str(location)
                slot_count = location_str.count('-Slot')
                
                if slot_count == 0:
                    # No slots = loose item/gear
                    return False
                elif slot_count == 1:
                    # One slot level - check if it's in a container or worn gear
                    if ('General' in location_str or 'Bank' in location_str or 'SharedBank' in location_str):
                        # General1-Slot1 = item in bag = Available
                        return False
                    else:
                        # Primary-Slot1 = augment in worn gear = Equipped
                        return True
                else:
                    # 2+ slot levels = augment in item = Equipped
                    # General2-Slot1-Slot2 = augment in item in bag = Equipped
                    return True
            
            # Add analysis columns
            all_non_empty_items = all_non_empty_items.copy()
            all_non_empty_items['SlotLevel'] = all_non_empty_items['Location'].apply(count_slot_levels)
            all_non_empty_items['IsEquippedLocation'] = all_non_empty_items['Location'].apply(is_equipped_location)
            
            # Equipped = items in equipped locations
            equipped_items = all_non_empty_items[all_non_empty_items['IsEquippedLocation'] == True]
            
            # Available = items in non-equipped locations
            available_items = all_non_empty_items[all_non_empty_items['IsEquippedLocation'] == False]
        else:
            # If including equipped, all non-empty items are "available"
            available_items = all_non_empty_items
            equipped_items = pd.DataFrame()  # Empty dataframe
        
        # Debug output - let's see what we're working with
        print(f"Debug: Total non-empty items: {len(all_non_empty_items)}")
        print(f"Debug: Available items: {len(available_items)}")
        if not include_equipped:
            print(f"Debug: Equipped items: {len(equipped_items)}")
            print(f"Debug: Sample available locations: {available_items['Location'].head(10).tolist()}")
            if len(equipped_items) > 0:
                print(f"Debug: Sample equipped locations: {equipped_items['Location'].head(10).tolist()}")
        
        results = {
            'fragments': {},
            'other_components': {},
            'missing_fragments': [],
            'missing_other': [],
            'can_make_weapon': False,
            'total_fragments_ready': 0,
            'include_equipped': include_equipped,
            'equipped_fragments': {},
            'available_fragments': {}
        }
        
        # Check each required fragment
        for fragment_base in required_fragments:
            legendary_name = f"{fragment_base} (Legendary)"
            enchanted_name = f"{fragment_base} (Enchanted)"
            
            # Count from available items (for crafting)
            legendary_count = len(available_items[
                available_items['Name'].str.contains(legendary_name, case=False, na=False, regex=False)
            ])
            
            enchanted_count = len(available_items[
                available_items['Name'].str.contains(enchanted_name, case=False, na=False, regex=False)
            ])
            
            # Count equipped versions for reporting (ALL equipped: worn + spare gear)
            equipped_legendary = 0
            equipped_enchanted = 0
            
            if not include_equipped and len(all_non_empty_items) > 0:
                # Count ALL equipped fragments (both worn and spare gear)
                all_equipped_legendary = len(all_non_empty_items[
                    (all_non_empty_items['Name'].str.contains(legendary_name, case=False, na=False, regex=False)) &
                    (all_non_empty_items['IsEquippedLocation'] == True)
                ])
                
                all_equipped_enchanted = len(all_non_empty_items[
                    (all_non_empty_items['Name'].str.contains(enchanted_name, case=False, na=False, regex=False)) &
                    (all_non_empty_items['IsEquippedLocation'] == True)
                ])
                
                equipped_legendary = all_equipped_legendary
                equipped_enchanted = all_equipped_enchanted
            
            # Debug output for specific fragments
            print(f"Debug {fragment_base}: Available L:{legendary_count} E:{enchanted_count}, Equipped L:{equipped_legendary} E:{equipped_enchanted}")
            
            # Calculate if we can make a legendary (need 4 enchanted available)
            can_make_legendary = enchanted_count >= 4
            has_legendary = legendary_count > 0
            
            results['fragments'][fragment_base] = {
                'legendary_count': legendary_count,
                'enchanted_count': enchanted_count,
                'equipped_legendary': equipped_legendary,
                'equipped_enchanted': equipped_enchanted,
                'has_legendary': has_legendary,
                'can_make_legendary': can_make_legendary,
                'ready': has_legendary or can_make_legendary
            }
            
            if has_legendary or can_make_legendary:
                results['total_fragments_ready'] += 1
            else:
                missing_info = {
                    'name': fragment_base,
                    'legendary_count': legendary_count,
                    'enchanted_count': enchanted_count,
                    'equipped_legendary': equipped_legendary,
                    'equipped_enchanted': equipped_enchanted,
                    'need_more': 4 - enchanted_count if enchanted_count < 4 else 0
                }
                results['missing_fragments'].append(missing_info)
        
        # Check other components
        for component in other_components:
            count = len(available_items[
                available_items['Name'].str.contains(component, case=False, na=False, regex=False)
            ])
            
            results['other_components'][component] = {
                'count': count,
                'ready': count > 0
            }
            
            if count == 0:
                results['missing_other'].append(component)
        
        # Determine if weapon can be made
        all_fragments_ready = results['total_fragments_ready'] == len(required_fragments)
        all_other_ready = len(results['missing_other']) == 0
        results['can_make_weapon'] = all_fragments_ready and all_other_ready
        
        return results
    
    def _show_zeb_weapon_results(self, results):
        """Display Zeb weapon component analysis in a popup window and update embedded results."""
        # Update embedded results first
        self._update_embedded_zeb_results(results)
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Zeb Weapon Component Check")
        popup.geometry("800x600")
        popup.configure(bg='#2c3e50')
        
        # Make it modal
        popup.transient(self.root)
        popup.grab_set()
        
        # Title
        title_frame = ttk.Frame(popup)
        title_frame.pack(fill='x', padx=10, pady=10)
        
        if results['can_make_weapon']:
            title_text = "🗡️ ZEB WEAPON READY! 🗡️"
            title_color = 'green'
        else:
            title_text = "🔍 Zeb Weapon Component Analysis"
            title_color = 'orange'
        
        title_label = tk.Label(title_frame, text=title_text, 
                              font=('Arial', 16, 'bold'), 
                              fg=title_color, bg='#2c3e50')
        title_label.pack()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(popup)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Summary tab
        self._create_zeb_summary_tab(notebook, results)
        
        # Details tab  
        self._create_zeb_details_tab(notebook, results)
        
        # Missing items tab
        if not results['can_make_weapon']:
            self._create_zeb_missing_tab(notebook, results)
        
        # Close button
        close_frame = ttk.Frame(popup)
        close_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(close_frame, text="Close", command=popup.destroy).pack(side='right')
        
        if results['can_make_weapon']:
            ttk.Button(close_frame, text="Show All Components", 
                      command=lambda: self._show_zeb_components_search(results)).pack(side='left')
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
    
    def _update_embedded_zeb_results(self, results):
        """Update the embedded Zeb weapon results display."""
        if not hasattr(self, 'zeb_results_text'):
            return
        
        # Create summary text for embedded display
        summary_lines = []
        
        if results['can_make_weapon']:
            summary_lines.append("✅ ZEB WEAPON READY!")
            summary_lines.append("")
            summary_lines.append(f"Fragments Ready: {results['total_fragments_ready']}/12")
            summary_lines.append(f"Other Components: {2 - len(results['missing_other'])}/2")
        else:
            summary_lines.append("❌ Missing Components")
            summary_lines.append("")
            summary_lines.append(f"Fragments Ready: {results['total_fragments_ready']}/12")
            summary_lines.append(f"Other Components: {2 - len(results['missing_other'])}/2")
            summary_lines.append("")
            
            if results['missing_fragments']:
                summary_lines.append("Missing Fragments:")
                for fragment in results['missing_fragments'][:3]:  # Show only first 3
                    fragment_short = fragment['name'].replace(" Fragment of Truth", "")
                    if fragment['enchanted_count'] > 0:
                        summary_lines.append(f"  • {fragment_short}: {fragment['need_more']} more needed")
                    else:
                        summary_lines.append(f"  • {fragment_short}: None available")
                
                if len(results['missing_fragments']) > 3:
                    summary_lines.append(f"  ... and {len(results['missing_fragments']) - 3} more")
            
            if results['missing_other']:
                summary_lines.append("")
                summary_lines.append("Missing Components:")
                for component in results['missing_other']:
                    summary_lines.append(f"  • {component}")
        
        # Update the text widget
        self.zeb_results_text.config(state='normal')
        self.zeb_results_text.delete(1.0, tk.END)
        self.zeb_results_text.insert(1.0, "\n".join(summary_lines))
        self.zeb_results_text.config(state='disabled')
    
    def _create_zeb_summary_tab(self, notebook, results):
        """Create summary tab for Zeb weapon analysis."""
        summary_frame = ttk.Frame(notebook)
        notebook.add(summary_frame, text="📊 Summary")
        
        # Summary text
        summary_text = scrolledtext.ScrolledText(summary_frame, height=25, width=80, 
                                               wrap='word', font=('Consolas', 10))
        summary_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Build summary content
        summary_content = f"""🗡️ ZEB WEAPON COMPONENT ANALYSIS
{'='*60}

"""
        
        if results['can_make_weapon']:
            summary_content += "✅ STATUS: READY TO CRAFT ZEB WEAPON!\n\n"
        else:
            summary_content += "❌ STATUS: Missing required components\n\n"
        
        summary_content += f"📦 FRAGMENT PROGRESS: {results['total_fragments_ready']}/12\n"
        summary_content += f"🔧 OTHER COMPONENTS: {2 - len(results['missing_other'])}/2\n"
        
        # Show filter status
        if results['include_equipped']:
            summary_content += "🛠️ FILTER: Including equipped fragments\n\n"
        else:
            summary_content += "🎯 FILTER: Only available fragments (equipped fragments excluded)\n\n"
        
        # Fragment status
        summary_content += "📋 FRAGMENT STATUS:\n"
        summary_content += "-" * 40 + "\n"
        
        ready_fragments = []
        partial_fragments = []
        missing_fragments = []
        
        for fragment, data in results['fragments'].items():
            fragment_short = fragment.replace(" Fragment of Truth", "")
            if data['ready']:
                if data['has_legendary']:
                    status = f"✅ {fragment_short} (Available: Legendary x{data['legendary_count']})"
                    if data['equipped_legendary'] > 0 and not results['include_equipped']:
                        status += f" [+{data['equipped_legendary']} equipped]"
                    ready_fragments.append(status)
                else:
                    status = f"🔄 {fragment_short} (Can make: {data['enchanted_count']} Enchanted)"
                    if data['equipped_enchanted'] > 0 and not results['include_equipped']:
                        status += f" [+{data['equipped_enchanted']} equipped]"
                    ready_fragments.append(status)
            else:
                if data['enchanted_count'] > 0:
                    need_more = 4 - data['enchanted_count']
                    status = f"🔸 {fragment_short} ({data['enchanted_count']}/4 Enchanted, need {need_more} more)"
                    if data['equipped_enchanted'] > 0 and not results['include_equipped']:
                        status += f" [+{data['equipped_enchanted']} equipped]"
                    partial_fragments.append(status)
                else:
                    status = f"❌ {fragment_short} (None available)"
                    if (data['equipped_legendary'] > 0 or data['equipped_enchanted'] > 0) and not results['include_equipped']:
                        equipped_info = []
                        if data['equipped_legendary'] > 0:
                            equipped_info.append(f"L:{data['equipped_legendary']}")
                        if data['equipped_enchanted'] > 0:
                            equipped_info.append(f"E:{data['equipped_enchanted']}")
                        status += f" [{'+'.join(equipped_info)} equipped]"
                    missing_fragments.append(status)
        
        for item in ready_fragments:
            summary_content += item + "\n"
        for item in partial_fragments:
            summary_content += item + "\n"
        for item in missing_fragments:
            summary_content += item + "\n"
        
        # Other components
        summary_content += "\n🔧 OTHER COMPONENTS:\n"
        summary_content += "-" * 40 + "\n"
        
        for component, data in results['other_components'].items():
            if data['ready']:
                summary_content += f"✅ {component} (Found x{data['count']})\n"
            else:
                summary_content += f"❌ {component} (Not found)\n"
        
        if results['can_make_weapon']:
            summary_content += "\n" + "="*60 + "\n"
            summary_content += "🎉 YOU CAN CRAFT A ZEB WEAPON! 🎉\n"
            summary_content += "Click 'Show All Components' to see all your items.\n"
        
        summary_text.insert(1.0, summary_content)
        summary_text.configure(state='disabled')
    
    def _create_zeb_details_tab(self, notebook, results):
        """Create details tab showing all found components."""
        details_frame = ttk.Frame(notebook)
        notebook.add(details_frame, text="📝 Details")
        
        # Create treeview for details
        columns = ('Component', 'Type', 'Status', 'Count', 'Notes')
        details_tree = ttk.Treeview(details_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            details_tree.heading(col, text=col)
            if col == 'Component':
                details_tree.column(col, width=200)
            elif col == 'Notes':
                details_tree.column(col, width=250)
            else:
                details_tree.column(col, width=80)
        
        scrollbar_details = ttk.Scrollbar(details_frame, orient='vertical', command=details_tree.yview)
        details_tree.configure(yscrollcommand=scrollbar_details.set)
        
        details_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar_details.pack(side='right', fill='y', pady=10)
        
        # Populate details
        for fragment, data in results['fragments'].items():
            fragment_short = fragment.replace(" Fragment of Truth", "")
            
            if data['ready']:
                if data['has_legendary']:
                    status = "✅ Ready"
                    notes = f"Available: {data['legendary_count']} Legendary"
                    if data['equipped_legendary'] > 0 and not results['include_equipped']:
                        notes += f", Equipped: {data['equipped_legendary']} Legendary"
                else:
                    status = "🔄 Can Make"
                    notes = f"Can combine {data['enchanted_count']} Enchanted → 1 Legendary"
                    if data['equipped_enchanted'] > 0 and not results['include_equipped']:
                        notes += f", Equipped: {data['equipped_enchanted']} Enchanted"
            else:
                status = "❌ Missing"
                if data['enchanted_count'] > 0:
                    need_more = 4 - data['enchanted_count']
                    notes = f"Available: {data['enchanted_count']}/4 Enchanted, need {need_more} more"
                    if data['equipped_enchanted'] > 0 and not results['include_equipped']:
                        notes += f", Equipped: {data['equipped_enchanted']} Enchanted"
                else:
                    notes = "None available"
                    if not results['include_equipped'] and (data['equipped_legendary'] > 0 or data['equipped_enchanted'] > 0):
                        equipped_parts = []
                        if data['equipped_legendary'] > 0:
                            equipped_parts.append(f"{data['equipped_legendary']} Legendary")
                        if data['equipped_enchanted'] > 0:
                            equipped_parts.append(f"{data['equipped_enchanted']} Enchanted")
                        notes += f", Equipped: {', '.join(equipped_parts)}"
            
            # Format count display
            if results['include_equipped']:
                count_display = f"L:{data['legendary_count']} E:{data['enchanted_count']}"
            else:
                count_display = f"Avail: L:{data['legendary_count']} E:{data['enchanted_count']}"
                if data['equipped_legendary'] > 0 or data['equipped_enchanted'] > 0:
                    count_display += f", Equip: L:{data['equipped_legendary']} E:{data['equipped_enchanted']}"
            
            details_tree.insert('', 'end', values=(
                fragment_short, 'Fragment', status, count_display, notes
            ))
        
        # Add other components
        for component, data in results['other_components'].items():
            if data['ready']:
                status = "✅ Ready"
                notes = f"Found {data['count']} in inventory"
            else:
                status = "❌ Missing"
                notes = "Not found in inventory"
            
            details_tree.insert('', 'end', values=(
                component, 'Component', status, data['count'], notes
            ))
    
    def _create_zeb_missing_tab(self, notebook, results):
        """Create missing items tab."""
        missing_frame = ttk.Frame(notebook)
        notebook.add(missing_frame, text="❌ Missing")
        
        missing_text = scrolledtext.ScrolledText(missing_frame, height=25, width=80, 
                                               wrap='word', font=('Consolas', 10))
        missing_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        missing_content = "❌ MISSING COMPONENTS FOR ZEB WEAPON\n"
        missing_content += "="*50 + "\n\n"
        
        if results['missing_fragments']:
            missing_content += "🔸 MISSING FRAGMENTS:\n"
            missing_content += "-" * 30 + "\n"
            for fragment in results['missing_fragments']:
                fragment_short = fragment['name'].replace(" Fragment of Truth", "")
                if fragment['enchanted_count'] > 0:
                    missing_content += f"• {fragment_short}: Need {fragment['need_more']} more Enchanted (available: {fragment['enchanted_count']}/4)\n"
                    if fragment['equipped_enchanted'] > 0 and not results['include_equipped']:
                        missing_content += f"  🔒 {fragment['equipped_enchanted']} Enchanted equipped (not available for crafting)\n"
                else:
                    missing_content += f"• {fragment_short}: Need 1 Legendary OR 4 Enchanted (none available)\n"
                    if not results['include_equipped'] and (fragment['equipped_legendary'] > 0 or fragment['equipped_enchanted'] > 0):
                        equipped_parts = []
                        if fragment['equipped_legendary'] > 0:
                            equipped_parts.append(f"{fragment['equipped_legendary']} Legendary")
                        if fragment['equipped_enchanted'] > 0:
                            equipped_parts.append(f"{fragment['equipped_enchanted']} Enchanted")
                        missing_content += f"  🔒 {', '.join(equipped_parts)} equipped (not available for crafting)\n"
            missing_content += "\n"
        
        if results['missing_other']:
            missing_content += "🔧 MISSING OTHER COMPONENTS:\n"
            missing_content += "-" * 30 + "\n"
            for component in results['missing_other']:
                missing_content += f"• {component}: Not found in inventory\n"
            missing_content += "\n"
        
        missing_content += "💡 TIPS:\n"
        missing_content += "-" * 10 + "\n"
        missing_content += "• You can combine 4 Enchanted fragments to make 1 Legendary\n"
        missing_content += "• Search for 'Fragment of Truth' to see all fragments you have\n"
        missing_content += "• Check other characters - fragments might be on different chars\n"
        missing_content += "• Time Phased Quintessence and Vortex of the Past are rare drops\n"
        
        missing_text.insert(1.0, missing_content)
        missing_text.configure(state='disabled')
    
    def _show_zeb_components_search(self, results):
        """Show all Zeb weapon components in main search results."""
        # Build a comprehensive search for all components
        all_components = []
        
        # Add all fragment names
        for fragment in results['fragments'].keys():
            all_components.append(fragment)
        
        # Add other components
        for component in results['other_components'].keys():
            all_components.append(component)
        
        # Create a regex pattern to match any component
        search_pattern = "|".join([f"({comp.replace('(', '\\(').replace(')', '\\)')})" for comp in all_components])
        
        # Perform search
        search_results = self.search_items(search_pattern, character=None, exact_match=False, item_type=None)
        
        # Display results
        self.display_results(search_results, "All Zeb Weapon Components")
        
        # Switch to main window
        self.root.lift()
    
    def quick_search(self, search_term):
        """Perform a quick search."""
        self.search_term_var.set(search_term)
        self.character_var.set('All')
        self.item_type_var.set('All')
        self.exact_match_var.set(False)
        self.perform_search()
    
    def find_duplicates(self):
        """Find duplicate items across characters."""
        if self.items_df.empty:
            messagebox.showwarning("Warning", "No inventory data loaded")
            return
        
        # Get minimum count from user
        min_count = simpledialog.askinteger("Find Duplicates", 
                                              "Minimum number of occurrences:", 
                                              initialvalue=2, minvalue=2)
        if not min_count:
            return
        
        item_counts = self.items_df[self.items_df['IsEmpty'] == False].groupby(['Name', 'ID']).agg({
            'Character': 'count',
            'Count': 'sum'
        }).rename(columns={'Character': 'CharacterCount'}).reset_index()
        
        duplicates = item_counts[item_counts['CharacterCount'] >= min_count]
        
        if duplicates.empty:
            messagebox.showinfo("No Duplicates", f"No items found appearing {min_count}+ times")
            return
        
        # Get details for duplicate items
        result_list = []
        for _, row in duplicates.iterrows():
            item_details = self.items_df[
                (self.items_df['Name'] == row['Name']) & 
                (self.items_df['ID'] == row['ID']) &
                (self.items_df['IsEmpty'] == False)
            ][['Character', 'Name', 'Location', 'ItemType', 'Count', 'ID']].copy()
            result_list.append(item_details)
            
        results = pd.concat(result_list, ignore_index=True)
        self.display_results(results, f"Duplicates ({min_count}+ occurrences)")
    
    def show_character_summary(self):
        """Show detailed character summary."""
        if not hasattr(self, 'last_search_results') or self.last_search_results.empty:
            messagebox.showinfo("Character Summary", "Please perform a search first to see character details")
            return
        
        char_counts = self.last_search_results['Character'].value_counts()
        
        summary_text = "CHARACTER BREAKDOWN OF CURRENT RESULTS:\n" + "="*50 + "\n\n"
        for char, count in char_counts.items():
            summary_text += f"{char}: {count} items\n"
        
        messagebox.showinfo("Character Summary", summary_text)
    
    def display_results(self, results, title):
        """Display search results in the results tab."""
        self.last_search_results = results
        
        # Clear existing results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Update count
        self.results_count_var.set(f"{title} - {len(results)} items found")
        
        # Add results to tree
        for _, row in results.iterrows():
            self.results_tree.insert('', 'end', values=(
                row['Character'],
                row['Name'],
                row['Location'],
                row['ItemType'],
                row['Count'],
                row['ID']
            ))
        
        # Switch to results tab automatically
        self.notebook.select(1)  # Results tab is index 1
    
    def clear_search(self):
        """Clear search fields and results."""
        self.search_term_var.set('')
        self.character_var.set('All')
        self.item_type_var.set('All')
        self.exact_match_var.set(False)
        
        # Clear results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.results_count_var.set("No search performed")
        self.last_search_results = pd.DataFrame()
    
    def export_results(self):
        """Export current search results."""
        if not hasattr(self, 'last_search_results') or self.last_search_results.empty:
            messagebox.showwarning("Warning", "No search results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Search Results"
        )
        
        if filename:
            try:
                self.last_search_results.to_csv(filename, index=False)
                messagebox.showinfo("Export Successful", f"Results exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export:\n{e}")
    

    
    def create_signet_quest_tab(self):
        """Create the Signet of Might quest tracking tab."""
        quest_frame = ttk.Frame(self.notebook)
        self.notebook.add(quest_frame, text="🏺 Signet of Might")
        
        # Initialize quest data
        self.signet_quest = SignetOfMightQuest()
        
        # Main container
        main_container = ttk.Frame(quest_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title and description
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill='x', pady=(0,10))
        
        title_label = ttk.Label(title_frame, text="🏺 Signet of Might Quest Tracker", 
                               font=('Arial', 16, 'bold'))
        title_label.pack()
        
        desc_label = ttk.Label(title_frame, 
                              text="Aid Grimel Quest Chain - Track your progress through all 7 tradeskill quests",
                              font=('Arial', 10))
        desc_label.pack(pady=(5,0))
        
        # Global requirements section
        req_frame = ttk.LabelFrame(main_container, text="📋 Global Requirements")
        req_frame.pack(fill='x', pady=(0,10))
        
        req_inner = ttk.Frame(req_frame)
        req_inner.pack(fill='x', padx=10, pady=5)
        
        req_text = tk.Text(req_inner, height=4, wrap='word', font=('Arial', 9),
                          bg='#f8f8f8', relief='flat', state='disabled')
        req_text.pack(fill='x')
        
        req_content = """Global Requirements:
• Elemental Planar Flags (progression)
• Tradeskills: 220+ unmodified in Blacksmithing, Brewing, Jewelcrafting, Pottery, Tailoring, Fletching, Baking"""
        
        req_text.config(state='normal')
        req_text.insert(1.0, req_content)
        req_text.config(state='disabled')
        
        # Control buttons
        control_frame = ttk.Frame(main_container)
        control_frame.pack(fill='x', pady=(0,10))
        
        ttk.Button(control_frame, text="🔍 Analyze Quest Progress", 
                  command=self.analyze_signet_quest_progress,
                  style='Accent.TButton').pack(side='left', padx=(0,10))
        
        ttk.Button(control_frame, text="📊 Show All Quest Items", 
                  command=self.show_all_quest_items).pack(side='left', padx=(0,10))
        
        ttk.Button(control_frame, text="💾 Export Quest Report", 
                  command=self.export_quest_report).pack(side='left')
        
        # Quest progress display
        progress_frame = ttk.LabelFrame(main_container, text="📈 Quest Progress")
        progress_frame.pack(fill='both', expand=True)
        
        # Create notebook for quest tabs
        self.quest_notebook = ttk.Notebook(progress_frame)
        self.quest_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Overview tab
        self.create_quest_overview_tab()
        
        # Individual quest tabs
        for quest_num in range(1, 8):
            self.create_individual_quest_tab(quest_num)
        
        # Items to Farm tab
        self.create_items_to_farm_tab()
    
    def create_quest_overview_tab(self):
        """Create the quest overview tab."""
        overview_frame = ttk.Frame(self.quest_notebook)
        self.quest_notebook.add(overview_frame, text="📊 Overview")
        
        # Progress summary
        summary_frame = ttk.LabelFrame(overview_frame, text="Quest Chain Progress")
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        self.quest_summary_text = tk.Text(summary_frame, height=12, wrap='word', 
                                         font=('Consolas', 10), state='disabled')
        self.quest_summary_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Initialize with placeholder
        self.quest_summary_text.config(state='normal')
        self.quest_summary_text.insert(1.0, "Click 'Analyze Quest Progress' to see your progress through the Signet of Might quest chain.")
        self.quest_summary_text.config(state='disabled')
        
        # Common items across quests
        common_frame = ttk.LabelFrame(overview_frame, text="Common Items Across Quests")
        common_frame.pack(fill='both', expand=True, padx=10, pady=(0,10))
        
        # Create treeview for common items
        common_columns = ('Item', 'Total Needed', 'Used In Quests', 'Source')
        self.common_items_tree = ttk.Treeview(common_frame, columns=common_columns, show='headings', height=8)
        
        for col in common_columns:
            self.common_items_tree.heading(col, text=col)
            if col == 'Item':
                self.common_items_tree.column(col, width=200)
            elif col == 'Used In Quests':
                self.common_items_tree.column(col, width=150)
            elif col == 'Source':
                self.common_items_tree.column(col, width=250)
            else:
                self.common_items_tree.column(col, width=100)
        
        common_scrollbar = ttk.Scrollbar(common_frame, orient='vertical', command=self.common_items_tree.yview)
        self.common_items_tree.configure(yscrollcommand=common_scrollbar.set)
        
        self.common_items_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        common_scrollbar.pack(side='right', fill='y', pady=10)
        
        # Populate common items
        self.populate_common_items()
    
    def create_individual_quest_tab(self, quest_num):
        """Create a tab for an individual quest."""
        quest_data = self.signet_quest.quest_chain[quest_num]
        quest_name = quest_data['name']
        
        quest_frame = ttk.Frame(self.quest_notebook)
        self.quest_notebook.add(quest_frame, text=f"{quest_num}. {quest_name}")
        
        # Quest description
        desc_frame = ttk.LabelFrame(quest_frame, text=f"Quest {quest_num}: {quest_name}")
        desc_frame.pack(fill='x', padx=10, pady=10)
        
        desc_text = tk.Text(desc_frame, height=3, wrap='word', font=('Arial', 9),
                           bg='#f8f8f8', relief='flat', state='disabled')
        desc_text.pack(fill='x', padx=10, pady=5)
        
        desc_content = quest_data['description']
        if 'prerequisite' in quest_data:
            desc_content += f"\nPrerequisite: {quest_data['prerequisite']}"
        
        desc_text.config(state='normal')
        desc_text.insert(1.0, desc_content)
        desc_text.config(state='disabled')
        
        # Key items needed
        items_frame = ttk.LabelFrame(quest_frame, text="Key Items Needed (💡 Double-click crafted items for recipe details)")
        items_frame.pack(fill='both', expand=True, padx=10, pady=(0,10))
        
        # Create treeview for quest items
        item_columns = ('Item', 'Qty', 'Owned', 'Status', 'Source', 'Type')
        quest_tree = ttk.Treeview(items_frame, columns=item_columns, show='headings', height=10)
        
        for col in item_columns:
            quest_tree.heading(col, text=col)
            if col == 'Item':
                quest_tree.column(col, width=200)
            elif col == 'Source':
                quest_tree.column(col, width=250)
            elif col in ['Qty', 'Owned']:
                quest_tree.column(col, width=60)
            elif col == 'Status':
                quest_tree.column(col, width=80)
            else:
                quest_tree.column(col, width=100)
        
        quest_scrollbar = ttk.Scrollbar(items_frame, orient='vertical', command=quest_tree.yview)
        quest_tree.configure(yscrollcommand=quest_scrollbar.set)
        
        quest_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        quest_scrollbar.pack(side='right', fill='y', pady=10)
        
        # Store reference to the treeview
        setattr(self, f'quest_{quest_num}_tree', quest_tree)
        
        # Bind double-click event for recipe details
        quest_tree.bind('<Double-1>', lambda event, qnum=quest_num: self.on_quest_item_double_click(event, qnum))
        
        # Populate with quest items (will be updated when analysis is run)
        key_items = quest_data.get('key_items', {})
        for item_name, item_info in key_items.items():
            quest_tree.insert('', 'end', values=(
                item_name,
                item_info['quantity'],
                '?',  # Will be filled during analysis
                '?',  # Will be filled during analysis
                item_info['source'],
                item_info['type'].title()
            ))
    
    def populate_common_items(self):
        """Populate the common items tree with items used across multiple quests."""
        all_items = self.signet_quest.get_all_unique_items()
        
        # Filter to show only items used in multiple quests or high quantities
        common_items = {name: data for name, data in all_items.items() 
                       if len(data['used_in_quests']) > 1 or data['total_quantity'] > 1}
        
        for item_name, item_data in common_items.items():
            quests_str = ', '.join(item_data['used_in_quests'])
            sources_str = ', '.join(item_data['sources'])
            
            self.common_items_tree.insert('', 'end', values=(
                item_name,
                item_data['total_quantity'],
                quests_str,
                sources_str
            ))
    
    def analyze_signet_quest_progress(self):
        """Analyze inventory for Signet of Might quest progress."""
        if self.items_df.empty:
            messagebox.showwarning("Warning", "No inventory data loaded")
            return
        
        # Get progress for all quests
        progress = self.signet_quest.get_quest_progress_summary(self.items_df)
        
        # Update overview
        self.update_quest_overview(progress)
        
        # Update individual quest tabs
        for quest_num in range(1, 8):
            quest_name = self.signet_quest.quest_chain[quest_num]['name']
            if quest_name in progress:
                self.update_individual_quest_tab(quest_num, progress[quest_name])
        
        messagebox.showinfo("Analysis Complete", "Quest progress analysis completed! Check the Overview tab for summary.")
    
    def update_quest_overview(self, progress):
        """Update the quest overview with progress data."""
        overview_lines = []
        overview_lines.append("🏺 SIGNET OF MIGHT QUEST PROGRESS")
        overview_lines.append("=" * 50)
        overview_lines.append("")
        
        total_quests = len(progress)
        completed_quests = len([q for q in progress.values() if q['can_complete']])
        
        overview_lines.append(f"Overall Progress: {completed_quests}/{total_quests} quests ready")
        overview_lines.append("")
        
        for quest_num in range(1, 8):
            quest_data = self.signet_quest.quest_chain[quest_num]
            quest_name = quest_data['name']
            
            if quest_name in progress:
                quest_progress = progress[quest_name]
                status_icon = "✅" if quest_progress['can_complete'] else "❌"
                percentage = quest_progress['progress_percentage']
                satisfied = quest_progress['items_satisfied']
                total = quest_progress['total_items']
                
                overview_lines.append(f"{status_icon} Quest {quest_num}: {quest_name}")
                overview_lines.append(f"   Progress: {satisfied}/{total} items ({percentage:.1f}%)")
                
                if not quest_progress['can_complete'] and quest_progress['missing_items']:
                    missing_count = len(quest_progress['missing_items'])
                    overview_lines.append(f"   Missing: {missing_count} items")
                    
                    # Show first few missing items
                    for i, (item_name, item_info) in enumerate(list(quest_progress['missing_items'].items())[:3]):
                        overview_lines.append(f"     • {item_name} (need {item_info['needed']})")
                    
                    if missing_count > 3:
                        overview_lines.append(f"     ... and {missing_count - 3} more")
                
                overview_lines.append("")
        
        # Update the text widget
        self.quest_summary_text.config(state='normal')
        self.quest_summary_text.delete(1.0, tk.END)
        self.quest_summary_text.insert(1.0, "\n".join(overview_lines))
        self.quest_summary_text.config(state='disabled')
    
    def update_individual_quest_tab(self, quest_num, quest_progress):
        """Update an individual quest tab with progress data."""
        quest_tree = getattr(self, f'quest_{quest_num}_tree')
        
        # Clear existing items
        for item in quest_tree.get_children():
            quest_tree.delete(item)
        
        # Repopulate with updated data
        quest_data = self.signet_quest.quest_chain[quest_num]
        key_items = quest_data.get('key_items', {})
        
        for item_name, item_info in key_items.items():
            if item_name in quest_progress['owned_items']:
                owned_data = quest_progress['owned_items'][item_name]
                owned_qty = owned_data['owned']
                required_qty = owned_data['required']
                status = "✅ Ready" if owned_data['satisfied'] else f"❌ Need {required_qty - owned_qty}"
            else:
                owned_qty = 0
                required_qty = item_info['quantity']
                status = f"❌ Need {required_qty}"
            
            quest_tree.insert('', 'end', values=(
                item_name,
                required_qty,
                owned_qty,
                status,
                item_info['source'],
                item_info['type'].title()
            ))
    
    def show_all_quest_items(self):
        """Show all quest items in the main search results."""
        if self.items_df.empty:
            messagebox.showwarning("Warning", "No inventory data loaded")
            return
        
        # Get all unique items from all quests
        all_items = self.signet_quest.get_all_unique_items()
        item_names = list(all_items.keys())
        
        # Create a regex pattern to match any quest item
        search_pattern = "|".join([f"({name.replace('(', '\\(').replace(')', '\\)')})" for name in item_names])
        
        # Perform search
        search_results = self.search_items(search_pattern, character=None, exact_match=False, item_type=None)
        
        # Display results
        self.display_results(search_results, "All Signet of Might Quest Items")
    
    def export_quest_report(self):
        """Export a detailed quest progress report."""
        if self.items_df.empty:
            messagebox.showwarning("Warning", "No inventory data loaded")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Quest Report"
        )
        
        if not filename:
            return
        
        try:
            # Get progress for all quests
            progress = self.signet_quest.get_quest_progress_summary(self.items_df)
            
            report_lines = []
            report_lines.append("SIGNET OF MIGHT QUEST PROGRESS REPORT")
            report_lines.append("=" * 60)
            report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")
            
            # Overall summary
            total_quests = len(progress)
            completed_quests = len([q for q in progress.values() if q['can_complete']])
            report_lines.append(f"Overall Progress: {completed_quests}/{total_quests} quests ready")
            report_lines.append("")
            
            # Detailed quest breakdown
            for quest_num in range(1, 8):
                quest_data = self.signet_quest.quest_chain[quest_num]
                quest_name = quest_data['name']
                
                report_lines.append(f"QUEST {quest_num}: {quest_name.upper()}")
                report_lines.append("-" * 40)
                report_lines.append(f"Description: {quest_data['description']}")
                
                if 'prerequisite' in quest_data:
                    report_lines.append(f"Prerequisite: {quest_data['prerequisite']}")
                
                if quest_name in progress:
                    quest_progress = progress[quest_name]
                    status = "READY" if quest_progress['can_complete'] else "NOT READY"
                    percentage = quest_progress['progress_percentage']
                    satisfied = quest_progress['items_satisfied']
                    total = quest_progress['total_items']
                    
                    report_lines.append(f"Status: {status}")
                    report_lines.append(f"Progress: {satisfied}/{total} items ({percentage:.1f}%)")
                    report_lines.append("")
                    
                    # Items breakdown
                    report_lines.append("Items Status:")
                    for item_name, item_data in quest_progress['owned_items'].items():
                        owned = item_data['owned']
                        required = item_data['required']
                        status_icon = "✅" if item_data['satisfied'] else "❌"
                        report_lines.append(f"  {status_icon} {item_name}: {owned}/{required} ({item_data['source']})")
                    
                    if quest_progress['missing_items']:
                        report_lines.append("")
                        report_lines.append("Missing Items:")
                        for item_name, item_data in quest_progress['missing_items'].items():
                            report_lines.append(f"  • {item_name}: Need {item_data['needed']} ({item_data['source']})")
                
                report_lines.append("")
                report_lines.append("")
            
            # Write report to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(report_lines))
            
            messagebox.showinfo("Export Successful", f"Quest report exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export quest report:\n{e}")
    
    def on_quest_item_double_click(self, event, quest_num):
        """Handle double-click on quest items to show recipe details."""
        quest_tree = getattr(self, f'quest_{quest_num}_tree')
        selection = quest_tree.selection()
        
        if not selection:
            return
        
        # Get the selected item
        item = quest_tree.item(selection[0])
        item_name = item['values'][0]
        
        # Get quest data
        quest_data = self.signet_quest.quest_chain[quest_num]
        key_items = quest_data.get('key_items', {})
        
        if item_name not in key_items:
            return
        
        item_info = key_items[item_name]
        
        # Check if this item has a recipe
        if item_info.get('type') == 'crafted' and 'recipe' in item_info:
            self.show_recipe_details(item_name, item_info['recipe'])
        else:
            # Show basic item information
            self.show_item_details(item_name, item_info)
    
    def show_recipe_details(self, item_name, recipe_data):
        """Show detailed recipe information in a popup window."""
        popup = tk.Toplevel(self.root)
        popup.title(f"Recipe Details: {item_name}")
        popup.geometry("800x700")
        popup.configure(bg='#f0f0f0')
        
        # Make it modal
        popup.transient(self.root)
        popup.grab_set()
        
        # Main container
        main_frame = ttk.Frame(popup)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"📜 Recipe: {item_name}", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0,10))
        
        # Recipe info
        info_frame = ttk.LabelFrame(main_frame, text="Recipe Information")
        info_frame.pack(fill='x', pady=(0,10))
        
        info_inner = ttk.Frame(info_frame)
        info_inner.pack(fill='x', padx=10, pady=5)
        
        # Recipe details
        recipe_info = []
        recipe_info.append(f"Skill: {recipe_data.get('skill', 'Unknown')}")
        recipe_info.append(f"Trivial: {recipe_data.get('trivial', 'Unknown')}")
        recipe_info.append(f"Container: {recipe_data.get('container', 'Unknown')}")
        recipe_info.append(f"Yields: {recipe_data.get('yields', 1)}")
        
        if 'note' in recipe_data:
            recipe_info.append(f"Note: {recipe_data['note']}")
        
        info_text = tk.Text(info_inner, height=4, wrap='word', font=('Arial', 10),
                           bg='#f8f8f8', relief='flat', state='disabled')
        info_text.pack(fill='x')
        
        info_text.config(state='normal')
        info_text.insert(1.0, '\n'.join(recipe_info))
        info_text.config(state='disabled')
        
        # Components
        components_frame = ttk.LabelFrame(main_frame, text="Required Components")
        components_frame.pack(fill='both', expand=True, pady=(0,10))
        
        # Create notebook for components (in case of nested recipes)
        components_notebook = ttk.Notebook(components_frame)
        components_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Main components tab
        main_components_frame = ttk.Frame(components_notebook)
        components_notebook.add(main_components_frame, text="Components")
        
        # Create treeview for components
        comp_columns = ('Component', 'Qty', 'Type', 'Source', 'Notes')
        comp_tree = ttk.Treeview(main_components_frame, columns=comp_columns, show='headings', height=12)
        
        for col in comp_columns:
            comp_tree.heading(col, text=col)
            if col == 'Component':
                comp_tree.column(col, width=200)
            elif col == 'Source':
                comp_tree.column(col, width=250)
            elif col == 'Notes':
                comp_tree.column(col, width=200)
            elif col == 'Qty':
                comp_tree.column(col, width=60)
            else:
                comp_tree.column(col, width=100)
        
        comp_scrollbar = ttk.Scrollbar(main_components_frame, orient='vertical', command=comp_tree.yview)
        comp_tree.configure(yscrollcommand=comp_scrollbar.set)
        
        comp_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        comp_scrollbar.pack(side='right', fill='y', pady=5)
        
        # Populate components
        components = recipe_data.get('components', {})
        sub_recipes = {}
        
        for comp_name, comp_info in components.items():
            comp_type = comp_info.get('type', 'unknown')
            comp_qty = comp_info.get('quantity', 1)
            comp_source = comp_info.get('source', 'Unknown')
            comp_notes = comp_info.get('note', '')
            
            # Check if this component has a sub-recipe
            if comp_type == 'crafted' and 'recipe' in comp_info:
                comp_notes = f"Crafted - Double-click for recipe"
                sub_recipes[comp_name] = comp_info['recipe']
            
            comp_tree.insert('', 'end', values=(
                comp_name,
                comp_qty,
                comp_type.title(),
                comp_source,
                comp_notes
            ))
        
        # Bind double-click for sub-recipes
        def on_component_double_click(event):
            selection = comp_tree.selection()
            if selection:
                comp_item = comp_tree.item(selection[0])
                comp_name = comp_item['values'][0]
                if comp_name in sub_recipes:
                    self.show_recipe_details(comp_name, sub_recipes[comp_name])
        
        comp_tree.bind('<Double-1>', on_component_double_click)
        
        # Add sub-recipe tabs if any exist
        for sub_name, sub_recipe in sub_recipes.items():
            sub_frame = ttk.Frame(components_notebook)
            components_notebook.add(sub_frame, text=f"📜 {sub_name}")
            
            # Sub-recipe info
            sub_info_frame = ttk.LabelFrame(sub_frame, text=f"Sub-Recipe: {sub_name}")
            sub_info_frame.pack(fill='x', padx=5, pady=5)
            
            sub_info_inner = ttk.Frame(sub_info_frame)
            sub_info_inner.pack(fill='x', padx=5, pady=5)
            
            sub_recipe_info = []
            sub_recipe_info.append(f"Skill: {sub_recipe.get('skill', 'Unknown')}")
            sub_recipe_info.append(f"Trivial: {sub_recipe.get('trivial', 'Unknown')}")
            sub_recipe_info.append(f"Container: {sub_recipe.get('container', 'Unknown')}")
            sub_recipe_info.append(f"Yields: {sub_recipe.get('yields', 1)}")
            
            if 'note' in sub_recipe:
                sub_recipe_info.append(f"Note: {sub_recipe['note']}")
            
            sub_info_text = tk.Text(sub_info_inner, height=3, wrap='word', font=('Arial', 9),
                                   bg='#f8f8f8', relief='flat', state='disabled')
            sub_info_text.pack(fill='x')
            
            sub_info_text.config(state='normal')
            sub_info_text.insert(1.0, '\n'.join(sub_recipe_info))
            sub_info_text.config(state='disabled')
            
            # Sub-components
            sub_comp_frame = ttk.LabelFrame(sub_frame, text="Components")
            sub_comp_frame.pack(fill='both', expand=True, padx=5, pady=5)
            
            sub_comp_tree = ttk.Treeview(sub_comp_frame, columns=comp_columns, show='headings', height=8)
            
            for col in comp_columns:
                sub_comp_tree.heading(col, text=col)
                if col == 'Component':
                    sub_comp_tree.column(col, width=150)
                elif col == 'Source':
                    sub_comp_tree.column(col, width=200)
                elif col == 'Notes':
                    sub_comp_tree.column(col, width=150)
                elif col == 'Qty':
                    sub_comp_tree.column(col, width=50)
                else:
                    sub_comp_tree.column(col, width=80)
            
            sub_comp_scrollbar = ttk.Scrollbar(sub_comp_frame, orient='vertical', command=sub_comp_tree.yview)
            sub_comp_tree.configure(yscrollcommand=sub_comp_scrollbar.set)
            
            sub_comp_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
            sub_comp_scrollbar.pack(side='right', fill='y', pady=5)
            
            # Populate sub-components
            sub_components = sub_recipe.get('components', {})
            for sub_comp_name, sub_comp_info in sub_components.items():
                sub_comp_type = sub_comp_info.get('type', 'unknown')
                sub_comp_qty = sub_comp_info.get('quantity', 1)
                sub_comp_source = sub_comp_info.get('source', 'Unknown')
                sub_comp_notes = sub_comp_info.get('note', '')
                
                sub_comp_tree.insert('', 'end', values=(
                    sub_comp_name,
                    sub_comp_qty,
                    sub_comp_type.title(),
                    sub_comp_source,
                    sub_comp_notes
                ))
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructions")
        instructions_frame.pack(fill='x', pady=(0,10))
        
        instructions_text = tk.Text(instructions_frame, height=3, wrap='word', font=('Arial', 9),
                                   bg='#f8f8f8', relief='flat', state='disabled')
        instructions_text.pack(fill='x', padx=10, pady=5)
        
        instructions_content = f"1. Gather all required components listed above\n"
        instructions_content += f"2. Use a {recipe_data.get('container', 'crafting container')}\n"
        instructions_content += f"3. Combine components (trivial: {recipe_data.get('trivial', 'Unknown')})\n"
        
        if 'note' in recipe_data:
            instructions_content += f"4. Note: {recipe_data['note']}"
        
        instructions_text.config(state='normal')
        instructions_text.insert(1.0, instructions_content)
        instructions_text.config(state='disabled')
        
        # Close button
        close_frame = ttk.Frame(main_frame)
        close_frame.pack(fill='x', pady=(10,0))
        
        ttk.Button(close_frame, text="Close", command=popup.destroy).pack(side='right')
        
        # Search for components button
        ttk.Button(close_frame, text="🔍 Search for Components", 
                  command=lambda: self.search_recipe_components(item_name, recipe_data)).pack(side='left')
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
    
    def show_item_details(self, item_name, item_info):
        """Show basic item information for non-crafted items."""
        popup = tk.Toplevel(self.root)
        popup.title(f"Item Details: {item_name}")
        popup.geometry("500x300")
        popup.configure(bg='#f0f0f0')
        
        # Make it modal
        popup.transient(self.root)
        popup.grab_set()
        
        # Main container
        main_frame = ttk.Frame(popup)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"📦 Item: {item_name}", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0,10))
        
        # Item info
        info_frame = ttk.LabelFrame(main_frame, text="Item Information")
        info_frame.pack(fill='both', expand=True, pady=(0,10))
        
        info_text = tk.Text(info_frame, wrap='word', font=('Arial', 10),
                           bg='#f8f8f8', relief='flat', state='disabled')
        info_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Build item info
        item_details = []
        item_details.append(f"Item: {item_name}")
        item_details.append(f"Type: {item_info.get('type', 'Unknown').title()}")
        item_details.append(f"Quantity Needed: {item_info.get('quantity', 1)}")
        item_details.append(f"Source: {item_info.get('source', 'Unknown')}")
        
        if 'note' in item_info:
            item_details.append(f"Note: {item_info['note']}")
        
        # Add acquisition tips based on type
        item_details.append("")
        item_details.append("Acquisition Tips:")
        
        item_type = item_info.get('type', '').lower()
        if item_type == 'vendor':
            item_details.append("• Purchase from the specified vendor")
            item_details.append("• Bring sufficient platinum/gold")
        elif item_type == 'drop':
            item_details.append("• Hunt the specified mobs/zones")
            item_details.append("• May require multiple kills for rare drops")
        elif item_type == 'quest':
            item_details.append("• Complete the specified quest")
            item_details.append("• Check prerequisites and faction requirements")
        elif item_type == 'foraged':
            item_details.append("• Use Forage skill in specified zones")
            item_details.append("• Higher skill increases success rate")
        elif item_type == 'ground_spawn':
            item_details.append("• Look for ground spawns in specified areas")
            item_details.append("• Respawn times may vary")
        
        info_text.config(state='normal')
        info_text.insert(1.0, '\n'.join(item_details))
        info_text.config(state='disabled')
        
        # Close button
        close_frame = ttk.Frame(main_frame)
        close_frame.pack(fill='x', pady=(10,0))
        
        ttk.Button(close_frame, text="Close", command=popup.destroy).pack(side='right')
        
        # Search for item button
        ttk.Button(close_frame, text="🔍 Search in Inventory", 
                  command=lambda: self.search_for_item(item_name)).pack(side='left')
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
    
    def search_recipe_components(self, recipe_name, recipe_data):
        """Search for all components of a recipe in inventory."""
        if self.items_df.empty:
            messagebox.showwarning("Warning", "No inventory data loaded")
            return
        
        components = recipe_data.get('components', {})
        if not components:
            messagebox.showinfo("No Components", f"No components found for {recipe_name}")
            return
        
        # Create search pattern for all components
        component_names = list(components.keys())
        search_pattern = "|".join([f"({name.replace('(', '\\(').replace(')', '\\)')})" for name in component_names])
        
        # Perform search
        search_results = self.search_items(search_pattern, character=None, exact_match=False, item_type=None)
        
        # Display results
        self.display_results(search_results, f"Components for {recipe_name}")
    
    def search_for_item(self, item_name):
        """Search for a specific item in inventory."""
        if self.items_df.empty:
            messagebox.showwarning("Warning", "No inventory data loaded")
            return
        
        # Perform search
        search_results = self.search_items(item_name, character=None, exact_match=False, item_type=None)
        
        # Display results
        self.display_results(search_results, f"Search: {item_name}")
    
    def create_items_to_farm_tab(self):
        """Create the Items to Farm tab showing all dropped items needed for the quest."""
        farm_frame = ttk.Frame(self.quest_notebook)
        self.quest_notebook.add(farm_frame, text="🎯 Items to Farm")
        
        # Title and description
        title_frame = ttk.Frame(farm_frame)
        title_frame.pack(fill='x', padx=10, pady=10)
        
        title_label = ttk.Label(title_frame, text="🎯 Items to Farm", 
                               font=('Arial', 14, 'bold'))
        title_label.pack()
        
        desc_label = ttk.Label(title_frame, 
                              text="All dropped items needed for the Signet of Might quest chain",
                              font=('Arial', 10))
        desc_label.pack(pady=(5,0))
        
        # Create treeview for farming items
        farm_columns = ('Item', 'Qty', 'Zone/Location', 'Mob/Source', 'Drop Rate', 'Quest', 'Notes')
        self.farm_tree = ttk.Treeview(farm_frame, columns=farm_columns, show='headings', height=20)
        
        for col in farm_columns:
            self.farm_tree.heading(col, text=col)
            if col == 'Item':
                self.farm_tree.column(col, width=200)
            elif col == 'Zone/Location':
                self.farm_tree.column(col, width=150)
            elif col == 'Mob/Source':
                self.farm_tree.column(col, width=150)
            elif col == 'Notes':
                self.farm_tree.column(col, width=200)
            elif col == 'Qty':
                self.farm_tree.column(col, width=50)
            elif col == 'Drop Rate':
                self.farm_tree.column(col, width=80)
            else:
                self.farm_tree.column(col, width=100)
        
        farm_scrollbar = ttk.Scrollbar(farm_frame, orient='vertical', command=self.farm_tree.yview)
        self.farm_tree.configure(yscrollcommand=farm_scrollbar.set)
        
        self.farm_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        farm_scrollbar.pack(side='right', fill='y', pady=10)
        
        # Populate farming items
        self.populate_farming_items()
    
    def populate_farming_items(self):
        """Populate the farming items tree with all dropped items from the quest chain."""
        farming_items = [
            # Blacksmithing Quest
            ("Drop of Pure Rain", 1, "Bastion of Thunder", "Vann mobs", "Rare", "Blacksmithing", "Rare drop from thunder elementals"),
            ("Sandstorm Pearl", 3, "Bastion of Thunder", "Jord mobs", "Uncommon", "Blacksmithing", "Earth elementals in BoT"),
            ("Storm Rider Blood", 1, "Bastion of Thunder", "Stormrider mobs", "Common", "Blacksmithing", "Flying storm creatures"),
            ("Raw Diamond", 2, "Various Zones", "Random world drop", "Rare", "Blacksmithing", "Can be found in many zones"),
            ("Nightmare Mephit Blood", 2, "Plane of Nightmare", "Nightmare mephits", "Common", "Blacksmithing", "Small flying creatures in PoN"),
            
            # Jewelcrafting Quest
            ("Blue Diamond", 1, "Various Zones", "Random world drop", "Rare", "Jewelcrafting", "Rare gem, check vendors too"),
            ("Branch of Sylvan Oak", 1, "Eastern Wastes/Wakening Lands", "Foraged", "Uncommon", "Jewelcrafting", "Forage skill required"),
            
            # Pottery Quest
            ("Iron Oxide", 1, "Various Zones", "Various mobs", "Uncommon", "Pottery", "Metallic creatures often drop"),
            ("Permafrost Crystals", 1, "Permafrost/Everfrost", "Ice creatures", "Uncommon", "Pottery", "Cold climate zones"),
            ("Sacred Water", 1, "Plane of Tranquility", "Various sources", "Uncommon", "Pottery", "Holy/divine creatures"),
            
            # Tailoring Quest
            ("Fire Mephit Blood", 1, "Plane of Fire", "Fire mephits", "Common", "Tailoring", "Small fire elementals"),
            ("Molten Ore", 1, "Plane of Fire", "Fire elementals", "Uncommon", "Tailoring", "Large fire creatures"),
            ("Obsidianwood Sap", 1, "Plane of Fire", "Burning trees", "Uncommon", "Tailoring", "Tree-like creatures in PoF"),
            ("Fire Arachnid Silk", 1, "Plane of Fire", "Fire spiders", "Uncommon", "Tailoring", "Spider creatures in PoF"),
            
            # Fletching Quest
            ("Featherwood Bowstave", 1, "Plane of Air", "Air elementals", "Uncommon", "Fletching", "Flying creatures in PoA"),
            ("Air Arachnid Silk", 2, "Plane of Air", "Air spiders", "Uncommon", "Fletching", "Spider creatures in PoA"),
            ("Chunk of Wind Metal", 2, "Plane of Air", "Air elementals", "Common", "Fletching", "For Wind Metal Bow Cam"),
            ("Clockwork Grease", 2, "Plane of Innovation", "Foraged", "Common", "Fletching", "Forage in mechanical areas"),
            
            # Baking Quest
            ("Hero Parts", 1, "Various Zones", "Heroic NPCs", "Uncommon", "Baking", "Named or heroic creatures"),
            ("Slarghilug Leg", 1, "Plane of Disease", "Slarghilug", "Uncommon", "Baking", "Large disease creatures"),
            ("Habanero Pepper", 1, "Various Zones", "Foraged", "Common", "Baking", "Hot climate zones"),
            ("Planar Fruit", 2, "Elemental Planes", "Foraged", "Uncommon", "Baking", "Any elemental plane"),
            
            # Final Quest
            ("Hope Stone", 1, "Elemental Planes", "Random rare drop", "Very Rare", "Final", "Extremely rare, any elemental plane"),
            
            # Ground Spawns
            ("Strange Dark Fungus", 6, "North Kaladim", "Ground spawn", "Common", "Brewing", "Farm area, 6min respawn"),
            ("Underfoot Mushroom", 6, "North Kaladim", "Ground spawn", "Common", "Brewing", "Farm area, 6min respawn"),
        ]
        
        for item_data in farming_items:
            self.farm_tree.insert('', 'end', values=item_data)

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    try:
        app = EQInventoryGUI()
        app.run()
    except Exception as e:
        import traceback
        error_msg = f"Error starting application:\n{e}\n\nFull traceback:\n{traceback.format_exc()}"
        
        # Try to show error in messagebox, fallback to print
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            messagebox.showerror("Application Error", error_msg)
        except:
            print(error_msg)
        finally:
            input("Press Enter to close...")


if __name__ == '__main__':
    main()

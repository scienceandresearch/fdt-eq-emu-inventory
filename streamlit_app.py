import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re
from signet_of_might_data import SignetOfMightQuest

# Page config
st.set_page_config(
    page_title="FDT EQ Emu Inventory Parser",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    text-align: center;
    padding: 1rem 0;
    background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
    color: white;
    border-radius: 10px;
    margin-bottom: 2rem;
}
.stButton > button {
    width: 100%;
    margin: 2px 0;
}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🎮 FDT EQ Emu Inventory Parser</h1>
    <p><em>Find DnK's Tulwar - Advanced inventory search for EverQuest Emulator servers</em></p>
    <p><strong>Web Version - Always Up to Date!</strong></p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'items_df' not in st.session_state:
    st.session_state.items_df = pd.DataFrame()
if 'search_term' not in st.session_state:
    st.session_state.search_term = ""
if 'zeb_results' not in st.session_state:
    st.session_state.zeb_results = None

# Helper function
def categorize_location(location):
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

# Sidebar for file upload and info
with st.sidebar:
    st.header("📁 Upload Inventory Files")
    st.markdown("Upload your `*-Inventory.txt` files to get started!")
    
    uploaded_files = st.file_uploader(
        "Select inventory files",
        accept_multiple_files=True,
        type=['txt'],
        help="Upload multiple character inventory files at once"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} files uploaded")
    
    st.markdown("---")
    st.subheader("📖 Quick Guide")
    st.markdown("""
    **Getting Your Files:**
    - Login to your character in EverQuest
    - Run `/outputfile inventory` in-game
    - If in the Bazaar, it captures bank slots too!
    - Find `CharacterName-Inventory.txt` in your EQ folder
    
    **Using the Tool:**
    - 📤 Upload one or more inventory files above
    - 🔍 Use search to find your Tulwar (or any item!)
    - ⚡ Try quick search buttons for common items
    - 🗡️ Check Zeb weapon components
    - 💾 Export results to CSV files
    """)
    
    st.markdown("---")
    st.markdown("**🔗 Links:**")
    st.markdown("[📥 Download Desktop Version](https://github.com/scienceandresearch/fdt-eq-emu-inventory)")
    st.markdown("[🐛 Report Issues](https://github.com/scienceandresearch/fdt-eq-emu-inventory/issues)")

# Main app logic
if uploaded_files:
    # Process files with caching for better performance
    @st.cache_data
    def load_web_inventory_files(files):
        result_list = []
        
        for file in files:
            try:
                # Read uploaded file
                content = file.read().decode('utf-8')
                lines = content.strip().split('\n')
                
                if len(lines) < 2:
                    st.warning(f"⚠️ {file.name} appears to be empty or invalid")
                    continue
                
                # Parse tab-separated data
                data = []
                headers = lines[0].split('\t')
                for line in lines[1:]:
                    if line.strip():  # Skip empty lines
                        data.append(line.split('\t'))
                
                if not data:
                    continue
                
                df = pd.DataFrame(data, columns=headers)
                
                # Extract character name from filename
                char_name = file.name.replace('-Inventory.txt', '').replace('.txt', '')
                
                # Handle shared bank deduplication (simplified for web)
                shared_bank_items = df[df['Location'].str.startswith('SharedBank', na=False)].copy()
                character_items = df[~df['Location'].str.startswith('SharedBank', na=False)].copy()
                
                # Add character name
                character_items.insert(0, 'Character', char_name)
                character_items['IsEmpty'] = character_items['Name'] == 'Empty'
                character_items['ItemType'] = character_items['Location'].apply(categorize_location)
                
                result_list.append(character_items)
                
                # Simple shared bank handling
                if not shared_bank_items.empty:
                    shared_bank_items.insert(0, 'Character', 'SHARED-BANK')
                    shared_bank_items['IsEmpty'] = shared_bank_items['Name'] == 'Empty'
                    shared_bank_items['ItemType'] = shared_bank_items['Location'].apply(categorize_location)
                    
                    # Only add if we haven't seen this shared bank before
                    if 'SHARED-BANK' not in [df['Character'].iloc[0] for df in result_list if not df.empty]:
                        result_list.append(shared_bank_items)
                
            except Exception as e:
                st.error(f"❌ Error processing {file.name}: {str(e)}")
                continue
        
        if result_list:
            final_df = pd.concat(result_list, ignore_index=True)
            return final_df
        return pd.DataFrame()
    
    # Load data
    with st.spinner("🔄 Processing inventory files..."):
        items_df = load_web_inventory_files(uploaded_files)
        st.session_state.items_df = items_df
    
    if not items_df.empty:
        # Statistics Dashboard
        st.subheader("📊 Inventory Overview")
        
        total_items = len(items_df)
        non_empty_items = len(items_df[items_df['IsEmpty'] == False])
        characters = items_df['Character'].nunique()
        empty_slots = len(items_df[items_df['IsEmpty'] == True])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Characters", characters)
        with col2:
            st.metric("📦 Total Items", f"{non_empty_items:,}")
        with col3:
            st.metric("🕳️ Empty Slots", f"{empty_slots:,}")
        with col4:
            st.metric("📁 Files Loaded", len(uploaded_files))
        
        # Character breakdown
        with st.expander("👥 Character Details", expanded=False):
            char_summary = items_df.groupby('Character').agg({
                'Name': lambda x: len(x[x != 'Empty']),
                'IsEmpty': lambda x: len(x[x == True])
            }).rename(columns={'Name': 'Items', 'IsEmpty': 'Empty_Slots'}).reset_index()
            
            st.dataframe(
                char_summary,
                width='stretch',
                hide_index=True
            )
        
        # Search Section
        st.subheader("🔍 Search Inventory")
        
        # Search controls
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            search_term = st.text_input("🔎 Item Name", 
                                      value=st.session_state.search_term,
                                      placeholder="Enter item name or pattern...")
        with col2:
            character_options = ['All'] + sorted([c for c in items_df['Character'].unique() if c != 'SHARED-BANK'])
            character = st.selectbox("👤 Character", character_options)
        with col3:
            item_type = st.selectbox("📂 Type", ['All', 'Equipped', 'Inventory', 'Bank'])
        with col4:
            st.write("") # Spacer
            exact_match = st.checkbox("Exact Match")
        
        # Condensed quick search buttons
        with st.expander("⚡ Quick Searches", expanded=False):
            # Equipment slots in 2 rows
            st.markdown("**⚔️ Equipment:**")
            eq_col1, eq_col2, eq_col3, eq_col4, eq_col5, eq_col6 = st.columns(6)
            
            if eq_col1.button("💍 Rings", key="ring_btn"):
                st.session_state.search_term = "Ring"
                st.rerun()
            if eq_col2.button("👑 Head", key="head_btn"):
                st.session_state.search_term = "Helm|Head"
                st.rerun()
            if eq_col3.button("👕 Chest", key="chest_btn"):
                st.session_state.search_term = "Chest|Breastplate|Robe|Tunic"
                st.rerun()
            if eq_col4.button("👖 Legs", key="legs_btn"):
                st.session_state.search_term = "Leg|Pant|Greave|Kilt"
                st.rerun()
            if eq_col5.button("👢 Feet", key="feet_btn"):
                st.session_state.search_term = "Feet|Boot|Shoe|Sandal"
                st.rerun()
            if eq_col6.button("🤚 Hands", key="hands_btn"):
                st.session_state.search_term = "Hand|Glove|Gauntlet"
                st.rerun()
            
            # Weapons and special items in one row
            st.markdown("**🗡️ Weapons & Special:**")
            quick_col1, quick_col2, quick_col3, quick_col4, quick_col5, quick_col6, quick_col7, quick_col8 = st.columns(8)
            
            if quick_col1.button("⚔️ Swords", key="sword_btn"):
                st.session_state.search_term = "Sword"
                st.rerun()
            if quick_col2.button("🗡️ Daggers", key="dagger_btn"):
                st.session_state.search_term = "Dagger"
                st.rerun()
            if quick_col3.button("🪓 Axes", key="axe_btn"):
                st.session_state.search_term = "Axe"
                st.rerun()
            if quick_col4.button("🔨 Maces", key="mace_btn"):
                st.session_state.search_term = "Mace"
                st.rerun()
            if quick_col5.button("🔮 Truth Fragments", key="truth_btn"):
                st.session_state.search_term = "Fragment of Truth"
                st.rerun()
            if quick_col6.button("⭐ Legendary", key="legendary_btn"):
                st.session_state.search_term = "Legendary"
                st.rerun()
            if quick_col7.button("🌟 Enchanted", key="enchanted_btn"):
                st.session_state.search_term = "Enchanted"
                st.rerun()
            if quick_col8.button("💎 Prismatic", key="prismatic_btn"):
                st.session_state.search_term = "Prismatic"
                st.rerun()
        
        # Use search term from session state if set by button
        if st.session_state.search_term and not search_term:
            search_term = st.session_state.search_term
        
        # Perform search
        if search_term:
            # Apply search logic (reuse from desktop version)
            df = items_df[items_df['IsEmpty'] == False].copy()
            
            if '|' in search_term:
                df = df[df['Name'].str.contains(search_term, case=False, na=False, regex=True)]
            elif exact_match:
                df = df[df['Name'].str.lower() == search_term.lower()]
            else:
                df = df[df['Name'].str.contains(search_term, case=False, na=False)]
            
            if character != 'All':
                df = df[df['Character'] == character]
            
            if item_type != 'All':
                df = df[df['ItemType'] == item_type]
            
            # Display results with enhanced highlighting
            st.markdown("---")
            st.success(f"📄 **Search Results:** '{search_term}' ({len(df)} items found)")
            
            if not df.empty:
                # Add action buttons
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    # Character summary for results
                    char_counts = df['Character'].value_counts()
                    if len(char_counts) > 1:
                        st.info(f"📊 Found across {len(char_counts)} characters: " + 
                                ", ".join([f"{char} ({count})" for char, count in char_counts.head(5).items()]))
                
                with col2:
                    # Export button
                    csv = df[['Character', 'Name', 'Location', 'ItemType', 'Count']].to_csv(index=False)
                    st.download_button(
                        "💾 Download Results CSV",
                        csv,
                        f"search_results_{search_term.replace('|', '_')}.csv",
                        "text/csv",
                        key="download_results"
                    )
                
                # Results table
                display_df = df[['Character', 'Name', 'Location', 'ItemType', 'Count']].copy()
                st.dataframe(
                    display_df,
                    width='stretch',
                    hide_index=True
                )
                
                # Find duplicates in results
                if len(df) > 1:
                    with st.expander(f"🔄 Find Duplicates in Results"):
                        duplicates = df.groupby(['Name', 'ID']).size().reset_index(name='Count')
                        duplicates = duplicates[duplicates['Count'] > 1]
                        
                        if not duplicates.empty:
                            st.dataframe(duplicates, hide_index=True)
                        else:
                            st.info("No duplicate items found in current results.")
            
            else:
                # Enhanced no results message
                st.markdown("---")
                st.warning(f"🔍 **No items found matching '{search_term}'**")
                st.info("""
                **💡 Search Tips:**
                - Try partial names (e.g., 'sword' instead of 'Legendary Sword')
                - Check spelling
                - Use broader search terms  
                - Try the Quick Search buttons above
                - Use regex patterns like `Sword|Axe|Mace` for multiple types
                """)
        
        # Signet of Might Quest Section
        st.markdown("---")
        st.header("🏺 Signet of Might Quest Tracker")
        st.markdown("*Track your progress through the Aid Grimel quest chain*")
        
        # Initialize quest data
        if 'signet_quest' not in st.session_state:
            st.session_state.signet_quest = SignetOfMightQuest()
        
        # Quest analysis controls
        quest_col1, quest_col2, quest_col3 = st.columns([2, 1, 1])
        
        with quest_col1:
            st.info("🎯 **Requirements:** Complete all 7 tradeskill quests (Blacksmithing → Brewing → Jewelcrafting → Pottery → Tailoring → Fletching → Baking)")
        
        with quest_col2:
            if st.button("🔍 Analyze Quest Progress", type="primary", key="analyze_quest"):
                with st.spinner("🔄 Analyzing quest progress..."):
                    progress = st.session_state.signet_quest.get_quest_progress_summary(items_df)
                    st.session_state.quest_progress = progress
                    st.success("Quest analysis complete!")
                    st.rerun()
        
        with quest_col3:
            if st.button("📊 Show All Quest Items", key="show_quest_items"):
                # Get all unique items from all quests
                all_items = st.session_state.signet_quest.get_all_unique_items()
                item_names = list(all_items.keys())
                
                # Create a regex pattern to match any quest item
                search_pattern = "|".join([f"({name.replace('(', '\\(').replace(')', '\\)')})" for name in item_names])
                
                # Perform search
                df_quest = items_df[items_df['IsEmpty'] == False].copy()
                df_quest = df_quest[df_quest['Name'].str.contains(search_pattern, case=False, na=False, regex=True)]
                
                st.markdown("---")
                st.success(f"📄 **All Signet of Might Quest Items** ({len(df_quest)} items found)")
                
                if not df_quest.empty:
                    display_df = df_quest[['Character', 'Name', 'Location', 'ItemType', 'Count']].copy()
                    st.dataframe(display_df, width='stretch', hide_index=True)
                else:
                    st.info("No quest items found in your inventory.")
        
        # Show quest progress if available
        if 'quest_progress' in st.session_state:
            progress = st.session_state.quest_progress
            
            st.subheader("📈 Quest Chain Progress")
            
            # Overall progress metrics
            total_quests = len(progress)
            completed_quests = len([q for q in progress.values() if q['can_complete']])
            
            progress_col1, progress_col2, progress_col3 = st.columns(3)
            with progress_col1:
                st.metric("Quests Ready", f"{completed_quests}/{total_quests}")
            with progress_col2:
                overall_percentage = (completed_quests / total_quests * 100) if total_quests > 0 else 0
                st.metric("Overall Progress", f"{overall_percentage:.1f}%")
            with progress_col3:
                if completed_quests == total_quests:
                    st.metric("Status", "🎉 READY!")
                else:
                    st.metric("Status", "⚠️ In Progress")
            
            # Individual quest progress
            st.subheader("📋 Individual Quest Status")
            st.info("💡 **Tip:** Crafted items have detailed recipes - check the desktop version for interactive recipe details!")
            
            # Create tabs for individual quests plus Items to Farm
            quest_tab_names = [f"Quest {i}: {st.session_state.signet_quest.quest_chain[i]['name']}" for i in range(1, 8)]
            quest_tab_names.append("🎯 Items to Farm")
            quest_tabs = st.tabs(quest_tab_names)
            
            # Individual quest tabs
            for i, tab in enumerate(quest_tabs[:-1], 1):  # Exclude the last tab (Items to Farm)
                with tab:
                    quest_data = st.session_state.signet_quest.quest_chain[i]
                    quest_name = quest_data['name']
                    
                    if quest_name in progress:
                        quest_progress = progress[quest_name]
                        
                        # Quest status
                        if quest_progress['can_complete']:
                            st.success(f"✅ **{quest_name} - READY TO COMPLETE!**")
                        else:
                            st.warning(f"❌ **{quest_name} - Missing Components**")
                        
                        # Progress bar
                        progress_percentage = quest_progress['progress_percentage']
                        st.progress(progress_percentage / 100)
                        st.write(f"Progress: {quest_progress['items_satisfied']}/{quest_progress['total_items']} items ({progress_percentage:.1f}%)")
                        
                        # Quest description
                        st.write(f"**Description:** {quest_data['description']}")
                        if 'prerequisite' in quest_data:
                            st.write(f"**Prerequisite:** {quest_data['prerequisite']}")
                        
                        # Items breakdown
                        st.subheader("Required Items")
                        
                        item_data = []
                        for item_name, item_info in quest_progress['owned_items'].items():
                            status = "✅ Ready" if item_info['satisfied'] else f"❌ Need {item_info['required'] - item_info['owned']}"
                            item_data.append({
                                'Item': item_name,
                                'Owned': item_info['owned'],
                                'Required': item_info['required'],
                                'Status': status,
                                'Source': item_info['source'],
                                'Type': item_info['type'].title()
                            })
                        
                        if item_data:
                            st.dataframe(
                                pd.DataFrame(item_data),
                                width='stretch',
                                hide_index=True,
                                column_config={
                                    "Item": st.column_config.TextColumn("Item", width="large"),
                                    "Owned": st.column_config.NumberColumn("Owned", width="small"),
                                    "Required": st.column_config.NumberColumn("Required", width="small"),
                                    "Status": st.column_config.TextColumn("Status", width="medium"),
                                    "Source": st.column_config.TextColumn("Source", width="large"),
                                    "Type": st.column_config.TextColumn("Type", width="small")
                                }
                            )
                        
                        # Missing items
                        if quest_progress['missing_items']:
                            st.subheader("Missing Items")
                            missing_data = []
                            for item_name, item_info in quest_progress['missing_items'].items():
                                missing_data.append({
                                    'Item': item_name,
                                    'Needed': item_info['needed'],
                                    'Source': item_info['source'],
                                    'Type': item_info['type'].title()
                                })
                            
                            st.dataframe(
                                pd.DataFrame(missing_data),
                                width='stretch',
                                hide_index=True
                            )
            
            # Items to Farm tab
            with quest_tabs[-1]:
                st.subheader("🎯 Items to Farm")
                st.write("All dropped items needed for the Signet of Might quest chain")
                
                # Create farming items data
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
                
                # Convert to DataFrame
                farm_df = pd.DataFrame(farming_items, columns=[
                    'Item', 'Qty', 'Zone/Location', 'Mob/Source', 'Drop Rate', 'Quest', 'Notes'
                ])
                
                # Display the farming table
                st.dataframe(
                    farm_df,
                    width='stretch',
                    hide_index=True,
                    column_config={
                        "Item": st.column_config.TextColumn("Item", width="medium"),
                        "Qty": st.column_config.NumberColumn("Qty", width="small"),
                        "Zone/Location": st.column_config.TextColumn("Zone/Location", width="medium"),
                        "Mob/Source": st.column_config.TextColumn("Mob/Source", width="medium"),
                        "Drop Rate": st.column_config.TextColumn("Drop Rate", width="small"),
                        "Quest": st.column_config.TextColumn("Quest", width="medium"),
                        "Notes": st.column_config.TextColumn("Notes", width="large")
                    }
                )
                
                st.info("💡 **Farming Tips:** Focus on rare drops first (Hope Stone, Drop of Pure Rain). Many items can be obtained from multiple sources - check vendors before farming!")
        
        # Move Zeb Weapon Analysis to center area
        st.markdown("---")
        st.header("🗡️ Zeb Weapon Component Analysis")
        st.markdown("*Check your progress toward crafting the legendary Zeb Weapon*")
        
        # Show persistent results if available (like desktop version)
        if st.session_state.zeb_results:
            results = st.session_state.zeb_results
            
            # Summary metrics in prominent display
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            with metric_col1:
                st.metric("Fragments Ready", f"{results['ready']}/12")
            with metric_col2:
                st.metric("Other Components", f"{results['other_ready']}/2")
            with metric_col3:
                craft_status = "YES! 🎉" if results['can_craft'] else "Not Yet"
                st.metric("Can Craft Zeb Weapon", craft_status)
            with metric_col4:
                # Add debug location button here - make it more prominent
                st.markdown("**🔍 Locations:**")
                if st.button("📍 Show Fragment Locations", help="Show detailed component locations", type="secondary", width='stretch'):
                    st.session_state.show_zeb_debug = True
            
            if results['can_craft']:
                st.success("🎉 **Zeb Weapon Ready!** All components available!")
                st.balloons()
            else:
                missing = results.get('missing_count', 0)
                st.warning(f"⚠️ Missing {missing} components. Keep collecting!")
            
            # Show detailed breakdown in center space
            breakdown_col1, breakdown_col2 = st.columns([3, 2])
            
            with breakdown_col1:
                st.subheader("🧩 Fragment Status")
                # Create enhanced fragment display
                fragment_data = []
                for frag in results.get('fragments', []):
                    fragment_data.append({
                        'Fragment': frag['Fragment'],
                        'Status': frag['Status'], 
                        'Legendary': frag['Legendary'],
                        'Enchanted': frag['Enchanted'],
                        'Notes': frag['Notes']
                    })
                
                if fragment_data:
                    st.dataframe(
                        pd.DataFrame(fragment_data),
                        width='stretch',
                        hide_index=True,
                        column_config={
                            "Fragment": st.column_config.TextColumn("🧩 Fragment", width="medium"),
                            "Status": st.column_config.TextColumn("📊 Status", width="small"),
                            "Legendary": st.column_config.NumberColumn("🏆 Legendary", width="small"),
                            "Enchanted": st.column_config.NumberColumn("⭐ Enchanted", width="small"),
                            "Notes": st.column_config.TextColumn("📝 Notes", width="large")
                        }
                    )
            
            with breakdown_col2:
                st.subheader("🔧 Other Components")
                other_data = []
                for comp in results.get('other_components', []):
                    other_data.append({
                        'Component': comp['Component'],
                        'Status': comp['Status'],
                        'Count': comp['Count']
                    })
                
                if other_data:
                    st.dataframe(
                        pd.DataFrame(other_data),
                        width='stretch',
                        hide_index=True
                    )
                
                st.markdown("**💡 Tips:**")
                st.info("""
                • Combine 4 Enchanted → 1 Legendary
                • Time Phased Quintessence & Vortex of the Past are rare drops
                • Use Show Fragment Locations to see exactly where your components are
                """)
            
            # Fragment location display
            if st.session_state.get('show_zeb_debug', False):
                st.markdown("---")
                st.subheader("📍 Fragment Location Details")
                st.markdown("*Detailed breakdown of where each component is located*")
                
                # Show locations for each component
                debug_items_df = st.session_state.items_df
                
                debug_col1, debug_col2 = st.columns(2)
                
                with debug_col1:
                    st.markdown("**🧩 Fragment Locations:**")
                    
                    required_fragments = [
                        "Akhevan Fragment of Truth", "Fiery Fragment of Truth", "Gelid Fragment of Truth",
                        "Hastened Fragment of Truth", "Healing Fragment of Truth", "Icy Fragment of Truth",
                        "Lethal Fragment of Truth", "Magical Fragment of Truth", "Replenishing Fragment of Truth",
                        "Runic Fragment of Truth", "Ssraeshzian Fragment of Truth", "Yttrium Fragment of Truth"
                    ]
                    
                    for fragment in required_fragments:
                        fragment_short = fragment.replace(" Fragment of Truth", "")
                        
                        # Find all instances of this fragment
                        legendary_items = debug_items_df[
                            debug_items_df['Name'].str.contains(f"{fragment} (Legendary)", case=False, na=False, regex=False)
                        ]
                        enchanted_items = debug_items_df[
                            debug_items_df['Name'].str.contains(f"{fragment} (Enchanted)", case=False, na=False, regex=False)
                        ]
                        
                        if not legendary_items.empty or not enchanted_items.empty:
                            with st.expander(f"🧩 {fragment_short} ({len(legendary_items) + len(enchanted_items)} found)"):
                                if not legendary_items.empty:
                                    st.write("**🏆 Legendary:**")
                                    for _, item in legendary_items.iterrows():
                                        st.write(f"• {item['Character']} - {item['Location']}")
                                
                                if not enchanted_items.empty:
                                    st.write("**⭐ Enchanted:**")
                                    for _, item in enchanted_items.iterrows():
                                        st.write(f"• {item['Character']} - {item['Location']}")
                
                with debug_col2:
                    st.markdown("**🔧 Other Component Locations:**")
                    
                    other_components = ["Time Phased Quintessence", "Vortex of the Past"]
                    
                    for component in other_components:
                        component_items = debug_items_df[
                            debug_items_df['Name'].str.contains(component, case=False, na=False, regex=False)
                        ]
                        
                        if not component_items.empty:
                            with st.expander(f"🔧 {component} ({len(component_items)} found)"):
                                for _, item in component_items.iterrows():
                                    st.write(f"• {item['Character']} - {item['Location']}")
                        else:
                            st.error(f"❌ {component} - Not found")
                
                # Add close debug button
                if st.button("❌ Close Fragment Locations"):
                    st.session_state.show_zeb_debug = False
                    st.rerun()
        
        # Analysis controls
        control_col1, control_col2, control_col3 = st.columns([2, 1, 1])
        
        with control_col1:
            st.info("🎯 **Requirements:** 12 different Fragment of Truth types (Legendary) + Time Phased Quintessence + Vortex of the Past")
        
        with control_col2:
            if st.button("🔍 Analyze My Components", type="primary"):
                with st.spinner("🔄 Analyzing components..."):
                    # Zeb weapon analysis
                    required_fragments = [
                        "Akhevan Fragment of Truth", "Fiery Fragment of Truth", "Gelid Fragment of Truth",
                        "Hastened Fragment of Truth", "Healing Fragment of Truth", "Icy Fragment of Truth",
                        "Lethal Fragment of Truth", "Magical Fragment of Truth", "Replenishing Fragment of Truth",
                        "Runic Fragment of Truth", "Ssraeshzian Fragment of Truth", "Yttrium Fragment of Truth"
                    ]
                    
                    other_components = ["Time Phased Quintessence", "Vortex of the Past"]
                    
                    fragment_status = []
                    for fragment in required_fragments:
                        legendary_count = len(items_df[
                            items_df['Name'].str.contains(f"{fragment} (Legendary)", case=False, na=False, regex=False)
                        ])
                        enchanted_count = len(items_df[
                            items_df['Name'].str.contains(f"{fragment} (Enchanted)", case=False, na=False, regex=False)
                        ])
                        
                        ready = legendary_count > 0 or enchanted_count >= 4
                        status = "✅ Ready" if ready else ("🔄 Can Make" if enchanted_count > 0 else "❌ Missing")
                        
                        fragment_status.append({
                            "Fragment": fragment.replace(" Fragment of Truth", ""),
                            "Status": status,
                            "Legendary": legendary_count,
                            "Enchanted": enchanted_count,
                            "Notes": f"Can make from {enchanted_count}/4 Enchanted" if enchanted_count > 0 and legendary_count == 0 else "Ready!" if ready else "Need more"
                        })
                    
                    # Other components
                    other_status = []
                    for component in other_components:
                        count = len(items_df[
                            items_df['Name'].str.contains(component, case=False, na=False, regex=False)
                        ])
                        other_status.append({
                            "Component": component,
                            "Status": "✅ Ready" if count > 0 else "❌ Missing",
                            "Count": count
                        })
                    
                    # Calculate totals
                    ready_fragments = len([f for f in fragment_status if f['Status'] == '✅ Ready'])
                    can_make_fragments = len([f for f in fragment_status if f['Status'] == '🔄 Can Make'])
                    ready_others = len([c for c in other_status if c['Status'] == '✅ Ready'])
                    
                    total_ready = ready_fragments + can_make_fragments
                    can_craft = total_ready == 12 and ready_others == 2
                    missing_count = (12 - total_ready) + (2 - ready_others)
                    
                    # Store results in session state
                    st.session_state.zeb_results = {
                        'ready': total_ready,
                        'other_ready': ready_others,
                        'can_craft': can_craft,
                        'missing_count': missing_count,
                        'fragments': fragment_status,
                        'other_components': other_status
                    }
                    
                    st.rerun()  # Refresh to show results

else:
    # Welcome screen
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""  
        ### 🚀 Welcome to FDT EQ Emu Inventory Parser!
        
        This web application helps you manage and search your **EverQuest Emulator** character inventories.
        
        **🎯 Key Features:**
        - **Advanced Search** - Find items across all characters
        - **Zeb Weapon Analyzer** - Check crafting components  
        - **Export Results** - Download search results as CSV
        - **Real-time Analysis** - Instant feedback and statistics
        
        **📁 Getting Started:**
        1. **In EverQuest**: Login to your character
        2. **Run Command**: Type `/outputfile inventory` in-game  
        3. **Pro Tip**: Do this in the Bazaar to include bank slots!
        4. **Find Files**: Look for `CharacterName-Inventory.txt` in your EQ folder
        5. **Upload Here**: Use the sidebar to upload your files
        6. **Search Away**: Find your Tulwar or any other item!
        
        **💡 This is the web version** - no installation required!
        
        For the full desktop application with additional features, 
        visit our [GitHub repository](https://github.com/scienceandresearch/fdt-eq-emu-inventory).
        """)
        
        # Sample file format
        with st.expander("📖 Expected File Format"):
            st.code("""
Location\tName\tID\tCount\tSlots
Primary\tLegendary Sword\t12345\t1\t0
General1\tFragment of Truth (Enchanted)\t67890\t1\t0
Bank1\tTime Phased Quintessence\t11111\t1\t0
""", language="tsv")
    
# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**🎮 FDT EQ Emu Inventory Parser**")
with col2:
    st.markdown("[📥 Desktop Version](https://github.com/scienceandresearch/fdt-eq-emu-inventory)")
with col3:
    st.markdown("[🐛 Report Issues](https://github.com/scienceandresearch/fdt-eq-emu-inventory/issues)")

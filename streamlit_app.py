import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re
import hashlib

# Page config
st.set_page_config(
    page_title="THJ Inventory Manager",
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
.metric-card {
    background: #f8fafc;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #3b82f6;
}
.stButton > button {
    width: 100%;
    margin: 2px 0;
}
.search-section {
    background: #f1f5f9;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🎮 The Heroes Journey Inventory Manager</h1>
    <p><em>Advanced inventory search and Zeb weapon component analyzer</em></p>
    <p><strong>Web Version - Always Up to Date!</strong></p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'items_df' not in st.session_state:
    st.session_state.items_df = pd.DataFrame()
if 'last_search' not in st.session_state:
    st.session_state.last_search = ""

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
    **File Format:**
    - `CharacterName-Inventory.txt`
    - Tab-separated columns
    - Location, Name, ID, Count, Slots
    
    **Features:**
    - 🔍 Advanced search with filters
    - ⚡ Quick search buttons
    - 🗡️ Zeb weapon analyzer
    - 💾 Export results to CSV
    - 🔄 Find duplicate items
    """)
    
    st.markdown("---")
    st.markdown("**🔗 Links:**")
    st.markdown("[📥 Download Desktop Version](https://github.com/scienceandresearch/thj-inventory-manager)")
    st.markdown("[🐛 Report Issues](https://github.com/scienceandresearch/thj-inventory-manager/issues)")

# Main app logic
if uploaded_files:
    # Process files with caching for better performance
    @st.cache_data
    def load_web_inventory_files(files):
        result_list = []
        shared_bank_data = {}
        
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
                use_container_width=True,
                hide_index=True
            )
        
        # Search Section
        st.markdown('<div class="search-section">', unsafe_allow_html=True)
        st.subheader("🔍 Search Inventory")
        
        # Search controls
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            search_term = st.text_input("🔎 Item Name", placeholder="Enter item name or pattern...")
        with col2:
            character_options = ['All'] + sorted([c for c in items_df['Character'].unique() if c != 'SHARED-BANK'])
            character = st.selectbox("👤 Character", character_options)
        with col3:
            item_type = st.selectbox("📂 Type", ['All', 'Equipped', 'Inventory', 'Bank'])
        with col4:
            st.write("") # Spacer
            exact_match = st.checkbox("Exact Match")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick search buttons
        st.subheader("⚡ Quick Searches")
        
        # Equipment slots
        st.markdown("**⚔️ Equipment Slots:**")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        equipment_searches = [
            ("💍 Rings", "Ring"), ("👑 Head/Helm", "Helm|Head"), ("👕 Chest", "Chest|Breastplate|Robe|Tunic"),
            ("👖 Legs", "Leg|Pant|Greave|Kilt"), ("👢 Feet", "Feet|Boot|Shoe|Sandal"), ("🤚 Hands", "Hand|Glove|Gauntlet")
        ]
        
        for i, (label, pattern) in enumerate(equipment_searches):\n            with [col1, col2, col3, col4, col5, col6][i]:\n                if st.button(label, key=f"equip_{i}"):\n                    search_term = pattern\n                    st.rerun()\n        \n        # Weapons\n        st.markdown("**🗡️ Weapons:**")\n        col1, col2, col3, col4 = st.columns(4)\n        weapon_searches = [\n            ("⚔️ Swords", "Sword"), ("🗡️ Daggers", "Dagger"), ("🪓 Axes", "Axe"), ("🔨 Maces", "Mace")\n        ]\n        \n        for i, (label, pattern) in enumerate(weapon_searches):\n            with [col1, col2, col3, col4][i]:\n                if st.button(label, key=f"weapon_{i}"):\n                    search_term = pattern\n                    st.rerun()\n        \n        # Special items\n        st.markdown("**✨ Special Items:**")\n        col1, col2, col3, col4 = st.columns(4)\n        special_searches = [\n            ("🔮 Truth Fragments", "Fragment of Truth"), ("⭐ Legendary", "Legendary"),\n            ("🌟 Enchanted", "Enchanted"), ("💎 Prismatic", "Prismatic")\n        ]\n        \n        for i, (label, pattern) in enumerate(special_searches):\n            with [col1, col2, col3, col4][i]:\n                if st.button(label, key=f"special_{i}"):\n                    search_term = pattern\n                    st.rerun()\n        \n        # Perform search\n        if search_term:\n            st.session_state.last_search = search_term\n            \n            # Apply search logic (reuse from desktop version)\n            df = items_df[items_df['IsEmpty'] == False].copy()\n            \n            if '|' in search_term:\n                df = df[df['Name'].str.contains(search_term, case=False, na=False, regex=True)]\n            elif exact_match:\n                df = df[df['Name'].str.lower() == search_term.lower()]\n            else:\n                df = df[df['Name'].str.contains(search_term, case=False, na=False)]\n            \n            if character != 'All':\n                df = df[df['Character'] == character]\n            \n            if item_type != 'All':\n                df = df[df['ItemType'] == item_type]\n            \n            # Display results\n            st.subheader(f"📄 Search Results ({len(df)} items found)")\n            \n            if not df.empty:\n                # Add action buttons\n                col1, col2, col3 = st.columns([2, 2, 1])\n                with col1:\n                    # Character summary for results\n                    char_counts = df['Character'].value_counts()\n                    if len(char_counts) > 1:\n                        st.info(f"📊 Found across {len(char_counts)} characters: " + \n                                ", ".join([f"{char} ({count})" for char, count in char_counts.head(5).items()]))\n                \n                with col2:\n                    # Export button\n                    csv = df[['Character', 'Name', 'Location', 'ItemType', 'Count']].to_csv(index=False)\n                    st.download_button(\n                        "💾 Download Results CSV",\n                        csv,\n                        f"search_results_{search_term.replace('|', '_')}.csv",\n                        "text/csv",\n                        key="download_results"\n                    )\n                \n                # Results table with better formatting\n                display_df = df[['Character', 'Name', 'Location', 'ItemType', 'Count']].copy()\n                \n                # Add some styling based on item type\n                def highlight_rows(row):\n                    if row['ItemType'] == 'Equipped':\n                        return ['background-color: #e6f3ff'] * len(row)\n                    elif row['ItemType'] == 'Bank':\n                        return ['background-color: #fff2e6'] * len(row)\n                    else:\n                        return [''] * len(row)\n                \n                st.dataframe(\n                    display_df.style.apply(highlight_rows, axis=1),\n                    use_container_width=True,\n                    hide_index=True\n                )\n                \n                # Quick actions on results\n                if len(df) > 1:\n                    with st.expander(f"🔄 Find Duplicates in Results"):\n                        duplicates = df.groupby(['Name', 'ID']).size().reset_index(name='Count')\n                        duplicates = duplicates[duplicates['Count'] > 1]\n                        \n                        if not duplicates.empty:\n                            st.dataframe(duplicates, hide_index=True)\n                        else:\n                            st.info("No duplicate items found in current results.")\n            \n            else:\n                st.info(f"🔍 No items found matching '{search_term}'. Try:\n\n" +\n                       "• Using partial names (e.g., 'sword' instead of 'Legendary Sword')\n\n" +\n                       "• Checking spelling\n\n" +\n                       "• Using broader search terms\n\n" +\n                       "• Trying the quick search buttons above")\n        \n        # Zeb Weapon Analysis\n        st.header("🗡️ Zeb Weapon Component Analysis")\n        \n        col1, col2 = st.columns([3, 1])\n        with col1:\n            st.info("🎯 **Zeb Weapon Requirements:** 12 different Fragment of Truth types (Legendary) + Time Phased Quintessence + Vortex of the Past")\n        with col2:\n            if st.button("🔍 Analyze Components", type="primary"):\n                with st.spinner("🔄 Analyzing Zeb weapon components..."):\n                    # Zeb weapon analysis (simplified for web)\n                    required_fragments = [\n                        "Akhevan Fragment of Truth", "Fiery Fragment of Truth", "Gelid Fragment of Truth",\n                        "Hastened Fragment of Truth", "Healing Fragment of Truth", "Icy Fragment of Truth",\n                        "Lethal Fragment of Truth", "Magical Fragment of Truth", "Replenishing Fragment of Truth",\n                        "Runic Fragment of Truth", "Ssraeshzian Fragment of Truth", "Yttrium Fragment of Truth"\n                    ]\n                    \n                    other_components = ["Time Phased Quintessence", "Vortex of the Past"]\n                    \n                    fragment_status = []\n                    for fragment in required_fragments:\n                        legendary_count = len(items_df[\n                            items_df['Name'].str.contains(f"{fragment} (Legendary)", case=False, na=False, regex=False)\n                        ])\n                        enchanted_count = len(items_df[\n                            items_df['Name'].str.contains(f"{fragment} (Enchanted)", case=False, na=False, regex=False)\n                        ])\n                        \n                        ready = legendary_count > 0 or enchanted_count >= 4\n                        status = "✅ Ready" if ready else ("🔄 Can Make" if enchanted_count > 0 else "❌ Missing")\n                        \n                        fragment_status.append({\n                            "Fragment": fragment.replace(" Fragment of Truth", ""),\n                            "Status": status,\n                            "Legendary": legendary_count,\n                            "Enchanted": enchanted_count,\n                            "Notes": f"Can make from {enchanted_count}/4 Enchanted" if enchanted_count > 0 and legendary_count == 0 else "Ready!" if ready else "Need more"\n                        })\n                    \n                    # Other components\n                    other_status = []\n                    for component in other_components:\n                        count = len(items_df[\n                            items_df['Name'].str.contains(component, case=False, na=False, regex=False)\n                        ])\n                        other_status.append({\n                            "Component": component,\n                            "Status": "✅ Ready" if count > 0 else "❌ Missing",\n                            "Count": count\n                        })\n                    \n                    # Display results\n                    ready_fragments = len([f for f in fragment_status if f['Status'] == '✅ Ready'])\n                    can_make_fragments = len([f for f in fragment_status if f['Status'] == '🔄 Can Make'])\n                    ready_others = len([c for c in other_status if c['Status'] == '✅ Ready'])\n                    \n                    total_ready = ready_fragments + can_make_fragments\n                    \n                    # Summary metrics\n                    col1, col2, col3 = st.columns(3)\n                    with col1:\n                        st.metric("Fragments Ready", f"{total_ready}/12", f"{total_ready - 12}" if total_ready < 12 else "Complete!")\n                    with col2:\n                        st.metric("Other Components", f"{ready_others}/2", f"{ready_others - 2}" if ready_others < 2 else "Complete!")\n                    with col3:\n                        can_craft = total_ready == 12 and ready_others == 2\n                        st.metric("Can Craft Zeb Weapon", "YES! 🎉" if can_craft else "Not Yet")\n                    \n                    if can_craft:\n                        st.success("🎉 **Congratulations!** You have all components needed to craft a Zeb Weapon!")\n                        st.balloons()\n                    else:\n                        missing = 12 - total_ready + (2 - ready_others)\n                        st.warning(f"⚠️ Missing {missing} components total. Keep collecting!")\n                    \n                    # Detailed breakdown\n                    with st.expander("📋 Detailed Component Breakdown", expanded=can_craft):\n                        st.subheader("Fragment Status")\n                        status_df = pd.DataFrame(fragment_status)\n                        st.dataframe(status_df, hide_index=True, use_container_width=True)\n                        \n                        st.subheader("Other Components")\n                        other_df = pd.DataFrame(other_status)\n                        st.dataframe(other_df, hide_index=True, use_container_width=True)\n                        \n                        if not can_craft:\n                            st.info("💡 **Tip:** You can combine 4 Enchanted fragments to make 1 Legendary fragment!")\n\nelse:\n    # Welcome screen\n    col1, col2, col3 = st.columns([1, 2, 1])\n    \n    with col2:\n        st.markdown(\"\"\"  \n        ### 🚀 Welcome to THJ Inventory Manager!\n        \n        This web application helps you manage and search your **The Heroes Journey** EverQuest character inventories.\n        \n        **🎯 Key Features:**\n        - **Advanced Search** - Find items across all characters\n        - **Zeb Weapon Analyzer** - Check crafting components  \n        - **Export Results** - Download search results as CSV\n        - **Real-time Analysis** - Instant feedback and statistics\n        \n        **📁 To Get Started:**\n        1. Use the sidebar to upload your `*-Inventory.txt` files\n        2. Files should be in tab-separated format from THJ\n        3. Upload multiple character files at once\n        \n        **💡 This is the web version** - no installation required!\n        \n        For the full desktop application with additional features, \n        visit our [GitHub repository](https://github.com/scienceandresearch/thj-inventory-manager).\n        \"\"\")\n        \n        # Sample file format\n        with st.expander("📖 Expected File Format"):\n            st.code(\"\"\"\nLocation\\tName\\tID\\tCount\\tSlots\nPrimary\\tLegendary Sword\\t12345\\t1\\t0\nGeneral1\\tFragment of Truth (Enchanted)\\t67890\\t1\\t0\nBank1\\tTime Phased Quintessence\\t11111\\t1\\t0\n\"\"\", language=\"tsv\")\n    \n# Footer\nst.markdown(\"---\")\ncol1, col2, col3 = st.columns(3)\nwith col1:\n    st.markdown(\"**🎮 THJ Inventory Manager**\")\nwith col2:\n    st.markdown(\"[📥 Desktop Version](https://github.com/scienceandresearch/thj-inventory-manager)\")\nwith col3:\n    st.markdown(\"[🐛 Report Issues](https://github.com/scienceandresearch/thj-inventory-manager/issues)\")\n
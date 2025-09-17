import streamlit as st
import pandas as pd
import os
from datetime import datetime
import re

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
if 'search_term' not in st.session_state:
    st.session_state.search_term = ""

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
                use_container_width=True,
                hide_index=True
            )
        
        # Search Section
        st.markdown('<div class="search-section">', unsafe_allow_html=True)
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
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick search buttons
        st.subheader("⚡ Quick Searches")
        
        # Equipment slots
        st.markdown("**⚔️ Equipment Slots:**")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        if col1.button("💍 Rings", key="ring_btn"):
            st.session_state.search_term = "Ring"
            st.rerun()
        if col2.button("👑 Head/Helm", key="head_btn"):
            st.session_state.search_term = "Helm|Head"
            st.rerun()
        if col3.button("👕 Chest", key="chest_btn"):
            st.session_state.search_term = "Chest|Breastplate|Robe|Tunic"
            st.rerun()
        if col4.button("👖 Legs", key="legs_btn"):
            st.session_state.search_term = "Leg|Pant|Greave|Kilt"
            st.rerun()
        if col5.button("👢 Feet", key="feet_btn"):
            st.session_state.search_term = "Feet|Boot|Shoe|Sandal"
            st.rerun()
        if col6.button("🤚 Hands", key="hands_btn"):
            st.session_state.search_term = "Hand|Glove|Gauntlet"
            st.rerun()
        
        # Weapons
        st.markdown("**🗡️ Weapons:**")
        col1, col2, col3, col4 = st.columns(4)
        
        if col1.button("⚔️ Swords", key="sword_btn"):
            st.session_state.search_term = "Sword"
            st.rerun()
        if col2.button("🗡️ Daggers", key="dagger_btn"):
            st.session_state.search_term = "Dagger"
            st.rerun()
        if col3.button("🪓 Axes", key="axe_btn"):
            st.session_state.search_term = "Axe"
            st.rerun()
        if col4.button("🔨 Maces", key="mace_btn"):
            st.session_state.search_term = "Mace"
            st.rerun()
        
        # Special items
        st.markdown("**✨ Special Items:**")
        col1, col2, col3, col4 = st.columns(4)
        
        if col1.button("🔮 Truth Fragments", key="truth_btn"):
            st.session_state.search_term = "Fragment of Truth"
            st.rerun()
        if col2.button("⭐ Legendary", key="legendary_btn"):
            st.session_state.search_term = "Legendary"
            st.rerun()
        if col3.button("🌟 Enchanted", key="enchanted_btn"):
            st.session_state.search_term = "Enchanted"
            st.rerun()
        if col4.button("💎 Prismatic", key="prismatic_btn"):
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
            
            # Display results
            st.subheader(f"📄 Search Results ({len(df)} items found)")
            
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
                    use_container_width=True,
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
                st.info(f"🔍 No items found matching '{search_term}'. Try:\n\n" +
                       "• Using partial names (e.g., 'sword' instead of 'Legendary Sword')\n\n" +
                       "• Checking spelling\n\n" +
                       "• Using broader search terms\n\n" +
                       "• Trying the quick search buttons above")
        
        # Zeb Weapon Analysis
        st.header("🗡️ Zeb Weapon Component Analysis")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("🎯 **Zeb Weapon Requirements:** 12 different Fragment of Truth types (Legendary) + Time Phased Quintessence + Vortex of the Past")
        with col2:
            if st.button("🔍 Analyze Components", type="primary"):
                with st.spinner("🔄 Analyzing Zeb weapon components..."):
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
                    
                    # Display results
                    ready_fragments = len([f for f in fragment_status if f['Status'] == '✅ Ready'])
                    can_make_fragments = len([f for f in fragment_status if f['Status'] == '🔄 Can Make'])
                    ready_others = len([c for c in other_status if c['Status'] == '✅ Ready'])
                    
                    total_ready = ready_fragments + can_make_fragments
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Fragments Ready", f"{total_ready}/12", f"{total_ready - 12}" if total_ready < 12 else "Complete!")
                    with col2:
                        st.metric("Other Components", f"{ready_others}/2", f"{ready_others - 2}" if ready_others < 2 else "Complete!")
                    with col3:
                        can_craft = total_ready == 12 and ready_others == 2
                        st.metric("Can Craft Zeb Weapon", "YES! 🎉" if can_craft else "Not Yet")
                    
                    if can_craft:
                        st.success("🎉 **Congratulations!** You have all components needed to craft a Zeb Weapon!")
                        st.balloons()
                    else:
                        missing = 12 - total_ready + (2 - ready_others)
                        st.warning(f"⚠️ Missing {missing} components total. Keep collecting!")
                    
                    # Detailed breakdown
                    with st.expander("📋 Detailed Component Breakdown", expanded=can_craft):
                        st.subheader("Fragment Status")
                        status_df = pd.DataFrame(fragment_status)
                        st.dataframe(status_df, hide_index=True, use_container_width=True)
                        
                        st.subheader("Other Components")
                        other_df = pd.DataFrame(other_status)
                        st.dataframe(other_df, hide_index=True, use_container_width=True)
                        
                        if not can_craft:
                            st.info("💡 **Tip:** You can combine 4 Enchanted fragments to make 1 Legendary fragment!")

else:
    # Welcome screen
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""  
        ### 🚀 Welcome to THJ Inventory Manager!
        
        This web application helps you manage and search your **The Heroes Journey** EverQuest character inventories.
        
        **🎯 Key Features:**
        - **Advanced Search** - Find items across all characters
        - **Zeb Weapon Analyzer** - Check crafting components  
        - **Export Results** - Download search results as CSV
        - **Real-time Analysis** - Instant feedback and statistics
        
        **📁 To Get Started:**
        1. Use the sidebar to upload your `*-Inventory.txt` files
        2. Files should be in tab-separated format from THJ
        3. Upload multiple character files at once
        
        **💡 This is the web version** - no installation required!
        
        For the full desktop application with additional features, 
        visit our [GitHub repository](https://github.com/scienceandresearch/thj-inventory-manager).
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
    st.markdown("**🎮 THJ Inventory Manager**")
with col2:
    st.markdown("[📥 Desktop Version](https://github.com/scienceandresearch/thj-inventory-manager)")
with col3:
    st.markdown("[🐛 Report Issues](https://github.com/scienceandresearch/thj-inventory-manager/issues)")

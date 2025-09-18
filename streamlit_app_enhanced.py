                # Character-specific Zeb analysis
                if st.button(f"🗡️ Check {selected_char}'s Zeb Components"):
                    char_zeb_results = analyze_zeb_components(char_data)
                    
                    st.subheader(f"🗡️ {selected_char}'s Zeb Components")
                    
                    if char_zeb_results['fragments']:
                        fragments_found = [f for f in char_zeb_results['fragments'] if f['legendary_count'] > 0 or f['enchanted_count'] > 0]
                        
                        if fragments_found:
                            st.success(f"Found {len(fragments_found)} fragment types on {selected_char}!")
                            
                            for fragment in fragments_found:
                                with st.expander(f"{fragment['status']} {fragment['fragment']}"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**Legendary:** {fragment['legendary_count']}")
                                        st.write(f"**Enchanted:** {fragment['enchanted_count']}")
                                    with col2:
                                        st.write("**Locations:**")
                                        for loc in fragment['locations']:
                                            st.write(f"• {loc}")
                        else:
                            st.info(f"No Zeb fragments found on {selected_char}")
                    
                    # Other components on this character
                    other_found = [c for c in char_zeb_results['other_components'] if c['count'] > 0]
                    if other_found:
                        st.subheader("🔧 Other Components")
                        for component in other_found:
                            st.success(f"✅ {component['component']} ({component['count']} found)")
                            for loc in component['locations']:
                                st.write(f"• {loc}")

else:
    # Welcome screen with better instructions
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""  
        ### 🚀 Welcome to FDT EQ Emu Inventory Parser!
        
        This web application helps you manage and search your **EverQuest Emulator** character inventories.
        
        **🎯 Key Features:**
        - **Advanced Search** - Find items across all characters
        - **Zeb Weapon Analyzer** - Check crafting components with detailed locations
        - **Character Deep Dive** - Individual character analysis
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

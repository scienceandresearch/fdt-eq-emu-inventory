        <div style=\"text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); border-radius: 10px; margin: 1rem 0;\">
            <h3 style=\"color: #1e40af;\">Ready to find your Tulwar? 🏺</h3>
            <p>Upload your inventory files using the sidebar to get started!</p>
        </div>
        """, unsafe_allow_html=True)

# Footer with enhanced styling
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown(
        "**🎮 FDT EQ Emu Inventory Parser**\n\n"
        "*Find DnK's Tulwar - Making inventory management easier!*"
    )

with footer_col2:
    st.markdown(
        "**🔗 Links:**\n\n"
        "[📥 Desktop Version](https://github.com/scienceandresearch/fdt-eq-emu-inventory)\n\n"
        "[🌐 Web App](https://fdt-eq-emu-inventory.streamlit.app)"
    )

with footer_col3:
    st.markdown(
        "**📞 Support:**\n\n"
        "[🐛 Report Issues](https://github.com/scienceandresearch/fdt-eq-emu-inventory/issues)\n\n"
        "[💡 Feature Requests](https://github.com/scienceandresearch/fdt-eq-emu-inventory/discussions)"
    )

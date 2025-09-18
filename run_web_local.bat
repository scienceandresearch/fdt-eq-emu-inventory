@echo off
echo ================================================================
echo    FDT EQ Emu Inventory Parser - Web Version (Local Testing)
echo    "Find DnK's Tulwar" - Advanced EQ Emulator Inventory Tool
echo ================================================================
echo.
echo Installing/updating dependencies...
pip install streamlit pandas

echo.
echo Starting local web server...
echo Your app will open in your browser automatically.
echo.
echo Press Ctrl+C to stop the server when done.
echo.
streamlit run streamlit_app.py

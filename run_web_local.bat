@echo off
echo ================================================================
echo    THJ Inventory Manager - Web Version (Local Testing)
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

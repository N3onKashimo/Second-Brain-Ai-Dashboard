
@echo off
REM 🚀 Safe launcher for Rogue AI Copilot (Streamlit + Memory Engine)
REM ✅ Disables file watcher to avoid PyTorch crash
REM 📂 Make sure you update the path below if you rename your script

streamlit run "F:\Important Projects\Local Ai Dashboard\dashboard.py" --server.fileWatcherType none
pause

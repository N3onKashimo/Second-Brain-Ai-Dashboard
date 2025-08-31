@echo off
title Rogue AI Launcher
echo ==========================
echo Choose your AI persona:
echo 1. Hobie Mode
echo 2. Shikamaru
echo 3. Shadow Coach
echo 4. Spike
echo 5. Batman
set /p choice=Enter 1-5:
if %choice%==1 ollama run dolphin-mistral
if %choice%==2 ollama run mythomax
if %choice%==3 ollama run openhermes
if %choice%==4 ollama run dolphin-llama3
if %choice%==5 ollama run llama3

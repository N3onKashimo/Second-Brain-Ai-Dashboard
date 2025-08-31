import json
import re
from pathlib import Path

def clean_filename(text):
    # Remove illegal characters for Windows filenames
    return re.sub(r'[<>:"/\\|?*\']', '', text)[:50]

# Load your exported ChatGPT file
with open("F:/OllamaModels/memory/chatgpt/conversations.json", "r", encoding="utf-8") as f:
    data = json.load(f)

output_dir = Path("F:/OllamaModels/memory/chatgpt-extracted/")
output_dir.mkdir(parents=True, exist_ok=True)

skipped = 0

for i, conv in enumerate(data):
    title = clean_filename(conv.get("title", f"conversation_{i}"))
    messages = conv.get("mapping", {})
    
    log = []
    for msg in messages.values():
        if msg.get("message"):
            try:
                role = msg["message"]["author"]["role"]
                parts = msg["message"]["content"].get("parts", [])
                if parts:
                    content = parts[0]
                    log.append(f"{role.upper()}: {content}\n")
            except Exception:
                skipped += 1
                continue
    
    if log:
        filename = output_dir / f"{i:03d}_{title}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(log)

print(f"✅ Export complete. Skipped {skipped} problematic messages.")

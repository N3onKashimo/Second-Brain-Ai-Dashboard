import streamlit as st
from pathlib import Path
import datetime
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.settings import Settings
from streamlit_calendar import calendar
from calendar_utils import fetch_upcoming_events, add_event
from notion_tasks import fetch_notion_tasks, mark_task_complete

# === CONFIGURATION ===
persona_dir = Path("F:/OllamaModels/prompts/personas")
plans_path = Path("F:/OllamaModels/plans.md")
log_dir = Path("F:/OllamaModels/logs")
persist_dir = "F:/OllamaModels/memory/vectorstore/"
log_dir.mkdir(parents=True, exist_ok=True)

# === ENSURE NO DEFAULT OPENAI USAGE ===
Settings.llm = None

# === LOAD PERSONAS ===
personas = {
    f.stem: f.read_text(encoding='utf-8')
    for f in persona_dir.glob("*.txt")
}

# === STREAMLIT TABS ===
tab1, tab2, tab3, tab4 = st.tabs(["\U0001f9e0 Chat", "\U0001f9e0 Memory Search", "\U0001f4c5 Calendar", "\U0001f4cb Notion Tasks"])

# === TAB 1: Persona Chat UI ===
with tab1:
    import ollama

    st.sidebar.title("\U0001f9e0 Rogue AI Copilot")
    persona_choice = st.sidebar.selectbox("Choose Persona", sorted(personas.keys()))
    model_choice = st.sidebar.selectbox("Base Model", ["mistral", "llama3", "dolphin-mistral", "phi3", "openhermes"])

    # Model Descriptions
    model_descriptions = {
        "llama3": "Best for logic-heavy chats and code.",
        "mistral": "General-purpose fast model.",
        "dolphin-mistral": "Fine-tuned for instruction following.",
        "phi3": "Small + fast with solid reasoning.",
        "openhermes": "Balanced mix of speed and creativity."
    }
    selected_description = model_descriptions.get(model_choice, "No description available.")
    st.sidebar.markdown(f"\U0001f4a1 {selected_description}")

    xp = st.sidebar.slider("Daily XP", 0, 100, 50)
    mood = st.sidebar.selectbox("Mood", ["Focused", "Burnt Out", "Creative", "Lazy Genius", "Shadow Mode"])

    if plans_path.exists():
        st.sidebar.markdown("### \U0001f4cb Life Plans")
        st.sidebar.text(plans_path.read_text(encoding='utf-8')[:1000])

    st.title(f"\U0001f4ac {persona_choice} Mode")
    st.markdown(f"**Model:** `{model_choice}` | **Mood:** *{mood}*")
    initial_prompt = personas[persona_choice]

    st.markdown("### \U0001f9e0 Persona Prompt")
    st.code(initial_prompt.strip(), language="markdown")

    st.markdown("### \U0001f4a1 Suggestions for Today")
    suggestions = {
        "Focused": ["Finish key task", "Deep work block", "Code 1hr"],
        "Burnt Out": ["Take a walk", "Journal for 10 min", "Low-effort planning"],
        "Creative": ["Sketch ideas", "Build project draft", "Try something new"],
        "Lazy Genius": ["Automate something", "Delegation review", "Quick win task"],
        "Shadow Mode": ["Do silent research", "Work behind scenes", "Private study"]
    }
    for task in suggestions[mood][:3]:
        icon = "\U0001f525" if xp > 60 else "\U0001f4a1"
        st.markdown(f"- {task} {icon}")

    user_input = st.text_area("You:", "", height=100)

    if st.button("Submit"):
        st.markdown("### \U0001f916 Prompt Sent to AI")
        full_prompt = f"{initial_prompt.strip()}\n\nUser: {user_input.strip()}\nAI:"

        with st.spinner("Sending prompt to model..."):
            try:
                response = ollama.chat(
                    model=model_choice,
                    messages=[{"role": "user", "content": full_prompt}]
                )
                ai_reply = response['message']['content']
            except Exception as e:
                ai_reply = f"Error: {e}"

        st.text_area("Prompt", full_prompt, height=300)
        st.text_area("AI:", value=ai_reply, height=200)

        # Save to log
        log_file = log_dir / f"{persona_choice}_{datetime.date.today()}.md"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"USER: {user_input}\nAI:\n{ai_reply}\n\n")

    st.markdown("### \U0001f553 Chat Log History")
    for log_file in sorted(log_dir.glob("*.md"), reverse=True):
        with st.expander(f"\U0001f5c2 {log_file.name}"):
            st.text(log_file.read_text(encoding='utf-8'))


# === TAB 2: MEMORY SEARCH  ===
with tab2:
    st.title("\U0001f9e0 Memory Search")
    try:
        embed_model = HuggingFaceEmbedding(model_name="nomic-ai/nomic-embed-text-v1", trust_remote_code=True)
        chroma_client = chromadb.PersistentClient(path=persist_dir)
        chroma_collection = chroma_client.get_or_create_collection("chatgpt-index")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context, vector_store=vector_store, embed_model=embed_model)
        query_engine = index.as_query_engine()

        memory_input = st.text_input("Ask your memory something:")
        if memory_input:
            memory_response = query_engine.query(memory_input)
            st.success(memory_response.response)

    except Exception as e:
        st.error(f"Memory engine error: {e}")

# === TAB 3: CALENDAR VIEWER + Add Event ===
import json
from calendar_utils import fetch_all_events, load_cached_events

calendar_cache_path = Path("F:/OllamaModels/memory/calendar_cache.json")

with tab3:
    st.title("📅 Calendar")

    if "cached_events" not in st.session_state:
        st.session_state.cached_events = []

    try:
        # Manual Sync Button
        if st.button("🔄 Sync Calendar Events"):
            with st.spinner("Fetching Google Calendar data..."):
                events = fetch_all_events()
                formatted_events = []
                for e in events:
                    start = e['start'].get('dateTime', e['start'].get('date'))
                    end = e['end'].get('dateTime', start)
                    formatted_events.append({
                        "title": e.get("summary", "No Title"),
                        "start": start,
                        "end": end
                    })

                # Save to cache (file)
                calendar_cache_path.write_text(json.dumps(formatted_events, indent=2), encoding="utf-8")

                # Save to session state (live cache)
                st.session_state.cached_events = formatted_events

                st.success("✅ Calendar synced and cached!")

        # Load from file if no session cache
        if not st.session_state.cached_events and calendar_cache_path.exists():
            st.session_state.cached_events = json.loads(calendar_cache_path.read_text(encoding="utf-8"))

        calendar_options = {
            "initialView": "dayGridMonth",
            "editable": False,
            "selectable": False,
            "height": 600,
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": ""
            }
        }

        calendar(events=st.session_state.cached_events, options=calendar_options)

        # Add new event form
        with st.expander("➕ Add New Event"):
            with st.form("add_event_form"):
                title = st.text_input("Event Title")
                date = st.date_input("Date", value=datetime.date.today())
                start_time = st.time_input("Start Time", value=datetime.time(9, 0))
                duration = st.number_input("Duration (hours)", min_value=0.25, max_value=24.0, step=0.25, value=1.0)
                submit = st.form_submit_button("Create Event")

                if submit:
                    start_dt = datetime.datetime.combine(date, start_time)
                    end_dt = start_dt + datetime.timedelta(hours=duration)
                    new_event = add_event(title, start_dt, end_dt)
                    st.success(f"✅ Event added: {new_event.get('summary')}")

    except Exception as e:
        st.error(f"❌ Calendar Error: {e}")

# === TAB 4: NOTION TASKS ===
with tab4:
    st.title("\U0001f4cb Synced Notion Tasks")
    try:
        raw_tasks = fetch_notion_tasks(limit=100)
        sort_by = st.selectbox("Sort by", ["xp", "roi", "name"])
        category_list = sorted({t.get("category", "None") or "None" for t in raw_tasks})
        status_list = sorted({t.get("status", "None") or "None" for t in raw_tasks})
        category = st.selectbox("Filter by Category", ["All"] + category_list)
        status = st.selectbox("Filter by Status", ["All"] + status_list)

        notion_tasks = [
            t for t in raw_tasks
            if (category == "All" or t.get("category", "None") == category)
            and (status == "All" or t.get("status", "None") == status)
        ]

        st.markdown("""
        <div style='max-height: 500px; overflow-y: auto; padding-right: 10px;'>
        """, unsafe_allow_html=True)

        for task in notion_tasks:
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                st.markdown(f"""
                **🧠 {task['name']}**  
                🧬 XP: **{task['xp']}** | 💹 ROI: **{task['roi']}**  
                🗂️ Category: *{task.get('category', 'None')}* | 📌 Status: *{task.get('status', 'None')}*  
                📝 Reason: _{task['reason']}_  
                <hr style=\"margin: 6px 0;\">
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✅", key=task['name']):
                    success = mark_task_complete(task['name'])
                    if success:
                        st.success(f"Marked '{task['name']}' as Done")
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Failed to fetch Notion tasks: {e}")

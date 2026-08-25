import streamlit as st
import sys
from pathlib import Path
import os
import shutil
import ollama
import json
import time

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from fashion_ai.wardrobeinference.build_wardrobe_yolo import build_wardrobe
from travel_context_ai.scripts.ocr_ticket import ocr_ticket
from travel_context_ai.scripts.travel_context import understand_trip
from recommendation_engine.scripts.recommend_outfit import recommend
from style_assistant.scripts.build_prompt import build_prompt_from_candidates
from style_assistant.scripts.outfit_validator import validate_outfit_json
from style_assistant.scripts.markdown_formatter import format_outfit_markdown, build_strict_markdown

from travel_context_ai.config import TICKET_IMAGE
from fashion_ai.wardrobeinference.config import PHOTOS_DIR, COLOR_CROPS_DIR

st.set_page_config(
    page_title="Jio Lookbook",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Injection
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}

/* Global Scale Down */
html {
    font-size: 90% !important;
}

.stApp {
    background: linear-gradient(135deg, #020617 0%, #0f172a 100%);
    color: #f8fafc;
}

/* Gradient Title */
h1 {
    background: linear-gradient(to right, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700 !important;
    padding-bottom: 10px;
}

/* Glassmorphism for Alerts/Info */
[data-testid="stAlert"] {
    background: rgba(255, 255, 255, 0.03) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    color: #e2e8f0;
}

/* File Uploaders */
[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.02);
    border: 1px dashed rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    padding: 10px;
    transition: all 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: #818cf8;
    background: rgba(255, 255, 255, 0.05);
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px -10px rgba(168, 85, 247, 0.8) !important;
}

/* Sliders */
.stSlider div[data-testid="stThumbValue"] {
    color: #c084fc !important;
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "trip_context" not in st.session_state:
    st.session_state.trip_context = None
if "wardrobe" not in st.session_state:
    st.session_state.wardrobe = None
if "rec_data" not in st.session_state:
    st.session_state.rec_data = None
if "messages" not in st.session_state:
    st.session_state.messages = []

def stream_ollama(model_name, messages):
    try:
        response = ollama.chat(
            model=model_name,
            messages=messages,
            stream=True,
            format="json"
        )
        for chunk in response:
            yield chunk['message']['content']
    except Exception as e:
        yield f"**Error connecting to Ollama:** {str(e)}\n\nPlease ensure Ollama is running locally and the '{model_name}' model is pulled."

def get_priority_stars(priority):
    p = priority.lower()
    if p == "high": return "⭐⭐⭐ High"
    if p == "medium": return "⭐⭐ Medium"
    return "⭐ Low"

st.title("👗 Jio Lookbook")
st.subheader("AI Travel Outfit Assistant")

with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("🧹 Clear Cache & Reset App"):
        st.session_state.clear()
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Overview", "👕 Wardrobe", "✨ AI Stylist"])

with tab1:
    input_col, info_col = st.columns([2, 1])

    with info_col:
        st.info("🤖 AI Stylist Model: **mistral** (running locally via Ollama)")
        budget = st.slider("Budget (₹)", 1000, 10000, 5000, step=500)

    with input_col:
        st.markdown("### ✨ What are you dressing for?")
        occasion = st.selectbox(
            "Occasion",
            ["✈️ Travel", "☕ Cafe", "💼 Office", "🍸 Bar / Club", "💍 Wedding", "🎉 Party", "🏃 Casual Day"],
            label_visibility="collapsed"
        )
        
        gender = st.radio("Gender", ["Women", "Men"], horizontal=True)
        
        # Map frontend occasion string to the dictionary key
        occ_key_map = {
            "✈️ Travel": "travel",
            "☕ Cafe": "cafe",
            "💼 Office": "office",
            "🍸 Bar / Club": "bar / club",
            "💍 Wedding": "wedding",
            "🎉 Party": "party",
            "🏃 Casual Day": "casual day"
        }
        occ_key = occ_key_map.get(occasion, "default")
        
        from metadata.outfit_presets import OUTFIT_PRESETS
        vibe_options = []
        if occ_key in OUTFIT_PRESETS:
            gender_key = gender.lower()
            if gender_key in OUTFIT_PRESETS[occ_key]:
                vibe_options = list(OUTFIT_PRESETS[occ_key][gender_key].keys())
                
        vibe = None
        if vibe_options and occasion != "✈️ Travel":
            vibe = st.selectbox("Vibe / Style", vibe_options)
        
        dyn_context = {}
        ticket = None
        
        if occasion == "✈️ Travel":
            dyn_context["trip"] = "Travel"
            
            # Destination Input and Auto-Detect
            dest = st.text_input("Destination", value=st.session_state.get("last_destination", "Zurich"))
            if dest != st.session_state.get("last_destination"):
                st.session_state["last_destination"] = dest
                
            ticket = st.file_uploader("📄 Travel Ticket (Optional OCR extraction)", type=["jpg", "jpeg", "png", "pdf"])
                
            if st.button("✨ Auto-Detect Trip Context"):
                with st.spinner("Analyzing destination..."):
                    from style_assistant.scripts.trip_detector import detect_trip_context, extract_destination_from_ticket
                    
                    # If a ticket was uploaded, run OCR first
                    if ticket is not None:
                        ocr_dest = extract_destination_from_ticket(ticket.getvalue())
                        if ocr_dest:
                            dest = ocr_dest
                            st.session_state["last_destination"] = dest
                    
                    res = detect_trip_context(dest)
                    st.session_state["detected_type"] = res.get("destination_type", "City")
                    st.session_state["detected_weather"] = res.get("weather", "Pleasant")
                st.rerun()
            
            col1, col2 = st.columns(2)
            
            dest_types = ["Beach", "Snow Mountains", "Hills", "City", "Countryside", "Desert", "Cruise", "Forest"]
            default_type = st.session_state.get("detected_type", "City")
            type_idx = dest_types.index(default_type) if default_type in dest_types else 3
            dest_type = col1.selectbox("Destination Type", dest_types, index=type_idx)
            
            weathers = ["Hot", "Warm", "Pleasant", "Rainy", "Cold", "Snow"]
            default_weather = st.session_state.get("detected_weather", "Pleasant")
            weather_idx = weathers.index(default_weather) if default_weather in weathers else 2
            dyn_context["weather"] = col2.selectbox("Weather", weathers, index=weather_idx)
            
            dyn_context["destination"] = dest
            vibe = dest_type
            
        elif occasion == "☕ Cafe":
            dyn_context["trip"] = "Cafe"
            col1, col2, col3 = st.columns(3)
            dyn_context["activities"] = ["Coffee", "Chatting", "Relaxing"]
            
        elif occasion == "💼 Office":
            dyn_context["trip"] = "Office"
            col1, col2 = st.columns(2)
            dyn_context["activities"] = ["Meetings", "Desk Work"]
            
        elif occasion == "💍 Wedding":
            dyn_context["trip"] = "Wedding"
            col1, col2 = st.columns(2)
            dyn_context["activities"] = ["Attending Wedding", "Photos"]
            
        else:
            dyn_context["trip"] = "Casual Day"
            dyn_context["activities"] = ["Walking", "Errands", "Relaxing"]
            
        st.markdown("---")
        photos = st.file_uploader("👕 Upload Wardrobe Photos (Optional)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        use_default = st.checkbox("Use sample wardrobe (Jio Lookbook defaults) if no photos uploaded", value=True)

    if st.button("✨ Generate Stylist Dashboard"):
        st.session_state.messages = [] # reset chat
        
        progress_bar = st.progress(0, text="Initializing Pipeline...")
        status_box = st.empty()
        
        # Step 1
        progress_bar.progress(10, text="Saving uploaded files...")
        status_box.markdown("✅ Processing Uploads...")
        if ticket:
            TICKET_IMAGE.parent.mkdir(parents=True, exist_ok=True)
            with open(TICKET_IMAGE, "wb") as f:
                f.write(ticket.getbuffer())
        if photos:
            if PHOTOS_DIR.exists():
                shutil.rmtree(PHOTOS_DIR)
            PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
            for photo in photos:
                photo_path = PHOTOS_DIR / photo.name
                with open(photo_path, "wb") as f:
                    f.write(photo.getbuffer())

        # Step 2
        progress_bar.progress(30, text="🧠 Setting up event context...")
        status_box.markdown("✅ Uploads Processed\n\n✅ Structuring Event...")
        
        if ticket and occasion == "✈️ Travel":
            ocr_ticket(silent=True)
            st.session_state.trip_context = understand_trip(silent=True)
            st.session_state.trip_context["gender"] = gender.lower()
            if vibe:
                st.session_state.trip_context["vibe"] = vibe
        else:
            st.session_state.trip_context = {
                "destination": dyn_context.get("destination", dyn_context.get("setting", dyn_context.get("wedding_type", dyn_context.get("cafe_type", "Local")))),
                "weather": dyn_context.get("weather", dyn_context.get("season", "Controlled")),
                "trip": dyn_context.get("trip", "Event"),
                "activities": dyn_context.get("activities", []),
                "gender": gender.lower()
            }
            if vibe:
                st.session_state.trip_context["vibe"] = vibe
            if "dress_code" in dyn_context:
                st.session_state.trip_context["activities"].append(f"Dress Code: {dyn_context['dress_code']}")
            if "time" in dyn_context:
                st.session_state.trip_context["activities"].append(f"Time: {dyn_context['time']}")

        # Step 3
        progress_bar.progress(60, text="🤖 Running LLaVA Vision Model on wardrobe photos (Heavy Step)...")
        status_box.markdown("✅ Context Ready\n\n⏳ Building Wardrobe...")
        
        if photos:
            from fashion_ai.wardrobeinference.build_wardrobe_llava import build_wardrobe
            st.session_state.wardrobe = build_wardrobe(silent=True)
        elif use_default:
            import json
            from fashion_ai.wardrobeinference.config import WARDROBE_FILE
            with open(WARDROBE_FILE, "r", encoding="utf-8") as f:
                st.session_state.wardrobe = json.load(f)
        else:
            st.session_state.wardrobe = []

        # Step 4
        progress_bar.progress(90, text="🛍️ Analyzing gaps and building privacy-safe query...")
        status_box.markdown("✔ Context Ready\n\n✔ Wardrobe Built\n\n⏳ Generating Recommendations...")
        st.session_state.rec_data = recommend(st.session_state.wardrobe, st.session_state.trip_context, silent=True)

        progress_bar.progress(100, text="Analysis complete! Check the AI Stylist tab.")
        status_box.markdown("✔ Context Ready\n\n✔ Wardrobe Built\n\n✔ Recommendations Ready\n\n✔ AI Stylist Ready!")
        time.sleep(1)
        progress_bar.empty()
        status_box.empty()
            
    if st.session_state.trip_context:
        st.success("Analysis complete! Head over to the **✨ AI Stylist** tab to see your outfits.")
        
        with st.expander("🔒 Privacy Layer", expanded=False):
            st.success("✓ Photos are processed locally and NEVER shared.")
            st.write("Instead of sending your personal photos to a store, we search their catalog using these text tags:")
            
            for query in st.session_state.rec_data['ajio_query']:
                category = query.get('category', '').title()
                colors = ", ".join(query.get('preferred_colors', []))
                st.markdown(f"- **Search:** `{colors} {category}`")
                
            st.code(json.dumps(st.session_state.rec_data['ajio_query'], indent=2), language="json")

with tab2:
    if st.session_state.wardrobe:
        st.markdown("### 👕 Wardrobe Summary")
        
        tops_cats = ["shirt", "t-shirt", "top", "jacket", "sweater", "hoodie"]
        bottoms_cats = ["pants", "jeans", "shorts", "skirt"]
        trad_cats = ["saree", "kurta", "churidaar", "dhoti", "lehenga", "anarkali", "sherwani", "kameez", "shalwar"]
        footwear_cats = ["shoes", "sandals", "boots"]
        
        tops = 0
        bottoms = 0
        trad = 0
        foot = 0
        others = 0
        
        for item in st.session_state.wardrobe:
            cat = item['category'].lower()
            if cat in tops_cats: tops += 1
            elif cat in bottoms_cats: bottoms += 1
            elif cat in trad_cats: trad += 1
            elif cat in footwear_cats: foot += 1
            else: others += 1
            
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("👕 Tops", tops)
        m2.metric("👖 Bottoms", bottoms)
        m3.metric("🥻 Traditional", trad)
        m4.metric("👟 Footwear", foot)
        
        st.markdown("---")
        with st.expander("🖼️ View Visual Gallery (YOLO Detections)", expanded=True):
            cols = st.columns(4)
            for i, item in enumerate(st.session_state.wardrobe):
                with cols[i % 4]:
                    crop_path = COLOR_CROPS_DIR / item.get("crop", "")
                    photo_path = PHOTOS_DIR / item.get("image", "")
                    
                    # Fallback for LLaVA which doesn't create crops
                    display_path = crop_path if crop_path.exists() else photo_path

                    with st.container(border=True):
                        if display_path.exists():
                            st.image(str(display_path), width=150)
                            st.caption(f"**👕 {item['color']} {item['category'].title()}**\n\nConfidence {item['confidence']*100:.0f}%")
                        else:
                            st.write(f"Missing image: {item.get('image')}")
    else:
        st.info("Run the Analysis in the Overview tab first.")

with tab3:
    if st.session_state.rec_data:
        st.markdown("## ✨ AI Stylist")
        st.markdown("────────────────────────")
        
        # Denser Layout
        col_trip, col_shop = st.columns(2)
        
        with col_trip:
            st.markdown("### 📅 Occasion Details")
            st.metric("📍 Location", st.session_state.trip_context.get('destination', 'Unknown'))
            st.metric("☀ Weather", st.session_state.trip_context.get('weather', 'Unknown').title())
            st.metric("🎉 Event", st.session_state.trip_context.get('trip', 'Unknown').title())
            vibe_val = st.session_state.trip_context.get('vibe')
            if vibe_val:
                st.metric("✨ Vibe", vibe_val.title())
            st.metric("👤 Gender", st.session_state.trip_context.get('gender', 'Unknown').title())
            
        with col_shop:
            st.markdown("### 🛍️ Shopping Recommendations")
            if st.session_state.rec_data['missing_items']:
                for item in st.session_state.rec_data['missing_items']:
                    p = item.get('priority', 'High').lower()
                    msg = f"**🩴 {item['category'].title()}**\n\nPriority: {get_priority_stars(item.get('priority', 'High'))}\n\nReason: {item['reason']}"
                    if p == "high":
                        st.warning(msg)
                    elif p == "medium":
                        st.info(msg)
                    else:
                        st.success(msg)
            else:
                st.success("✓ You have everything you need!")
                
        st.markdown("────────────────────────")
        
        # Initialize first message if empty
        if len(st.session_state.messages) == 0:
            system_prompt, initial_prompt = build_prompt_from_candidates(st.session_state.rec_data)
            st.session_state.messages.append({"role": "system", "content": system_prompt})
            st.session_state.messages.append({"role": "user", "content": initial_prompt})
            
            # Generate initial response invisibly, then format
            with st.chat_message("assistant"):
                with st.spinner("✨ The Stylist is building your perfect outfit..."):
                    
                    # 1. Check for Strict Template match (The guaranteed good fallback)
                    strict_look = None
                    occ_str = st.session_state.rec_data.get("occasion", "").lower()
                    
                    gender_str = gender.lower()
                    vibe_str = vibe # this captures both standard vibes and Destination Types for Travel
                    
                    try:
                        from metadata.strict_templates import STRICT_TEMPLATES
                        if occ_str in STRICT_TEMPLATES and gender_str in STRICT_TEMPLATES[occ_str]:
                            if vibe_str in STRICT_TEMPLATES[occ_str][gender_str]:
                                strict_look = STRICT_TEMPLATES[occ_str][gender_str][vibe_str]
                    except ImportError:
                        pass
                        
                    # 2. Get LLM response
                    raw_json_response = ""
                    cands = st.session_state.rec_data.get("candidates", {})
                    has_cands = any(len(lst) > 0 for lst in cands.values())
                    
                    for chunk in stream_ollama("mistral", st.session_state.messages):
                        raw_json_response += chunk
                        
                    validated = validate_outfit_json(raw_json_response, st.session_state.rec_data)
                    ai_markdown = format_outfit_markdown(validated)
                    
                    if not has_cands:
                        ai_markdown = "⚠️ **Note: Since your wardrobe is empty, the AI has acted as a personal shopper and built a completely new outfit for you from scratch!**\n\n" + ai_markdown
                    
                    # 3. Combine if strict exists
                    if strict_look:
                        strict_markdown = build_strict_markdown(strict_look, st.session_state.rec_data)
                        final_markdown = strict_markdown + "\n\n---\n\n### 🤖 AI Alternative Suggestion\n\n" + ai_markdown
                    else:
                        final_markdown = ai_markdown
                        
                st.markdown(final_markdown)
            # Store the markdown in history so it renders nicely next time
            st.session_state.messages.append({"role": "assistant", "content": final_markdown, "raw_json": raw_json_response})
            
        else:
            # Display past messages
            for message in st.session_state.messages:
                if message["role"] == "system":
                    continue
                # Skip the user's initial giant JSON prompt payload for cleaner UI
                if message["role"] == "user" and "Here are the candidates" in message["content"]:
                    continue
                    
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input("💬 Ask the stylist (e.g., Can I wear a saree for dinner?)", key="stylist_chat_input"):
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            # Add to state
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Generate assistant response
            with st.chat_message("assistant"):
                with st.spinner("Styling outfit..."):
                    raw_json_response = ""
                    for chunk in stream_ollama("mistral", st.session_state.messages):
                        raw_json_response += chunk
                        
                    validated = validate_outfit_json(raw_json_response, st.session_state.rec_data)
                    markdown_out = format_outfit_markdown(validated)
                    
                st.markdown(markdown_out)
            st.session_state.messages.append({"role": "assistant", "content": markdown_out, "raw_json": raw_json_response})
    else:
        st.info("Run the Analysis in the Overview tab first.")
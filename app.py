import streamlit as st
import sys
from pathlib import Path
import os
import shutil
import os
from groq import Groq
import json
import time

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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Global Font & Text */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #1e293b !important;
}

/* Global Scale */
html {
    font-size: 95% !important;
}

/* Bright & Clean App Background */
.stApp {
    background: #f8fafc;
    background-image: radial-gradient(circle at 100% 0%, #ffffff 0%, #f1f5f9 100%);
    color: #0f172a;
}

/* Vibrant Gradient Title */
h1 {
    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    padding-bottom: 10px;
}

/* Headers */
h2, h3, h4, label {
    color: #334155 !important;
    font-weight: 700 !important;
}

/* Beautiful White Cards for Info/Expanders */
[data-testid="stAlert"], [data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
    color: #334155 !important;
}

/* Aesthetic File Uploaders */
[data-testid="stFileUploader"] {
    background: #ffffff;
    border: 2px dashed #cbd5e1;
    border-radius: 16px;
    padding: 15px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
}
[data-testid="stFileUploader"]:hover {
    border-color: #FF6B6B;
    background: #fff5f5;
    transform: translateY(-2px);
}

/* Pinterest Style Image Gallery */
.stImage > img {
    border-radius: 16px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.stImage > img:hover {
    transform: scale(1.03);
    box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    cursor: pointer;
}

/* Vibrant Action Buttons */
.stButton > button {
    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%) !important;
    color: white !important;
    border-radius: 30px !important;
    border: none !important;
    padding: 0.6rem 2.5rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 14px rgba(255, 107, 107, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(255, 107, 107, 0.5) !important;
}

/* Beautiful Floating Metric Cards */
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #f1f5f9;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
    transition: all 0.3s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.08);
}
div[data-testid="stMetricValue"] {
    color: #0f172a !important;
    font-weight: 800 !important;
}

/* Clean Input Fields */
.stTextInput input, .stSelectbox > div[data-baseweb="select"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    color: #1e293b !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
}
.stTextInput input:focus, .stSelectbox > div[data-baseweb="select"]:focus-within {
    border-color: #FF6B6B !important;
    box-shadow: 0 0 0 1px #FF6B6B !important;
}

/* Custom Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 15px;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    border-radius: 12px 12px 0 0;
    padding: 10px 25px;
    font-weight: 600;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-bottom: none;
    color: #64748b;
}
.stTabs [aria-selected="true"] {
    background: #FF6B6B !important;
    color: white !important;
    border-color: #FF6B6B !important;
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

def stream_llm(model_name, messages):
    try:
        api_key = None
        try:
            api_key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            pass
            
        if not api_key:
            api_key = os.environ.get("GROQ_API_KEY")
            
        if not api_key:
            yield "**Error:** GROQ_API_KEY is missing! If you are on Streamlit Cloud, you MUST add it via the website: Click 'Manage app' (bottom right) -> '⋮' -> 'Settings' -> 'Secrets'."
            return

        client = Groq(api_key=api_key)
        
        # Groq uses different model names, map mistral to miqtral-8x7b-32768
        groq_model = "openai/gpt-oss-20b" 
        
        clean_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
        response = client.chat.completions.create(
            model=groq_model,
            messages=clean_messages,
            stream=True,
            response_format={"type": "json_object"}
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"**Error connecting to Cloud API:** {str(e)}"

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
        st.info("?? AI Stylist Model: **GPT OSS 20B** (Cloud API via Groq)")
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
        
        from recommendation_engine.metadata.outfit_presets import OUTFIT_PRESETS
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
            if "dest_val" not in st.session_state:
                st.session_state["dest_val"] = "Zurich"
                
            dest = st.text_input("Destination", value=st.session_state["dest_val"])
            st.session_state["dest_val"] = dest
            dyn_context["destination"] = dest
                
            ticket = st.file_uploader("📄 Travel Ticket (Optional OCR extraction)", type=["jpg", "jpeg", "png", "pdf"], key="ticket_upload")
            
            if st.button("✨ Auto-Detect Trip Context"):
                st.session_state["run_auto_detect_flag"] = True

            if st.session_state.get("run_auto_detect_flag"):
                st.session_state["run_auto_detect_flag"] = False
                with st.spinner("🤖 AI is analyzing your ticket and trip context... (This takes about 10-15 seconds)"):
                    ticket_file = st.session_state.get("ticket_upload")
                    current_dest = st.session_state.get("dest_val", "Zurich")
                    
                    if ticket_file is not None:
                        try:
                            ticket_bytes = ticket_file.getvalue()
                            from style_assistant.scripts.trip_detector import extract_destination_from_ticket, get_groq_client
                            
                            if not get_groq_client():
                                st.error("🚨 **API KEY MISSING!** The Cloud server cannot see your local secrets.toml. Please add it to 'Manage app' > 'Settings' > 'Secrets'!")
                            
                            ocr_dest = extract_destination_from_ticket(ticket_bytes)
                            if ocr_dest == "ERROR_RATE_LIMIT":
                                st.error("🚨 **API Rate Limit Reached!** You clicked too fast and hit Groq's 8,000 Token-Per-Minute limit. **Please wait exactly 60 seconds** and try again.")
                            elif ocr_dest:
                                current_dest = ocr_dest
                                st.session_state["dest_val"] = ocr_dest
                            else:
                                if get_groq_client():
                                    st.error("🚨 **API Request Failed!** The vision model returned an empty string. This could be a rate limit or a timeout.")
                        except Exception as e:
                            st.warning(f"⚠️ Pipeline crashed: {e}")
                    
                    from style_assistant.scripts.trip_detector import detect_trip_context
                    res = detect_trip_context(current_dest)
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
            PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
            for photo in photos:
                photo_path = PHOTOS_DIR / photo.name
                with open(photo_path, "wb") as f:
                    f.write(photo.getbuffer())

        # Step 2
        progress_bar.progress(30, text="🧠 Setting up event context...")
        status_box.markdown("✅ Uploads Processed\n\n✅ Structuring Event...")
        
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
            with open(WARDROBE_FILE, "r", encoding="utf-8-sig") as f:
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
            
    if st.session_state.rec_data:
        st.success("Analysis complete! Head over to the **✨ AI Stylist** tab to see your outfits.")
        
        with st.expander("🔒 Privacy Layer", expanded=False):
            st.success("✅ Photos are processed locally and NEVER shared.")
            st.write("Instead of sending your personal photos to a store, we search their catalog using these text tags:")
            
            for query in st.session_state.rec_data.get('ajio_query', []):
                category = query.get('category', '').title()
                colors = ", ".join(query.get('preferred_colors', []))
                st.markdown(f"- **Search:** `{colors} {category}`")
                
            st.code(json.dumps(st.session_state.rec_data['ajio_query'], indent=2), language="json")

with tab2:
    if "wardrobe" in st.session_state and st.session_state.wardrobe is not None:
        if len(st.session_state.wardrobe) == 0:
            st.warning("Your wardrobe is empty! Upload some photos or use the default sample wardrobe.")
        else:
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
            cat = item.get('category', '').lower()
            if any(t in cat for t in tops_cats): tops += 1
            elif any(t in cat for t in bottoms_cats): bottoms += 1
            elif any(t in cat for t in trad_cats): trad += 1
            elif any(t in cat for t in footwear_cats): foot += 1
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
                    crop_val = item.get("crop")
                    image_val = item.get("image")
                    
                    display_path = None
                    if crop_val and (COLOR_CROPS_DIR / crop_val).is_file():
                        display_path = COLOR_CROPS_DIR / crop_val
                    elif image_val and (PHOTOS_DIR / image_val).is_file():
                        display_path = PHOTOS_DIR / image_val
                    
                    with st.container(border=True):
                        if display_path:
                            st.image(str(display_path), width=150)
                            st.caption(f"**👕 {item.get('color', '')} {item.get('category', '').title()}**\n\nConfidence {item.get('confidence', 0)*100:.0f}%")
                        else:
                            st.write(f"Missing image: {image_val}")
    else:
        st.info("Run the Analysis in the Overview tab first.")

with tab3:
    if "rec_data" in st.session_state and st.session_state.rec_data is not None:
        if len(st.session_state.rec_data) == 0:
            st.warning("No recommendations could be generated. Please ensure your wardrobe is not empty.")
        else:
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
                        from recommendation_engine.metadata.strict_templates import STRICT_TEMPLATES
                        if occ_str in STRICT_TEMPLATES and gender_str in STRICT_TEMPLATES[occ_str]:
                            if vibe_str in STRICT_TEMPLATES[occ_str][gender_str]:
                                strict_look = STRICT_TEMPLATES[occ_str][gender_str][vibe_str]
                    except ImportError:
                        pass
                        
                    # 2. Get LLM response
                    raw_json_response = ""
                    cands = st.session_state.rec_data.get("candidates", {})
                    has_cands = any(len(lst) > 0 for lst in cands.values())
                    
                    for chunk in stream_llm("mistral", st.session_state.messages):
                        raw_json_response += chunk
                        
                    if "**Error" in raw_json_response:
                        ai_markdown = raw_json_response
                    else:
                        validated = validate_outfit_json(raw_json_response, st.session_state.rec_data)
                        ai_markdown = format_outfit_markdown(validated)
                    
                    if not has_cands and "**Error" not in raw_json_response:
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
                    for chunk in stream_llm("mistral", st.session_state.messages):
                        raw_json_response += chunk
                        
                    if "**Error" in raw_json_response:
                        markdown_out = raw_json_response
                    else:
                        validated = validate_outfit_json(raw_json_response, st.session_state.rec_data)
                        markdown_out = format_outfit_markdown(validated)
                    
                st.markdown(markdown_out)
            st.session_state.messages.append({"role": "assistant", "content": markdown_out, "raw_json": raw_json_response})
    else:
        st.info("Run the Analysis in the Overview tab first.")
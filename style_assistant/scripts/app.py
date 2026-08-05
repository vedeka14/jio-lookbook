import streamlit as st
import ollama
import time
import re
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from style_assistant.scripts.build_prompt import build_prompt, trip, grouped

st.set_page_config(page_title="Goa Trip Outfit Helper", page_icon="🌴", layout="wide")

st.title("🌴 Goa Trip Outfit Helper")
st.markdown("Your personal AI fashion consultant for your Goa vacation, powered by local LLMs.")

# Sidebar for config
with st.sidebar:
    model_name = "llama3"
    
    st.header("📊 Pipeline Status")
    st.markdown("✅ Ticket Processed")
    st.markdown("✅ Trip Understood")
    st.markdown("✅ Wardrobe Built")
    st.markdown("✅ Recommendations Generated")
    st.markdown("🤖 **AI Stylist Ready**")
    st.markdown("---")
    st.markdown("**Model Used:** Llama 3")

# Build the prompt
try:
    prompt = build_prompt()
except Exception as e:
    st.error(f"Failed to build prompt from JSON data. Error: {e}")
    st.stop()

import os
import glob
from collections import defaultdict

# Display CV Pipeline Gallery
with st.expander("🖼️ Computer Vision Pipeline", expanded=False):
    st.markdown("Raw data processed by the OCR and YOLO vision models.")
    cv_col1, cv_col2 = st.columns([1, 2])
    
    with cv_col1:
        st.markdown("**1. Travel Ticket (OCR Input)**")
        ticket_dir = str(Path(__file__).resolve().parent.parent.parent / "travel_context_ai" / "data" / "tickets")
        tickets = glob.glob(os.path.join(ticket_dir, "*.*"))
        if tickets:
            st.image(tickets[0], use_container_width=True, caption="Uploaded Ticket")
            st.info(f"**✈ Flight** | {trip.get('origin', 'Unknown')} → {trip.get('destination', 'Unknown')} | 📅 {trip.get('travel_date', 'Unknown')} | 🛫 IndiGo")
        else:
            st.info("No ticket found.")
            
    with cv_col2:
        from style_assistant.scripts.build_prompt import wardrobe
        st.markdown("**2. Detected Wardrobe (YOLO Output)**")
        
        # Group wardrobe items by category
        w_grouped = defaultdict(list)
        for item in wardrobe:
            cat = item.get("category", "Unknown")
            conf = item.get("confidence", 0.0)
            img = item.get("image", "")
            w_grouped[cat].append((item.get("color", ""), conf, img))
            
        crop_dir = str(Path(__file__).resolve().parent.parent.parent / "fashion_ai" / "wardrobeinference" / "data" / "crops")
        
        for cat, items in w_grouped.items():
            st.markdown(f"**{cat}**")
            cat_cols = st.columns(len(items) + 1) # Extra column to avoid stretching if few
            for i, (color, conf, img) in enumerate(items):
                crop_path = glob.glob(os.path.join(crop_dir, f"*{img.replace('.jpg', '')}*.jpg"))
                with cat_cols[i]:
                    if crop_path:
                        st.image(crop_path[0], width=120)
                    st.caption(f"{color} {cat}\n🟢 {int(conf*100)}% Confidence")
        
        st.markdown("---")
        with st.expander("Original Photos ▼"):
            photo_dir = str(Path(__file__).resolve().parent.parent.parent / "fashion_ai" / "wardrobeinference" / "data" / "photos")
            photos = glob.glob(os.path.join(photo_dir, "*.*"))
            if photos:
                st.image(photos, width=100)

# Display Context Summaries
with st.expander("📍 Trip Context", expanded=True):
    col_dest, col_weath, col_act = st.columns(3)
    col_dest.metric("Destination", trip.get("destination", "Unknown"))
    col_weath.metric("Weather", trip.get("weather", "Unknown"))
    col_act.markdown("**Activities:** " + " • ".join(trip.get("activities", ["None"])))

with st.expander("👚 Wardrobe Summary", expanded=True):
    s_col1, s_col2, s_col3, s_col4, s_col5 = st.columns(5)
    s_col1.metric("Base Layers", len(grouped["Base Layers"]))
    s_col2.metric("Outerwear", len(grouped["Outerwear"]))
    s_col3.metric("Bottoms", len(grouped["Bottoms"]))
    s_col4.metric("Footwear", len(grouped["Footwear"]))
    s_col5.metric("Accessories", len(grouped["Accessories"]))

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    
def parse_stylist_response(text):
    patterns = {
        "Trip Summary": r"Trip Summary[\s\r\n]+(.*?)(?=Outfit 1|\Z)",
        "Outfit 1": r"Outfit 1[\s\r\n]+(.*?)(?=Outfit 2|\Z)",
        "Outfit 2": r"Outfit 2[\s\r\n]+(.*?)(?=Shopping Recommendations|\Z)",
        "Shopping Recommendations": r"Shopping Recommendations[\s\r\n]+(.*?)(?=Styling Tips|\Z)",
        "Styling Tips": r"Styling Tips[\s\r\n]+(.*?)\Z"
    }
    parsed = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            parsed[key] = match.group(1).strip()
            
    if not parsed.get("Outfit 1") or not parsed.get("Shopping Recommendations"):
        return None
    return parsed

def apply_badges_and_icons(text):
    text = text.replace("Top:", "👕 **Top**")
    text = text.replace("Layer:", "🧥 **Layer**")
    text = text.replace("Bottom:", "👖 **Bottom**")
    text = text.replace("Footwear:", "🥾 **Footwear**")
    text = text.replace("Accessories:", "🧤 **Accessories**")
    text = text.replace("Reason:", "💡 **Reason**")
    
    # HTML Badges
    wardrobe_badge = '<span style="background-color: #1E3A8A; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-left: 8px; vertical-align: middle;">Wardrobe</span>'
    buy_badge = '<span style="background-color: #9A3412; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-left: 8px; vertical-align: middle;">Buy</span>'
    
    text = text.replace("(Wardrobe)", wardrobe_badge)
    text = text.replace("(Shopping Recommendation)", buy_badge)
    return text

def format_shopping_list(text):
    # Split by double newlines into blocks
    blocks = text.split("\n\n")
    formatted_blocks = []
    for block in blocks:
        if not block.strip(): continue
        # Add emojis to common items
        if "Jacket" in block or "Coat" in block or "Sweater" in block or "Hoodie" in block:
            block = "🧥 **" + block.replace("**", "")
        elif "Boots" in block or "Shoes" in block or "Sneakers" in block:
            block = "🥾 **" + block.replace("**", "")
        elif "Gloves" in block or "Scarf" in block or "Cap" in block:
            block = "🧤 **" + block.replace("**", "")
        else:
            block = "🛍️ **" + block.replace("**", "")
            
        block = block.replace("Priority: High", "🔴 **High Priority**")
        block = block.replace("Priority: Medium", "🟡 **Medium Priority**")
        block = block.replace("Priority: Low", "🟢 **Low Priority**")
            
        # Ensure the first newline acts as the end of the bold item name
        block = block.replace("\n", "**\n", 1)
        formatted_blocks.append(block)
        
    return "\n\n---\n\n".join(formatted_blocks)

def find_crop_image(item_text):
    text_lower = item_text.lower()
    from style_assistant.scripts.build_prompt import wardrobe
    crop_dir = str(Path(__file__).resolve().parent.parent.parent / "fashion_ai" / "wardrobeinference" / "data" / "crops")
    for item in wardrobe:
        cat = item.get("category", "").lower()
        col = item.get("color", "").lower()
        if cat and col and cat in text_lower and col in text_lower:
            img = item.get("image", "")
            crop_path = glob.glob(os.path.join(crop_dir, f"*{img.replace('.jpg', '')}*.jpg"))
            if crop_path:
                return crop_path[0]
    return None

def render_outfit_with_images(parsed_outfit):
    lines = apply_badges_and_icons(parsed_outfit).split("\n")
    for line in lines:
        if line.strip():
            st.markdown(line, unsafe_allow_html=True)
            if "Wardrobe" in line:
                crop = find_crop_image(line)
                if crop:
                    st.image(crop, width=60)

def render_cards(parsed_data):
    if parsed_data.get("Trip Summary"):
        st.markdown("### 🧳 Trip Summary")
        st.info(parsed_data["Trip Summary"])
        
    col1, col2 = st.columns(2)
    with col1:
        if parsed_data.get("Outfit 1"):
            with st.container(border=True):
                st.markdown("### 👕 Outfit 1")
                render_outfit_with_images(parsed_data["Outfit 1"])
    with col2:
        if parsed_data.get("Outfit 2"):
            with st.container(border=True):
                st.markdown("### 👖 Outfit 2")
                render_outfit_with_images(parsed_data["Outfit 2"])
            
    col3, col4 = st.columns(2)
    with col3:
        if parsed_data.get("Shopping Recommendations"):
            with st.container(border=True):
                st.markdown("### 🛍 Shopping List")
                formatted_shopping = format_shopping_list(parsed_data["Shopping Recommendations"])
                st.markdown(formatted_shopping)
    with col4:
        if parsed_data.get("Styling Tips"):
            with st.container(border=True):
                st.markdown("### 💡 Styling Tips")
                st.warning(parsed_data["Styling Tips"])

st.markdown("---")
tab_plan, tab_chat, tab_lookbook = st.tabs(["👗 Wardrobe Plan", "💬 Stylist Chat", "📖 My Lookbook"])
has_plan = False

import json
lookbook_path = str(Path(__file__).resolve().parent.parent.parent / "lookbook.json")

def save_to_lookbook(parsed):
    try:
        with open(lookbook_path, "r") as f:
            saved = json.load(f)
    except:
        saved = []
    saved.append(parsed)
    with open(lookbook_path, "w") as f:
        json.dump(saved, f)

with tab_lookbook:
    st.markdown("### 📖 My Saved Outfits")
    if os.path.exists(lookbook_path):
        try:
            with open(lookbook_path, "r") as f:
                saved_looks = json.load(f)
            for i, look in enumerate(reversed(saved_looks)):
                with st.expander(f"Saved Look {len(saved_looks)-i}", expanded=(i==0)):
                    render_cards(look)
        except Exception as e:
            st.error("Could not load lookbook.")
    else:
        st.info("No outfits saved yet. Generate a plan and click 'Save to Lookbook'!")

# Display chat history
with tab_chat:
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
            
        if message["role"] == "assistant" and not has_plan:
            parsed = parse_stylist_response(message["content"])
            if parsed:
                has_plan = True
                with tab_plan:
                    render_cards(parsed)
                    if st.button("💾 Save to Lookbook", type="primary", key="save_btn"):
                        save_to_lookbook(parsed)
                        st.toast("Saved to My Lookbook!")
                with st.chat_message("assistant"):
                    st.info("I've generated your Wardrobe Plan! Check the **👗 Wardrobe Plan** tab above. Let me know if you have any follow-up questions here.")
                continue

        with st.chat_message(message["role"]):
            if message.get("is_initial"):
                st.markdown("*(System generated prompt based on wardrobe and trip data)*")
            else:
                st.markdown(message["content"])

    if len(st.session_state.messages) == 0:
        st.info("Click below to ask the AI stylist to plan your outfits based on your trip context and wardrobe.")
        if st.button("✨ Generate Wardrobe Plan", type="primary"):
            st.session_state.messages.append({"role": "system", "content": "You are an expert AI fashion stylist. Give practical, personalized outfit recommendations based on the user's trip, wardrobe, and preferences."})
            st.session_state.messages.append({"role": "user", "content": prompt, "is_initial": True})
            st.rerun()

    user_input = st.chat_input("Ask a follow-up question (e.g. 'Suggest a different jacket')")
    
    if len(st.session_state.messages) > 0:
        st.markdown("💬 **Try asking:**")
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("Suggest another outfit", use_container_width=True): user_input = "Suggest another outfit"
        if c2.button("What if it rains?", use_container_width=True): user_input = "What if it rains?"
        if c3.button("What jewellery?", use_container_width=True): user_input = "What jewellery?"
        if c4.button("Show formal look", use_container_width=True): user_input = "Show formal look"

    if user_input:
        if len(st.session_state.messages) == 0:
            st.session_state.messages.append({"role": "system", "content": "You are an expert AI fashion stylist. Give practical, personalized outfit recommendations based on the user's trip, wardrobe, and preferences."})
            st.session_state.messages.append({"role": "user", "content": prompt, "is_initial": True})
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

    # Generation step
    if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            try:
                clean_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                response = ollama.chat(
                    model=model_name,
                    messages=clean_messages,
                    stream=True
                )
                for chunk in response:
                    full_response += chunk['message']['content']
                    response_placeholder.markdown(full_response + "▌")
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.rerun()
                
            except Exception as e:
                st.error(f"Error communicating with Ollama: {e}")

# style_assistant/scripts/markdown_formatter.py

def format_outfit_markdown(valid_outfit_json):
    """
    Takes the validated JSON output from the LLM and formats it into the UI Markdown.
    """
    if not valid_outfit_json:
        return "⚠️ Error: The AI produced an invalid outfit combination. Please try again."
        
    outfit = valid_outfit_json.get("outfit", {})
    missing = valid_outfit_json.get("missing", [])
    reason = valid_outfit_json.get("reason", "No reason provided.")
    
    top = outfit.get("top", "")
    bottom = outfit.get("bottom", "")
    full_body = outfit.get("full_body", "")
    outerwear = outfit.get("outerwear", "")
    footwear = outfit.get("footwear", "")
    accessory = outfit.get("accessory", "")
    
    md = "━━━━━━━━━━━━━━\n\n### 👗 Suggested Outfit\n\n"
    
    if full_body:
        md += f"**👗 Full Body:** {full_body}\n\n"
    else:
        if top: md += f"**👕 Top:** {top}\n\n"
        if bottom: md += f"**👖 Bottom:** {bottom}\n\n"
        
    if outerwear: md += f"**🧥 Outerwear:** {outerwear}\n\n"
    if footwear: md += f"**👟 Footwear:** {footwear}\n\n"
    if accessory: md += f"**👜 Accessories:** {accessory}\n\n"
    
    if missing:
        md += "**🛍️ Suggested Purchases:**\n"
        for m in missing:
            md += f"- {m}\n"
        md += "\n"
        
    md += f"💡 **Why?**\n{reason}\n\n━━━━━━━━━━━━━━\n"
    return md

def build_strict_markdown(strict_template, candidate_json):
    """
    Builds a markdown string for the strict template (hardcoded uniform).
    Checks the user's candidates to see if the required items exist.
    """
    outfit = {}
    missing = []
    
    candidates = candidate_json.get("candidates", {})
    
    for slot, required_item in strict_template.items():
        if slot in candidates and candidates[slot]:
            # Simple substring match: if required_item is "Bandhgala", check if "Bandhgala" is in candidate category
            found = False
            for c in candidates[slot]:
                cat = c.get("category", "").lower()
                if cat in required_item.lower() or required_item.lower() in cat:
                    outfit[slot] = c.get("category", required_item).title()
                    found = True
                    break
            
            if not found:
                missing.append(required_item.title())
        else:
            missing.append(required_item.title())
            
    # Format the markdown
    md = "━━━━━━━━━━━━━━\n\n### 🥇 Primary Recommendation (Classic Look)\n\n"
    
    full_body = outfit.get("full_body", "")
    if full_body:
        md += f"**👗 Full Body:** {full_body}\n\n"
    else:
        top = outfit.get("top", "")
        if top: md += f"**👕 Top:** {top}\n\n"
        bottom = outfit.get("bottom", "")
        if bottom: md += f"**👖 Bottom:** {bottom}\n\n"
        
    outerwear = outfit.get("outerwear", "")
    if outerwear: md += f"**🧥 Outerwear:** {outerwear}\n\n"
    footwear = outfit.get("footwear", "")
    if footwear: md += f"**👟 Footwear:** {footwear}\n\n"
    accessory = outfit.get("accessory", "")
    if accessory: md += f"**👜 Accessories:** {accessory}\n\n"
    
    if missing:
        md += "**🛍️ Suggested Purchases:**\n"
        for m in missing:
            md += f"- {m}\n"
        md += "\n"
        
    md += f"💡 **Why?**\nThis is a guaranteed, classic look that perfectly fits the occasion's dress code.\n\n━━━━━━━━━━━━━━\n"
    return md

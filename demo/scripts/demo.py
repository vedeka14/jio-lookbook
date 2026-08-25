import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from fashion_ai.wardrobeinference.build_wardrobe_yolo import build_wardrobe
from travel_context_ai.scripts.ocr_ticket import ocr_ticket
from travel_context_ai.scripts.travel_context import understand_trip
from recommendation_engine.scripts.recommend_outfit import recommend

def print_ok(text):
    try:
        print(f"✓ {text}")
    except UnicodeEncodeError:
        print(f"[OK] {text}")

def main():
    print("\n" + "=" * 60)
    print("          Jio Lookbook – AI Travel Outfit Assistant")
    print("=" * 60)
    print("\nGoal\n")
    print("Personalised travel outfit recommendations")
    print("using AI while keeping wardrobe photos private.")

    print("\nScenario\n")
    print("A user is travelling from Mumbai to Goa and wants")
    print("outfit recommendations based on their existing wardrobe.")

    print("\n" + "=" * 60)
    print("STEP 1 : Building Personal Wardrobe Inventory")
    print("=" * 60)
    print("\nScanning 17 wardrobe images...\n")
    print("Running YOLO11 clothing detection...\n")

    wardrobe = build_wardrobe(silent=True)

    print("\nDetected Clothing & Dominant Colors\n")
    # Display detected items nicely
    for item in wardrobe:
        display_cat = item['category']
        if display_cat.lower() == "t-shirt":
            display_cat = "T-Shirt"
        print_ok(f"{item['color']} {display_cat.title()}")

    print("\nWardrobe inventory created.")
    print_ok(f"{len(wardrobe)} clothing items indexed for recommendations.")

    print("\n" + "=" * 60)
    print("STEP 2 : Reading Travel Ticket")
    print("=" * 60)
    
    ocr_data = ocr_ticket(silent=True)
    
    print("\nTravel Document\n")
    print(f"{ocr_data['origin']}")
    print("↓")
    print(f"{ocr_data['destination']}")
    print("\nTravel Date\n")
    print(f"{ocr_data['travel_date']}")
    
    print("\nRunning EasyOCR document analysis...\n")
    if ocr_data['destination'] != "Unknown":
        print_ok("Destination Found")
    if ocr_data['travel_date'] != "Unknown":
        print_ok("Date Found")

    print("\n" + "=" * 60)
    print("STEP 3 : Understanding Your Trip")
    print("=" * 60)

    print("\nAnalysing travel context using AI...\n")
    trip_context = understand_trip(silent=True)

    print(f"\nDestination\n{trip_context.get('destination', 'Unknown')}\n")
    print(f"Trip Type\n{trip_context.get('trip', 'Unknown')}\n")
    print(f"Weather\n{trip_context.get('weather', 'Unknown')}\n")
    
    packing = trip_context.get('packing_style', 'Unknown')
    if isinstance(packing, list):
        packing = ", ".join(packing)
    print(f"Packing Style\n{packing}")
    print("\n")
    print_ok("Trip profile generated successfully.")

    print("\n" + "=" * 60)
    print("STEP 4 : Personalised Outfit Recommendation")
    print("=" * 60)

    rec_data = recommend(wardrobe, trip_context, silent=True)

    print("\nAvailable Wardrobe")
    for item in wardrobe:
        display_cat = item['category']
        if display_cat.lower() == "t-shirt":
            display_cat = "T-Shirt"
        print_ok(f"{item['color']} {display_cat.title()}")

    for i, item in enumerate(rec_data['missing_items']):
        missing_cat = item['category'].title()
        
        rec_color = ""
        for cat, products in rec_data['recommendations'].items():
            if cat.lower() == item['category'].lower() and products:
                rec_color = products[0]['color'] + " "
                break
                
        trip_type = trip_context.get('trip', 'Unknown').title()
        
        print(f"\nReason {i+1}\n")
        print(f"• {trip_type} destination")
        print(f"• No {missing_cat.lower()} detected\n")
        print("↓\n")
        print_ok(f"Recommended: {rec_color}{missing_cat}")
        
        if i < len(rec_data['missing_items']) - 1:
            print("\n--------------------------------")

    print("\n" + "=" * 60)
    print("Privacy Layer")
    print("=" * 60)
    
    print("\nAll wardrobe images are processed locally.")
    print("\nOnly semantic clothing queries")
    print("are shared with the retail catalog.\n")
    print("Privacy-safe AJIO Query\n")
    if rec_data['missing_items']:
        print("Looking for:")
        for i in rec_data['missing_items']:
            print(f"• {i['category'].title()}")
    if rec_data['ajio_query'] and rec_data['ajio_query'][0].get('preferred_colors'):
        print("\nPreferred Colors")
        for color in rec_data['ajio_query'][0]['preferred_colors']:
            print(f"• {color}")
    print("\nNOT SENT\n")
    print("✗ Wardrobe Images")
    print("✗ Personal Photos")
    print("✗ Face Data")
    print_ok("Only Clothing Metadata\n")
    print_ok("User privacy preserved")

    print("\n" + "=" * 60)
    print("AI Summary")
    print("=" * 60)
    
    print("\nTravel Destination")
    print(trip_context.get('destination', 'Unknown'))
    
    print("\nWardrobe Images Analysed")
    print("17")
    
    print("\nClothing Items Detected")
    print(len(wardrobe))
    
    print("\nNew Items Suggested")
    print(len(rec_data['missing_items']))
    
    print("\nPrivacy")
    print("Images processed locally")
    print("No wardrobe photos shared")
    
    print("\nInference Pipeline\n")
    print("EasyOCR")
    print("→ Travel Context AI")
    print("→ YOLO11")
    print("→ Color Extraction")
    print("→ Recommendation Engine")
    
    print("\n" + "=" * 60)
    print("Business Impact")
    print("=" * 60)
    
    print("\n")
    print_ok("Personalises shopping")
    print_ok("Understands travel context")
    print_ok("Uses existing wardrobe")
    print_ok("Recommends only missing items")
    print_ok("Preserves user privacy")
    print_ok("Promotes smarter and sustainable shopping")
    
    print("\n" + "=" * 60)
    print("Thank You")
    print("=" * 60)
    
    print("\nJio Lookbook demonstrates how multimodal AI,")
    print("computer vision, OCR and privacy-preserving")
    print("recommendation systems can create a personalised")
    print("shopping experience without exposing user photos.")
    print("\n")

if __name__ == "__main__":
    main()
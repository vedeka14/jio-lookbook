# Jio Lookbook

An AI-powered fashion recommendation system that combines travel context and wardrobe analysis to generate personalized outfit recommendations while preserving user privacy.

## Architecture

### 1. Fashion AI
- **Wardrobe Building**: Uses local Vision LLMs (LLaVA via Ollama) to scan user photos and catalog clothing items.
- **Color Extraction**: Analyzes images to determine dominant clothing colors.

### 2. Travel Context AI
- **OCR**: Reads travel documents (tickets, itineraries) to extract context.
- **Context Extraction**: Determines destination, weather, and trip type to inform recommendations.

### 3. Recommendation Engine
- **Wardrobe Matching**: Cross-references trip requirements with the user's existing wardrobe.
- **AJIO Catalog Search**: Finds missing pieces from the AJIO store.
- **Styling**: Recommends complete, personalized outfits.

## Quickstart

1. Place your clothing photos in `fashion_ai/wardrobeinference/data/photos/`.
2. Double-click `start_lookbook.bat`. This will:
   - Automatically boot the Ollama AI Engine in the background.
   - Launch the interactive Streamlit web application.
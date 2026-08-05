import json
import sys
import copy
import os

from style_assistant.config import (
    TRAVEL_CONTEXT_FILE,
    WARDROBE_FILE,
    AJIO_QUERY_FILE,
    USER_PROFILE_FILE,
)

# Load current data
with open(TRAVEL_CONTEXT_FILE, 'r') as f: orig_trip = json.load(f)
with open(WARDROBE_FILE, 'r') as f: orig_wardrobe = json.load(f)
with open(AJIO_QUERY_FILE, 'r') as f: orig_ajio = json.load(f)
with open(USER_PROFILE_FILE, 'r') as f: orig_profile = json.load(f)

def write_files(trip, wardrobe, ajio, profile):
    with open(TRAVEL_CONTEXT_FILE, 'w') as f: json.dump(trip, f, indent=4)
    with open(WARDROBE_FILE, 'w') as f: json.dump(wardrobe, f, indent=4)
    with open(AJIO_QUERY_FILE, 'w') as f: json.dump(ajio, f, indent=4)
    with open(USER_PROFILE_FILE, 'w') as f: json.dump(profile, f, indent=4)

def restore_files():
    write_files(orig_trip, orig_wardrobe, orig_ajio, orig_profile)

def get_prompt():
    import style_assistant.scripts.build_prompt as bp
    import importlib
    importlib.reload(bp)
    return bp.build_prompt()

def run_tests():
    print('Starting Pipeline Tests (Prompt Verification)')
    print('-'*50)
    
    # Test 2
    print('Test 2: Change destination')
    trip = copy.deepcopy(orig_trip)
    trip['destination'] = 'Shimla'
    trip['weather'] = 'Cold'
    trip['activities'] = ['Sightseeing', 'Snow']
    write_files(trip, orig_wardrobe, orig_ajio, orig_profile)
    prompt = get_prompt()
    assert 'Destination:\nShimla' in prompt, 'Shimla not in prompt'
    assert 'Weather:\nCold' in prompt, 'Cold not in prompt'
    assert 'Sightseeing' in prompt, 'Sightseeing not in prompt'
    print('[PASS] Test 2')

    # Test 3
    print('Test 3: Remove all shirts')
    wardrobe = [
        {'category': 'Jeans', 'color': 'Grey'},
        {'category': 'Saree', 'color': 'Beige'}
    ]
    write_files(orig_trip, wardrobe, orig_ajio, orig_profile)
    prompt = get_prompt()
    assert 'Beige Shirt' not in prompt, 'Shirt still in prompt'
    assert 'Tops' not in prompt or ('Tops' in prompt and 'None Detected' in prompt), 'Tops section incorrect'
    assert 'Bottoms\n- Grey Jeans' in prompt, 'Jeans missing'
    print('[PASS] Test 3')

    # Test 4
    print('Test 4: Change favorite colors')
    profile = copy.deepcopy(orig_profile)
    profile['favorite_colors'] = ['Green', 'White']
    write_files(orig_trip, orig_wardrobe, orig_ajio, profile)
    prompt = get_prompt()
    assert 'Favorite Colors:\nGreen, White' in prompt, 'Favorite colors not updated'
    print('[PASS] Test 4')

    # Test 5
    print('Test 5: Budget')
    profile = copy.deepcopy(orig_profile)
    profile['budget'] = 1000
    write_files(orig_trip, orig_wardrobe, orig_ajio, profile)
    prompt = get_prompt()
    assert 'Budget:\n1000' in prompt, 'Budget not updated'
    print('[PASS] Test 5')

    # Test 6
    print('Test 6: Weather')
    trip = copy.deepcopy(orig_trip)
    trip['weather'] = 'Rainy'
    write_files(trip, orig_wardrobe, orig_ajio, orig_profile)
    prompt = get_prompt()
    assert 'Weather:\nRainy' in prompt, 'Weather not updated'
    print('[PASS] Test 6')

    # Test 7
    print('Test 7: Wardrobe consistency')
    wardrobe = [item for item in orig_wardrobe if not (item['category'].lower() == 'jeans' and item['color'].lower() == 'grey')]
    write_files(orig_trip, wardrobe, orig_ajio, orig_profile)
    prompt = get_prompt()
    assert 'Grey Jeans' not in prompt, 'Grey Jeans still in prompt'
    print('[PASS] Test 7')

    # Test 8
    print('Test 8: Missing items')
    ajio = [item for item in orig_ajio if item['category'].lower() != 'hat']
    write_files(orig_trip, orig_wardrobe, ajio, orig_profile)
    prompt = get_prompt()
    assert '- Hat' not in prompt, 'Hat still in missing items'
    assert '- Shorts' in prompt, 'Shorts missing'
    print('[PASS] Test 8')

    restore_files()
    print('All tests passed successfully!')

try:
    run_tests()
finally:
    restore_files()

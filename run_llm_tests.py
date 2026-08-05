import json
import subprocess
import copy
import sys
import os

from style_assistant.config import (
    TRAVEL_CONTEXT_FILE,
    WARDROBE_FILE,
    USER_PROFILE_FILE
)

with open(TRAVEL_CONTEXT_FILE, 'r') as f: orig_trip = json.load(f)
with open(WARDROBE_FILE, 'r') as f: orig_wardrobe = json.load(f)
with open(USER_PROFILE_FILE, 'r') as f: orig_profile = json.load(f)

def write_files(trip=None, wardrobe=None, profile=None):
    if trip is not None:
        with open(TRAVEL_CONTEXT_FILE, 'w') as f: json.dump(trip, f, indent=4)
    if wardrobe is not None:
        with open(WARDROBE_FILE, 'w') as f: json.dump(wardrobe, f, indent=4)
    if profile is not None:
        with open(USER_PROFILE_FILE, 'w') as f: json.dump(profile, f, indent=4)

def restore_files():
    write_files(orig_trip, orig_wardrobe, orig_profile)

def run_bot(test_name):
    print(f"\n{'='*20} {test_name} {'='*20}")
    env = os.environ.copy()
    env['PYTHONUTF8'] = '1'
    result = subprocess.run(['python', '-m', 'style_assistant.scripts.chatbot'], capture_output=True, text=True, env=env, encoding='utf-8')
    out = result.stdout
    if 'Fashion Advice' in out:
        advice = out.split('Fashion Advice')[-1].strip('= \n')
        print(advice)
    else:
        print("ERROR or output not found:")
        print(out)
        print(result.stderr)

try:
    # Test A: Shimla
    trip = copy.deepcopy(orig_trip)
    trip['destination'] = 'Shimla'
    trip['weather'] = 'Cold'
    write_files(trip=trip)
    run_bot('TEST A - SHIMLA')
    restore_files()

    # Test B: No tops
    wardrobe = [
        {"category": "Jeans", "color": "Grey"},
        {"category": "Saree", "color": "Beige"}
    ]
    write_files(wardrobe=wardrobe)
    run_bot('TEST B - NO TOPS')
    restore_files()

    # Test C: Budget 1000
    profile = copy.deepcopy(orig_profile)
    profile['budget'] = 1000
    write_files(profile=profile)
    run_bot('TEST C - BUDGET 1000')

finally:
    restore_files()

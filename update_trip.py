import json
with open('c:/Users/Vedeka/Downloads/Jio_Lookbook/travel_context_ai/data/output/travel_context.json', 'r', encoding='utf-8') as f:
    trip = json.load(f)
trip['destination'] = 'Shimla'
trip['weather'] = 'Cold'
trip['activities'] = ['Sightseeing', 'Snow', 'Cafe Hopping', 'Nature Walks']
with open('c:/Users/Vedeka/Downloads/Jio_Lookbook/travel_context_ai/data/output/travel_context.json', 'w', encoding='utf-8') as f:
    json.dump(trip, f, indent=4)

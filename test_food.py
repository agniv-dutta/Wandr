import requests
import json

r2 = requests.post('http://localhost:8000/api/food/day-plan', json={
    'city': 'New Delhi',
    'country': 'India',
    'days': 3,
    'budget_level': 'moderate',
    'itinerary_days': ['Museum tours', 'Street food and nightlife', 'Shopping']
}, timeout=30)

food_data = r2.json()
print(f"Currency: {food_data.get('currency')}")
print(f"Daily Average: {food_data.get('daily_average')}")
print(f"Total Cost: {food_data.get('total_food_cost')}")

if food_data.get('days'):
    for i, day in enumerate(food_data['days'][:2], 1):
        print(f"\nDay {i} (Theme: {day.get('theme')}):")
        print(f"  Breakfast ({day['breakfast']['amount']}): {day['breakfast']['suggestion']}")
        print(f"  Lunch ({day['lunch']['amount']}): {day['lunch']['suggestion']}")
        print(f"  Dinner ({day['dinner']['amount']}): {day['dinner']['suggestion']}")
        print(f"  Daily Total: {day['daily_total']}")

from backend.tools.food_price_tool import build_daily_food_plan

result = build_daily_food_plan(
    city='New Delhi',
    country='India',
    days=3,
    budget_level='moderate',
    day_contexts=['Museum tours', 'Street food and nightlife', 'Shopping']
)

print('Currency:', result.get('currency'))
print('Daily Average:', result.get('daily_average'))
print('Total Cost:', result.get('total_food_cost'))
print()
for day in result['days'][:2]:
    print(f"Day {day['day']} ({day['theme']}):")
    print(f"  Breakfast {day['breakfast']['amount']}: {day['breakfast']['suggestion']}")
    print(f"  Lunch {day['lunch']['amount']}: {day['lunch']['suggestion']}")
    print(f"  Dinner {day['dinner']['amount']}: {day['dinner']['suggestion']}")
    print(f"  Daily Total: {day['daily_total']}")

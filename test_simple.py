#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

try:
    from backend.tools.food_price_tool import build_daily_food_plan
    print("Import successful")
    
    result = build_daily_food_plan(
        city='New Delhi',
        country='India',
        days=2,
        budget_level='moderate'
    )
    
    print('---')
    print('Currency:', result.get('currency'))
    print('Daily Average:', result.get('daily_average'))
    print('Total Cost:', result.get('total_food_cost'))
    print()
    
    day1 = result['days'][0]
    print('Day 1:')
    print('  Breakfast:', day1['breakfast']['amount'], '-', day1['breakfast']['suggestion'])
    print('  Lunch:', day1['lunch']['amount'], '-', day1['lunch']['suggestion'])
    print('  Dinner:', day1['dinner']['amount'], '-', day1['dinner']['suggestion'])
    print('  Total:', day1['daily_total'])
    
except Exception as e:
    print('ERROR:', e)
    import traceback
    traceback.print_exc()

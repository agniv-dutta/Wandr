import React, { useEffect, useState } from 'react';
import { ChevronDown, ChevronUp, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';
import { travelApi } from '../../api/travel';
import { FoodDayPlan, FoodDayPlanItem } from '../../types';

interface ItineraryTabProps {
  finalAnswer: string;
  destination: string;
  duration: number;
  budgetLevel: 'Budget' | 'Moderate' | 'Luxury';
  budgetCurrency: string;
}

interface DayPlan {
  dayNumber: number;
  activities: string[];
  theme?: string;
}

const parseDayPlan = (text: string): DayPlan[] => {
  const patterns = [
    /(?:^|\n)(?:\*\*)?(?:#+\s*)?Day\s+(\d+)[:\s-]*([\s\S]*?)(?=(?:\n(?:\*\*)?(?:#+\s*)?Day\s+\d+)|\n\s*(?:\*\*)?Budget Summary|$)/gi,
    /(?:^|\n)(?:\*\*)?Day\s+(\d+)[:\s-]*([\s\S]*?)(?=(?:\n(?:\*\*)?Day\s+\d+)|\n\s*(?:\*\*)?Budget Summary|$)/gi,
  ];

  const days: DayPlan[] = [];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      const dayNum = parseInt(match[1]);
      const content = match[2];
      const activities: string[] = [];

      const lines = content.split('\n').filter(l => l.trim());
      lines.forEach(line => {
        const cleaned = line.replace(/^[-•*]\s*/, '').trim();
        if (!cleaned) return;
        if (/^Day\s+\d+/i.test(cleaned)) return;
        activities.push(cleaned);
      });

      if (activities.length > 0) {
        days.push({
          dayNumber: dayNum,
          activities: activities.slice(0, 6),
          theme: activities[0]?.split(',')[0],
        });
      }
    }

    if (days.length > 0) break;
  }

  return days;
};

export const ItineraryTab: React.FC<ItineraryTabProps> = ({ finalAnswer, destination, duration, budgetLevel, budgetCurrency }) => {
  const [expandedDays, setExpandedDays] = useState<Set<number>>(new Set([1]));
  const [foodPlan, setFoodPlan] = useState<FoodDayPlan | null>(null);
  const [foodError, setFoodError] = useState<string | null>(null);
  const [foodRate, setFoodRate] = useState(1);

  const days = parseDayPlan(finalAnswer);
  const budgetMatch = finalAnswer.match(/(?:\*\*)?Budget[^]*?(?=\n\n|$)/i);
  const budgetSummary = budgetMatch ? budgetMatch[0] : null;

  useEffect(() => {
    const fetchFood = async () => {
      try {
        const response = await travelApi.getDailyFoodPlan({
          city: destination,
          country: '',
          days: duration,
          budget_level: budgetLevel.toLowerCase(),
          itinerary_days: days.map(day => day.activities.join('; ')),
        });
        setFoodPlan(response);
      } catch (err) {
        setFoodError(err instanceof Error ? err.message : 'Failed to fetch food estimate');
      }
    };

    if (destination && days.length > 0) {
      fetchFood();
    }
  }, [destination, duration, budgetLevel, finalAnswer]);

  useEffect(() => {
    const fetchFoodRate = async () => {
      if (!foodPlan || foodPlan.currency === budgetCurrency) {
        setFoodRate(1);
        return;
      }
      const response = await travelApi.convertCurrency(foodPlan.currency, budgetCurrency, 1);
      setFoodRate(response.rate || 1);
    };

    fetchFoodRate();
  }, [foodPlan, budgetCurrency]);

  const getFoodForDay = (dayNumber: number): FoodDayPlanItem | null => {
    if (!foodPlan?.days?.length) return null;
    return foodPlan.days.find(item => item.day === dayNumber) || foodPlan.days[0] || null;
  };

  const toggleDay = (dayNum: number) => {
    const newExpanded = new Set(expandedDays);
    if (newExpanded.has(dayNum)) {
      newExpanded.delete(dayNum);
    } else {
      newExpanded.add(dayNum);
    }
    setExpandedDays(newExpanded);
  };

  return (
    <div className="space-y-4">
      {days.length > 0 ? (
        <>
          <div className="space-y-3">
            {days.map((day, idx) => {
              const dayFood = getFoodForDay(day.dayNumber);
              return (
              <motion.div
                key={day.dayNumber}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <div
                  onClick={() => toggleDay(day.dayNumber)}
                  className="bg-zinc-800/50 border border-l-4 border-l-violet-500 rounded-xl p-4 cursor-pointer hover:bg-zinc-800 transition-all duration-300 group"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Calendar className="text-violet-400" size={20} />
                      <div>
                        <h4 className="font-semibold text-zinc-50">
                          Day {day.dayNumber}
                        </h4>
                        {day.theme && (
                          <p className="text-xs text-zinc-400">{day.theme}</p>
                        )}
                      </div>
                    </div>
                    {expandedDays.has(day.dayNumber) ? (
                      <ChevronUp className="text-zinc-400 group-hover:text-violet-400" size={20} />
                    ) : (
                      <ChevronDown className="text-zinc-400 group-hover:text-violet-400" size={20} />
                    )}
                  </div>

                  {expandedDays.has(day.dayNumber) && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3 }}
                      className="mt-4 space-y-2 pt-4 border-t border-zinc-700"
                    >
                      {day.activities.map((activity, i) => (
                        <div key={i} className="flex gap-3 items-start">
                          <span className="text-violet-400 mt-1 flex-shrink-0">▶</span>
                          <p className="text-sm text-zinc-300">{activity}</p>
                        </div>
                      ))}

                      <div className="mt-4 bg-zinc-900/60 border border-zinc-700 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h5 className="text-sm font-semibold text-amber-300">Food Budget</h5>
                          <span className="text-xs text-zinc-400">per day</span>
                        </div>
                        {foodError && (
                          <p className="text-xs text-red-400">{foodError}</p>
                        )}
                        {dayFood && dayFood.daily_total > 0 && (
                          <div className="space-y-2">
                            <div className="flex flex-wrap gap-2">
                              <span className="px-3 py-1 text-xs bg-amber-500/10 text-amber-300 rounded-full">
                                Breakfast {budgetCurrency} {(dayFood.breakfast.amount * foodRate).toFixed(0)}
                              </span>
                              <span className="px-3 py-1 text-xs bg-amber-500/10 text-amber-300 rounded-full">
                                Lunch {budgetCurrency} {(dayFood.lunch.amount * foodRate).toFixed(0)}
                              </span>
                              <span className="px-3 py-1 text-xs bg-amber-500/10 text-amber-300 rounded-full">
                                Dinner {budgetCurrency} {(dayFood.dinner.amount * foodRate).toFixed(0)}
                              </span>
                            </div>
                            <p className="text-sm font-semibold text-zinc-200">
                              Daily subtotal: {budgetCurrency} {(dayFood.daily_total * foodRate).toFixed(0)}
                            </p>
                            <p className="text-xs text-zinc-400">🍽 Breakfast idea: {dayFood.breakfast.suggestion}</p>
                            <p className="text-xs text-zinc-400">🥗 Lunch idea: {dayFood.lunch.suggestion}</p>
                            <p className="text-xs text-zinc-400">🍲 Dinner idea: {dayFood.dinner.suggestion}</p>
                            <p className="text-xs text-zinc-500">{foodPlan?.notes}</p>
                            {dayFood.nearby_source && (
                              <a
                                href={dayFood.nearby_source}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-block text-xs text-violet-300 hover:text-violet-200 underline"
                              >
                                Explore nearby food picks
                              </a>
                            )}
                          </div>
                        )}
                        {dayFood && dayFood.daily_total === 0 && (
                          <p className="text-xs text-zinc-400">Food estimate unavailable for this destination.</p>
                        )}
                      </div>
                    </motion.div>
                  )}
                </div>
              </motion.div>
              );
            })}
          </div>

          {budgetSummary && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-8 p-6 bg-gradient-to-br from-violet-900/20 to-indigo-900/20 rounded-xl border border-violet-700/30"
            >
              <h4 className="font-semibold text-violet-300 mb-4">Budget Summary</h4>
              <div className="text-sm text-zinc-300 whitespace-pre-wrap font-mono">
                {budgetSummary}
              </div>
            </motion.div>
          )}
        </>
      ) : (
        <div className="text-center py-8">
          <p className="text-zinc-400">Could not parse itinerary. Here's the raw response:</p>
          <div className="mt-4 p-4 bg-zinc-800/50 rounded-xl text-left max-h-96 overflow-y-auto">
            <p className="text-sm text-zinc-300 whitespace-pre-wrap font-mono text-xs">
              {finalAnswer}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

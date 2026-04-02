import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';

interface ItineraryTabProps {
  finalAnswer: string;
}

interface DayPlan {
  dayNumber: number;
  activities: string[];
  theme?: string;
}

const parseDayPlan = (text: string): DayPlan[] => {
  const dayPattern = /Day\s+(\d+)[:\s]*(.*?)(?=Day\s+\d+:|Budget Summary|$)/gis;
  const days: DayPlan[] = [];

  let match;
  while ((match = dayPattern.exec(text)) !== null) {
    const dayNum = parseInt(match[1]);
    const content = match[2];

    // Extract activities
    const activities: string[] = [];
    const lines = content.split('\n').filter(l => l.trim());

    lines.forEach(line => {
      if (line.trim() && !line.includes('Day')) {
        activities.push(line.replace(/^[-•*]\s*/, '').trim());
      }
    });

    if (activities.length > 0) {
      days.push({
        dayNumber: dayNum,
        activities: activities.slice(0, 5), // Limit to 5 activities per day
        theme: activities[0]?.split(',')[0],
      });
    }
  }

  return days;
};

export const ItineraryTab: React.FC<ItineraryTabProps> = ({ finalAnswer }) => {
  const [expandedDays, setExpandedDays] = useState<Set<number>>(new Set([1]));

  const days = parseDayPlan(finalAnswer);
  const budgetMatch = finalAnswer.match(/Budget[^]*?(?=\n\n|$)/i);
  const budgetSummary = budgetMatch ? budgetMatch[0] : null;

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
            {days.map((day, idx) => (
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
                    </motion.div>
                  )}
                </div>
              </motion.div>
            ))}
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

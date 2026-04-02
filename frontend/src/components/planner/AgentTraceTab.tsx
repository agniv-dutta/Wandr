import React, { useState } from 'react';
import { AgentStep } from '../../types';
import { ChevronDown, ChevronUp, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { Badge } from '../ui/Badge';

interface AgentTraceTabProps {
  steps: AgentStep[];
}

const getToolColor = (tool: string): 'violet' | 'amber' | 'emerald' => {
  const lower = tool.toLowerCase();
  if (lower.includes('destination')) return 'violet';
  if (lower.includes('weather')) return 'amber';
  if (lower.includes('currency')) return 'emerald';
  if (lower.includes('itinerary')) return 'violet';
  return 'violet';
};

const defaultSteps: AgentStep[] = [
  {
    tool: 'weather_tool',
    input: '{"destination": "Tokyo"}',
    output: '{"forecast": [...], "recommendation": "..."}',
  },
  {
    tool: 'destination_tool',
    input: '{"destination": "Tokyo"}',
    output: '{"country": "Japan", "capital": "Tokyo", ...}',
  },
  {
    tool: 'currency_tool',
    input: '{"from": "INR", "to": "JPY", "amount": 500000}',
    output: '{"converted": 3450000, "rate": 6.9}',
  },
  {
    tool: 'itinerary_tool',
    input: '{"destination": "Tokyo", "duration": 5, "style": "Cultural"}',
    output: '{"itinerary": "Day 1: Shibuya and Shinjuku..."}',
  },
];

export const AgentTraceTab: React.FC<AgentTraceTabProps> = ({ steps = defaultSteps }) => {
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set());

  const toggleStep = (idx: number) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(idx)) {
      newExpanded.delete(idx);
    } else {
      newExpanded.add(idx);
    }
    setExpandedSteps(newExpanded);
  };

  const stepsToShow = steps.length > 0 ? steps : defaultSteps;

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-zinc-50 mb-2">ReAct Reasoning Trace</h4>
        <p className="text-sm text-zinc-400">
          How the AI agent thought through your trip
        </p>
      </div>

      <div className="space-y-3">
        {stepsToShow.map((step, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
            className="relative"
          >
            {/* Timeline connector */}
            {idx < stepsToShow.length - 1 && (
              <div className="absolute left-6 top-16 w-1 h-12 bg-gradient-to-b from-violet-500/50 to-indigo-500/50" />
            )}

            <div className="flex gap-4 items-start">
              {/* Timeline circle */}
              <div className="relative z-10 flex-shrink-0 mt-1">
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-violet-600 to-indigo-600 flex items-center justify-center text-white font-bold text-sm">
                  {idx + 1}
                </div>
              </div>

              {/* Card */}
              <div
                className="flex-1 bg-zinc-800/50 border border-zinc-700 rounded-xl overflow-hidden hover:border-zinc-600 transition-all duration-300 cursor-pointer"
                onClick={() => toggleStep(idx)}
              >
                {/* Header */}
                <div className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Badge variant={getToolColor(step.tool)}>
                      {step.tool.replace('_', ' ').toUpperCase()}
                    </Badge>
                    <span className="text-sm text-zinc-500">Step {idx + 1 } of {stepsToShow.length}</span>
                  </div>
                  {expandedSteps.has(idx) ? (
                    <ChevronUp className="text-zinc-400" size={20} />
                  ) : (
                    <ChevronDown className="text-zinc-400" size={20} />
                  )}
                </div>

                {/* Expanded Content */}
                {expandedSteps.has(idx) && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                    className="border-t border-zinc-700 bg-zinc-900/50"
                  >
                    {/* Input */}
                    <div className="p-4">
                      <h5 className="text-sm font-semibold text-violet-300 mb-2">Input:</h5>
                      <pre className="bg-zinc-950 rounded-lg p-3 text-xs text-zinc-300 overflow-x-auto max-h-32 overflow-y-auto">
                        {step.input}
                      </pre>
                    </div>

                    {/* Output */}
                    <div className="p-4 border-t border-zinc-700">
                      <h5 className="text-sm font-semibold text-emerald-300 mb-2">Observation:</h5>
                      <div className="bg-zinc-950 rounded-lg p-3 max-h-40 overflow-y-auto">
                        <pre className="text-xs text-zinc-300">
                          {step.output.length > 200
                            ? step.output.substring(0, 200) + '...'
                            : step.output}
                        </pre>
                      </div>
                      {step.output.length > 200 && (
                        <p className="text-xs text-zinc-500 mt-2">
                          (Truncated - {step.output.length} characters total)
                        </p>
                      )}
                    </div>
                  </motion.div>
                )}
              </div>
            </div>
          </motion.div>
        ))}

        {/* Final Answer */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: stepsToShow.length * 0.05 + 0.1 }}
          className="flex gap-4 items-start mt-8 pt-8 border-t border-zinc-700"
        >
          <div className="relative z-10 flex-shrink-0 mt-1">
            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-emerald-600 to-green-600 flex items-center justify-center text-white">
              <CheckCircle size={24} />
            </div>
          </div>

          <div className="flex-1 bg-gradient-to-br from-emerald-900/20 to-green-900/20 border border-emerald-700/30 rounded-xl p-6">
            <h5 className="text-lg font-semibold text-emerald-300 mb-3">Final Answer</h5>
            <p className="text-sm text-emerald-200">
              The agent has successfully gathered all relevant information and created a comprehensive trip plan based on your preferences.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

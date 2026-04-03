import React, { useEffect, useMemo, useState } from 'react';
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import { travelApi } from '../../api/travel';
import { BudgetBreakdown } from '../../types';

interface BudgetSummaryProps {
  destination: string;
  origin: string;
  duration: number;
  budgetLevel: 'Budget' | 'Moderate' | 'Luxury';
  startDate: string;
  budgetCurrency: string;
}

export const BudgetSummary: React.FC<BudgetSummaryProps> = ({ destination, origin, duration, budgetLevel, startDate, budgetCurrency }) => {
  const [budget, setBudget] = useState<BudgetBreakdown | null>(null);
  const [rates, setRates] = useState<Record<string, number>>({});
  const [ratesReady, setRatesReady] = useState(false);

  const dates = useMemo(() => {
    const start = new Date(startDate);
    const end = new Date(startDate);
    end.setDate(end.getDate() + Math.max(duration - 1, 0));
    return {
      start_date: start.toISOString().slice(0, 10),
      end_date: end.toISOString().slice(0, 10),
    };
  }, [startDate, duration]);

  useEffect(() => {
    const fetchBudget = async () => {
      if (!destination) return;
      const response = await travelApi.getBudgetEstimate({
        destination,
        origin: origin || 'your city',
        start_date: dates.start_date,
        end_date: dates.end_date,
        travelers: 1,
        budget_level: budgetLevel.toLowerCase(),
      });
      setBudget(response);
    };

    fetchBudget();
  }, [destination, origin, dates, budgetLevel]);

  useEffect(() => {
    const fetchRate = async () => {
      if (!budget) {
        setRates({});
        setRatesReady(false);
        return;
      }

      const currencies = Array.from(
        new Set(
          [
            budget.transport.currency,
            budget.accommodation.currency,
            budget.food.currency,
            budget.activities.currency,
            budget.currency,
          ].filter(Boolean)
        )
      );

      setRatesReady(false);

      const entries = await Promise.all(
        currencies.map(async currency => {
          if (currency === budgetCurrency) {
            return [currency, 1] as const;
          }

          try {
            const response = await travelApi.convertCurrency(currency, budgetCurrency, 1);
            return [currency, response.rate || 1] as const;
          } catch {
            return [currency, 1] as const;
          }
        })
      );

      setRates(Object.fromEntries(entries));
      setRatesReady(true);
    };

    fetchRate();
  }, [budget, budgetCurrency]);

  const getRate = (currency?: string) => {
    if (!currency || currency === budgetCurrency) {
      return 1;
    }

    return rates[currency] || 1;
  };

  const convertAmount = (amount: number | undefined, currency?: string) => (amount ?? 0) * getRate(currency);

  const transportTotal = budget ? convertAmount(budget.transport.amount, budget.transport.currency) : 0;
  const accommodationTotal = budget ? convertAmount(budget.accommodation.amount, budget.accommodation.currency) : 0;
  const foodTotal = budget ? convertAmount(budget.food.amount, budget.food.currency) : 0;
  const activitiesTotal = budget ? convertAmount(budget.activities.amount, budget.activities.currency) : 0;
  const miscTotal = (transportTotal + accommodationTotal + foodTotal + activitiesTotal) * 0.1;
  const convertedTotal = transportTotal + accommodationTotal + foodTotal + activitiesTotal + miscTotal;

  if (!budget || !budget.transport || !budget.accommodation || !budget.food || !budget.activities || !ratesReady) {
    return (
      <div className="fixed bottom-4 right-6 left-6 lg:left-[40%] bg-zinc-900/95 border border-zinc-800 rounded-2xl p-6 shadow-xl">
        <p className="text-sm text-zinc-400">Budget summary is normalizing currencies…</p>
      </div>
    );
  }

  const data = [
    { name: 'Transport', value: transportTotal, color: '#3B82F6' },
    { name: 'Hotel', value: accommodationTotal, color: '#8B5CF6' },
    { name: 'Food', value: foodTotal, color: '#F59E0B' },
    { name: 'Activities', value: activitiesTotal, color: '#14B8A6' },
    { name: 'Misc', value: miscTotal, color: '#94A3B8' },
  ];

  const confidenceColor = {
    high: 'bg-emerald-500/20 text-emerald-300',
    medium: 'bg-amber-500/20 text-amber-300',
    low: 'bg-red-500/20 text-red-300',
  }[budget.confidence];

  return (
    <div className="fixed bottom-4 right-6 left-6 lg:left-[40%] bg-zinc-900/95 border border-zinc-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-zinc-50">Budget Summary</h3>
          <p className="text-xs text-zinc-400">Converted category-by-category for {destination}</p>
        </div>
        <span className={`text-xs px-3 py-1 rounded-full ${confidenceColor}`}>
          {budget.confidence.toUpperCase()} confidence
        </span>
      </div>

      <div className="grid lg:grid-cols-[1fr_220px] gap-6 items-center">
        <div className="h-40">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ left: 0 }}>
              <XAxis type="number" hide />
              <YAxis type="category" dataKey="name" width={90} tick={{ fill: '#9CA3AF', fontSize: 12 }} />
              <Tooltip cursor={{ fill: 'rgba(255,255,255,0.06)' }} />
              <Bar dataKey="value" radius={[0, 8, 8, 0]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="text-right">
          <p className="text-xs text-zinc-400">Estimated total</p>
          <p className="text-3xl font-bold text-zinc-50">
            {budgetCurrency} {convertedTotal.toFixed(0)}
          </p>
          <p className="text-sm text-zinc-400">
            Per person: {budgetCurrency} {convertedTotal.toFixed(0)}
          </p>
          <p className="mt-3 text-xs text-zinc-500 leading-relaxed max-w-[220px] ml-auto">
            Transport, hotel, food, and activities are converted from their source currencies individually.
            Misc is a 10% buffer on the converted subtotal.
          </p>
        </div>
      </div>
    </div>
  );
};

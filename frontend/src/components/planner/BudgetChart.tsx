import React, { useEffect, useMemo, useState } from 'react';
import { Plane, Calculator } from 'lucide-react';
import { travelApi } from '../../api/travel';
import { BudgetBreakdownCategory, BudgetBreakdownResponse } from '../../types';

interface BudgetChartProps {
  destination: string;
  origin: string;
  duration: number;
  budgetAmount: number;
  budgetCurrency: string;
  budgetLevel: 'Budget' | 'Moderate' | 'Luxury';
  departureDate: string;
  adults?: number;
}

type CategoryKey = 'transport' | 'accommodation' | 'food' | 'activities' | 'misc';

const categoryLabels: Record<CategoryKey, string> = {
  transport: 'Transport',
  accommodation: 'Accommodation',
  food: 'Food',
  activities: 'Activities',
  misc: 'Misc',
};

const confidenceClass = (confidence: 'high' | 'medium' | 'low') => {
  if (confidence === 'high') return 'bg-violet-500';
  if (confidence === 'medium') return 'bg-amber-500';
  return 'bg-zinc-500 bg-[repeating-linear-gradient(45deg,rgba(255,255,255,0.16)_0,rgba(255,255,255,0.16)_6px,transparent_6px,transparent_12px)]';
};

const sourcePill = (source: string) => {
  if (source.endsWith('_live')) return '🟣 Live data (Free API)';
  if (source === 'calculated') return '⬜ Calculated (derived)';
  return '🟡 Estimated (formula-based)';
};

export const BudgetChart: React.FC<BudgetChartProps> = ({
  destination,
  origin,
  duration,
  budgetAmount,
  budgetCurrency,
  budgetLevel,
  departureDate,
  adults = 1,
}) => {
  const [data, setData] = useState<BudgetBreakdownResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBreakdown = async () => {
      if (!destination) return;
      setLoading(true);
      setError(null);
      try {
        const response = await travelApi.getBudgetBreakdown({
          destination,
          origin,
          duration,
          budgetAmount,
          budgetCurrency,
          budgetLevel: budgetLevel.toLowerCase(),
          departureDate,
          adults,
        });
        setData(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch budget breakdown');
      } finally {
        setLoading(false);
      }
    };

    fetchBreakdown();
  }, [destination, origin, duration, budgetAmount, budgetCurrency, budgetLevel, departureDate, adults]);

  const categories = useMemo(() => {
    if (!data) return [];
    const entries: Array<{ key: CategoryKey; value: BudgetBreakdownCategory }> = [
      { key: 'transport', value: data.breakdown.transport },
      { key: 'accommodation', value: data.breakdown.accommodation },
      { key: 'food', value: data.breakdown.food },
      { key: 'activities', value: data.breakdown.activities },
      { key: 'misc', value: data.breakdown.misc },
    ];
    const maxAmount = Math.max(...entries.map(item => item.value.amount), 1);

    return entries.map(item => ({
      ...item,
      widthPercent: Math.max((item.value.amount / maxAmount) * 100, 6),
    }));
  }, [data]);

  const progressPercent = useMemo(() => {
    if (!data || budgetAmount <= 0) return 0;
    return Math.min((data.total / budgetAmount) * 100, 100);
  }, [data, budgetAmount]);

  if (loading) {
    return (
      <div className="fixed bottom-4 right-6 left-6 lg:left-[40%] rounded-2xl border border-zinc-800 bg-zinc-900/95 p-6 shadow-xl">
        <p className="text-sm text-zinc-400">Loading budget breakdown...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed bottom-4 right-6 left-6 lg:left-[40%] rounded-2xl border border-red-700/40 bg-zinc-900/95 p-6 shadow-xl">
        <p className="text-sm text-red-300">{error}</p>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-6 left-6 lg:left-[40%] rounded-2xl border border-zinc-800 bg-zinc-900/95 p-6 shadow-xl">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-zinc-50">Budget Breakdown</h3>
          <p className="text-xs text-zinc-400">Estimated spend for {destination}</p>
        </div>
      </div>

      <div className="space-y-3">
        {categories.map(item => (
          <div key={item.key} className="group">
            <div className="mb-1 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 text-zinc-200">
                {item.key === 'transport' && item.value.source.endsWith('_live') ? <Plane size={12} /> : null}
                {item.key === 'transport' && !item.value.source.endsWith('_live') ? <Calculator size={12} /> : null}
                <span>{categoryLabels[item.key]}</span>
                <span className="text-zinc-500">{sourcePill(item.value.source)}</span>
              </div>
              <span className="font-semibold text-zinc-100">
                {data.currency} {item.value.amount.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </span>
            </div>
            <div
              className="relative h-7 overflow-hidden rounded-lg bg-zinc-800"
              title={`${categoryLabels[item.key]} | ${data.currency} ${item.value.amount.toLocaleString()} | ${item.value.source} | ${item.value.detail}`}
            >
              <div
                className={`h-full ${confidenceClass(item.value.confidence)} transition-all duration-500`}
                style={{ width: `${item.widthPercent}%` }}
              />
            </div>
            <p className="mt-1 text-[11px] text-zinc-500">{item.value.detail}</p>
          </div>
        ))}
      </div>

      <div className="mt-5 rounded-xl border border-zinc-800 bg-zinc-950/70 p-4">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="text-zinc-300">Total vs Budget</span>
          <span className="font-semibold text-zinc-100">
            {data.currency} {data.total.toLocaleString(undefined, { maximumFractionDigits: 0 })} / {data.currency} {budgetAmount.toLocaleString()}
          </span>
        </div>

        <div className="h-2 rounded-full bg-zinc-800">
          <div
            className={`h-2 rounded-full ${data.withinBudget ? 'bg-emerald-500' : 'bg-red-500'}`}
            style={{ width: `${Math.max(progressPercent, 2)}%` }}
          />
        </div>

        <p className={`mt-2 text-sm ${data.withinBudget ? 'text-emerald-300' : 'text-red-300'}`}>
          {data.withinBudget
            ? 'Within budget ✓'
            : `Over by ${data.currency} ${data.overage.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
        </p>

        {adults > 1 && (
          <p className="mt-1 text-xs text-zinc-400">
            Per person: {data.currency} {data.perPerson.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </p>
        )}
      </div>

      <div className="mt-4 flex flex-wrap gap-2 text-xs text-zinc-300">
        <span className="rounded-full border border-zinc-700 px-3 py-1">🟣 Live data (Free API)</span>
        <span className="rounded-full border border-zinc-700 px-3 py-1">🟡 Estimated (formula-based)</span>
        <span className="rounded-full border border-zinc-700 px-3 py-1">⬜ Calculated (derived)</span>
      </div>

      <p className="mt-3 text-[11px] leading-relaxed text-zinc-500">
        Flight prices from a free live provider. Hotel, food and activity costs are formula-based estimates.
        Actual costs may vary.
      </p>
    </div>
  );
};

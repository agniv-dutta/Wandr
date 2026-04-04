import React, { useState, useEffect } from 'react';
import { CurrencyConversion } from '../../types';
import { travelApi } from '../../api/travel';
import { Spinner } from '../ui/Spinner';
import { AlertCircle, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

interface CurrencyTabProps {
  destination: string;
  budgetCurrency: string;
  budgetAmount: number;
}

const currencySymbols: Record<string, string> = {
  INR: '₹',
  USD: '$',
  EUR: '€',
  GBP: '£',
  JPY: '¥',
  AUD: 'A$',
  THB: '฿',
  SGD: 'S$',
};

const commonAmounts = [100, 500, 1000, 5000, 10000];

export const CurrencyTab: React.FC<CurrencyTabProps> = ({ destination, budgetCurrency, budgetAmount }) => {
  const [conversion, setConversion] = useState<CurrencyConversion | null>(null);
  const [conversionTable, setConversionTable] = useState<Record<number, number>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const inferCurrencyCode = (raw: string): string | null => {
    if (!raw) return null;

    const exact = raw.trim().toUpperCase();
    if (/^[A-Z]{3}$/.test(exact)) return exact;

    const codeMatch = raw.match(/\b([A-Z]{3})\b/);
    if (codeMatch?.[1]) return codeMatch[1].toUpperCase();

    const lower = raw.toLowerCase();
    const aliases: Record<string, string> = {
      euro: 'EUR',
      dollar: 'USD',
      usd: 'USD',
      aud: 'AUD',
      rupee: 'INR',
      inr: 'INR',
      yen: 'JPY',
      jpy: 'JPY',
      pound: 'GBP',
      gbp: 'GBP',
      baht: 'THB',
      thb: 'THB',
      sgd: 'SGD',
    };

    for (const [needle, code] of Object.entries(aliases)) {
      if (lower.includes(needle)) return code;
    }

    return null;
  };

  useEffect(() => {
    const fetchCurrency = async () => {
      try {
        setLoading(true);
        setError(null);

        const destinationInfo = await travelApi.getDestination(destination);
        const fromCurrency = (budgetCurrency || 'USD').toUpperCase();
        const toCurrency = inferCurrencyCode(destinationInfo.currency) || 'USD';

        const data = await travelApi.convertCurrency(fromCurrency, toCurrency, budgetAmount || 0);
        setConversion(data);

        const tableEntries = await Promise.all(
          commonAmounts.map(async amount => {
            const converted = await travelApi.convertCurrency(fromCurrency, toCurrency, amount);
            return [amount, converted.converted] as const;
          })
        );

        const table: Record<number, number> = Object.fromEntries(tableEntries);
        setConversionTable(table);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch currency data');
      } finally {
        setLoading(false);
      }
    };

    fetchCurrency();
  }, [destination, budgetCurrency, budgetAmount]);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-400/10 border border-red-500/30 rounded-xl text-red-300">
        <p className="flex items-center gap-2">
          <AlertCircle size={20} />
          {error}
        </p>
      </div>
    );
  }

  if (!conversion) {
    return <div className="text-center text-zinc-400">No currency data available</div>;
  }

  const fromSymbol = currencySymbols[conversion.from] || conversion.from;
  const toSymbol = currencySymbols[conversion.to] || conversion.to;

  return (
    <div className="space-y-6">
      {/* Main Conversion Display */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-violet-900/20 to-indigo-900/20 rounded-2xl p-8 border border-violet-700/30 text-center"
      >
        <div className="flex items-center justify-center gap-6 flex-wrap">
          <div>
            <p className="text-sm text-zinc-400 mb-2">From</p>
            <div className="flex items-baseline gap-2">
              <span className="text-5xl font-bold text-amber-400">
                {fromSymbol}
              </span>
              <p className="text-4xl font-bold text-zinc-50">
                {conversion.amount.toLocaleString('en-IN')}
              </p>
            </div>
            <p className="text-xs text-zinc-500 mt-1">{conversion.from}</p>
          </div>

          <div className="bg-violet-600 rounded-full p-3">
            <ArrowRight className="text-white" size={24} />
          </div>

          <div>
            <p className="text-sm text-zinc-400 mb-2">To</p>
            <div className="flex items-baseline gap-2">
              <span className="text-5xl font-bold text-emerald-400">
                {toSymbol}
              </span>
              <p className="text-4xl font-bold text-zinc-50">
                {conversion.converted.toLocaleString('en-US', {
                  maximumFractionDigits: 2,
                })}
              </p>
            </div>
            <p className="text-xs text-zinc-500 mt-1">{conversion.to}</p>
          </div>
        </div>

        {/* Exchange Rate Info */}
        <div className="mt-8 pt-8 border-t border-violet-700/30">
          <p className="text-zinc-400 text-sm mb-2">Current Exchange Rate</p>
          <p className="text-2xl font-bold text-zinc-50">
            1 {conversion.from} = {conversion.rate.toFixed(4)} {conversion.to}
          </p>
          <p className="text-xs text-zinc-500 mt-2">
            Updated: {new Date(conversion.updated).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
        </div>
      </motion.div>

      {/* Quick Reference Table */}
      {Object.keys(conversionTable).length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h4 className="font-semibold text-zinc-50 mb-4">Quick Reference</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-700">
                  <th className="text-left text-zinc-400 font-medium py-2 px-3">
                    {conversion.from}
                  </th>
                  {commonAmounts.map(amount => (
                    <th
                      key={amount}
                      className="text-right text-zinc-400 font-medium py-2 px-3"
                    >
                      {fromSymbol}{amount.toLocaleString()}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-zinc-700">
                  <td className="text-left text-zinc-400 font-medium py-3 px-3">
                    {conversion.to}
                  </td>
                  {commonAmounts.map(amount => (
                    <td
                      key={amount}
                      className="text-right text-emerald-400 font-semibold py-3 px-3"
                    >
                      {toSymbol}
                      {conversionTable[amount]?.toLocaleString('en-US', {
                        maximumFractionDigits: 2,
                      }) || '-'}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* Info Note */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="p-4 bg-zinc-800/50 rounded-xl border border-zinc-700"
      >
        <p className="text-xs text-zinc-400">
          💡 Exchange rates are updated hourly. Actual rates may vary at your bank or exchange service.
        </p>
      </motion.div>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { WeatherForecast } from '../../types';
import { travelApi } from '../../api/travel';
import { Spinner } from '../ui/Spinner';
import { AlertCircle, Wind, Droplets } from 'lucide-react';
import { motion } from 'framer-motion';

interface WeatherTabProps {
  destination: string;
}

const weatherEmojis: Record<string, string> = {
  clear: '☀️',
  sunny: '☀️',
  cloudy: '☁️',
  rain: '🌧️',
  snow: '❄️',
  storm: '⛈️',
  rainy: '🌧️',
  partly: '⛅',
};

const getWeatherEmoji = (condition: string): string => {
  const lower = condition.toLowerCase();
  for (const [key, emoji] of Object.entries(weatherEmojis)) {
    if (lower.includes(key)) return emoji;
  }
  return '🌡️';
};

const getWarningType = (temps: number[], rainData: number[]): string => {
  const avgTemp = temps.reduce((a, b) => a + b) / temps.length;
  const hasRain = rainData.some(r => r > 5);

  if (hasRain) return 'rain';
  if (avgTemp > 35) return 'heat';
  if (avgTemp < 0) return 'cold';
  return 'good';
};

export const WeatherTab: React.FC<WeatherTabProps> = ({ destination }) => {
  const [weather, setWeather] = useState<WeatherForecast | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        setLoading(true);
        const data = await travelApi.getWeather(destination);
        setWeather(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch weather');
      } finally {
        setLoading(false);
      }
    };

    fetchWeather();
  }, [destination]);

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

  if (!weather) {
    return <div className="text-center text-zinc-400">No weather data available</div>;
  }

  const temps = weather.forecast.map(d => d.maxTemp);
  const rainData = weather.forecast.map(d => d.precipitation);
  const warningType = getWarningType(temps, rainData);

  const warningMessages = {
    rain: { emoji: '🌧️', title: 'Rain Expected', message: 'Pack an umbrella and water-resistant clothing', color: 'bg-amber-400/10 border-amber-500/30 text-amber-300' },
    heat: { emoji: '🔥', title: 'Hot Weather Alert', message: 'Stay hydrated and use plenty of sunscreen', color: 'bg-red-400/10 border-red-500/30 text-red-300' },
    cold: { emoji: '❄️', title: 'Cold Weather Alert', message: 'Pack warm layers and thermal clothing', color: 'bg-blue-400/10 border-blue-500/30 text-blue-300' },
    good: { emoji: '✅', title: 'Great Weather Ahead!', message: 'Perfect conditions for your trip', color: 'bg-emerald-400/10 border-emerald-500/30 text-emerald-300' },
  };

  const warning = warningMessages[warningType as keyof typeof warningMessages];

  return (
    <div className="space-y-6">
      {/* Warning Banner */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`p-4 rounded-xl border flex items-start gap-3 ${warning.color}`}
      >
        <span className="text-2xl mt-1">{warning.emoji}</span>
        <div>
          <p className="font-semibold">{warning.title}</p>
          <p className="text-sm opacity-90">{warning.message}</p>
        </div>
      </motion.div>

      {/* 7-Day Forecast */}
      <div>
        <h4 className="font-semibold text-zinc-50 mb-4">7-Day Forecast</h4>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3">
          {weather.forecast.map((day, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.05 }}
              className="bg-zinc-800/50 rounded-xl p-4 text-center border border-zinc-700 hover:border-violet-500/50 transition-all duration-300"
            >
              <p className="text-xs text-zinc-400 mb-2">
                {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
              </p>
              <div className="text-3xl mb-2">{getWeatherEmoji(day.condition)}</div>
              <p className="text-2xl font-bold text-amber-400 mb-1">{Math.round(day.maxTemp)}°</p>
              <p className="text-xs text-zinc-500 mb-3">{Math.round(day.minTemp)}°</p>

              <div className="space-y-2 text-xs text-zinc-400 border-t border-zinc-700 pt-3">
                <div className="flex items-center justify-center gap-1">
                  <Droplets size={14} className="text-blue-400" />
                  {Math.round(day.precipitation)} mm
                </div>
                <div className="flex items-center justify-center gap-1">
                  <Wind size={14} className="text-zinc-400" />
                  {Math.round(day.windSpeed)} km/h
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Recommendation */}
      {weather.recommendation && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="p-4 bg-zinc-800/50 rounded-xl border border-zinc-700"
        >
          <p className="text-sm text-zinc-300">{weather.recommendation}</p>
        </motion.div>
      )}
    </div>
  );
};

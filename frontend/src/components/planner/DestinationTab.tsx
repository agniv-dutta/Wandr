import React, { useState, useEffect } from 'react';
import { DestinationInfo } from '../../types';
import { travelApi } from '../../api/travel';
import { Spinner } from '../ui/Spinner';
import { AlertCircle, Globe, Users, Clock, DollarSign, BookOpen, MapPin } from 'lucide-react';
import { motion } from 'framer-motion';
import { Badge } from '../ui/Badge';

interface DestinationTabProps {
  destination: string;
}

export const DestinationTab: React.FC<DestinationTabProps> = ({ destination }) => {
  const [info, setInfo] = useState<DestinationInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDestination = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await travelApi.getDestination(destination);
        setInfo(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch destination info');
      } finally {
        setLoading(false);
      }
    };

    fetchDestination();
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

  if (!info) {
    return <div className="text-center text-zinc-400">No destination data available</div>;
  }

  return (
    <div className="space-y-6">
      {/* Hero Info */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-violet-900/20 to-indigo-900/20 rounded-2xl p-8 border border-violet-700/30"
      >
        <div className="flex items-start justify-between gap-6 flex-wrap">
          <div>
            <h3 className="text-4xl font-black text-zinc-50 mb-2">{info.country}</h3>
            <Badge variant="violet" className="inline-block">
              {destination}
            </Badge>
          </div>
          <Globe className="text-violet-400" size={40} />
        </div>
      </motion.div>

      {/* Quick Info Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {[
          { icon: MapPin, label: 'Capital', value: info.capital },
          { icon: Users, label: 'Population', value: info.population },
          { icon: Clock, label: 'Timezone', value: info.timezone },
          { icon: DollarSign, label: 'Currency', value: info.currency },
        ].map((item, idx) => {
          const Icon = item.icon;
          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 + idx * 0.05 }}
              className="bg-zinc-800/50 border border-zinc-700 rounded-xl p-4"
            >
              <div className="flex items-center gap-2 mb-2">
                <Icon className="text-violet-400" size={20} />
                <p className="text-xs font-medium text-zinc-400">{item.label}</p>
              </div>
              <p className="text-lg font-semibold text-zinc-50">{item.value}</p>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Languages */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-zinc-800/50 border border-zinc-700 rounded-xl p-6"
      >
        <h4 className="font-semibold text-zinc-50 mb-4 flex items-center gap-2">
          <BookOpen size={20} className="text-amber-400" />
          Languages Spoken
        </h4>
        <div className="flex flex-wrap gap-2">
          {info.languages.map((lang, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.25 + idx * 0.05 }}
            >
              <Badge variant="amber">{lang}</Badge>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Coordinates */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-zinc-800/50 border border-zinc-700 rounded-xl p-6"
      >
        <h4 className="font-semibold text-zinc-50 mb-4 flex items-center gap-2">
          <MapPin size={20} className="text-emerald-400" />
          Coordinates
        </h4>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-zinc-400 mb-1">Latitude</p>
            <p className="text-lg font-mono font-semibold text-zinc-50">
              {info.coordinates.latitude.toFixed(4)}°
            </p>
          </div>
          <div>
            <p className="text-xs text-zinc-400 mb-1">Longitude</p>
            <p className="text-lg font-mono font-semibold text-zinc-50">
              {info.coordinates.longitude.toFixed(4)}°
            </p>
          </div>
        </div>
      </motion.div>

      {/* Travel Tips */}
      {info.tips && info.tips.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-gradient-to-br from-amber-900/20 to-orange-900/20 rounded-xl p-6 border border-amber-700/30"
        >
          <h4 className="font-semibold text-amber-300 mb-4">Good to Know</h4>
          <ul className="space-y-3">
            {info.tips.map((tip, idx) => (
              <motion.li
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.45 + idx * 0.05 }}
                className="flex gap-3 items-start text-sm text-amber-200"
              >
                <span className="text-amber-400 mt-1 flex-shrink-0">•</span>
                <span>{tip}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>
      )}
    </div>
  );
};

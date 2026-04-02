import React from 'react';
import { Card } from '../ui/Card';
import { MapPin, Cloud, DollarSign, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';

const features = [
  {
    icon: MapPin,
    color: 'text-violet-400',
    title: 'Destination Intelligence',
    description:
      'Real country facts, currency, languages, and timezone — fetched live.',
  },
  {
    icon: Cloud,
    color: 'text-amber-400',
    title: 'Live Weather Forecast',
    description:
      '7-day forecast so you pack right and pick the perfect dates.',
  },
  {
    icon: DollarSign,
    color: 'text-emerald-400',
    title: 'Budget Converter',
    description:
      'Instant currency conversion with live exchange rates.',
  },
  {
    icon: Calendar,
    color: 'text-indigo-400',
    title: 'Smart Itinerary',
    description:
      'Day-by-day plan tailored to your style, budget, and preferences.',
  },
];

export const FeatureCards: React.FC = () => {
  return (
    <section className="bg-zinc-950 py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Section title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-zinc-50">
            Everything you need to plan smarter
          </h2>
        </motion.div>

        {/* Feature cards grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full hover:border-violet-500/50 group">
                  <div className={`${feature.color} mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon size={32} />
                  </div>
                  <h3 className="text-lg font-semibold text-zinc-50 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-zinc-400 text-sm leading-relaxed">
                    {feature.description}
                  </p>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {/* How It Works Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="mt-32 text-center"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-zinc-50 mb-16">
            Three steps to your dream trip
          </h2>

          <div className="grid sm:grid-cols-3 gap-8 relative">
            {/* Dashed line connecting steps (hidden on mobile) */}
            <div className="absolute top-12 left-0 right-0 h-1 border-t-2 border-dashed border-zinc-700 hidden sm:block" />

            {[
              {
                number: '1',
                title: 'Tell us your trip',
                desc: 'Destination, dates, budget, and travel style',
              },
              {
                number: '2',
                title: 'AI does the research',
                desc: 'Our agent calls 4 tools to gather everything',
              },
              {
                number: '3',
                title: 'Get your plan',
                desc: 'Full itinerary, weather, budget breakdown',
              },
            ].map((step, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: idx * 0.15 }}
                viewport={{ once: true }}
                className="relative"
              >
                <div className="flex flex-col items-center">
                  <div className="w-24 h-24 rounded-full bg-gradient-to-r from-violet-600 to-indigo-600 flex items-center justify-center mb-6 text-white text-3xl font-black relative z-10">
                    {step.number}
                  </div>
                  <h3 className="text-lg font-semibold text-zinc-50 mb-2">
                    {step.title}
                  </h3>
                  <p className="text-zinc-400 text-sm max-w-xs">
                    {step.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Example Trips Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="mt-32"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-zinc-50 mb-12">
            Popular trips to inspire you
          </h2>

          <div className="flex gap-6 overflow-x-auto pb-4 scrollbar-hide">
            {[
              {
                name: 'Tokyo',
                duration: '5 days',
                style: 'Cultural',
                gradient: 'from-red-900 to-zinc-900',
              },
              {
                name: 'Bali',
                duration: '7 days',
                style: 'Beach',
                gradient: 'from-teal-900 to-zinc-900',
              },
              {
                name: 'Paris',
                duration: '4 days',
                style: 'Cultural',
                gradient: 'from-blue-900 to-zinc-900',
              },
            ].map((trip, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: idx * 0.1 }}
                viewport={{ once: true }}
                className="flex-shrink-0"
              >
                <div
                  className={`w-64 aspect-[3/4] bg-gradient-to-br ${trip.gradient} rounded-2xl p-6 flex flex-col justify-end cursor-pointer hover:shadow-xl hover:shadow-violet-500/20 transition-all duration-300 group`}
                >
                  <div className="group-hover:translate-y-0 transition-transform duration-300">
                    <h3 className="text-2xl font-bold text-white mb-1">
                      {trip.name}
                    </h3>
                    <p className="text-amber-400 text-sm mb-2">{trip.duration}</p>
                    <p className="text-zinc-300 text-sm">{trip.style}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { motion } from 'framer-motion';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: 'easeOut',
    },
  },
};

export const Hero: React.FC = () => {
  return (
    <div className="relative min-h-screen bg-zinc-950 overflow-hidden pt-20 flex items-center justify-center px-4">
      {/* Animated gradient orbs */}
      <div className="absolute top-20 left-1/4 w-96 h-96 bg-violet-600/20 blur-3xl rounded-full animate-pulse" />
      <div className="absolute bottom-20 right-1/4 w-80 h-80 bg-indigo-600/20 blur-3xl rounded-full animate-pulse delay-1000" />

      <motion.div
        className="max-w-4xl mx-auto text-center relative z-10"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Badge */}
        <motion.div variants={itemVariants} className="mb-8">
          <Badge variant="violet">✨ Powered by Llama 3 + LangChain</Badge>
        </motion.div>

        {/* Main heading */}
        <motion.div variants={itemVariants} className="mb-6">
          <h1 className="text-5xl sm:text-6xl font-black tracking-tight text-zinc-50 mb-2">
            Plan your perfect trip
          </h1>
          <h2 className="text-4xl sm:text-6xl font-black bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
            with AI.
          </h2>
        </motion.div>

        {/* Subheading */}
        <motion.p
          variants={itemVariants}
          className="text-zinc-400 text-lg sm:text-xl max-w-2xl mx-auto mb-12 leading-relaxed"
        >
          Tell Wandr where you want to go. Our AI agent researches destinations, checks live weather, converts your budget, and builds a day-by-day itinerary — all in seconds.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div variants={itemVariants} className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
          <Link to="/plan">
            <Button size="lg" className="whitespace-nowrap">
              Plan My Trip →
            </Button>
          </Link>
          <Button variant="secondary" size="lg" className="whitespace-nowrap">
            See how it works
          </Button>
        </motion.div>

        {/* Trust badges */}
        <motion.div variants={itemVariants} className="flex flex-col sm:flex-row gap-6 justify-center text-center">
          <div className="text-zinc-400">
            <p className="text-2xl mb-2">🌍</p>
            <p className="text-sm font-medium">190+ destinations</p>
          </div>
          <div className="text-zinc-400">
            <p className="text-2xl mb-2">⚡</p>
            <p className="text-sm font-medium">Powered by Groq</p>
          </div>
          <div className="text-zinc-400">
            <p className="text-2xl mb-2">🔓</p>
            <p className="text-sm font-medium">100% Free APIs</p>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

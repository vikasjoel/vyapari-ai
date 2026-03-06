import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import LanguageToggle from './LanguageToggle';
import { StoreCardSkeleton } from './SkeletonLoader';
import { showError } from '../utils/errorHandler';

interface Props {
  onStart: (storeType: string) => void;
  language: string;
  onLanguageChange: (lang: string) => void;
}

interface DemoMerchant {
  merchant_id: string;
  shop_name: string;
  shop_name_hi: string;
  store_type: string;
  location: string;
  product_count: number;
  icon: string;
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Fallback store types (used if API fails)
const FALLBACK_STORE_TYPES = [
  {
    id: 'kirana',
    emoji: '🏪',
    name_hi: 'किराना',
    name_en: 'Kirana',
    description: 'Grocery & Daily Needs',
    productCount: 134,
    color: 'from-blue-500 to-blue-600',
  },
  {
    id: 'restaurant',
    emoji: '🍛',
    name_hi: 'रेस्टोरेंट',
    name_en: 'Restaurant',
    description: 'Food & Beverages',
    productCount: 73,
    color: 'from-orange-500 to-orange-600',
  },
  {
    id: 'sweet_shop',
    emoji: '🍬',
    name_hi: 'मिठाई की दुकान',
    name_en: 'Sweet Shop',
    description: 'Mithai & Namkeen',
    productCount: 51,
    color: 'from-pink-500 to-pink-600',
  },
  {
    id: 'bakery',
    emoji: '🍰',
    name_hi: 'बेकरी',
    name_en: 'Bakery',
    description: 'Cakes, Breads & Pastries',
    productCount: 20,
    color: 'from-amber-500 to-amber-600',
  },
];

// Color mapping for store types
const STORE_COLORS: Record<string, string> = {
  kirana: 'from-blue-500 to-blue-600',
  restaurant: 'from-orange-500 to-orange-600',
  sweet_shop: 'from-pink-500 to-pink-600',
  bakery: 'from-amber-500 to-amber-600',
};

// Description mapping
const STORE_DESCRIPTIONS: Record<string, string> = {
  kirana: 'Grocery & Daily Needs',
  restaurant: 'Food & Beverages',
  sweet_shop: 'Mithai & Namkeen',
  bakery: 'Cakes, Breads & Pastries',
};

export default function LandingPage({ onStart, language, onLanguageChange }: Props) {
  const [selected, setSelected] = useState<string | null>(null);
  const [demoMerchants, setDemoMerchants] = useState<DemoMerchant[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch demo merchants from API
  useEffect(() => {
    fetch(`${API_BASE}/demo/merchants`)
      .then((res) => res.json())
      .then((data) => {
        setDemoMerchants(data.merchants || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch demo merchants:', err);
        showError('catalog_load_failed', language as 'hi' | 'en');
        setLoading(false);
      });
  }, [language]);

  const handleStart = () => {
    if (selected) {
      onStart(selected);
    }
  };

  // Use demo merchants if available, otherwise use fallback
  const storeTypes =
    demoMerchants.length > 0
      ? demoMerchants.map((merchant) => ({
          id: merchant.store_type,
          emoji: merchant.icon,
          name_hi: merchant.shop_name_hi,
          name_en: merchant.shop_name,
          description: STORE_DESCRIPTIONS[merchant.store_type] || merchant.location,
          productCount: merchant.product_count,
          color: STORE_COLORS[merchant.store_type] || 'from-gray-500 to-gray-600',
        }))
      : FALLBACK_STORE_TYPES;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a365d] via-[#2d3748] to-[#1a202c] text-white">
      {/* Header with Language Selector */}
      <header className="flex justify-between items-center px-6 py-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#f97316] to-[#ea580c] flex items-center justify-center text-2xl font-black shadow-lg">
            व्य
          </div>
          <div>
            <h1 className="text-xl font-bold">Vyapari.ai</h1>
            <p className="text-xs text-gray-400">AI Commerce Copilot</p>
          </div>
        </div>
        <LanguageToggle current={language as any} onChange={onLanguageChange as any} />
      </header>

      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-6 py-16 text-center">
        <div className="mb-8">
          <h2 className="text-4xl md:text-6xl font-black mb-4 leading-tight">
            <span className="text-white">1.3 करोड़ दुकान.</span>
            <br />
            <span className="text-white">सिर्फ 15,000 ONDC पे.</span>
            <br />
            <span className="bg-gradient-to-r from-[#f97316] to-[#ea580c] text-transparent bg-clip-text">
              हम यह बदलेंगे।
            </span>
          </h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            AI Commerce Copilot for Bharat
          </p>
        </div>

        {/* Value Proposition */}
        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-16">
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
            <div className="text-4xl mb-3">🎤</div>
            <h3 className="text-lg font-bold mb-2">Hindi Voice</h3>
            <p className="text-sm text-gray-400">
              बोलो और काम हो जाए — Photo upload, price update, order management
            </p>
          </div>
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
            <div className="text-4xl mb-3">📸</div>
            <h3 className="text-lg font-bold mb-2">Shelf to Catalog</h3>
            <p className="text-sm text-gray-400">
              1 photo → 50 products identified → ONDC ready in 2 minutes
            </p>
          </div>
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
            <div className="text-4xl mb-3">💰</div>
            <h3 className="text-lg font-bold mb-2">Save 20-30%</h3>
            <p className="text-sm text-gray-400">
              ONDC 3-5% fees vs Swiggy 25-35% — ₹20,000/month extra earnings
            </p>
          </div>
        </div>

        {/* Store Type Selector */}
        <div className="max-w-5xl mx-auto">
          <h3 className="text-2xl font-bold mb-2">अपनी दुकान का प्रकार चुनें</h3>
          <p className="text-gray-400 mb-8">Select Your Store Type</p>

          {/* Loading state */}
          {loading && (
            <div className="grid md:grid-cols-4 gap-6 mb-12 store-type-cards">
              {[1, 2, 3, 4].map((i) => (
                <StoreCardSkeleton key={i} />
              ))}
            </div>
          )}

          {/* Store cards */}
          {!loading && (
            <div className="grid md:grid-cols-4 gap-6 mb-12 store-type-cards">
              {storeTypes.map((type) => (
              <motion.button
                key={type.id}
                onClick={() => setSelected(type.id)}
                className={`relative bg-white/5 backdrop-blur-sm rounded-2xl p-6 border-2 ${
                  selected === type.id
                    ? 'border-[#f97316] shadow-xl shadow-orange-500/20'
                    : 'border-white/10'
                }`}
                whileHover={{ scale: 1.05, borderColor: 'rgba(255, 255, 255, 0.3)' }}
                whileTap={{ scale: 0.98 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              >
                {/* Selection Checkmark */}
                {selected === type.id && (
                  <div className="absolute -top-3 -right-3 w-8 h-8 bg-[#f97316] rounded-full flex items-center justify-center text-white font-bold shadow-lg">
                    ✓
                  </div>
                )}

                {/* Store Icon */}
                <div className="text-6xl mb-4">{type.emoji}</div>

                {/* Store Name */}
                <h4 className="text-xl font-bold mb-1">{type.name_hi}</h4>
                <p className="text-sm text-gray-400 mb-3">{type.name_en}</p>

                {/* Product Count Badge */}
                <div className={`inline-block bg-gradient-to-r ${type.color} text-white text-xs font-bold px-3 py-1 rounded-full mb-3`}>
                  {type.productCount} products ready
                </div>

                {/* Description */}
                <p className="text-xs text-gray-500">{type.description}</p>

                {/* CTA */}
                <div className="mt-4 text-sm font-semibold text-[#f97316]">
                  शुरू करें →
                </div>
              </motion.button>
              ))}
            </div>
          )}

          {/* Start Button */}
          <button
            onClick={handleStart}
            disabled={!selected}
            className={`w-full max-w-md mx-auto block py-5 rounded-2xl text-lg font-bold transition-all duration-300 ${
              selected
                ? 'bg-gradient-to-r from-[#f97316] to-[#ea580c] text-white shadow-2xl shadow-orange-500/30 hover:shadow-orange-500/50 hover:scale-105'
                : 'bg-gray-800 text-gray-500 cursor-not-allowed'
            }`}
          >
            {selected ? '🚀 Start Your ONDC Journey' : 'Select a store type above'}
          </button>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <div className="flex items-center justify-center gap-3 mb-3">
            <img
              src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E%3Cpath fill='%23FF9900' d='M43.8 25.5c-1.1 4.7-5.2 8.2-10.2 8.2-5.7 0-10.3-4.6-10.3-10.3s4.6-10.3 10.3-10.3c2.8 0 5.4 1.1 7.3 3l3.1-3.1c-2.7-2.7-6.4-4.4-10.4-4.4-8.1 0-14.7 6.6-14.7 14.7s6.6 14.7 14.7 14.7c7.3 0 13.4-5.3 14.5-12.3h-4.3z'/%3E%3Cpath fill='%23232F3E' d='M33.6 33.7c-5.7 0-10.3-4.6-10.3-10.3s4.6-10.3 10.3-10.3c2.8 0 5.4 1.1 7.3 3l-2.1 2.1c-1.4-1.4-3.3-2.2-5.2-2.2-4.1 0-7.4 3.3-7.4 7.4s3.3 7.4 7.4 7.4c3.6 0 6.6-2.6 7.2-6h-7.2v-2.9h10.1c.1.5.1 1 .1 1.5 0 5.7-4.6 10.3-10.2 10.3z'/%3E%3C/svg%3E"
              alt="AWS"
              className="h-6 opacity-70"
            />
            <span className="text-sm text-gray-400">
              Powered by <strong className="text-white">Amazon Bedrock AgentCore</strong>
            </span>
          </div>
          <p className="text-xs text-gray-500">
            Built for AWS AI for Bharat Hackathon 2026 | Professional Track
          </p>
          <p className="text-xs text-gray-600 mt-2">
            Multi-Agent AI System with Claude Sonnet 4 + Nova Embeddings + Transcribe + Polly
          </p>
        </div>
      </footer>
    </div>
  );
}

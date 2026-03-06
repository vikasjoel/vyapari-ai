/**
 * Split Screen Component
 *
 * Desktop-only view showing buyer simulator on left and merchant chat on right
 * For demo purposes to show order flow from both perspectives simultaneously
 */

import { useState, useEffect } from 'react';
import BuyerSimulator from './BuyerSimulator';
import ChatInterface from './ChatInterface';

interface Props {
  merchantId: string;
  onBack: () => void;
}

export default function SplitScreen({ merchantId, onBack }: Props) {
  const [, setOrderCount] = useState(0);

  // Poll for new orders every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      // Trigger a re-render to check for new orders
      setOrderCount((prev) => prev + 1);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Hide on mobile (< 1024px)
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  if (isMobile) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md text-center">
          <div className="text-6xl mb-4">💻</div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">
            Desktop Only Feature
          </h2>
          <p className="text-gray-600 mb-6">
            Split-screen mode is available on desktop devices (1024px+ width) to show both buyer
            and merchant perspectives side-by-side.
          </p>
          <button
            onClick={onBack}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-lg hover:shadow-lg transition-all"
          >
            ← Back to Chat
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#1a365d] to-[#2d3748] text-white px-6 py-4 flex items-center justify-between shadow-lg flex-shrink-0">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div>
            <h1 className="text-lg font-bold">Split-Screen Demo</h1>
            <p className="text-xs text-gray-300">
              See order flow from both buyer and merchant perspectives
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          <span className="text-xs font-medium">Live Demo</span>
        </div>
      </div>

      {/* Split View */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Buyer Simulator */}
        <div className="w-1/2 border-r-2 border-gray-300 flex flex-col bg-white">
          <div className="bg-[#002e6e] text-white px-4 py-2 text-center flex-shrink-0">
            <div className="flex items-center justify-center gap-2">
              <span className="text-lg">👤</span>
              <div>
                <div className="text-sm font-bold">Buyer View</div>
                <div className="text-xs text-blue-200">ONDC Marketplace (Paytm)</div>
              </div>
            </div>
          </div>
          <div className="flex-1 overflow-hidden">
            <div className="h-full overflow-y-auto">
              <BuyerSimulator merchantId={merchantId} onBack={() => {}} />
            </div>
          </div>
        </div>

        {/* Right: Merchant Chat */}
        <div className="w-1/2 flex flex-col bg-[#ece5dd]">
          <div className="bg-[#075e54] text-white px-4 py-2 text-center flex-shrink-0">
            <div className="flex items-center justify-center gap-2">
              <span className="text-lg">🏪</span>
              <div>
                <div className="text-sm font-bold">Merchant View</div>
                <div className="text-xs text-green-200">Vyapari.ai Chat</div>
              </div>
            </div>
          </div>
          <div className="flex-1 overflow-hidden">
            <ChatInterface
              merchantId={merchantId}
              onOpenBuyerSim={() => {}}
              onOpenCatalog={() => {}}
              onOpenTemplate={() => {}}
              onReset={() => {}}
            />
          </div>
        </div>
      </div>

      {/* Instructions Footer */}
      <div className="bg-white border-t border-gray-300 px-6 py-3 flex items-center justify-center gap-6 flex-shrink-0">
        <div className="flex items-center gap-2 text-xs text-gray-600">
          <span className="font-semibold text-[#002e6e]">1.</span>
          <span>Place order on left (buyer view)</span>
        </div>
        <div className="text-gray-300">→</div>
        <div className="flex items-center gap-2 text-xs text-gray-600">
          <span className="font-semibold text-[#075e54]">2.</span>
          <span>See order notification on right (merchant view)</span>
        </div>
        <div className="text-gray-300">→</div>
        <div className="flex items-center gap-2 text-xs text-gray-600">
          <span className="font-semibold text-orange-600">3.</span>
          <span>Accept order and see commission savings</span>
        </div>
      </div>
    </div>
  );
}

/**
 * Intelligence Card Component
 *
 * Displays morning brief, business insights, stock alerts, and demand forecasts
 * Appears as a special message type in the chat interface
 */

import type { Language } from '../types';

interface StockAlert {
  product: string;
  product_hi: string;
  severity: 'high' | 'medium' | 'low';
  current_stock?: number;
  message?: string;
}

interface ForecastData {
  festival?: string;
  festival_hi?: string;
  predicted_demand: string;
  predicted_demand_hi: string;
  date?: string;
  suggested_stock_up?: string[];
}

interface Suggestion {
  text: string;
  text_hi: string;
  action?: string;
  icon?: string;
}

interface IntelligenceData {
  greeting: string;
  greeting_hi: string;
  date: string;
  stats: {
    orders_today: number;
    orders_yesterday: number;
    revenue_today: number;
    revenue_yesterday: number;
    amount_received: number;
    commission_saved: number;
  };
  stock_alerts?: StockAlert[];
  forecast?: ForecastData;
  suggestions?: Suggestion[];
  trending_products?: Array<{ name: string; name_hi: string }>;
}

interface Props {
  data: IntelligenceData;
  language?: Language;
}

export default function IntelligenceCard({ data, language = 'hi' }: Props) {
  const isHindi = language === 'hi';

  return (
    <div className="max-w-md mx-auto">
      {/* Intelligence Card */}
      <div className="bg-gradient-to-br from-[#1a365d] via-[#2d3748] to-[#1a202c] rounded-2xl shadow-2xl overflow-hidden border-2 border-[#f97316]/30">
        {/* Header */}
        <div className="bg-gradient-to-r from-[#f97316] to-[#ea580c] px-4 py-3">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-white font-bold text-lg">
                {isHindi ? data.greeting_hi : data.greeting}
              </h3>
              <p className="text-orange-100 text-xs">{data.date}</p>
            </div>
            <div className="text-3xl">🌅</div>
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-3 gap-2 p-3 bg-white/5 backdrop-blur-sm">
          {/* Orders */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 text-center border border-white/10">
            <div className="text-2xl font-bold text-white">{data.stats.orders_today}</div>
            <div className="text-[10px] text-gray-300 mt-0.5">
              {isHindi ? 'आज के ऑर्डर' : 'Orders Today'}
            </div>
            {data.stats.orders_yesterday > 0 && (
              <div className="text-[9px] text-green-400 mt-1">
                ↑ {data.stats.orders_today - data.stats.orders_yesterday > 0 ? '+' : ''}
                {data.stats.orders_today - data.stats.orders_yesterday}
              </div>
            )}
          </div>

          {/* Revenue */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 text-center border border-white/10">
            <div className="text-2xl font-bold text-white">₹{data.stats.revenue_today}</div>
            <div className="text-[10px] text-gray-300 mt-0.5">
              {isHindi ? 'आज का बिक्री' : 'Revenue Today'}
            </div>
            {data.stats.revenue_yesterday > 0 && (
              <div className="text-[9px] text-green-400 mt-1">
                ↑ ₹{data.stats.revenue_today - data.stats.revenue_yesterday > 0 ? '+' : ''}
                {data.stats.revenue_today - data.stats.revenue_yesterday}
              </div>
            )}
          </div>

          {/* Received */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 text-center border border-white/10">
            <div className="text-2xl font-bold text-[#25d366]">₹{data.stats.amount_received}</div>
            <div className="text-[10px] text-gray-300 mt-0.5">
              {isHindi ? 'मिलेंगे' : 'You Get'}
            </div>
            {data.stats.commission_saved > 0 && (
              <div className="text-[9px] text-orange-400 mt-1">
                💰 ₹{data.stats.commission_saved} {isHindi ? 'बचत' : 'saved'}
              </div>
            )}
          </div>
        </div>

        {/* Stock Alerts */}
        {data.stock_alerts && data.stock_alerts.length > 0 && (
          <div className="px-3 pb-3">
            <div className="bg-red-500/20 backdrop-blur-sm rounded-xl border border-red-500/30 p-3">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">⚠️</span>
                <h4 className="text-white font-semibold text-sm">
                  {isHindi ? 'स्टॉक अलर्ट' : 'Stock Alerts'}
                </h4>
              </div>
              <div className="space-y-1.5">
                {data.stock_alerts.slice(0, 3).map((alert, idx) => (
                  <div
                    key={idx}
                    className={`flex items-center justify-between text-xs p-2 rounded-lg ${
                      alert.severity === 'high'
                        ? 'bg-red-500/20 border border-red-400/30'
                        : 'bg-orange-500/20 border border-orange-400/30'
                    }`}
                  >
                    <span className="text-white font-medium">
                      {isHindi ? alert.product_hi : alert.product}
                    </span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full ${
                        alert.severity === 'high'
                          ? 'bg-red-500 text-white'
                          : 'bg-orange-500 text-white'
                      }`}
                    >
                      {alert.severity === 'high'
                        ? isHindi
                          ? 'खत्म हो रहा'
                          : 'Low Stock'
                        : isHindi
                        ? 'कम स्टॉक'
                        : 'Running Low'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Forecast */}
        {data.forecast && (
          <div className="px-3 pb-3">
            <div className="bg-blue-500/20 backdrop-blur-sm rounded-xl border border-blue-500/30 p-3">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">📊</span>
                <h4 className="text-white font-semibold text-sm">
                  {isHindi ? 'मांग का अनुमान' : 'Demand Forecast'}
                </h4>
              </div>
              <div className="space-y-2">
                {data.forecast.festival && (
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-yellow-400 text-base">🎉</span>
                    <span className="text-white">
                      {isHindi ? data.forecast.festival_hi : data.forecast.festival}
                      {data.forecast.date && (
                        <span className="text-gray-400 ml-1">({data.forecast.date})</span>
                      )}
                    </span>
                  </div>
                )}
                <div className="text-xs text-gray-300">
                  {isHindi ? data.forecast.predicted_demand_hi : data.forecast.predicted_demand}
                </div>
                {data.forecast.suggested_stock_up && data.forecast.suggested_stock_up.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {data.forecast.suggested_stock_up.slice(0, 4).map((item, idx) => (
                      <span
                        key={idx}
                        className="text-[10px] bg-blue-500/30 text-blue-200 px-2 py-0.5 rounded-full"
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Suggestions */}
        {data.suggestions && data.suggestions.length > 0 && (
          <div className="px-3 pb-3">
            <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-3">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">💡</span>
                <h4 className="text-white font-semibold text-sm">
                  {isHindi ? 'सुझाव' : 'Suggestions'}
                </h4>
              </div>
              <div className="space-y-1.5">
                {data.suggestions.map((suggestion, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs text-gray-300">
                    <span className="text-orange-400 mt-0.5">→</span>
                    <span>{isHindi ? suggestion.text_hi : suggestion.text}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Trending Products */}
        {data.trending_products && data.trending_products.length > 0 && (
          <div className="px-3 pb-3">
            <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-3">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">🔥</span>
                <h4 className="text-white font-semibold text-sm">
                  {isHindi ? 'ट्रेंडिंग उत्पाद' : 'Trending Products'}
                </h4>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {data.trending_products.slice(0, 5).map((product, idx) => (
                  <span
                    key={idx}
                    className="text-[10px] bg-orange-500/20 text-orange-200 px-2 py-1 rounded-lg border border-orange-500/30"
                  >
                    {isHindi ? product.name_hi : product.name}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="bg-white/5 backdrop-blur-sm px-4 py-2 border-t border-white/10">
          <p className="text-xs text-gray-400 text-center">
            {isHindi
              ? '🤖 Vyapari.ai द्वारा तैयार किया गया'
              : '🤖 Generated by Vyapari.ai Intelligence'}
          </p>
        </div>
      </div>
    </div>
  );
}

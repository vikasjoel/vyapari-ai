import { useState, useEffect } from 'react';
import { getCatalog, simulateOrder } from '../services/api';
import FeeBreakdownCard from './FeeBreakdownCard';
import LogisticsCard from './LogisticsCard';
import { BuyerProductSkeleton } from './SkeletonLoader';
import { showError, showSuccess } from '../utils/errorHandler';
import type { ONDCOrder, Product } from '../types';

interface Props {
  merchantId: string;
  onBack: () => void;
}

interface CartItem {
  product_id: string;
  name: string;
  price: number;
  qty: number;
}

const BUYER_APPS = [
  { name: 'Paytm', color: 'bg-blue-500' },
  { name: 'Magicpin', color: 'bg-purple-500' },
  { name: 'Ola', color: 'bg-gray-800' },
];

// Mock competitor stores for the search results
const MOCK_COMPETITORS = [
  { name: 'Big Bazaar', distance: '2.1 km', products: '500+', rating: '3.8', type: 'Supermarket' },
  { name: 'DMart', distance: '3.5 km', products: '300+', rating: '4.0', type: 'Hypermarket' },
  { name: 'Reliance Fresh', distance: '1.8 km', products: '200+', rating: '3.6', type: 'Supermarket' },
];

type Step = 'search' | 'store' | 'confirmation';

export default function BuyerSimulator({ merchantId, onBack }: Props) {
  const [step, setStep] = useState<Step>('search');
  const [selectedApp, setSelectedApp] = useState('Paytm');
  const [merchantData, setMerchantData] = useState<{ shop_name: string; location: string; type: string; product_count: number } | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [cart, setCart] = useState<CartItem[]>([]);
  const [order, setOrder] = useState<ONDCOrder | null>(null);
  const [loading, setLoading] = useState(true);
  const [ordering, setOrdering] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const result = await getCatalog(merchantId);
        setMerchantData(result.merchant);
        setProducts(result.products as unknown as Product[]);
        setCategories(result.categories);
      } catch (err) {
        console.error('Failed to load catalog:', err);
        showError('catalog_load_failed', 'en');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [merchantId]);

  const cartTotal = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
  const cartCount = cart.reduce((sum, item) => sum + item.qty, 0);

  const addToCart = (product: Product) => {
    setCart((prev) => {
      const existing = prev.find((i) => i.product_id === product.product_id);
      if (existing) {
        return prev.map((i) =>
          i.product_id === product.product_id ? { ...i, qty: i.qty + 1 } : i
        );
      }
      return [...prev, { product_id: product.product_id, name: product.name_en || product.name_hi, price: product.price, qty: 1 }];
    });
  };

  const removeFromCart = (productId: string) => {
    setCart((prev) => {
      const existing = prev.find((i) => i.product_id === productId);
      if (existing && existing.qty > 1) {
        return prev.map((i) =>
          i.product_id === productId ? { ...i, qty: i.qty - 1 } : i
        );
      }
      return prev.filter((i) => i.product_id !== productId);
    });
  };

  const placeOrder = async () => {
    if (cart.length === 0) return;
    setOrdering(true);
    try {
      const result = await simulateOrder(merchantId, cart, selectedApp);
      setOrder(result);
      showSuccess('order_placed', 'en');
      setStep('confirmation');
    } catch (err) {
      console.error('Failed to place order:', err);
      showError('order_failed', 'en');
    } finally {
      setOrdering(false);
    }
  };

  const filteredProducts = selectedCategory === 'All'
    ? products
    : products.filter((p) => p.category === selectedCategory);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col max-w-lg mx-auto">
        {/* Header */}
        <div className="bg-[#002e6e] text-white px-4 py-3 flex items-center gap-3 flex-shrink-0 shadow-lg">
          <button onClick={onBack} className="p-1 hover:bg-white/10 rounded-lg transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div className="flex-1">
            <div className="text-sm font-bold">ONDC Marketplace</div>
            <div className="text-[10px] text-blue-200">Loading...</div>
          </div>
        </div>
        {/* Skeleton Products */}
        <div className="p-3 space-y-2">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <BuyerProductSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col max-w-lg mx-auto">
      {/* Header — Paytm Blue */}
      <div className="bg-[#002e6e] text-white px-4 py-3 flex items-center gap-3 flex-shrink-0 shadow-lg">
        <button onClick={onBack} className="p-1 hover:bg-white/10 rounded-lg transition-colors">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div className="flex-1">
          <div className="text-sm font-bold flex items-center gap-2">
            <span>ONDC Marketplace</span>
            <span className="text-xs bg-[#00baf2] px-2 py-0.5 rounded-full font-semibold">Demo</span>
          </div>
          <div className="text-[10px] text-blue-200">See how customers discover your store</div>
        </div>
      </div>

      {/* Buyer App Tabs */}
      <div className="bg-white border-b border-gray-200 px-3 py-2 flex gap-2 flex-shrink-0">
        {BUYER_APPS.map((app) => (
          <button
            key={app.name}
            onClick={() => setSelectedApp(app.name)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
              selectedApp === app.name
                ? `${app.color} text-white shadow-sm`
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {app.name}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto">
        {/* ── Step 1: Search Results ── */}
        {step === 'search' && (
          <div className="p-3 space-y-2">
            {/* Search Bar */}
            <div className="bg-white rounded-xl border border-gray-200 px-3 py-2.5 flex items-center gap-2 shadow-sm">
              <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span className="text-sm text-gray-500">
                Grocery near {merchantData?.location || 'you'}
              </span>
            </div>

            <div className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider px-1 pt-1">
              Stores on ONDC ({selectedApp})
            </div>

            {/* Merchant's Store — Highlighted */}
            <button
              onClick={() => setStep('store')}
              className="w-full bg-white rounded-xl border-2 border-green-400 p-3 text-left shadow-sm hover:shadow-md transition-shadow relative"
            >
              <div className="absolute -top-2 left-3 bg-green-500 text-white text-[9px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                ONDC
              </div>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center text-xl flex-shrink-0">
                  🏪
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-bold text-sm text-gray-900 truncate">{merchantData?.shop_name || 'Your Store'}</div>
                  <div className="text-xs text-gray-500">{merchantData?.location}</div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] bg-green-50 text-green-700 font-medium px-1.5 py-0.5 rounded">
                      {merchantData?.product_count || 0} products
                    </span>
                    <span className="text-[10px] text-gray-400">0.5 km</span>
                    <span className="text-[10px] text-yellow-600">★ New</span>
                  </div>
                </div>
                <svg className="w-4 h-4 text-gray-300 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </button>

            {/* Competitor Stores — Grayed */}
            {MOCK_COMPETITORS.map((store) => (
              <div
                key={store.name}
                className="bg-white rounded-xl border border-gray-200 p-3 opacity-60 cursor-not-allowed"
              >
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center text-xl flex-shrink-0">
                    🏬
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-sm text-gray-700">{store.name}</div>
                    <div className="text-xs text-gray-400">{store.type}</div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] text-gray-400">{store.products} products</span>
                      <span className="text-[10px] text-gray-400">{store.distance}</span>
                      <span className="text-[10px] text-yellow-500">★ {store.rating}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ── Step 2: Store Detail + Cart ── */}
        {step === 'store' && (
          <div>
            {/* Store Header */}
            <div className="bg-white border-b border-gray-200 p-3">
              <div className="flex items-center gap-3">
                <button onClick={() => setStep('search')} className="text-gray-400 hover:text-gray-600">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <div>
                  <div className="font-bold text-sm">{merchantData?.shop_name}</div>
                  <div className="text-xs text-gray-500">{merchantData?.product_count} products · {merchantData?.location}</div>
                </div>
              </div>
            </div>

            {/* Category Tabs — Paytm Style */}
            <div className="bg-white border-b border-gray-200 overflow-x-auto">
              <div className="flex gap-1.5 px-3 py-2">
                {['All', ...categories].map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
                      selectedCategory === cat
                        ? 'bg-[#002e6e] text-white shadow-sm'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Product List */}
            <div className="p-3 space-y-2 pb-24">
              {filteredProducts.map((product) => {
                const inCart = cart.find((i) => i.product_id === product.product_id);
                const isVyapariSeller = product.source === 'template' || product.source === 'vision';
                return (
                  <div key={product.product_id} className="bg-white rounded-lg border border-gray-200 p-2.5 flex items-center gap-3 relative overflow-hidden">
                    {/* Vyapari.ai Seller Badge */}
                    {isVyapariSeller && (
                      <div className="absolute top-0 right-0">
                        <div className="bg-gradient-to-br from-[#f97316] to-[#ea580c] text-white text-[8px] font-bold px-2 py-0.5 rounded-bl-lg shadow-sm">
                          ⚡ Vyapari.ai
                        </div>
                      </div>
                    )}
                    <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center text-lg flex-shrink-0">
                      {product.category === 'Dairy' ? '🥛' :
                       product.category === 'Snacks' ? '🍿' :
                       product.category === 'Beverages' ? '🥤' :
                       product.category === 'Staples' ? '🌾' :
                       product.category === 'Personal Care' ? '🧴' : '📦'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-semibold text-gray-900 truncate">{product.name_en || product.name_hi}</div>
                      {product.brand && <div className="text-[10px] text-gray-400">{product.brand}</div>}
                      <div className="text-sm font-bold text-[#002e6e] mt-0.5">₹{product.price}</div>
                    </div>
                    {inCart ? (
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => removeFromCart(product.product_id)}
                          className="w-7 h-7 rounded-full bg-gray-100 text-gray-600 flex items-center justify-center text-sm font-bold hover:bg-gray-200 transition-colors"
                        >
                          -
                        </button>
                        <span className="text-sm font-bold w-4 text-center text-[#002e6e]">{inCart.qty}</span>
                        <button
                          onClick={() => addToCart(product)}
                          className="w-7 h-7 rounded-full bg-[#002e6e] text-white flex items-center justify-center text-sm font-bold hover:bg-[#00366e] transition-colors"
                        >
                          +
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => addToCart(product)}
                        className="px-3 py-1.5 bg-[#002e6e] text-white text-xs font-semibold rounded-lg hover:bg-[#00366e] transition-colors"
                      >
                        Add
                      </button>
                    )}
                  </div>
                );
              })}

              {filteredProducts.length === 0 && (
                <div className="text-center text-gray-400 py-8 text-sm">No products in this category</div>
              )}
            </div>

            {/* Floating Cart Bar — Paytm Style */}
            {cart.length > 0 && (
              <div className="fixed bottom-0 left-0 right-0 max-w-lg mx-auto">
                <div className="bg-gradient-to-r from-[#002e6e] to-[#003a7e] mx-3 mb-3 rounded-xl px-4 py-3 flex items-center justify-between shadow-2xl border border-[#00baf2]/30">
                  <div>
                    <div className="text-white text-sm font-bold">{cartCount} items · ₹{cartTotal}</div>
                    <div className="text-blue-200 text-[10px] flex items-center gap-1">
                      <span>via ONDC on {selectedApp}</span>
                      <span className="inline-block w-1 h-1 bg-[#00baf2] rounded-full animate-pulse" />
                    </div>
                  </div>
                  <button
                    onClick={placeOrder}
                    disabled={ordering}
                    className="bg-gradient-to-r from-[#00baf2] to-[#0098d4] text-white font-bold text-sm px-5 py-2.5 rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {ordering ? '⏳ Placing...' : 'Place Order →'}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── Step 3: Order Confirmation ── */}
        {step === 'confirmation' && order && (
          <div className="p-3 space-y-3 pb-24">
            {/* Success Banner */}
            <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-4 text-center text-white">
              <div className="text-2xl mb-1">✓</div>
              <div className="font-bold text-base">Order Placed on ONDC!</div>
              <div className="text-green-100 text-xs mt-1">
                Order #{order.order_id?.slice(0, 8)} · {order.customer_name} via {order.buyer_app}
              </div>
            </div>

            {/* Items Summary */}
            <div className="bg-white rounded-xl border border-gray-200 p-3">
              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Order Items</div>
              {order.items.map((item, i) => (
                <div key={i} className="flex justify-between text-sm py-1">
                  <span className="text-gray-700">{item.name} x{item.qty}</span>
                  <span className="font-semibold">₹{(item.price * item.qty).toFixed(0)}</span>
                </div>
              ))}
              <div className="border-t border-gray-200 mt-1 pt-1 flex justify-between font-bold text-sm">
                <span>Total</span>
                <span>₹{order.total.toFixed(0)}</span>
              </div>
            </div>

            {/* Fee Breakdown */}
            {order.ondc_fees && order.aggregator_comparison?.swiggy && (
              <FeeBreakdownCard
                orderTotal={order.total}
                ondcFees={order.ondc_fees}
                swiggyFees={order.aggregator_comparison.swiggy}
                savingsVsSwiggy={order.savings_vs_swiggy}
              />
            )}

            {/* Logistics */}
            {order.logistics && <LogisticsCard logistics={order.logistics} />}

            {/* Back to Chat */}
            <button
              onClick={onBack}
              className="w-full bg-[#075e54] text-white font-bold py-3 rounded-xl text-sm hover:bg-[#064e3b] transition-colors"
            >
              ← See This in Merchant's Chat
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

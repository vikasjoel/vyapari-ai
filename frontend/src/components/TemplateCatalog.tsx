import { useState, useEffect } from 'react';
import type { TemplateProduct } from '../types';
import { getTemplate, confirmTemplate } from '../services/api';
import { celebrateGoLive } from './ConfettiAnimation';
import { TemplateCatalogSkeleton } from './SkeletonLoader';
import { showError, showSuccess } from '../utils/errorHandler';

interface Props {
  storeType: string;
  merchantId: string;
  onConfirm: (count: number) => void;
  onBack: () => void;
}

const STORE_META: Record<string, { label_hi: string; emoji: string }> = {
  kirana: { label_hi: 'किराना स्टोर', emoji: '🏪' },
  restaurant: { label_hi: 'रेस्टोरेंट', emoji: '🍛' },
  sweet_shop: { label_hi: 'मिठाई की दुकान', emoji: '🍬' },
  bakery: { label_hi: 'बेकरी', emoji: '🧁' },
};

export default function TemplateCatalog({ storeType, merchantId, onConfirm, onBack }: Props) {
  const [categories, setCategories] = useState<Record<string, TemplateProduct[]>>({});
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [priceOverrides, setPriceOverrides] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState('');
  const [totalProducts, setTotalProducts] = useState(0);
  const [editingPrice, setEditingPrice] = useState<string | null>(null);

  useEffect(() => {
    loadTemplate();
  }, [storeType]);

  const loadTemplate = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getTemplate(storeType);
      setCategories(data.categories);
      setTotalProducts(data.total_products);

      // Auto-select products with popularity_score >= 7 (if available)
      // Otherwise select all
      const autoSelected = new Set<string>();
      let hasPopularityScore = false;

      Object.values(data.categories).forEach((products) => {
        products.forEach((p) => {
          if (p.popularity_score !== undefined && p.popularity_score !== null) {
            hasPopularityScore = true;
            if (p.popularity_score >= 7) {
              autoSelected.add(p.product_id);
            }
          }
        });
      });

      // If no popularity scores, select all
      if (!hasPopularityScore) {
        Object.values(data.categories).forEach((products) => {
          products.forEach((p) => autoSelected.add(p.product_id));
        });
      }

      setSelected(autoSelected);

      // Expand first category by default
      const cats = Object.keys(data.categories);
      if (cats.length > 0) {
        setExpandedCategories(new Set([cats[0]]));
      }
    } catch (err) {
      console.error('Failed to load template:', err);
      setError('Failed to load template. Please try again.');
      showError('template_load_failed', 'hi');
    } finally {
      setLoading(false);
    }
  };

  const toggleCategory = (cat: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat);
      else next.add(cat);
      return next;
    });
  };

  const toggleProduct = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const selectAllInCategory = (cat: string) => {
    const products = categories[cat] || [];
    setSelected((prev) => {
      const next = new Set(prev);
      products.forEach((p) => next.add(p.product_id));
      return next;
    });
  };

  const deselectAllInCategory = (cat: string) => {
    const products = categories[cat] || [];
    setSelected((prev) => {
      const next = new Set(prev);
      products.forEach((p) => next.delete(p.product_id));
      return next;
    });
  };

  const isCategoryFullySelected = (cat: string): boolean => {
    const products = categories[cat] || [];
    return products.every((p) => selected.has(p.product_id));
  };

  const selectedInCategory = (cat: string): number => {
    const products = categories[cat] || [];
    return products.filter((p) => selected.has(p.product_id)).length;
  };

  const handlePriceChange = (productId: string, newPrice: string) => {
    const price = parseInt(newPrice);
    if (!isNaN(price) && price > 0) {
      setPriceOverrides((prev) => ({ ...prev, [productId]: price }));
    }
  };

  const handleConfirm = async () => {
    if (selected.size === 0) return;
    setConfirming(true);
    try {
      const result = await confirmTemplate(
        merchantId,
        storeType,
        Array.from(selected),
        priceOverrides
      );

      // Celebrate! 🎉
      celebrateGoLive();
      showSuccess('catalog_saved', 'hi');

      // Wait for confetti to start, then navigate
      setTimeout(() => {
        onConfirm(result.products_saved);
      }, 500);
    } catch (err) {
      console.error('Failed to save catalog:', err);
      setError('Failed to save catalog. Please try again.');
      showError('catalog_load_failed', 'hi');
    } finally {
      setConfirming(false);
    }
  };

  const storeMeta = STORE_META[storeType] || { label_hi: storeType, emoji: '🏪' };
  const categoryKeys = Object.keys(categories);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#1a365d] via-[#2d3748] to-[#1a202c]">
        <TemplateCatalogSkeleton />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen max-w-lg mx-auto bg-gradient-to-br from-[#1a365d] via-[#2d3748] to-[#1a202c]">
      {/* Header */}
      <div className="bg-[#1a365d] text-white px-4 py-3 flex items-center gap-3 shadow-lg flex-shrink-0 border-b border-white/10">
        <button
          onClick={onBack}
          className="p-1 hover:bg-white/10 rounded-full transition-colors"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div className="flex-1">
          <div className="font-bold text-base flex items-center gap-2">
            <span>{storeMeta.emoji}</span>
            <span>Build Your Catalog</span>
          </div>
          <div className="text-xs text-gray-300">
            {storeMeta.label_hi} — {totalProducts} products available
          </div>
        </div>
      </div>

      {/* Sticky Counter Bar */}
      <div className="bg-gradient-to-r from-[#f97316] to-[#ea580c] px-4 py-3 flex items-center justify-between shadow-md flex-shrink-0 sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
            <span className="text-lg">✅</span>
          </div>
          <div>
            <div className="text-white font-bold text-lg">
              {selected.size} <span className="text-sm text-orange-100">/ {totalProducts}</span>
            </div>
            <div className="text-xs text-orange-100">products selected</div>
          </div>
        </div>
        {Object.keys(priceOverrides).length > 0 && (
          <div className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full">
            <div className="text-xs text-white font-medium">
              ✏️ {Object.keys(priceOverrides).length} edited
            </div>
          </div>
        )}
      </div>

      {/* Instruction bar */}
      <div className="bg-white/5 backdrop-blur-sm px-4 py-2 text-xs text-gray-300 flex items-center gap-2 border-b border-white/10 flex-shrink-0">
        <span className="text-base">💡</span>
        <span>अपनी दुकान के products चुनिए — price tap करके edit करें</span>
      </div>

      {/* Accordion Categories */}
      <div className="flex-1 overflow-y-auto">
        {error && (
          <div className="mx-3 mt-3 bg-red-500/20 border border-red-500/50 rounded-lg px-3 py-2 text-xs text-red-200 backdrop-blur-sm">
            {error}
          </div>
        )}

        <div className="space-y-2 p-3">
          {categoryKeys.map((cat) => {
            const products = categories[cat] || [];
            const selCount = selectedInCategory(cat);
            const isExpanded = expandedCategories.has(cat);
            const isFullySelected = isCategoryFullySelected(cat);

            return (
              <div
                key={cat}
                className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 overflow-hidden"
              >
                {/* Category Header — clickable accordion */}
                <button
                  onClick={() => toggleCategory(cat)}
                  className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
                        isFullySelected
                          ? 'bg-[#25d366]'
                          : selCount > 0
                          ? 'bg-orange-500'
                          : 'bg-white/10'
                      }`}
                    >
                      {isFullySelected ? (
                        <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        <span className="text-white text-xs font-bold">{selCount}</span>
                      )}
                    </div>
                    <div className="text-left">
                      <div className="text-white font-semibold text-sm capitalize">
                        {cat.replace(/_/g, ' ')}
                      </div>
                      <div className="text-xs text-gray-400">
                        {selCount}/{products.length} selected
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <svg
                      className={`w-5 h-5 text-gray-400 transition-transform ${
                        isExpanded ? 'rotate-180' : ''
                      }`}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </button>

                {/* Category Actions (when expanded) */}
                {isExpanded && (
                  <>
                    <div className="flex items-center justify-end gap-3 px-4 pb-2 border-t border-white/5">
                      <button
                        onClick={() => selectAllInCategory(cat)}
                        disabled={isFullySelected}
                        className="text-[10px] text-[#25d366] font-semibold hover:underline disabled:text-gray-600 disabled:no-underline"
                      >
                        Select All
                      </button>
                      <span className="text-gray-600">|</span>
                      <button
                        onClick={() => deselectAllInCategory(cat)}
                        disabled={selCount === 0}
                        className="text-[10px] text-red-400 font-semibold hover:underline disabled:text-gray-600 disabled:no-underline"
                      >
                        Deselect All
                      </button>
                    </div>

                    {/* Product List */}
                    <div className="px-2 pb-2 space-y-1.5">
                      {products.map((product) => {
                        const isSelected = selected.has(product.product_id);
                        const displayPrice = priceOverrides[product.product_id] ?? product.mrp;
                        const isEditing = editingPrice === product.product_id;

                        return (
                          <div
                            key={product.product_id}
                            className={`flex items-center gap-2.5 bg-white/5 backdrop-blur-sm rounded-lg p-2.5 border transition-all ${
                              isSelected
                                ? 'border-[#25d366]/50 shadow-sm shadow-green-500/20'
                                : 'border-white/5 opacity-40'
                            }`}
                          >
                            {/* Checkbox */}
                            <button
                              onClick={() => toggleProduct(product.product_id)}
                              className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                                isSelected
                                  ? 'bg-[#25d366] border-[#25d366]'
                                  : 'border-gray-500 hover:border-gray-400'
                              }`}
                            >
                              {isSelected && (
                                <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                                </svg>
                              )}
                            </button>

                            {/* Product image */}
                            <div className="w-11 h-11 rounded-lg bg-white/10 flex-shrink-0 overflow-hidden">
                              {product.image_url ? (
                                <img
                                  src={product.image_url}
                                  alt={product.name}
                                  className="w-full h-full object-cover"
                                  loading="lazy"
                                  onError={(e) => {
                                    (e.target as HTMLImageElement).style.display = 'none';
                                  }}
                                />
                              ) : (
                                <div className="w-full h-full flex items-center justify-center text-lg">
                                  {storeMeta.emoji}
                                </div>
                              )}
                            </div>

                            {/* Product info */}
                            <div className="flex-1 min-w-0">
                              <div className="text-xs font-medium text-white truncate">
                                {product.name_hi}
                              </div>
                              <div className="text-[10px] text-gray-400 truncate">
                                {product.name}
                                {product.brand && product.brand !== 'House' ? ` · ${product.brand}` : ''}
                              </div>
                              {product.size_weight && (
                                <div className="text-[9px] text-gray-500">{product.size_weight}</div>
                              )}
                            </div>

                            {/* Veg badge */}
                            {product.veg !== undefined && (
                              <div
                                className={`flex-shrink-0 w-3.5 h-3.5 border rounded-sm flex items-center justify-center ${
                                  product.veg ? 'border-green-500' : 'border-red-500'
                                }`}
                              >
                                <div
                                  className={`w-1.5 h-1.5 rounded-full ${
                                    product.veg ? 'bg-green-500' : 'bg-red-500'
                                  }`}
                                />
                              </div>
                            )}

                            {/* Price — editable */}
                            <div className="flex-shrink-0 text-right">
                              {isEditing ? (
                                <input
                                  type="number"
                                  defaultValue={displayPrice}
                                  autoFocus
                                  className="w-16 text-xs font-bold text-right bg-orange-500/20 border border-orange-400 rounded px-1.5 py-0.5 outline-none focus:border-[#25d366] text-white"
                                  onBlur={(e) => {
                                    handlePriceChange(product.product_id, e.target.value);
                                    setEditingPrice(null);
                                  }}
                                  onKeyDown={(e) => {
                                    if (e.key === 'Enter') {
                                      handlePriceChange(product.product_id, (e.target as HTMLInputElement).value);
                                      setEditingPrice(null);
                                    }
                                  }}
                                />
                              ) : (
                                <button
                                  onClick={() => setEditingPrice(product.product_id)}
                                  className="text-xs font-bold text-white hover:text-[#25d366] transition-colors"
                                  title="Edit price"
                                >
                                  ₹{displayPrice}
                                </button>
                              )}
                              {priceOverrides[product.product_id] !== undefined && (
                                <div className="text-[9px] text-orange-400 line-through">₹{product.mrp}</div>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom action bar — sticky */}
      <div className="bg-[#1a365d] border-t border-white/10 px-4 py-4 flex-shrink-0 shadow-[0_-4px_20px_rgba(0,0,0,0.3)]">
        <button
          onClick={handleConfirm}
          disabled={selected.size === 0 || confirming}
          className={`w-full py-4 rounded-2xl text-base font-bold transition-all ${
            selected.size > 0 && !confirming
              ? 'bg-gradient-to-r from-[#25d366] to-[#20bd5a] text-white shadow-2xl shadow-green-500/30 hover:shadow-green-500/50 hover:scale-[1.02] active:scale-[0.98]'
              : 'bg-white/10 text-gray-500 cursor-not-allowed'
          }`}
        >
          {confirming ? (
            <span className="flex items-center justify-center gap-2">
              <div className="w-5 h-5 border-3 border-white border-t-transparent rounded-full animate-spin" />
              Publishing to ONDC...
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              🚀 <span>Go Live with {selected.size} Products</span>
            </span>
          )}
        </button>

        <div className="text-center mt-2 text-xs text-gray-400">
          {selected.size > 0 ? (
            <>
              Your catalog will be live on ONDC in seconds
              {Object.keys(priceOverrides).length > 0 && (
                <span className="text-orange-400"> · {Object.keys(priceOverrides).length} prices edited</span>
              )}
            </>
          ) : (
            'Select products to continue'
          )}
        </div>
      </div>
    </div>
  );
}

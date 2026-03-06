import { useState, useEffect } from 'react';
import { getCatalog } from '../services/api';
import ProductCard from './ProductCard';
import type { Product } from '../types';

interface Props {
  merchantId: string;
}

interface CatalogData {
  merchant: {
    shop_name: string;
    location: string;
    type: string;
    product_count: number;
  };
  products: Product[];
  categories: string[];
}

export default function BuyerCatalogView({ merchantId }: Props) {
  const [data, setData] = useState<CatalogData | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const result = await getCatalog(merchantId);
        setData(result as unknown as CatalogData);
      } catch {
        setError('Could not load catalog. Please check the merchant ID.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [merchantId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl animate-bounce mb-2">🏪</div>
          <div className="text-gray-500">Loading catalog...</div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center bg-white rounded-xl p-6 shadow">
          <div className="text-4xl mb-2">😔</div>
          <div className="text-gray-700 font-medium">{error || 'Catalog not found'}</div>
        </div>
      </div>
    );
  }

  const filteredProducts =
    selectedCategory === 'All'
      ? data.products
      : data.products.filter((p) => p.category === selectedCategory);

  const allCategories = ['All', ...data.categories];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-[#075e54] text-white px-4 py-5">
        <div className="max-w-lg mx-auto">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-[#25d366] flex items-center justify-center text-xl">
              🏪
            </div>
            <div>
              <h1 className="text-xl font-bold">{data.merchant.shop_name}</h1>
              <p className="text-green-200 text-sm">{data.merchant.location}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 mt-3 text-sm text-green-200">
            <span>{data.merchant.type}</span>
            <span>·</span>
            <span>{data.merchant.product_count} products</span>
            <span className="ml-auto bg-green-700 px-2 py-0.5 rounded text-xs">
              ONDC Verified
            </span>
          </div>
        </div>
      </div>

      {/* Category tabs */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-lg mx-auto overflow-x-auto">
          <div className="flex gap-1 px-3 py-2">
            {allCategories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
                  selectedCategory === cat
                    ? 'bg-[#075e54] text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Products grid */}
      <div className="max-w-lg mx-auto px-3 py-3 space-y-2">
        {filteredProducts.map((product) => (
          <ProductCard key={product.product_id} product={product} />
        ))}

        {filteredProducts.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            No products in this category
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="bg-white border-t border-gray-200 py-4 text-center text-xs text-gray-400">
        Powered by <span className="font-semibold text-[#075e54]">Vyapari.ai</span> on ONDC
      </div>
    </div>
  );
}

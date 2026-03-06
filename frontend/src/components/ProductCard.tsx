import type { Product } from '../types';

interface Props {
  product: Product;
  compact?: boolean;
}

export default function ProductCard({ product, compact }: Props) {
  const confidenceColor =
    product.confidence >= 0.9
      ? 'bg-green-100 text-green-700'
      : product.confidence >= 0.7
        ? 'bg-yellow-100 text-yellow-700'
        : 'bg-red-100 text-red-700';

  if (compact) {
    return (
      <div className="flex items-center gap-2 py-1 border-b border-gray-100 last:border-0">
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium truncate">{product.name_hi || product.name_en}</div>
          <div className="text-xs text-gray-500">{product.brand} · {product.category}</div>
        </div>
        <div className="text-sm font-bold text-green-700">₹{product.price}</div>
        {!product.available && (
          <span className="text-[10px] bg-red-100 text-red-600 px-1.5 py-0.5 rounded">Out</span>
        )}
      </div>
    );
  }

  return (
    <div className="bg-gray-50 rounded-lg p-2.5 border border-gray-200">
      <div className="flex items-start gap-2">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name_en}
            className="w-12 h-12 rounded object-cover flex-shrink-0"
          />
        ) : (
          <div className="w-12 h-12 rounded bg-gray-200 flex items-center justify-center text-lg flex-shrink-0">
            {product.category === 'Dairy' ? '🥛' :
             product.category === 'Snacks' ? '🍪' :
             product.category === 'Staples' ? '🌾' :
             product.category === 'Beverages' ? '🥤' :
             product.category === 'Personal Care' ? '🧴' :
             product.category === 'Household' ? '🏠' : '📦'}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold text-gray-900">{product.name_hi}</div>
          <div className="text-xs text-gray-500">{product.name_en}</div>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-sm font-bold text-green-700">₹{product.price}</span>
            <span className={`text-[10px] px-1.5 py-0.5 rounded ${confidenceColor}`}>
              {Math.round(product.confidence * 100)}%
            </span>
            <span className="text-[10px] text-gray-400">{product.source}</span>
          </div>
        </div>
        {!product.available && (
          <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full">
            Out of stock
          </span>
        )}
      </div>
    </div>
  );
}

/**
 * Skeleton Loader Components
 *
 * Reusable skeleton loaders for various content types
 */

// Base skeleton with shimmer effect
export function Skeleton({ className = '' }: { className?: string }) {
  return (
    <div
      className={`animate-pulse bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 bg-[length:200%_100%] rounded ${className}`}
      style={{
        animation: 'shimmer 1.5s ease-in-out infinite',
      }}
    />
  );
}

// Product card skeleton
export function ProductCardSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-2.5 flex items-center gap-3">
      <Skeleton className="w-12 h-12 rounded-lg flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-3 w-3/4" />
        <Skeleton className="h-2 w-1/2" />
        <Skeleton className="h-3 w-1/4" />
      </div>
      <Skeleton className="w-16 h-8 rounded-lg" />
    </div>
  );
}

// Chat message skeleton
export function ChatMessageSkeleton() {
  return (
    <div className="flex justify-start mb-2">
      <div className="bg-white rounded-lg rounded-bl-none px-3 py-2 shadow-sm max-w-[85%]">
        <div className="space-y-2">
          <Skeleton className="h-3 w-48" />
          <Skeleton className="h-3 w-36" />
          <Skeleton className="h-2 w-20" />
        </div>
      </div>
    </div>
  );
}

// Template catalog skeleton
export function TemplateCatalogSkeleton() {
  return (
    <div className="space-y-3 p-3">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-4">
          <div className="flex items-center gap-3 mb-3">
            <Skeleton className="w-8 h-8 rounded-full" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-3 w-24" />
            </div>
          </div>
          <div className="space-y-2">
            <ProductCardSkeleton />
            <ProductCardSkeleton />
            <ProductCardSkeleton />
          </div>
        </div>
      ))}
    </div>
  );
}

// Store card skeleton (for landing page)
export function StoreCardSkeleton() {
  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border-2 border-white/10">
      <Skeleton className="w-16 h-16 rounded-full mx-auto mb-4" />
      <Skeleton className="h-5 w-24 mx-auto mb-2" />
      <Skeleton className="h-3 w-32 mx-auto mb-3" />
      <Skeleton className="h-6 w-28 mx-auto mb-3 rounded-full" />
      <Skeleton className="h-3 w-full" />
    </div>
  );
}

// Buyer simulator product skeleton
export function BuyerProductSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-2.5 flex items-center gap-3">
      <Skeleton className="w-12 h-12 rounded-lg flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-3 w-3/4" />
        <Skeleton className="h-2 w-1/2" />
        <Skeleton className="h-4 w-16" />
      </div>
      <Skeleton className="w-12 h-8 rounded-lg" />
    </div>
  );
}

// Add shimmer animation to CSS
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes shimmer {
      0% {
        background-position: -200% 0;
      }
      100% {
        background-position: 200% 0;
      }
    }
  `;
  document.head.appendChild(style);
}

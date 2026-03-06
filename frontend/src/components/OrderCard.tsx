import type { Order } from '../types';

interface Props {
  order: Order;
  onAccept?: (orderId: string) => void;
  onReject?: (orderId: string) => void;
}

export default function OrderCard({ order, onAccept, onReject }: Props) {
  const savingsPercent = order.total > 0
    ? Math.round((order.savings / order.total) * 100)
    : 0;

  return (
    <div className="bg-white rounded-lg border border-green-200 p-3 my-2 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5">
          <span className="text-base">🔔</span>
          <span className="font-semibold text-sm text-gray-900">New Order!</span>
        </div>
        <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">
          {order.buyer_app}
        </span>
      </div>

      {/* Customer */}
      <div className="text-xs text-gray-500 mb-2">
        From: {order.customer_name}
      </div>

      {/* Items */}
      <div className="bg-gray-50 rounded p-2 mb-2">
        {order.items.map((item, i) => (
          <div key={i} className="flex justify-between text-xs py-0.5">
            <span>{item.name} x{item.qty}</span>
            <span className="font-medium">₹{item.price * item.qty}</span>
          </div>
        ))}
        <div className="flex justify-between text-sm font-bold mt-1 pt-1 border-t border-gray-200">
          <span>Total</span>
          <span>₹{order.total}</span>
        </div>
      </div>

      {/* Savings */}
      <div className="bg-green-50 rounded p-2 mb-2">
        <div className="flex justify-between text-xs">
          <span className="text-gray-600">ONDC Commission</span>
          <span className="text-green-700 font-medium">₹{order.commission_ondc}</span>
        </div>
        <div className="flex justify-between text-xs mt-0.5">
          <span className="text-gray-600">Swiggy would be</span>
          <span className="text-red-500 line-through">₹{order.commission_swiggy}</span>
        </div>
        <div className="flex justify-between text-sm font-bold mt-1 pt-1 border-t border-green-200">
          <span className="text-green-700">You save</span>
          <span className="text-green-700">₹{order.savings} ({savingsPercent}%)</span>
        </div>
      </div>

      {/* Actions */}
      {order.status === 'new' && (onAccept || onReject) && (
        <div className="flex gap-2">
          <button
            onClick={() => onAccept?.(order.order_id)}
            className="flex-1 bg-green-600 text-white text-sm py-1.5 rounded-lg font-medium hover:bg-green-700 transition-colors"
          >
            Accept
          </button>
          <button
            onClick={() => onReject?.(order.order_id)}
            className="flex-1 bg-gray-100 text-gray-700 text-sm py-1.5 rounded-lg font-medium hover:bg-gray-200 transition-colors"
          >
            Reject
          </button>
        </div>
      )}

      {order.status !== 'new' && (
        <div className={`text-center text-xs py-1 rounded ${
          order.status === 'accepted' ? 'bg-green-100 text-green-700' :
          order.status === 'cancelled' ? 'bg-red-100 text-red-600' :
          'bg-blue-50 text-blue-600'
        }`}>
          {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
        </div>
      )}
    </div>
  );
}

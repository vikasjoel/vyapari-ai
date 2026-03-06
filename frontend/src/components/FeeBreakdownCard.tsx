import type { ONDCFeeBreakdown, AggregatorComparison } from '../types';

interface Props {
  orderTotal: number;
  ondcFees: ONDCFeeBreakdown;
  swiggyFees: AggregatorComparison;
  savingsVsSwiggy: number;
}

export default function FeeBreakdownCard({ orderTotal, ondcFees, swiggyFees, savingsVsSwiggy }: Props) {
  const savingsPercent = orderTotal > 0 ? Math.round((savingsVsSwiggy / orderTotal) * 100) : 0;
  const monthlyProjection = Math.round(savingsVsSwiggy * 30);
  const yearlyProjection = Math.round(savingsVsSwiggy * 365);

  return (
    <div className="rounded-xl overflow-hidden my-2 shadow-md border border-gray-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 px-3 py-2 text-center">
        <span className="text-[10px] font-bold text-gray-300 uppercase tracking-widest">Fee Comparison</span>
      </div>

      {/* Side by side */}
      <div className="grid grid-cols-2 divide-x divide-gray-200">
        {/* ONDC Side — Green */}
        <div className="bg-gradient-to-b from-green-50 to-white p-3">
          <div className="text-center mb-2">
            <div className="text-[10px] font-bold text-green-700 uppercase tracking-wider">ONDC</div>
            <div className="text-[9px] text-green-600/60">Your Path</div>
          </div>
          <div className="space-y-1.5">
            <FeeRow label={`Buyer App (${ondcFees.buyer_app})`} amount={ondcFees.buyer_app_finder_fee} pct={ondcFees.buyer_app_finder_fee_pct} color="green" />
            <FeeRow label="Seller App (Vyapari)" amount={ondcFees.seller_app_fee} pct={ondcFees.seller_app_fee_pct} color="green" />
            <FeeRow label="ONDC Network" amount={ondcFees.ondc_network_fee} pct={ondcFees.ondc_network_fee_pct} color="green" />
            <FeeRow label={`Logistics (${ondcFees.logistics_partner})`} amount={ondcFees.logistics_cost} color="green" />
            <FeeRow label="GST on Fees" amount={ondcFees.gst_on_fees} color="green" />
            <div className="border-t border-green-200 pt-1.5 mt-1.5">
              <div className="flex justify-between text-xs font-bold text-green-800">
                <span>Total Cut</span>
                <span>₹{ondcFees.total_deductions.toFixed(0)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Swiggy Side — Red */}
        <div className="bg-gradient-to-b from-red-50 to-white p-3">
          <div className="text-center mb-2">
            <div className="text-[10px] font-bold text-red-600 uppercase tracking-wider">Swiggy</div>
            <div className="text-[9px] text-red-500/60">Old Path</div>
          </div>
          <div className="space-y-1.5">
            <FeeRow label={`Commission (${swiggyFees.commission_pct}%)`} amount={swiggyFees.commission} color="red" />
            <FeeRow label="GST on Commission" amount={swiggyFees.gst} color="red" />
            <div className="h-[1px]" /> {/* spacer to align */}
            <div className="h-[1px]" />
            <div className="h-[1px]" />
            <div className="border-t border-red-200 pt-1.5 mt-1.5">
              <div className="flex justify-between text-xs font-bold text-red-700">
                <span>Total Cut</span>
                <span className="line-through">₹{swiggyFees.total_deductions.toFixed(0)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* YOU RECEIVE comparison */}
      <div className="grid grid-cols-2 divide-x divide-gray-200 border-t border-gray-200">
        <div className="bg-green-100 px-3 py-2 text-center">
          <div className="text-[9px] text-green-700 font-semibold uppercase">You Receive</div>
          <div className="text-lg font-black text-green-800">₹{ondcFees.merchant_receives.toFixed(0)}</div>
        </div>
        <div className="bg-red-100 px-3 py-2 text-center">
          <div className="text-[9px] text-red-600 font-semibold uppercase">You'd Receive</div>
          <div className="text-lg font-black text-red-700 line-through opacity-60">₹{swiggyFees.merchant_receives.toFixed(0)}</div>
        </div>
      </div>

      {/* Savings Banner */}
      <div className="bg-gradient-to-r from-green-500 to-emerald-600 px-3 py-2.5 text-center">
        <div className="text-white text-sm font-black">
          You SAVE ₹{savingsVsSwiggy.toFixed(0)} per order! ({savingsPercent}%)
        </div>
        <div className="text-green-100 text-[10px] mt-0.5">
          ~₹{monthlyProjection.toLocaleString('en-IN')}/month · ~₹{yearlyProjection.toLocaleString('en-IN')}/year
        </div>
      </div>
    </div>
  );
}

function FeeRow({ label, amount, pct, color }: { label: string; amount: number; pct?: number; color: 'green' | 'red' }) {
  const textColor = color === 'green' ? 'text-green-700' : 'text-red-600';
  const amountColor = color === 'green' ? 'text-green-800' : 'text-red-700';

  return (
    <div className="flex justify-between items-center">
      <span className={`text-[10px] ${textColor} leading-tight`}>
        {label}{pct !== undefined ? ` ${pct}%` : ''}
      </span>
      <span className={`text-[11px] font-semibold ${amountColor} tabular-nums`}>
        ₹{amount.toFixed(0)}
      </span>
    </div>
  );
}

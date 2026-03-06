import type { ONDCRegistration } from '../types';

interface Props {
  registration: ONDCRegistration;
}

export default function ONDCRegistrationCard({ registration }: Props) {
  return (
    <div className="rounded-xl overflow-hidden my-2 shadow-md border border-green-200">
      {/* Header with celebration gradient */}
      <div className="bg-gradient-to-r from-[#075e54] to-[#128c7e] px-4 py-3 flex items-center justify-between">
        <div>
          <div className="text-white font-bold text-sm">{registration.shop_name}</div>
          <div className="text-green-200 text-[10px]">ONDC Seller ID: {registration.ondc_seller_id}</div>
        </div>
        <div className="bg-green-400 text-green-900 text-[10px] font-black px-2.5 py-1 rounded-full uppercase tracking-wider animate-pulse">
          LIVE
        </div>
      </div>

      <div className="bg-white p-3 space-y-3">
        {/* Domain Badge */}
        <div className="flex items-center gap-2">
          <div className="bg-blue-50 border border-blue-200 rounded-lg px-2.5 py-1.5 flex items-center gap-1.5">
            <span className="text-blue-600 text-xs font-mono font-bold">{registration.ondc_domain}</span>
            <span className="text-blue-400 text-[10px]">—</span>
            <span className="text-blue-600 text-xs">{registration.ondc_domain_label}</span>
          </div>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-2 gap-2">
          <InfoPill icon="🚚" label="Delivery" value={`${registration.serviceability_radius} km`} />
          <InfoPill icon="⏰" label="Hours" value={registration.operating_hours} />
          <InfoPill icon="💳" label="Payment" value={registration.payment_modes.join(', ')} />
          <InfoPill icon="📦" label="Fulfillment" value={registration.fulfillment_types.join(', ')} />
        </div>

        {/* Discoverable On */}
        <div>
          <div className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider mb-1.5">Discoverable on</div>
          <div className="flex flex-wrap gap-1.5">
            {registration.discoverable_on.map((app) => (
              <span
                key={app}
                className="inline-flex items-center gap-1 bg-gray-50 border border-gray-200 rounded-full px-2.5 py-1 text-[10px] font-medium text-gray-700"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                {app}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-green-50 border-t border-green-100 px-3 py-1.5 flex items-center justify-center gap-1">
        <span className="text-[10px] text-green-700 font-medium">ONDC Compliant</span>
        <span className="text-green-600 text-xs">✓</span>
        <span className="text-[10px] text-green-500 mx-1">|</span>
        <span className="text-[10px] text-green-600 font-medium">Powered by Vyapari.ai</span>
      </div>
    </div>
  );
}

function InfoPill({ icon, label, value }: { icon: string; label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-lg px-2.5 py-1.5">
      <div className="flex items-center gap-1 mb-0.5">
        <span className="text-xs">{icon}</span>
        <span className="text-[9px] text-gray-400 font-semibold uppercase">{label}</span>
      </div>
      <div className="text-[11px] text-gray-800 font-medium">{value}</div>
    </div>
  );
}

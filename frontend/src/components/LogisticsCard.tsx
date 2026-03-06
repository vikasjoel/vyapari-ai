import type { LogisticsInfo } from '../types';

interface Props {
  logistics: LogisticsInfo;
}

const STEPS = ['Assigned', 'Picking Up', 'On the Way', 'Delivered'];

export default function LogisticsCard({ logistics }: Props) {
  // For simulation, randomly pick a progress step (mostly early stages)
  const currentStep = 1;

  return (
    <div className="rounded-lg border border-blue-200 bg-blue-50/50 p-2.5 my-1.5">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-sm">🚚</span>
          <div>
            <span className="text-xs font-semibold text-gray-800">{logistics.partner}</span>
            <span className="text-gray-400 mx-1">·</span>
            <span className="text-xs text-gray-600">{logistics.rider_name}</span>
          </div>
        </div>
        <div className="text-[10px] bg-blue-100 text-blue-700 font-semibold px-2 py-0.5 rounded-full">
          {logistics.eta_minutes} min · {logistics.distance_km} km
        </div>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center gap-0.5">
        {STEPS.map((step, i) => (
          <div key={step} className="flex-1 flex items-center">
            <div className="flex flex-col items-center w-full">
              <div className={`w-full h-1 rounded-full ${
                i <= currentStep ? 'bg-blue-500' : 'bg-gray-200'
              }`} />
              <span className={`text-[8px] mt-0.5 ${
                i <= currentStep ? 'text-blue-600 font-semibold' : 'text-gray-400'
              }`}>
                {step}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Cost */}
      <div className="flex justify-end mt-1">
        <span className="text-[10px] text-gray-500">Delivery: ₹{logistics.cost}</span>
      </div>
    </div>
  );
}

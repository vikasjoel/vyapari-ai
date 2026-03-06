import { useState } from 'react';
import type { AgentActivity } from '../types';

interface Props {
  activity: AgentActivity | null;
}

export default function AgentActivityPanel({ activity }: Props) {
  const [expanded, setExpanded] = useState(false);

  if (!activity) return null;

  return (
    <div className="border-t border-gray-200 bg-gray-50">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-2 text-xs text-gray-500 hover:bg-gray-100"
      >
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          Agent Activity
          {activity.supervisorRoutedTo && (
            <span className="text-gray-400">
              — {activity.supervisorRoutedTo}
            </span>
          )}
        </span>
        <span>{expanded ? '▼' : '▶'}</span>
      </button>

      {expanded && (
        <div className="px-4 pb-3 space-y-2 text-xs">
          {/* Routing */}
          {activity.supervisorRoutedTo && (
            <div className="flex items-center gap-2">
              <span className="text-gray-400 w-20">Routed to</span>
              <span className="bg-blue-50 text-blue-600 px-2 py-0.5 rounded">
                {activity.supervisorRoutedTo}
              </span>
            </div>
          )}

          {/* Tools called */}
          {activity.toolsCalled && activity.toolsCalled.length > 0 && (
            <div className="flex items-start gap-2">
              <span className="text-gray-400 w-20 mt-0.5">Tools</span>
              <div className="flex flex-wrap gap-1">
                {activity.toolsCalled.map((t, i) => (
                  <span key={i} className="bg-purple-50 text-purple-600 px-2 py-0.5 rounded">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Intent */}
          {activity.intent && (
            <div className="flex items-center gap-2">
              <span className="text-gray-400 w-20">Intent</span>
              <span className="bg-orange-50 text-orange-600 px-2 py-0.5 rounded font-mono">
                {activity.intent}
              </span>
            </div>
          )}

          {/* Slots */}
          {activity.slotsExtracted && Object.keys(activity.slotsExtracted).length > 0 && (
            <div className="flex items-start gap-2">
              <span className="text-gray-400 w-20 mt-0.5">Slots</span>
              <div className="flex flex-wrap gap-1">
                {Object.entries(activity.slotsExtracted).map(([k, v]) => (
                  <span key={k} className="bg-green-50 text-green-700 px-2 py-0.5 rounded">
                    {k}: {v}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Performance */}
          <div className="flex items-center gap-4 pt-1 border-t border-gray-200">
            {activity.latencyMs && (
              <span className="text-gray-400">
                ⏱ {activity.latencyMs}ms
              </span>
            )}
            {activity.tokensUsed && (
              <span className="text-gray-400">
                🔤 {activity.tokensUsed} tokens
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

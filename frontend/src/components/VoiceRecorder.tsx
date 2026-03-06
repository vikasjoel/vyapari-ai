import { useState } from 'react';
import { startRecording, stopRecording, isRecording } from '../services/audioUtils';

interface Props {
  onVoiceRecorded: (blob: Blob) => void;
  onSampleCommand: (command: string) => void;
  disabled?: boolean;
}

const SAMPLE_COMMANDS = [
  { id: 'price-update', label: 'Amul ka rate 32 karo', emoji: '💰' },
  { id: 'out-of-stock', label: 'Atta khatam ho gaya', emoji: '❌' },
  { id: 'add-product', label: 'Maggi add karo, 14 rupees', emoji: '➕' },
  { id: 'catalog-query', label: 'Kitne products hain?', emoji: '📋' },
];

export default function VoiceRecorder({ onVoiceRecorded, onSampleCommand, disabled }: Props) {
  const [recording, setRecording] = useState(false);

  const toggleRecording = async () => {
    if (recording || isRecording()) {
      const blob = await stopRecording();
      setRecording(false);
      onVoiceRecorded(blob);
    } else {
      await startRecording();
      setRecording(true);
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-3">
      <div className="text-xs font-semibold text-gray-500 uppercase mb-2">
        Hindi Voice Commands
      </div>

      {/* Record button */}
      <button
        onClick={toggleRecording}
        disabled={disabled}
        className={`w-full py-3 rounded-lg text-center font-medium transition-all disabled:opacity-50 ${
          recording
            ? 'bg-red-500 text-white animate-pulse'
            : 'bg-green-600 text-white hover:bg-green-700'
        }`}
      >
        {recording ? (
          <span>🔴 Recording... Tap to stop</span>
        ) : (
          <span>🎤 Hold to record Hindi voice</span>
        )}
      </button>

      {/* Pre-recorded sample commands */}
      <div className="mt-3">
        <div className="text-xs text-gray-400 mb-1.5">Or try pre-recorded commands:</div>
        <div className="grid grid-cols-2 gap-1.5">
          {SAMPLE_COMMANDS.map((cmd) => (
            <button
              key={cmd.id}
              onClick={() => onSampleCommand(cmd.id)}
              disabled={disabled}
              className="bg-gray-50 border border-gray-200 rounded-lg px-2 py-2 text-left hover:bg-gray-100 transition-colors disabled:opacity-50"
            >
              <div className="text-xs text-gray-700">
                <span className="mr-1">{cmd.emoji}</span>
                {cmd.label}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

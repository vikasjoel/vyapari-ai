import { useRef } from 'react';

interface Props {
  onPhotoSelect: (file: File) => void;
  onSampleSelect: (sampleName: string) => void;
  disabled?: boolean;
}

const SAMPLE_PHOTOS = [
  { id: 'snacks-shelf', label: 'Snacks Shelf', emoji: '🍪' },
  { id: 'dairy-shelf', label: 'Dairy Shelf', emoji: '🥛' },
  { id: 'grocery-shelf', label: 'Grocery Shelf', emoji: '🛒' },
];

export default function PhotoUpload({ onPhotoSelect, onSampleSelect, disabled }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onPhotoSelect(file);
      e.target.value = '';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-3">
      <div className="text-xs font-semibold text-gray-500 uppercase mb-2">Upload Shelf Photo</div>

      {/* File upload */}
      <button
        onClick={() => inputRef.current?.click()}
        disabled={disabled}
        className="w-full bg-green-50 border-2 border-dashed border-green-300 rounded-lg py-3 text-center hover:bg-green-100 transition-colors disabled:opacity-50"
      >
        <div className="text-2xl mb-1">📸</div>
        <div className="text-sm text-green-700 font-medium">Tap to upload photo</div>
        <div className="text-xs text-gray-400">JPG, PNG up to 5MB</div>
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="hidden"
      />

      {/* Sample photos for judges */}
      <div className="mt-3">
        <div className="text-xs text-gray-400 mb-1.5">Or try sample photos:</div>
        <div className="flex gap-2">
          {SAMPLE_PHOTOS.map((sample) => (
            <button
              key={sample.id}
              onClick={() => onSampleSelect(sample.id)}
              disabled={disabled}
              className="flex-1 bg-gray-50 border border-gray-200 rounded-lg py-2 text-center hover:bg-gray-100 transition-colors disabled:opacity-50"
            >
              <div className="text-lg">{sample.emoji}</div>
              <div className="text-[10px] text-gray-600">{sample.label}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

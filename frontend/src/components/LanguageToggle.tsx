import type { Language } from '../types';

interface Props {
  current: Language;
  onChange: (lang: Language) => void;
}

const LANGUAGES: { code: Language; label: string }[] = [
  { code: 'hi', label: 'हिंदी' },
  { code: 'en', label: 'EN' },
  { code: 'ta', label: 'தமிழ்' },
  { code: 'te', label: 'తెలుగు' },
];

export default function LanguageToggle({ current, onChange }: Props) {
  return (
    <div className="flex gap-0.5 bg-[#064e48] rounded-lg p-0.5">
      {LANGUAGES.map((lang) => (
        <button
          key={lang.code}
          onClick={() => onChange(lang.code)}
          className={`px-2 py-0.5 rounded text-xs font-medium transition-colors ${
            current === lang.code
              ? 'bg-white text-[#075e54]'
              : 'text-green-100 hover:text-white'
          }`}
        >
          {lang.label}
        </button>
      ))}
    </div>
  );
}

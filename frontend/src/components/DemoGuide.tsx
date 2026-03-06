import { useState, useEffect } from 'react';

interface Props {
  onDismiss: () => void;
}

interface Step {
  num: number;
  emoji: string;
  title: string;
  title_hi: string;
  desc: string;
  desc_hi: string;
  highlightSelector?: string;
  action?: string;
  autoTrigger?: boolean;
}

const STEPS: Step[] = [
  {
    num: 1,
    emoji: '🏪',
    title: 'Choose a store type',
    title_hi: 'अपनी दुकान का प्रकार चुनें',
    desc: 'Select Kirana, Restaurant, Sweet Shop, or Bakery',
    desc_hi: 'किराना, रेस्टोरेंट, मिठाई की दुकान, या बेकरी चुनें',
    highlightSelector: '.store-type-cards',
  },
  {
    num: 2,
    emoji: '💬',
    title: 'Chat in Hindi to register',
    title_hi: 'हिंदी में चैट करें',
    desc: 'Try: "Main Ramesh hoon, Delhi mein kirana store hai"',
    desc_hi: 'कोशिश करें: "मैं रमेश हूं, दिल्ली में किराना स्टोर है"',
    highlightSelector: '.chat-input',
  },
  {
    num: 3,
    emoji: '📦',
    title: 'Build your catalog',
    title_hi: 'अपनी सूची बनाएं',
    desc: 'Select products from template or upload shelf photo',
    desc_hi: 'टेम्पलेट से उत्पाद चुनें या शेल्फ की फोटो अपलोड करें',
    highlightSelector: '.template-catalog-button',
  },
  {
    num: 4,
    emoji: '🛒',
    title: 'See buyer view',
    title_hi: 'खरीदार का नज़रिया देखें',
    desc: 'Experience how customers discover your ONDC store',
    desc_hi: 'ग्राहक आपकी ONDC दुकान कैसे खोजते हैं, देखें',
    highlightSelector: '.buyer-sim-button',
  },
  {
    num: 5,
    emoji: '📋',
    title: 'Receive an order',
    title_hi: 'एक ऑर्डर प्राप्त करें',
    desc: 'A simulated order will arrive via ONDC',
    desc_hi: 'ONDC के माध्यम से एक नकली ऑर्डर आएगा',
    autoTrigger: true,
    action: 'simulate_order',
  },
  {
    num: 6,
    emoji: '📊',
    title: 'Check morning brief',
    title_hi: 'सुबह की रिपोर्ट देखें',
    desc: 'See business stats, stock alerts, and demand forecasts',
    desc_hi: 'व्यापार आंकड़े, स्टॉक अलर्ट और मांग पूर्वानुमान देखें',
    autoTrigger: true,
    action: 'morning_brief',
  },
];

export default function DemoGuide({ onDismiss }: Props) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [language] = useState<'hi' | 'en'>('hi');

  useEffect(() => {
    // Check if user wants demo mode
    const urlParams = new URLSearchParams(window.location.search);
    const demoMode = urlParams.get('demo');
    if (demoMode === 'true') {
      setIsActive(true);
    }

    // Check localStorage for first visit
    const hasSeenDemo = localStorage.getItem('vyapari_demo_seen');
    if (!hasSeenDemo) {
      setIsActive(true);
      localStorage.setItem('vyapari_demo_seen', 'true');
    }
  }, []);

  const step = STEPS[currentStep];

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);

      // Auto-trigger actions
      const nextStep = STEPS[currentStep + 1];
      if (nextStep.autoTrigger && nextStep.action) {
        setTimeout(() => {
          triggerAction(nextStep.action!);
        }, 1000);
      }
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    setIsActive(false);
    onDismiss();
  };

  const handleSkip = () => {
    localStorage.setItem('vyapari_demo_seen', 'true');
    setIsActive(false);
    onDismiss();
  };

  const triggerAction = (action: string) => {
    // Trigger actions based on step
    if (action === 'simulate_order') {
      // Simulate order via API or trigger in chat
      console.log('Triggering simulated order...');
      // This would integrate with the simulate API endpoint
    } else if (action === 'morning_brief') {
      // Trigger morning brief generation
      console.log('Triggering morning brief...');
      // This would integrate with the intelligence API
    }
  };

  const getSpotlightPosition = () => {
    if (!step.highlightSelector) return null;

    const element = document.querySelector(step.highlightSelector);
    if (!element) return null;

    const rect = element.getBoundingClientRect();
    return {
      top: rect.top,
      left: rect.left,
      width: rect.width,
      height: rect.height,
    };
  };

  if (!isActive) return null;

  const spotlight = getSpotlightPosition();
  const isHindi = language === 'hi';

  return (
    <>
      {/* Dark overlay */}
      <div className="fixed inset-0 bg-black/70 z-[100] transition-opacity" />

      {/* Spotlight circle */}
      {spotlight && (
        <div
          className="fixed z-[101] rounded-xl pointer-events-none transition-all duration-300"
          style={{
            top: spotlight.top - 8,
            left: spotlight.left - 8,
            width: spotlight.width + 16,
            height: spotlight.height + 16,
            boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.7)',
            border: '3px solid #f97316',
          }}
        />
      )}

      {/* Guide Card */}
      <div className="fixed bottom-4 left-4 right-4 md:bottom-8 md:left-auto md:right-8 md:w-96 z-[102] animate-slide-up">
        <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-2xl overflow-hidden border-2 border-[#f97316]/30">
          {/* Progress Bar */}
          <div className="bg-[#1a365d] px-4 py-2">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-semibold text-white">
                {isHindi ? 'डेमो गाइड' : 'Demo Guide'}
              </span>
              <span className="text-xs text-gray-300">
                {currentStep + 1} / {STEPS.length}
              </span>
            </div>
            <div className="h-1.5 bg-white/20 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-[#f97316] to-[#ea580c] transition-all duration-300"
                style={{ width: `${((currentStep + 1) / STEPS.length) * 100}%` }}
              />
            </div>
          </div>

          {/* Content */}
          <div className="p-5">
            <div className="flex items-start gap-3 mb-4">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#f97316] to-[#ea580c] flex items-center justify-center text-2xl flex-shrink-0 shadow-lg">
                {step.emoji}
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-gray-900">
                  {isHindi ? step.title_hi : step.title}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  {isHindi ? step.desc_hi : step.desc}
                </p>
              </div>
            </div>

            {/* Step-specific hints */}
            {step.autoTrigger && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 mb-4">
                <p className="text-xs text-blue-700">
                  {isHindi
                    ? '⚡ यह स्टेप अपने आप चलेगा'
                    : '⚡ This step will trigger automatically'}
                </p>
              </div>
            )}

            {/* Navigation */}
            <div className="flex items-center justify-between gap-2">
              <button
                onClick={handleSkip}
                className="text-sm text-gray-500 hover:text-gray-700 font-medium"
              >
                {isHindi ? 'छोड़ें' : 'Skip'}
              </button>
              <div className="flex items-center gap-2">
                {currentStep > 0 && (
                  <button
                    onClick={handlePrevious}
                    className="px-4 py-2 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    ← {isHindi ? 'पिछला' : 'Back'}
                  </button>
                )}
                <button
                  onClick={handleNext}
                  className="px-5 py-2 bg-gradient-to-r from-[#f97316] to-[#ea580c] text-white font-bold rounded-lg hover:shadow-lg transition-all"
                >
                  {currentStep === STEPS.length - 1
                    ? isHindi
                      ? 'पूरा किया ✓'
                      : 'Complete ✓'
                    : isHindi
                    ? 'अगला →'
                    : 'Next →'}
                </button>
              </div>
            </div>
          </div>

          {/* Mini step indicators */}
          <div className="flex items-center justify-center gap-1.5 px-5 pb-4">
            {STEPS.map((_, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentStep(idx)}
                className={`h-1.5 rounded-full transition-all ${
                  idx === currentStep
                    ? 'w-6 bg-[#f97316]'
                    : idx < currentStep
                    ? 'w-1.5 bg-[#25d366]'
                    : 'w-1.5 bg-gray-300'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

/**
 * Error Handler Utility
 *
 * Centralized error handling with Hindi support
 */

import toast from 'react-hot-toast';

export interface ErrorMessages {
  hi: string;
  en: string;
}

// Common error messages
export const ERROR_MESSAGES: Record<string, ErrorMessages> = {
  network: {
    hi: 'इंटरनेट कनेक्शन की समस्या। कृपया फिर से प्रयास करें।',
    en: 'Network error. Please try again.',
  },
  api_error: {
    hi: 'कुछ गड़बड़ हो गई। कृपया फिर से प्रयास करें।',
    en: 'Something went wrong. Please try again.',
  },
  upload_failed: {
    hi: 'फोटो अपलोड नहीं हो सका। कृपया फिर से प्रयास करें।',
    en: 'Photo upload failed. Please try again.',
  },
  voice_failed: {
    hi: 'आवाज़ रिकॉर्ड नहीं हो सकी। कृपया फिर से प्रयास करें।',
    en: 'Voice recording failed. Please try again.',
  },
  catalog_load_failed: {
    hi: 'कैटलॉग लोड नहीं हो सका। कृपया फिर से प्रयास करें।',
    en: 'Failed to load catalog. Please try again.',
  },
  template_load_failed: {
    hi: 'टेम्पलेट लोड नहीं हो सका। कृपया फिर से प्रयास करें।',
    en: 'Failed to load template. Please try again.',
  },
  order_failed: {
    hi: 'ऑर्डर नहीं हो सका। कृपया फिर से प्रयास करें।',
    en: 'Order failed. Please try again.',
  },
  session_expired: {
    hi: 'सेशन समाप्त हो गया। कृपया नया सेशन शुरू करें।',
    en: 'Session expired. Please start a new session.',
  },
  agent_timeout: {
    hi: 'प्रतिक्रिया में देरी हो रही है। कृपया प्रतीक्षा करें या फिर से प्रयास करें।',
    en: 'Response taking longer than expected. Please wait or try again.',
  },
  invalid_input: {
    hi: 'अमान्य इनपुट। कृपया सही जानकारी दर्ज करें।',
    en: 'Invalid input. Please enter correct information.',
  },
};

// Success messages
export const SUCCESS_MESSAGES: Record<string, ErrorMessages> = {
  upload_success: {
    hi: '✅ फोटो अपलोड हो गई!',
    en: '✅ Photo uploaded!',
  },
  voice_success: {
    hi: '✅ आवाज़ रिकॉर्ड हो गई!',
    en: '✅ Voice recorded!',
  },
  catalog_saved: {
    hi: '✅ कैटलॉग सेव हो गया!',
    en: '✅ Catalog saved!',
  },
  order_placed: {
    hi: '✅ ऑर्डर सफलतापूर्वक हो गया!',
    en: '✅ Order placed successfully!',
  },
  registration_complete: {
    hi: '✅ ONDC पर रजिस्ट्रेशन पूरा हुआ!',
    en: '✅ ONDC registration complete!',
  },
};

// Show error toast
export function showError(
  errorKey: string,
  language: 'hi' | 'en' = 'hi',
  customMessage?: string
) {
  const message = customMessage || ERROR_MESSAGES[errorKey]?.[language] || ERROR_MESSAGES.api_error[language];

  toast.error(message, {
    duration: 4000,
    position: 'top-center',
    style: {
      background: '#ef4444',
      color: '#ffffff',
      fontWeight: '600',
      borderRadius: '12px',
      padding: '12px 20px',
      fontSize: '14px',
      fontFamily: language === 'hi' ? "'Noto Sans Devanagari', sans-serif" : "'Inter', sans-serif",
    },
    icon: '❌',
  });
}

// Show success toast
export function showSuccess(
  successKey: string,
  language: 'hi' | 'en' = 'hi',
  customMessage?: string
) {
  const message = customMessage || SUCCESS_MESSAGES[successKey]?.[language] || '✅ Success!';

  toast.success(message, {
    duration: 3000,
    position: 'top-center',
    style: {
      background: '#10b981',
      color: '#ffffff',
      fontWeight: '600',
      borderRadius: '12px',
      padding: '12px 20px',
      fontSize: '14px',
      fontFamily: language === 'hi' ? "'Noto Sans Devanagari', sans-serif" : "'Inter', sans-serif",
    },
    icon: '✅',
  });
}

// Show info toast
export function showInfo(message: string, language: 'hi' | 'en' = 'hi') {
  toast(message, {
    duration: 3000,
    position: 'top-center',
    style: {
      background: '#3b82f6',
      color: '#ffffff',
      fontWeight: '600',
      borderRadius: '12px',
      padding: '12px 20px',
      fontSize: '14px',
      fontFamily: language === 'hi' ? "'Noto Sans Devanagari', sans-serif" : "'Inter', sans-serif",
    },
    icon: 'ℹ️',
  });
}

// Handle API errors
export function handleApiError(error: unknown, language: 'hi' | 'en' = 'hi') {
  console.error('API Error:', error);

  if (error instanceof Error) {
    // Network error
    if (error.message.includes('fetch') || error.message.includes('network')) {
      showError('network', language);
      return;
    }

    // Timeout error
    if (error.message.includes('timeout')) {
      showError('agent_timeout', language);
      return;
    }
  }

  // Generic error
  showError('api_error', language);
}

// Loading toast (use with promise)
export function showLoading(message: string, language: 'hi' | 'en' = 'hi') {
  return toast.loading(message, {
    position: 'top-center',
    style: {
      background: '#1a365d',
      color: '#ffffff',
      fontWeight: '600',
      borderRadius: '12px',
      padding: '12px 20px',
      fontSize: '14px',
      fontFamily: language === 'hi' ? "'Noto Sans Devanagari', sans-serif" : "'Inter', sans-serif",
    },
  });
}

// Dismiss loading toast
export function dismissLoading(toastId: string) {
  toast.dismiss(toastId);
}

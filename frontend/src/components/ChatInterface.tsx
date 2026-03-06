import { useState, useRef, useEffect, useCallback } from 'react';
import type { ChatMessage, AgentActivity, Language, ONDCRegistration } from '../types';
import { sendMessage, uploadPhoto, sendVoice } from '../services/api';
import ChatBubble from './ChatBubble';
import PhotoUpload from './PhotoUpload';
import VoiceRecorder from './VoiceRecorder';
import AgentActivityPanel from './AgentActivityPanel';
import LanguageToggle from './LanguageToggle';
import DemoGuide from './DemoGuide';

interface Props {
  initialStoreType?: string;
  merchantId?: string;
  onMerchantRegistered?: (mid: string) => void;
  onOpenBuyerSim?: () => void;
  onOpenCatalog?: () => void;
  onOpenTemplate?: () => void;
  onReset?: () => void;
}

export default function ChatInterface({
  initialStoreType,
  merchantId: externalMerchantId,
  onMerchantRegistered,
  onOpenBuyerSim,
  onOpenCatalog,
  onOpenTemplate,
  onReset,
}: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [language, setLanguage] = useState<Language>('hi');
  const [lastActivity, setLastActivity] = useState<AgentActivity | null>(null);
  const [showGuide, setShowGuide] = useState(!initialStoreType);
  const [showMediaPanel, setShowMediaPanel] = useState<'none' | 'photo' | 'voice'>('none');
  const [merchantId, setMerchantId] = useState(externalMerchantId || '');
  const [hasSentInitial, setHasSentInitial] = useState(false);
  const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 1024);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Check if desktop
  useEffect(() => {
    const handleResize = () => {
      setIsDesktop(window.innerWidth >= 1024);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Sync external merchantId
  useEffect(() => {
    if (externalMerchantId) setMerchantId(externalMerchantId);
  }, [externalMerchantId]);

  const addMessage = useCallback(
    (role: 'user' | 'bot', content: string, extra?: Partial<ChatMessage>) => {
      const msg: ChatMessage = {
        id: crypto.randomUUID(),
        role,
        content,
        type: 'text',
        timestamp: new Date(),
        ...extra,
      };
      setMessages((prev) => [...prev, msg]);
      return msg;
    },
    []
  );

  // Helper to detect ONDC registration data in response
  const detectRegistrationData = (responseText: string, merchantIdFromApi?: string): ONDCRegistration | null => {
    // Look for registration-like patterns in the response
    if (!merchantIdFromApi) return null;
    if (!responseText.includes('ONDC') || !responseText.includes('register')) return null;

    // Check for common registration success patterns
    const hasSellerIdPattern = /ONDC-[A-F0-9]{8}/i.test(responseText);
    const hasSuccessPatterns = /(?:LIVE|register|बधाई|success)/i.test(responseText);

    if (hasSellerIdPattern && hasSuccessPatterns) {
      const sellerIdMatch = responseText.match(/ONDC-[A-F0-9]{8}/i);
      const domainMatch = responseText.match(/ONDC:RET(\d{2})/);
      const domainLabels: Record<string, string> = {
        '10': 'Grocery', '11': 'F&B', '12': 'Fashion',
        '14': 'Electronics', '16': 'Home & Kitchen', '18': 'Health & Wellness',
      };

      return {
        merchant_id: merchantIdFromApi,
        ondc_seller_id: sellerIdMatch?.[0] || `ONDC-${merchantIdFromApi.slice(0, 8).toUpperCase()}`,
        ondc_domain: domainMatch?.[0] || 'ONDC:RET10',
        ondc_domain_label: domainLabels[domainMatch?.[1] || '10'] || 'Grocery',
        shop_name: '', // Will be populated from context
        serviceability_radius: '3',
        operating_hours: '9:00 AM - 9:00 PM',
        discoverable_on: ['Paytm', 'Magicpin', 'Ola', 'myStore', 'ONDC Reference App'],
        fulfillment_types: ['delivery', 'pickup'],
        payment_modes: ['cash', 'upi'],
      };
    }

    return null;
  };

  // ── Send text message ──
  const handleSend = async (overrideText?: string) => {
    const text = overrideText || input.trim();
    if (!text || loading) return;

    if (!overrideText) setInput('');
    setShowMediaPanel('none');
    addMessage('user', text);
    setLoading(true);

    // If this is the first message to the agent and we have a store type,
    // prepend context so the agent knows the store type and starts onboarding
    let agentText = text;
    if (!sessionId && initialStoreType) {
      agentText = `I want to register my ${initialStoreType} store on ONDC. My name is ${text}`;
    }

    try {
      const data = await sendMessage(sessionId, agentText, language);
      setSessionId(data.session_id);
      setLastActivity(data.agent_activity as AgentActivity);

      // Track merchant_id from API response
      if (data.merchant_id && data.merchant_id !== merchantId) {
        setMerchantId(data.merchant_id);
        onMerchantRegistered?.(data.merchant_id);
      }

      // Detect registration card data
      const registration = detectRegistrationData(data.response, data.merchant_id);
      const extra: Partial<ChatMessage> = {
        agentActivity: data.agent_activity as AgentActivity,
      };
      if (registration) {
        extra.type = 'ondc_registration';
        extra.ondcRegistration = registration;
      }

      addMessage('bot', data.response, extra);
    } catch {
      const errorMsg = language === 'hi'
        ? 'कनेक्शन में समस्या आ रही है। कृपया दोबारा कोशिश करें। 🙏'
        : language === 'ta' ? 'இணைப்பு பிழை. மீண்டும் முயற்சிக்கவும். 🙏'
        : language === 'te' ? 'కనెక్షన్ లోపం. మళ్ళీ ప్రయత్నించండి. 🙏'
        : 'Connection error. Please try again. 🙏';
      addMessage('bot', errorMsg);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  // When store type is selected from landing page, show a rich welcome message then start agent
  useEffect(() => {
    if (initialStoreType && !hasSentInitial && !loading && messages.length === 0) {
      setHasSentInitial(true);

      const storeLabels: Record<string, { en: string; hi: string; emoji: string }> = {
        kirana: { en: 'Kirana Store', hi: 'किराना स्टोर', emoji: '🏪' },
        restaurant: { en: 'Restaurant', hi: 'रेस्टोरेंट', emoji: '🍛' },
        sweet_shop: { en: 'Sweet Shop', hi: 'मिठाई की दुकान', emoji: '🍬' },
        bakery: { en: 'Bakery', hi: 'बेकरी', emoji: '🧁' },
      };
      const store = storeLabels[initialStoreType] || storeLabels.other;

      // Show a rich welcome message from the bot immediately (no API call)
      const welcomeText = `🙏 नमस्ते! Vyapari.ai में आपका स्वागत है!

${store.emoji} आप अपनी **${store.hi}** को ONDC पर register करना चाहते हैं — बहुत बढ़िया फैसला!

💡 **ONDC पर आपको क्या मिलेगा:**
• Swiggy/Zomato पर 25-35% commission कटता है
• ONDC पर सिर्फ 3-5% fees — बाकी सब आपका!
• Paytm, Magicpin, Ola जैसे 5+ buyer apps पर दिखेंगे
• कोई lock-in नहीं — आपकी दुकान, आपका data

📋 **मुझे बस कुछ details चाहिए:**
  1. आपका नाम
  2. दुकान का नाम
  3. Location (area, city)
  4. Mobile number
  5. Operating hours & delivery radius

चलिए शुरू करते हैं! 😊 **आपका शुभ नाम क्या है?**`;

      addMessage('bot', welcomeText);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialStoreType, hasSentInitial]);

  // ── Upload photo ──
  const handlePhotoSelect = async (file: File) => {
    setShowMediaPanel('none');
    const url = URL.createObjectURL(file);
    addMessage('user', 'Photo uploaded', { type: 'photo', photoUrl: url });
    setLoading(true);

    try {
      const data = await uploadPhoto(sessionId, file, undefined, language);
      setSessionId(data.session_id);
      setLastActivity(data.agent_activity as AgentActivity);
      if (data.merchant_id && data.merchant_id !== merchantId) {
        setMerchantId(data.merchant_id);
        onMerchantRegistered?.(data.merchant_id);
      }
      addMessage('bot', data.response, {
        agentActivity: data.agent_activity as AgentActivity,
      });
    } catch {
      const errorMsg = language === 'hi'
        ? 'फोटो अपलोड नहीं हो पाई। कृपया दोबारा कोशिश करें। 📸'
        : 'Photo upload failed. Please try again. 📸';
      addMessage('bot', errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleSamplePhoto = async (sampleName: string) => {
    setShowMediaPanel('none');
    addMessage('user', `Sample photo: ${sampleName}`);
    setLoading(true);

    try {
      const data = await sendMessage(
        sessionId,
        `I'm sending a sample shelf photo (${sampleName}). Please analyze it and create a product catalog.`,
        language
      );
      setSessionId(data.session_id);
      setLastActivity(data.agent_activity as AgentActivity);
      if (data.merchant_id && data.merchant_id !== merchantId) {
        setMerchantId(data.merchant_id);
        onMerchantRegistered?.(data.merchant_id);
      }
      addMessage('bot', data.response, {
        agentActivity: data.agent_activity as AgentActivity,
      });
    } catch {
      const errorMsg = language === 'hi'
        ? 'फोटो प्रोसेस नहीं हो पाई। कृपया दोबारा कोशिश करें।'
        : 'Sample photo processing failed. Please try again.';
      addMessage('bot', errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // ── Voice recording ──
  const handleVoiceRecorded = async (blob: Blob) => {
    setShowMediaPanel('none');
    addMessage('user', '🎤 Voice message sent');
    setLoading(true);

    try {
      const data = await sendVoice(sessionId, blob, undefined, language);
      setSessionId(data.session_id);
      setLastActivity(data.agent_activity as AgentActivity);
      if (data.merchant_id && data.merchant_id !== merchantId) {
        setMerchantId(data.merchant_id);
        onMerchantRegistered?.(data.merchant_id);
      }
      const response = data.transcript
        ? `🎤 Suna: "${data.transcript}"\n\n${data.response}`
        : data.response;
      addMessage('bot', response, {
        audioUrl: data.audio_url,
        agentActivity: data.agent_activity as AgentActivity,
      });
    } catch {
      const errorMsg = language === 'hi'
        ? 'वॉइस मैसेज प्रोसेस नहीं हो पाया। कृपया दोबारा कोशिश करें। 🎤'
        : 'Voice processing failed. Please try again. 🎤';
      addMessage('bot', errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleSampleCommand = async (commandId: string) => {
    setShowMediaPanel('none');
    const labels: Record<string, string> = {
      'price-update': 'Amul ka rate 32 karo',
      'out-of-stock': 'Atta khatam ho gaya',
      'add-product': 'Maggi add karo, 14 rupees',
      'catalog-query': 'Kitne products hain?',
    };
    const label = labels[commandId] || commandId;
    addMessage('user', `🎤 Voice: "${label}"`);
    setLoading(true);

    try {
      const data = await sendMessage(
        sessionId,
        `Merchant sent a voice command. Audio transcript: "${label}". Detect the intent and respond.`,
        language
      );
      setSessionId(data.session_id);
      setLastActivity(data.agent_activity as AgentActivity);
      if (data.merchant_id && data.merchant_id !== merchantId) {
        setMerchantId(data.merchant_id);
        onMerchantRegistered?.(data.merchant_id);
      }
      addMessage('bot', data.response, {
        agentActivity: data.agent_activity as AgentActivity,
      });
    } catch {
      const errorMsg = language === 'hi'
        ? 'वॉइस कमांड प्रोसेस नहीं हो पाया। कृपया दोबारा कोशिश करें। 🎤'
        : 'Voice command processing failed. Please try again. 🎤';
      addMessage('bot', errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // ── Reset session ──
  const handleReset = () => {
    setMessages([]);
    setSessionId(null);
    setLastActivity(null);
    setShowMediaPanel('none');
    setInput('');
    setShowGuide(true);
    setMerchantId('');
    setHasSentInitial(false);
    onReset?.();
  };

  const isDemoMode = new URLSearchParams(window.location.search).get('demo') === 'true';

  return (
    <div className="flex flex-col h-screen max-w-lg mx-auto bg-[#ece5dd]">
      {/* Demo Guide Overlay */}
      {showGuide && !initialStoreType && <DemoGuide onDismiss={() => setShowGuide(false)} />}

      {/* Header — WhatsApp green */}
      <div className="bg-[#075e54] text-white px-4 py-3 flex items-center justify-between shadow-md flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-[#25d366] flex items-center justify-center text-lg font-bold">
            V
          </div>
          <div>
            <div className="font-semibold text-sm flex items-center gap-2">
              <span>Vyapari.ai</span>
              {isDemoMode && (
                <span className="text-[9px] bg-[#f97316] px-1.5 py-0.5 rounded-full font-bold">
                  🎬 DEMO
                </span>
              )}
            </div>
            <div className="text-[10px] text-green-200">
              {loading ? 'typing...' : 'AI Commerce Copilot'}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <LanguageToggle current={language} onChange={setLanguage} />
          <button
            onClick={handleReset}
            className="text-xs bg-red-500/20 text-red-100 px-2 py-1 rounded hover:bg-red-500/40 transition-colors"
            title="Reset conversation"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Action bar — when merchant is registered */}
      {merchantId && (
        <div className="bg-[#064e3b] px-3 py-1.5 flex items-center gap-2 flex-shrink-0 border-b border-green-800">
          <div className="flex-1 flex items-center gap-1.5 overflow-x-auto">
            {onOpenTemplate && (
              <button
                onClick={onOpenTemplate}
                className="template-catalog-button flex items-center gap-1 bg-yellow-500/20 text-yellow-200 text-[10px] font-medium px-2.5 py-1 rounded-full hover:bg-yellow-500/30 transition-colors whitespace-nowrap border border-yellow-400/20"
              >
                <span>📋</span> Build Catalog
              </button>
            )}
            {onOpenBuyerSim && (
              <button
                onClick={onOpenBuyerSim}
                className="buyer-sim-button flex items-center gap-1 bg-blue-500/20 text-blue-200 text-[10px] font-medium px-2.5 py-1 rounded-full hover:bg-blue-500/30 transition-colors whitespace-nowrap border border-blue-400/20"
              >
                <span>🛒</span> {isDesktop ? 'Buyer View' : 'Buyer Simulator'}
              </button>
            )}
            {isDesktop && merchantId && (
              <button
                onClick={() => {
                  // Navigate to split-screen
                  window.location.hash = '#/split-screen';
                }}
                className="flex items-center gap-1 bg-purple-500/20 text-purple-200 text-[10px] font-medium px-2.5 py-1 rounded-full hover:bg-purple-500/30 transition-colors whitespace-nowrap border border-purple-400/20"
              >
                <span>⚡</span> Split-Screen Demo
              </button>
            )}
            {onOpenCatalog && (
              <button
                onClick={onOpenCatalog}
                className="flex items-center gap-1 bg-green-500/20 text-green-200 text-[10px] font-medium px-2.5 py-1 rounded-full hover:bg-green-500/30 transition-colors whitespace-nowrap border border-green-400/20"
              >
                <span>🏪</span> ONDC Store
              </button>
            )}
          </div>
          <span className="text-[9px] text-green-400/60 tabular-nums">ID: {merchantId.slice(0, 8)}</span>
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
        {messages.length === 0 && !initialStoreType && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500 bg-white/70 rounded-xl px-6 py-4 shadow-sm">
              <div className="text-4xl mb-2">🙏</div>
              <div className="font-semibold text-gray-700">
                {language === 'hi' ? 'Namaste!' : language === 'ta' ? 'வணக்கம்!' : language === 'te' ? 'నమస్కారం!' : 'Welcome!'}
              </div>
              <div className="text-sm mt-1">
                {language === 'hi' ? 'ONDC par apni dukaan shuru karne ke liye hello bolein'
                  : language === 'ta' ? 'ONDC இல் உங்கள் கடையை தொடங்க வணக்கம் சொல்லுங்கள்'
                  : language === 'te' ? 'ONDC లో మీ దుకాణాన్ని ప్రారంభించడానికి హలో చెప్పండి'
                  : 'Say hello to start onboarding your shop on ONDC'}
              </div>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <ChatBubble key={msg.id} message={msg} language={language} />
        ))}

        {loading && (
          <div className="flex justify-start mb-2">
            <div className="bg-white rounded-lg rounded-bl-none px-4 py-3 shadow-sm">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-xs text-gray-500 ml-1">
                  {language === 'hi' ? 'Vyapari soch raha hai...' : 'Vyapari is thinking...'}
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Agent Activity Panel */}
      <AgentActivityPanel activity={lastActivity} />

      {/* Media panels */}
      {showMediaPanel === 'photo' && (
        <div className="px-3 pb-2">
          <PhotoUpload
            onPhotoSelect={handlePhotoSelect}
            onSampleSelect={handleSamplePhoto}
            disabled={loading}
          />
        </div>
      )}
      {showMediaPanel === 'voice' && (
        <div className="px-3 pb-2">
          <VoiceRecorder
            onVoiceRecorded={handleVoiceRecorded}
            onSampleCommand={handleSampleCommand}
            disabled={loading}
          />
        </div>
      )}

      {/* Quick Action Buttons */}
      {merchantId && (
        <div className="bg-white border-t border-gray-200 px-3 py-2 flex items-center gap-2 overflow-x-auto flex-shrink-0" style={{ scrollbarWidth: 'none' }}>
          <button
            onClick={onOpenTemplate}
            className="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-xs font-medium rounded-full hover:shadow-md transition-all"
          >
            <span>📦</span>
            <span>{language === 'hi' ? 'Add Products' : 'Add Products'}</span>
          </button>
          <button
            onClick={() => {
              // Trigger simulated order
              setInput(language === 'hi' ? 'Ek order simulate karo' : 'Simulate an order');
              handleSend();
            }}
            className="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-orange-500 to-orange-600 text-white text-xs font-medium rounded-full hover:shadow-md transition-all"
          >
            <span>📋</span>
            <span>{language === 'hi' ? 'View Orders' : 'View Orders'}</span>
          </button>
          <button
            onClick={() => {
              // Trigger morning brief
              setInput(language === 'hi' ? 'Aaj ka business report dikhao' : 'Show today\'s business report');
              handleSend();
            }}
            className="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-green-500 to-green-600 text-white text-xs font-medium rounded-full hover:shadow-md transition-all"
          >
            <span>📊</span>
            <span>{language === 'hi' ? 'Business Report' : 'Business Report'}</span>
          </button>
          {onReset && (
            <button
              onClick={onReset}
              className="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-gray-500 to-gray-600 text-white text-xs font-medium rounded-full hover:shadow-md transition-all"
            >
              <span>🔄</span>
              <span>{language === 'hi' ? 'Reset Demo' : 'Reset Demo'}</span>
            </button>
          )}
        </div>
      )}

      {/* Input bar — WhatsApp style */}
      <div className="bg-[#f0f0f0] px-2 py-2 flex items-center gap-2 flex-shrink-0">
        {/* Photo button */}
        <button
          onClick={() => setShowMediaPanel(showMediaPanel === 'photo' ? 'none' : 'photo')}
          className={`p-2 rounded-full transition-colors ${
            showMediaPanel === 'photo' ? 'bg-green-600 text-white' : 'text-gray-500 hover:bg-gray-200'
          }`}
          title="Upload photo"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </button>

        {/* Text input */}
        <div className="flex-1 relative">
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={language === 'hi' ? 'Message type karein...' : language === 'ta' ? 'செய்தி தட்டச்சு செய்யுங்கள்...' : language === 'te' ? 'సందేశం టైప్ చేయండి...' : 'Type a message...'}
            disabled={loading}
            className="chat-input w-full bg-white rounded-full px-4 py-2 text-sm outline-none border border-gray-200 focus:border-green-400 disabled:opacity-50"
          />
        </div>

        {/* Voice button */}
        <button
          onClick={() => setShowMediaPanel(showMediaPanel === 'voice' ? 'none' : 'voice')}
          className={`p-2 rounded-full transition-colors ${
            showMediaPanel === 'voice' ? 'bg-green-600 text-white' : 'text-gray-500 hover:bg-gray-200'
          }`}
          title="Voice command"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </button>

        {/* Send button */}
        <button
          onClick={() => handleSend()}
          disabled={!input.trim() || loading}
          className="p-2 bg-[#25d366] text-white rounded-full hover:bg-[#20bd5a] transition-colors disabled:opacity-40"
          title="Send"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
    </div>
  );
}

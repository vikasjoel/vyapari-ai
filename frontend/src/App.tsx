import { useState, useEffect, lazy, Suspense } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import './index.css';

// Lazy load components for code splitting
const ChatInterface = lazy(() => import('./components/ChatInterface'));
const BuyerCatalogView = lazy(() => import('./components/BuyerCatalogView'));
const BuyerSimulator = lazy(() => import('./components/BuyerSimulator'));
const LandingPage = lazy(() => import('./components/LandingPage'));
const TemplateCatalog = lazy(() => import('./components/TemplateCatalog'));
const SplitScreen = lazy(() => import('./components/SplitScreen'));

// Loading fallback component
function PageLoader() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a365d] via-[#2d3748] to-[#1a202c] flex items-center justify-center">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-[#f97316] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-white font-medium">Loading...</p>
      </div>
    </div>
  );
}

type View = 'landing' | 'chat' | 'catalog' | 'buyer-sim' | 'template' | 'split-screen';
type Language = 'hi' | 'en' | 'ta' | 'te';

// Page transition variants
const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3 } },
  exit: { opacity: 0, y: -20, transition: { duration: 0.2 } },
};

function App() {
  const [view, setView] = useState<View>('landing');
  const [selectedStoreType, setSelectedStoreType] = useState('');
  const [merchantId, setMerchantId] = useState('');
  const [language, setLanguage] = useState<Language>('hi');

  // Load language from localStorage on mount
  useEffect(() => {
    const savedLanguage = localStorage.getItem('vyapari_language');
    if (savedLanguage && ['hi', 'en', 'ta', 'te'].includes(savedLanguage)) {
      setLanguage(savedLanguage as Language);
    }
  }, []);

  // Persist language to localStorage when changed
  useEffect(() => {
    localStorage.setItem('vyapari_language', language);
  }, [language]);

  // Check URL for catalog/buyer-sim/split-screen views
  useEffect(() => {
    const hash = window.location.hash;

    const catalogMatch = hash.match(/^#\/catalog\/(.+)$/);
    if (catalogMatch) {
      setMerchantId(catalogMatch[1]);
      setView('catalog');
      return;
    }

    const buyerMatch = hash.match(/^#\/buyer\/(.+)$/);
    if (buyerMatch) {
      setMerchantId(buyerMatch[1]);
      setView('buyer-sim');
      return;
    }

    // Split-screen view
    if (hash === '#/split-screen' && merchantId) {
      setView('split-screen');
      return;
    }

    // Also check path-based routing
    const path = window.location.pathname;
    const pathMatch = path.match(/^\/catalog\/(.+)$/);
    if (pathMatch) {
      setMerchantId(pathMatch[1]);
      setView('catalog');
    }
  }, [merchantId]);

  const handleLandingStart = (storeType: string) => {
    setSelectedStoreType(storeType);
    setView('chat');
  };

  const handleMerchantRegistered = (mid: string) => {
    setMerchantId(mid);
  };

  const handleOpenBuyerSim = () => {
    if (merchantId) {
      setView('buyer-sim');
    }
  };

  const handleOpenCatalog = () => {
    if (merchantId) {
      setView('catalog');
    }
  };

  const handleOpenTemplate = () => {
    if (merchantId && selectedStoreType) {
      setView('template');
    }
  };

  const handleBackToChat = () => {
    setView('chat');
  };

  const handleTemplateConfirm = (_count: number) => {
    // After template confirmation, go back to chat
    setView('chat');
  };

  const handleReset = () => {
    setView('landing');
    setSelectedStoreType('');
    setMerchantId('');
  };

  const handleLanguageChange = (newLanguage: string) => {
    setLanguage(newLanguage as Language);
  };

  return (
    <>
      {/* Toast notifications */}
      <Toaster position="top-center" />

      {/* Animated page transitions */}
      <Suspense fallback={<PageLoader />}>
        <AnimatePresence mode="wait">
        {view === 'catalog' && merchantId && (
          <motion.div key="catalog" variants={pageVariants} initial="initial" animate="animate" exit="exit">
            <BuyerCatalogView merchantId={merchantId} />
          </motion.div>
        )}

        {view === 'buyer-sim' && merchantId && (
          <motion.div key="buyer-sim" variants={pageVariants} initial="initial" animate="animate" exit="exit">
            <BuyerSimulator merchantId={merchantId} onBack={handleBackToChat} />
          </motion.div>
        )}

        {view === 'split-screen' && merchantId && (
          <motion.div key="split-screen" variants={pageVariants} initial="initial" animate="animate" exit="exit">
            <SplitScreen merchantId={merchantId} onBack={handleBackToChat} />
          </motion.div>
        )}

        {view === 'template' && merchantId && selectedStoreType && (
          <motion.div key="template" variants={pageVariants} initial="initial" animate="animate" exit="exit">
            <TemplateCatalog
              storeType={selectedStoreType}
              merchantId={merchantId}
              onConfirm={handleTemplateConfirm}
              onBack={handleBackToChat}
            />
          </motion.div>
        )}

        {view === 'landing' && (
          <motion.div key="landing" variants={pageVariants} initial="initial" animate="animate" exit="exit">
            <LandingPage
              onStart={handleLandingStart}
              language={language}
              onLanguageChange={handleLanguageChange}
            />
          </motion.div>
        )}

        {view === 'chat' && (
          <motion.div key="chat" variants={pageVariants} initial="initial" animate="animate" exit="exit">
            <ChatInterface
              initialStoreType={selectedStoreType}
              merchantId={merchantId}
              onMerchantRegistered={handleMerchantRegistered}
              onOpenBuyerSim={handleOpenBuyerSim}
              onOpenCatalog={handleOpenCatalog}
              onOpenTemplate={handleOpenTemplate}
              onReset={handleReset}
            />
          </motion.div>
        )}
        </AnimatePresence>
      </Suspense>
    </>
  );
}

export default App;

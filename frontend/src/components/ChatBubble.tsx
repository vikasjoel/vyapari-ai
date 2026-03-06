import type { ChatMessage } from '../types';
import ProductCard from './ProductCard';
import OrderCard from './OrderCard';
import ONDCRegistrationCard from './ONDCRegistrationCard';
import FeeBreakdownCard from './FeeBreakdownCard';
import LogisticsCard from './LogisticsCard';
import IntelligenceCard from './IntelligenceCard';
import { motion } from 'framer-motion';
import { format, isToday, isYesterday } from 'date-fns';
import type { Language } from '../types';

interface Props {
  message: ChatMessage;
  language?: Language;
}

export default function ChatBubble({ message, language = 'hi' }: Props) {
  const isUser = message.role === 'user';

  // Format timestamp intelligently
  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - timestamp.getTime()) / 60000);

    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes} min ago`;
    if (isToday(timestamp)) return format(timestamp, 'h:mm a');
    if (isYesterday(timestamp)) return `Yesterday ${format(timestamp, 'h:mm a')}`;
    return format(timestamp, 'MMM d, h:mm a');
  };

  // Intelligence cards are full-width and don't need bubble styling
  if (message.type === 'intelligence' && message.intelligenceData) {
    return (
      <motion.div
        className="mb-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <IntelligenceCard data={message.intelligenceData} language={language} />
        <div className="text-[10px] text-gray-400 text-center mt-2">
          {formatTimestamp(message.timestamp)}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-2`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <div
        className={`max-w-[85%] rounded-lg px-3 py-2 shadow-sm ${
          isUser
            ? 'bg-[#dcf8c6] text-gray-900 rounded-br-none'
            : 'bg-white text-gray-900 rounded-bl-none'
        }`}
      >
        {/* Photo message */}
        {message.type === 'photo' && message.photoUrl && (
          <img
            src={message.photoUrl}
            alt="Uploaded photo"
            className="rounded-md mb-1 max-h-48 object-cover"
          />
        )}

        {/* Text content */}
        {message.content && (
          <div className="text-sm whitespace-pre-wrap leading-relaxed">
            {message.content}
          </div>
        )}

        {/* ONDC Registration Card */}
        {message.ondcRegistration && (
          <ONDCRegistrationCard registration={message.ondcRegistration} />
        )}

        {/* Product cards */}
        {message.products && message.products.length > 0 && (
          <div className="mt-2 space-y-2">
            {message.products.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        )}

        {/* Order card */}
        {message.order && <OrderCard order={message.order} />}

        {/* ONDC Order with fee breakdown */}
        {message.ondcOrder && (
          <div className="mt-2">
            {message.ondcOrder.ondc_fees && message.ondcOrder.aggregator_comparison?.swiggy && (
              <FeeBreakdownCard
                orderTotal={message.ondcOrder.total}
                ondcFees={message.ondcOrder.ondc_fees}
                swiggyFees={message.ondcOrder.aggregator_comparison.swiggy}
                savingsVsSwiggy={message.ondcOrder.savings_vs_swiggy}
              />
            )}
            {message.ondcOrder.logistics && (
              <LogisticsCard logistics={message.ondcOrder.logistics} />
            )}
          </div>
        )}

        {/* Audio player */}
        {message.audioUrl && (
          <audio controls className="mt-2 w-full" src={message.audioUrl} />
        )}

        {/* Timestamp */}
        <div
          className={`text-[10px] mt-1 ${
            isUser ? 'text-green-800/60' : 'text-gray-400'
          } text-right`}
        >
          {formatTimestamp(message.timestamp)}
        </div>
      </div>
    </motion.div>
  );
}

export interface IntelligenceData {
  greeting: string;
  greeting_hi: string;
  date: string;
  stats: {
    orders_today: number;
    orders_yesterday: number;
    revenue_today: number;
    revenue_yesterday: number;
    amount_received: number;
    commission_saved: number;
  };
  stock_alerts?: Array<{
    product: string;
    product_hi: string;
    severity: 'high' | 'medium' | 'low';
    current_stock?: number;
    message?: string;
  }>;
  forecast?: {
    festival?: string;
    festival_hi?: string;
    predicted_demand: string;
    predicted_demand_hi: string;
    date?: string;
    suggested_stock_up?: string[];
  };
  suggestions?: Array<{
    text: string;
    text_hi: string;
    action?: string;
    icon?: string;
  }>;
  trending_products?: Array<{ name: string; name_hi: string }>;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'bot';
  content: string;
  type: 'text' | 'product_card' | 'order_card' | 'audio_url' | 'progress' | 'photo' | 'ondc_registration' | 'fee_breakdown' | 'intelligence';
  timestamp: Date;
  agentActivity?: AgentActivity;
  products?: Product[];
  order?: Order;
  ondcOrder?: ONDCOrder;
  audioUrl?: string;
  photoUrl?: string;
  ondcRegistration?: ONDCRegistration;
  intelligenceData?: IntelligenceData;
}

export interface AgentActivity {
  supervisorRoutedTo?: string;
  toolsCalled?: string[];
  intent?: string;
  params?: Record<string, string>;
  latencyMs?: number;
  tokensUsed?: number;
  slotsExtracted?: Record<string, string>;
  slotsMissing?: string[];
  memoryEvents?: string[];
}

export interface Product {
  product_id: string;
  name_en: string;
  name_hi: string;
  brand: string;
  variant: string;
  price: number;
  category: string;
  description_hi: string;
  image_url: string;
  available: boolean;
  confidence: number;
  source: string;
}

export interface Order {
  order_id: string;
  customer_name: string;
  buyer_app: string;
  items: OrderItem[];
  total: number;
  commission_ondc: number;
  commission_swiggy: number;
  savings: number;
  status: string;
  created_at: string;
}

export interface OrderItem {
  product_id: string;
  name: string;
  qty: number;
  price: number;
}

export interface ONDCFeeBreakdown {
  buyer_app: string;
  buyer_app_finder_fee: number;
  buyer_app_finder_fee_pct: number;
  seller_app_fee: number;
  seller_app_fee_pct: number;
  ondc_network_fee: number;
  ondc_network_fee_pct: number;
  logistics_cost: number;
  logistics_partner: string;
  logistics_eta: number;
  logistics_rider: string;
  logistics_distance_km: number;
  gst_on_fees: number;
  total_deductions: number;
  merchant_receives: number;
  commission_ondc: number;
}

export interface AggregatorComparison {
  platform: string;
  commission: number;
  commission_pct: number;
  gst: number;
  total_deductions: number;
  merchant_receives: number;
}

export interface LogisticsInfo {
  partner: string;
  rider_name: string;
  eta_minutes: number;
  distance_km: number;
  cost: number;
}

export interface ONDCOrder {
  order_id: string;
  customer_name: string;
  buyer_app: string;
  items: OrderItem[];
  total: number;
  ondc_fees: ONDCFeeBreakdown;
  aggregator_comparison: {
    swiggy: AggregatorComparison;
    zomato?: AggregatorComparison;
  };
  savings_vs_swiggy: number;
  savings_vs_zomato?: number;
  logistics: LogisticsInfo;
  status?: string;
}

export interface ONDCRegistration {
  merchant_id: string;
  ondc_seller_id: string;
  ondc_domain: string;
  ondc_domain_label: string;
  shop_name: string;
  serviceability_radius: string;
  operating_hours: string;
  discoverable_on: string[];
  fulfillment_types: string[];
  payment_modes: string[];
}

export interface StoreType {
  id: string;
  label_en: string;
  label_hi: string;
  emoji: string;
  ondc_domain: string;
}

export interface MerchantProfile {
  merchant_id: string;
  name: string;
  shop_name: string;
  shop_type: string;
  location: {
    city: string;
    area: string;
    state: string;
    pincode: string;
  };
  ondc_seller_id: string;
  product_count?: number;
}

export interface ChatResponse {
  session_id: string;
  responses: Array<{
    type: string;
    content: string;
    agent?: string;
  }>;
  agent_activity?: AgentActivity;
}

export type Language = 'hi' | 'en' | 'ta' | 'te';

export interface TemplateProduct {
  product_id: string;
  name: string;
  name_hi: string;
  brand: string;
  mrp: number;
  hsn_code: string;
  gst_rate: number;
  ondc_category: string;
  ondc_sub_category: string;
  veg: boolean;
  image_url: string;
  description: string;
  size_weight: string;
  popularity_score?: number; // For auto-selection based on popularity
  // Restaurant-specific
  prep_time?: string;
  serves?: number;
  cuisine?: string;
  meal_type?: string;
  // Sweet shop-specific
  shelf_life?: string;
  storage?: string;
  item_type?: string;
  per_kg_price?: number;
  // Bakery-specific
  eggless_available?: boolean;
}

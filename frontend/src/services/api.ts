import type { ONDCOrder, TemplateProduct } from '../types';

const API_BASE = '/api';

export async function sendMessage(
  sessionId: string | null,
  message: string,
  language: string = 'hi'
): Promise<{
  session_id: string;
  response: string;
  agent_activity?: Record<string, unknown>;
  merchant_id?: string;
}> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message, language }),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return res.json();
}

export async function uploadPhoto(
  sessionId: string | null,
  file: File,
  message?: string,
  language: string = 'hi'
): Promise<{
  session_id: string;
  response: string;
  agent_activity?: Record<string, unknown>;
  merchant_id?: string;
}> {
  const formData = new FormData();
  formData.append('photo', file);
  if (sessionId) formData.append('session_id', sessionId);
  if (message) formData.append('message', message);
  formData.append('language', language);

  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
  return res.json();
}

export async function sendVoice(
  sessionId: string | null,
  audioBlob: Blob,
  sampleCommand?: string,
  language: string = 'hi'
): Promise<{
  session_id: string;
  transcript?: string;
  response: string;
  audio_url?: string;
  agent_activity?: Record<string, unknown>;
  merchant_id?: string;
}> {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');
  if (sessionId) formData.append('session_id', sessionId);
  if (sampleCommand) formData.append('sample_command', sampleCommand);
  formData.append('language', language);

  const res = await fetch(`${API_BASE}/voice`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error(`Voice failed: ${res.status}`);
  return res.json();
}

export async function getCatalog(merchantId: string): Promise<{
  merchant: {
    shop_name: string;
    location: string;
    type: string;
    product_count: number;
  };
  products: Array<{
    product_id: string;
    name_hi: string;
    name_en: string;
    price: number;
    category: string;
    image_url: string;
    available: boolean;
  }>;
  categories: string[];
}> {
  const res = await fetch(`${API_BASE}/catalog/${merchantId}`);
  if (!res.ok) throw new Error(`Catalog failed: ${res.status}`);
  return res.json();
}

export async function simulateOrder(
  merchantId: string,
  items?: Array<{ product_id?: string; name: string; qty: number; price: number }>,
  buyerApp: string = 'Paytm'
): Promise<ONDCOrder> {
  const res = await fetch(`${API_BASE}/simulate-order/${merchantId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items: items || null, buyer_app: buyerApp }),
  });
  if (!res.ok) throw new Error(`Simulate order failed: ${res.status}`);
  return res.json();
}

export async function checkHealth(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function getTemplate(
  storeType: string,
  region: string = 'north'
): Promise<{
  store_type: string;
  label_en: string;
  label_hi: string;
  ondc_domain: string;
  region: string;
  total_products: number;
  categories: Record<string, TemplateProduct[]>;
}> {
  const res = await fetch(`${API_BASE}/template/${storeType}?region=${region}`);
  if (!res.ok) throw new Error(`Template failed: ${res.status}`);
  return res.json();
}

export async function confirmTemplate(
  merchantId: string,
  storeType: string,
  selectedIds: string[],
  priceOverrides: Record<string, number> = {}
): Promise<{
  status: string;
  merchant_id: string;
  store_type: string;
  products_saved: number;
  message: string;
}> {
  const res = await fetch(`${API_BASE}/template/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      merchant_id: merchantId,
      store_type: storeType,
      selected_product_ids: selectedIds,
      price_overrides: priceOverrides,
    }),
  });
  if (!res.ok) throw new Error(`Confirm template failed: ${res.status}`);
  return res.json();
}

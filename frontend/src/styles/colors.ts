/**
 * Vyapari.ai Color Theme
 *
 * Blue + Saffron color scheme for hackathon branding
 * WhatsApp green preserved for chat interface
 */

export const colors = {
  // Primary: Deep Blue
  primary: {
    deep_blue: '#1a365d',
    light_blue: '#2563eb',
    blue_dark: '#1a202c',
    blue_mid: '#2d3748',
  },

  // Accent: Saffron (Indian flag inspiration)
  accent: {
    saffron: '#f97316',
    saffron_dark: '#ea580c',
    saffron_light: '#fb923c',
  },

  // WhatsApp colors (for chat interface)
  whatsapp: {
    green: '#25d366',
    green_dark: '#075e54',
    bg_light: '#ece5dd',
    bubble_user: '#dcf8c6',
    bubble_bot: '#ffffff',
  },

  // Paytm colors (for buyer simulator)
  paytm: {
    blue: '#002e6e',
    light_blue: '#00baf2',
  },

  // UI colors
  ui: {
    error: '#ef4444',
    success: '#10b981',
    warning: '#f59e0b',
    info: '#3b82f6',
  },
} as const;

// Gradient presets
export const gradients = {
  primary: `linear-gradient(135deg, ${colors.primary.deep_blue} 0%, ${colors.primary.blue_dark} 100%)`,
  accent: `linear-gradient(135deg, ${colors.accent.saffron} 0%, ${colors.accent.saffron_dark} 100%)`,
  hero: `linear-gradient(to bottom right, ${colors.primary.deep_blue}, ${colors.primary.blue_mid}, ${colors.primary.blue_dark})`,
} as const;

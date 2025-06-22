import { MD3LightTheme } from 'react-native-paper';

export const theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#3b82f6',
    primaryContainer: '#dbeafe',
    secondary: '#64748b',
    secondaryContainer: '#f1f5f9',
    tertiary: '#10b981',
    tertiaryContainer: '#d1fae5',
    error: '#ef4444',
    errorContainer: '#fef2f2',
    background: '#f8fafc',
    surface: '#ffffff',
    surfaceVariant: '#f1f5f9',
    outline: '#e2e8f0',
    outlineVariant: '#cbd5e1',
    onPrimary: '#ffffff',
    onPrimaryContainer: '#1e3a8a',
    onSecondary: '#ffffff',
    onSecondaryContainer: '#334155',
    onTertiary: '#ffffff',
    onTertiaryContainer: '#065f46',
    onError: '#ffffff',
    onErrorContainer: '#7f1d1d',
    onBackground: '#1e293b',
    onSurface: '#1e293b',
    onSurfaceVariant: '#475569',
    onOutline: '#64748b',
    onOutlineVariant: '#94a3b8',
  },
  roundness: 12,
};

export const colors = {
  // Fire alert severity colors
  critical: '#dc2626',
  high: '#ef4444',
  medium: '#f97316',
  low: '#f59e0b',
  
  // Status colors
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',
  
  // Background gradients
  primaryGradient: ['#3b82f6', '#2563eb'],
  successGradient: ['#10b981', '#059669'],
  errorGradient: ['#ef4444', '#dc2626'],
  warningGradient: ['#f59e0b', '#d97706'],
  
  // Text colors
  textPrimary: '#1e293b',
  textSecondary: '#64748b',
  textTertiary: '#94a3b8',
  
  // Border colors
  borderLight: '#e2e8f0',
  borderMedium: '#cbd5e1',
  borderDark: '#94a3b8',
  
  // Background colors
  backgroundPrimary: '#f8fafc',
  backgroundSecondary: '#f1f5f9',
  backgroundTertiary: '#e2e8f0',
  
  // Card colors
  cardBackground: '#ffffff',
  cardBorder: '#e2e8f0',
  cardShadow: 'rgba(0, 0, 0, 0.1)',
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const typography = {
  h1: {
    fontSize: 28,
    fontWeight: '700',
    lineHeight: 36,
  },
  h2: {
    fontSize: 24,
    fontWeight: '600',
    lineHeight: 32,
  },
  h3: {
    fontSize: 20,
    fontWeight: '600',
    lineHeight: 28,
  },
  h4: {
    fontSize: 18,
    fontWeight: '600',
    lineHeight: 24,
  },
  body1: {
    fontSize: 16,
    fontWeight: '400',
    lineHeight: 24,
  },
  body2: {
    fontSize: 14,
    fontWeight: '400',
    lineHeight: 20,
  },
  caption: {
    fontSize: 12,
    fontWeight: '500',
    lineHeight: 16,
  },
  button: {
    fontSize: 16,
    fontWeight: '600',
    lineHeight: 24,
  },
}; 
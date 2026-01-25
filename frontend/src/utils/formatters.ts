import { format, formatDistanceToNow } from 'date-fns';

export const formatCurrency = (
  value: number,
  currency: string = 'USD'
): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

export const formatCurrencyDetailed = (
  value: number,
  currency: string = 'USD'
): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

export const formatPercent = (value: number): string => {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
};

export const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('en-US').format(value);
};

export const formatDate = (dateString: string): string => {
  return format(new Date(dateString), 'MMM d, yyyy');
};

export const formatDateTime = (dateString: string): string => {
  return format(new Date(dateString), 'MMM d, yyyy HH:mm');
};

export const formatRelativeTime = (dateString: string): string => {
  return formatDistanceToNow(new Date(dateString), { addSuffix: true });
};

export const truncateText = (
  text: string,
  maxLength: number
): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

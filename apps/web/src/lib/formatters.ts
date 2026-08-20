/**
 * CC Track — Financial & Numerical Formatter Utilities
 * Formats values according to the Indian Numbering System and Bauhaus Typography standards.
 */

export function formatINR(
  value: number | string | null | undefined,
  options?: {
    showDecimals?: boolean;
    compact?: boolean;
    includeSymbol?: boolean;
  }
): string {
  if (value === null || value === undefined || value === '') {
    return '₹ 0.00';
  }

  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) {
    return '₹ 0.00';
  }

  const {
    showDecimals = true,
    compact = false,
    includeSymbol = true,
  } = options || {};

  const symbol = includeSymbol ? '₹ ' : '';

  if (compact) {
    if (Math.abs(num) >= 10000000) {
      return `${symbol}${(num / 10000000).toFixed(2)} Cr`;
    }
    if (Math.abs(num) >= 100000) {
      return `${symbol}${(num / 100000).toFixed(2)} L`;
    }
    if (Math.abs(num) >= 1000) {
      return `${symbol}${(num / 1000).toFixed(1)} K`;
    }
  }

  const formattedNumber = num.toLocaleString('en-IN', {
    minimumFractionDigits: showDecimals ? 2 : 0,
    maximumFractionDigits: showDecimals ? 2 : 0,
  });

  return `${symbol}${formattedNumber}`;
}

export function formatDate(
  dateStr: string | null | undefined,
  format: 'short' | 'medium' | 'full' = 'medium'
): string {
  if (!dateStr) return 'N/A';

  // Handle DD/MM/YYYY or YYYY-MM-DD
  let d: Date;
  if (dateStr.includes('/')) {
    const parts = dateStr.split('/');
    if (parts.length === 3) {
      // DD/MM/YYYY
      d = new Date(parseInt(parts[2], 10), parseInt(parts[1], 10) - 1, parseInt(parts[0], 10));
    } else {
      d = new Date(dateStr);
    }
  } else {
    d = new Date(dateStr);
  }

  if (isNaN(d.getTime())) {
    return dateStr;
  }

  if (format === 'short') {
    return d.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
    });
  }

  if (format === 'full') {
    return d.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  }

  return d.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

export function formatPercent(
  val: number | string | null | undefined,
  decimals: number = 1
): string {
  if (val === null || val === undefined || val === '') return '0.0%';
  const num = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(num)) return '0.0%';
  return `${num.toFixed(decimals)}%`;
}

export function formatNumber(
  val: number | string | null | undefined,
  decimals: number = 0
): string {
  if (val === null || val === undefined || val === '') return '0';
  const num = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(num)) return '0';
  return num.toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

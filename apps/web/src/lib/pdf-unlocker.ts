import * as pdfjsLib from 'pdfjs-dist';

// Ensure worker is configured only in browser environment
if (typeof window !== 'undefined') {
  pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.mjs`;
}

export interface BankPasswordHint {
  bankName: string;
  code: 'HDFC' | 'ICICI' | 'SBI' | 'AXIS' | 'AMEX' | 'OTHER';
  format: string;
  example: string;
  notes: string;
}

export const BANK_PASSWORD_HINTS: BankPasswordHint[] = [
  {
    bankName: 'HDFC Bank',
    code: 'HDFC',
    format: 'First 4 characters of Name in UPPERCASE + Date & Month of Birth (DDMM)',
    example: 'ROHA1504 (for Rohan born on 15th April)',
    notes: 'If your name has fewer than 4 letters, use full name in uppercase + DDMM.',
  },
  {
    bankName: 'ICICI Bank',
    code: 'ICICI',
    format: 'First 4 characters of Name in lowercase + Date & Month of Birth (DDMM)',
    example: 'roha1504 or PAN in UPPERCASE',
    notes: 'For older statements, ICICI may use your 10-character PAN number.',
  },
  {
    bankName: 'SBI Card',
    code: 'SBI',
    format: 'Date of Birth (DDMMYYYY) + Last 4 digits of Credit Card',
    example: '150419951234 (for 15/04/1995 and card ending 1234)',
    notes: 'No spaces or special characters between DOB and card digits.',
  },
  {
    bankName: 'Axis Bank',
    code: 'AXIS',
    format: 'First 4 characters of Name in UPPERCASE + Last 4 digits of Card',
    example: 'ROHA7890',
    notes: 'Alternatively: First 4 characters of Name + DDMM of Birth.',
  },
  {
    bankName: 'American Express',
    code: 'AMEX',
    format: '5-Digit Postal / PIN Code of billing address or DOB (DDMMYYYY)',
    example: '560001 or 15041995',
    notes: 'Usually requires the 6-digit or 5-digit PIN code registered on the card.',
  },
];

export interface UnlockPdfResult {
  isEncrypted: boolean;
  decryptedBuffer: ArrayBuffer;
  pageCount: number;
  unlockedWithPassword: boolean;
}

/**
 * Checks whether a PDF ArrayBuffer is password-protected without throwing.
 */
export async function checkIsPdfEncrypted(fileBuffer: ArrayBuffer): Promise<boolean> {
  try {
    const loadingTask = pdfjsLib.getDocument({
      data: new Uint8Array(fileBuffer),
      password: '',
    });
    await loadingTask.promise;
    return false;
  } catch (error: unknown) {
    if (error && typeof error === 'object' && 'name' in error) {
      const errName = (error as { name: string }).name;
      if (errName === 'PasswordException') {
        return true;
      }
    }
    return false;
  }
}

/**
 * Attempts to unlock a PDF in client-side memory using the provided password.
 * Returns decrypted ArrayBuffer and page count.
 * Throws an error if the password is incorrect or PDF is malformed.
 */
export async function unlockPdf(
  fileBuffer: ArrayBuffer,
  password?: string
): Promise<UnlockPdfResult> {
  const isEncrypted = await checkIsPdfEncrypted(fileBuffer);

  if (!isEncrypted) {
    const loadingTask = pdfjsLib.getDocument({
      data: new Uint8Array(fileBuffer),
    });
    const pdfDoc = await loadingTask.promise;
    return {
      isEncrypted: false,
      decryptedBuffer: fileBuffer,
      pageCount: pdfDoc.numPages,
      unlockedWithPassword: false,
    };
  }

  if (!password) {
    throw new Error('PASSWORD_REQUIRED');
  }

  try {
    const loadingTask = pdfjsLib.getDocument({
      data: new Uint8Array(fileBuffer),
      password: password,
    });
    const pdfDoc = await loadingTask.promise;

    // Save decrypted document bytes in client RAM
    let decryptedBytes: Uint8Array;
    if (typeof pdfDoc.saveDocument === 'function') {
      decryptedBytes = await pdfDoc.saveDocument();
    } else {
      decryptedBytes = await pdfDoc.getData();
    }

    return {
      isEncrypted: true,
      decryptedBuffer: decryptedBytes.buffer as ArrayBuffer,
      pageCount: pdfDoc.numPages,
      unlockedWithPassword: true,
    };
  } catch (error: unknown) {
    if (error && typeof error === 'object' && 'name' in error) {
      const errName = (error as { name: string }).name;
      if (errName === 'PasswordException') {
        throw new Error('INCORRECT_PASSWORD');
      }
    }
    throw error;
  }
}

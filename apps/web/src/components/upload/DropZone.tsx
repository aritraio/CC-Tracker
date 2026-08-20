'use client';

import React, { useState, useRef, DragEvent, ChangeEvent } from 'react';
import {
  checkIsPdfEncrypted,
  unlockPdf,
} from '@/lib/pdf-unlocker';
import { parseStatementPdf, ApiError } from '@/lib/api';
import { ParseStatementResponse } from '@/types';
import { PasswordModal } from './PasswordModal';
import { ProcessingProgress, ProcessingStepId } from './ProcessingProgress';
import { Button } from '@/components/ui/button';
import {
  Upload,
  FileText,
  ShieldCheck,
  Lock,
  Sparkles,
  AlertCircle,
  CreditCard,
} from 'lucide-react';

export interface DropZoneProps {
  onStatementParsed: (data: ParseStatementResponse) => void;
}

const MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024; // 15MB

// Sample test statement text templates for one-click demo testing
const DEMO_TEMPLATES = {
  HDFC: `HDFC BANK
Credit Card Statement
Card No: 4524 XXXX XXXX 1234
Statement Period : 16/03/2024 to 15/04/2024
Statement Date : 15/04/2024
Payment Due Date : 05/05/2024
Total Amount Due : 45,230.50
Minimum Amount Due : 2,300.00
Credit Limit : 3,00,000.00
Available Credit Limit : 2,54,769.50
Opening Balance : 0.00
Total Debits : 45,230.50
Total Credits : 0.00

Date Transaction Description Amount (in Rs.)
16/03/2024 SWIGGY BANGALORE IN 549.00
18/03/2024 BLINKIT COMMERCE GURGAON 1,240.50
22/03/2024 AMAZON SELLER SERVICES MUMBAI 3,499.00
25/03/2024 NETFLIX ENTERTAINMENT SERVICES 649.00
01/04/2024 HPCL AUTO FUELS BANGALORE 2,500.00
04/04/2024 ANNUAL MEMBERSHIP FEE 1,500.00
04/04/2024 IGST-DB@18.00% 270.00
10/04/2024 ZOMATO RESTAURANTS NEW DELHI 820.00
12/04/2024 UBER INDIA SYSTEMS MUMBAI 403.00
14/04/2024 APPLE SERVICES RETAIL 33,800.00
`,
  ICICI: `ICICI BANK LIMITED
Statement of Card Account
Card No: 4375 12XX XXXX 4321
Statement Period : From 21/03/2024 to 20/04/2024
Statement Date : 20/04/2024
Payment Due Date : 10/05/2024
Total Amount Due : ₹ 32,450.00
Minimum Amount Due : ₹ 1,650.00
Credit Limit : ₹ 4,50,000.00
Available Credit Limit : ₹ 4,17,550.00
Opening Balance : ₹ 0.00
Total Debits : ₹ 32,450.00
Total Credits : ₹ 0.00

Transaction Details
Date Ref No Details Amount (INR)
22/03/2024 10928374 SWIGGY FOOD DELIVERY BANGALORE 680.00 DR
26/03/2024 10928375 AMAZON INDIA PAYMENTS 12,999.00 DR
30/03/2024 10928376 MAKEMYTRIP TRAVEL GURGAON 14,500.00 DR
05/04/2024 10928377 STARBUCKS COFFEE KORAMANGALA 750.00 DR
10/04/2024 10928378 BLINKIT COMMERCE 1,521.00 DR
15/04/2024 10928379 BOOKMYSHOW TICKETS MUMBAI 2,000.00 DR
`,
  SBI: `SBI Cards and Payment Services Limited
SBI Card Statement
Card No: 4129 XXXX XXXX 9876
Statement Period : From 13/03/2024 to 12/04/2024
Statement Date : 12 Apr 2024
Payment Due Date : 02 May 2024
Total Amount Due : Rs. 28,950.00
Minimum Amount Due : Rs. 1,450.00
Credit Limit : Rs. 2,00,000.00
Available Credit Limit : Rs. 1,71,050.00
Previous Balance : Rs. 0.00
Total Debits : Rs. 28,950.00
Total Credits : Rs. 0.00

Date Transaction Details Type Amount (in Rs.)
15 Mar 2024 ZOMATO ORDER ONLINE D 890.00
18 Mar 2024 FLIPKART INTERNET BANGALORE D 18,490.00
24 Mar 2024 CULT FIT HEALTHCARE BANGALORE D 6,990.00
29 Mar 2024 UBER TRIP BANGALORE D 380.00
05 Apr 2024 SHELL PETROL PUMP WHITEFIELD D 2,200.00
`,
};

export const DropZone: React.FC<DropZoneProps> = ({ onStatementParsed }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState<ProcessingStepId>('unlocking');
  const [stepIndex, setStepIndex] = useState(0);
  const [errorState, setErrorState] = useState<{ isError: boolean; message: string }>({
    isError: false,
    message: '',
  });

  // Password Modal state
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [pendingFile, setPendingFile] = useState<{ buffer: ArrayBuffer; name: string } | null>(null);
  const [modalError, setModalError] = useState<string | null>(null);
  const [isUnlocking, setIsUnlocking] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = async (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      await processSelectedFile(files[0]);
    }
  };

  const handleFileInputChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await processSelectedFile(files[0]);
    }
    // Reset file input value to allow re-selecting same file
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const processSelectedFile = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setErrorState({
        isError: true,
        message: 'Invalid file format. Please upload a PDF credit card statement.',
      });
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setErrorState({
        isError: true,
        message: 'File size exceeds 15MB limit. Please upload a standard statement.',
      });
      return;
    }

    setErrorState({ isError: false, message: '' });

    try {
      const buffer = await file.arrayBuffer();
      const isEncrypted = await checkIsPdfEncrypted(buffer);

      if (isEncrypted) {
        // Show password dialog
        setPendingFile({ buffer, name: file.name });
        setShowPasswordModal(true);
        setModalError(null);
      } else {
        // Proceed directly with parsing
        await executeUploadAndParse(buffer, file.name);
      }
    } catch (err: unknown) {
      console.error('Error reading PDF file:', err);
      setErrorState({
        isError: true,
        message: 'Failed to read PDF file. Please ensure it is a valid, uncorrupted PDF.',
      });
    }
  };

  const handlePasswordUnlock = async (password: string) => {
    if (!pendingFile) return;

    setIsUnlocking(true);
    setModalError(null);

    try {
      const unlockResult = await unlockPdf(pendingFile.buffer, password);
      setShowPasswordModal(false);
      setIsUnlocking(false);

      // Execute upload with decrypted buffer
      await executeUploadAndParse(unlockResult.decryptedBuffer, pendingFile.name);
    } catch (err: unknown) {
      setIsUnlocking(false);
      if (err instanceof Error && err.message === 'INCORRECT_PASSWORD') {
        setModalError('INCORRECT_PASSWORD');
      } else {
        setModalError('Failed to unlock document. Please check the password formula.');
      }
    }
  };

  const executeUploadAndParse = async (buffer: ArrayBuffer, fileName: string) => {
    setIsProcessing(true);
    setErrorState({ isError: false, message: '' });

    // Step 1: Unlocking
    setCurrentStep('unlocking');
    setStepIndex(0);

    // Simulate stepped transitions for high-polish UX
    const timer1 = setTimeout(() => {
      setCurrentStep('extracting');
      setStepIndex(1);
    }, 200);

    const timer2 = setTimeout(() => {
      setCurrentStep('reconciling');
      setStepIndex(2);
    }, 450);

    const timer3 = setTimeout(() => {
      setCurrentStep('categorizing');
      setStepIndex(3);
    }, 700);

    const timer4 = setTimeout(() => {
      setCurrentStep('synthesizing');
      setStepIndex(4);
    }, 950);

    try {
      const blob = new Blob([buffer], { type: 'application/pdf' });
      const parsedData = await parseStatementPdf(blob, fileName);

      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);

      setCurrentStep('synthesizing');
      setStepIndex(4);

      setTimeout(() => {
        setIsProcessing(false);
        onStatementParsed(parsedData);
      }, 500);
    } catch (err: unknown) {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);

      let msg = 'Failed to parse statement. Please check your backend connection.';
      if (err instanceof ApiError) {
        msg = err.message;
      } else if (err instanceof Error) {
        msg = err.message;
      }

      setErrorState({
        isError: true,
        message: msg,
      });
    }
  };

  /**
   * Generates a minimal, valid in-browser PDF for sample testing without external file upload.
   */
  const handleLoadDemoStatement = async (bankCode: 'HDFC' | 'ICICI' | 'SBI') => {
    setErrorState({ isError: false, message: '' });
    try {
      const templateText = DEMO_TEMPLATES[bankCode];

      // Pure TypeScript zero-dependency PDF generation
      const lines = templateText.split('\n');
      let streamContent = 'BT /F1 9 Tf 30 800 Td 11 TL\n';
      for (const line of lines) {
        const escaped = line
          .replace(/\\/g, '\\\\')
          .replace(/\(/g, '\\(')
          .replace(/\)/g, '\\)');
        streamContent += `(${escaped}) ' \n`;
      }
      streamContent += 'ET';

      const streamLength = streamContent.length;
      const pdfSource = `%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>
endobj
5 0 obj
<< /Length ${streamLength} >>
stream
${streamContent}
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000234 00000 n 
0000000305 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
${400 + streamLength}
%%EOF`;

      const pdfBlob = new Blob([pdfSource], { type: 'application/pdf' });
      const buffer = await pdfBlob.arrayBuffer();
      await executeUploadAndParse(buffer, `${bankCode.toLowerCase()}_sample_statement.pdf`);
    } catch (err: unknown) {
      console.error('Failed to generate demo statement:', err);
      setErrorState({
        isError: true,
        message: 'Could not load demo statement. Please verify that backend is running on localhost:8000.',
      });
    }
  };

  return (
    <div id="dropzone" className="w-full">
      {/* Password Decryption Modal */}
      <PasswordModal
        isOpen={showPasswordModal}
        fileName={pendingFile?.name || 'statement.pdf'}
        onUnlock={handlePasswordUnlock}
        onCancel={() => {
          setShowPasswordModal(false);
          setPendingFile(null);
          setModalError(null);
        }}
        errorMessage={modalError}
        isUnlocking={isUnlocking}
      />

      {isProcessing ? (
        <ProcessingProgress
          currentStep={currentStep}
          stepIndex={stepIndex}
          isError={errorState.isError}
          errorMessage={errorState.message}
          onRetry={() => {
            setIsProcessing(false);
            setErrorState({ isError: false, message: '' });
          }}
        />
      ) : (
        <div className="flex flex-col gap-6">
          {/* Main DropZone Card */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`cursor-pointer transition-all duration-150 p-8 sm:p-12 text-center relative border-4 ${
              isDragOver
                ? 'bg-bauhaus-yellow border-black shadow-[10px_10px_0px_0px_#121212] scale-[1.01]'
                : 'bg-paper border-black shadow-bauhaus-lg hover:-translate-y-1 hover:shadow-bauhaus-xl'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileInputChange}
              className="hidden"
            />

            {/* Top Corner Geometric Markers */}
            <div className="absolute top-4 right-4 flex items-center gap-1.5" aria-hidden="true">
              <div className="w-3.5 h-3.5 rounded-full bg-bauhaus-red border-2 border-black" />
              <div className="w-3.5 h-3.5 rounded-none bg-bauhaus-blue border-2 border-black" />
              <div className="w-3.5 h-3.5 bg-bauhaus-yellow bauhaus-clip-triangle" />
            </div>

            {/* Hero Dropzone Center Content */}
            <div className="max-w-xl mx-auto flex flex-col items-center">
              <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-none bg-canvas border-4 border-black flex items-center justify-center mb-6 shadow-[4px_4px_0px_0px_#121212]">
                <Upload className="w-8 h-8 sm:w-10 sm:h-10 text-ink" />
              </div>

              <h3 className="text-2xl sm:text-3xl font-black uppercase tracking-tight text-ink mb-3">
                Drag & Drop PDF Statement
              </h3>

              <p className="text-sm sm:text-base font-medium text-ink/75 mb-6 max-w-md">
                Drop your password-protected or decrypted monthly credit card statement here.
                Supports all major Indian card issuers.
              </p>

              {/* Supported Banks Row */}
              <div className="flex flex-wrap items-center justify-center gap-2 mb-8">
                {['HDFC Bank', 'ICICI Bank', 'SBI Card', 'Axis Bank', 'Amex'].map((bank) => (
                  <span
                    key={bank}
                    className="px-2.5 py-1 text-xs font-bold uppercase tracking-wider bg-canvas border-2 border-black text-ink shadow-[2px_2px_0px_0px_#121212]"
                  >
                    {bank}
                  </span>
                ))}
              </div>

              <Button
                type="button"
                variant="primary"
                size="lg"
                className="gap-2 pointer-events-none"
              >
                <FileText className="w-5 h-5" />
                <span>Select PDF File</span>
              </Button>

              {/* Privacy Badges Footer */}
              <div className="flex flex-wrap items-center justify-center gap-4 mt-8 pt-6 border-t-2 border-black/20 text-xs font-bold text-ink/80">
                <div className="flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-bauhaus-blue" />
                  <span>100% In-Memory Parsing</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Lock className="w-4 h-4 text-bauhaus-red" />
                  <span>Zero Password Transmission</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-bauhaus-yellow" />
                  <span>Deterministic Reconciliation</span>
                </div>
              </div>
            </div>
          </div>

          {/* Error Alert Display */}
          {errorState.isError && (
            <div className="p-4 bg-bauhaus-red/10 border-4 border-bauhaus-red text-ink flex items-start gap-3 animate-in fade-in">
              <AlertCircle className="w-5 h-5 text-bauhaus-red shrink-0 mt-0.5" />
              <div>
                <h5 className="font-bold uppercase text-xs text-bauhaus-red">Upload Error</h5>
                <p className="text-sm font-medium mt-0.5">{errorState.message}</p>
              </div>
            </div>
          )}

          {/* One-Click Quick Demo Statement Loaders */}
          <div className="bg-canvas border-2 md:border-4 border-black p-5 shadow-[4px_4px_0px_0px_#121212]">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
              <div className="flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-bauhaus-blue" />
                <h4 className="font-black uppercase tracking-tight text-sm text-ink">
                  Don&apos;t have a PDF on hand? Try Demo Statements:
                </h4>
              </div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-ink/60">
                Instant RAM Verification
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => handleLoadDemoStatement('HDFC')}
                className="py-2.5 px-3 bg-paper border-2 border-black font-bold uppercase text-xs text-ink hover:bg-bauhaus-yellow hover:shadow-[3px_3px_0px_0px_#121212] transition-all flex items-center justify-between"
              >
                <span>HDFC Regalia Statement</span>
                <span className="text-[10px] font-mono font-bold text-bauhaus-blue">10 TXNS</span>
              </button>

              <button
                type="button"
                onClick={() => handleLoadDemoStatement('ICICI')}
                className="py-2.5 px-3 bg-paper border-2 border-black font-bold uppercase text-xs text-ink hover:bg-bauhaus-yellow hover:shadow-[3px_3px_0px_0px_#121212] transition-all flex items-center justify-between"
              >
                <span>ICICI Amazon Pay Statement</span>
                <span className="text-[10px] font-mono font-bold text-bauhaus-blue">6 TXNS</span>
              </button>

              <button
                type="button"
                onClick={() => handleLoadDemoStatement('SBI')}
                className="py-2.5 px-3 bg-paper border-2 border-black font-bold uppercase text-xs text-ink hover:bg-bauhaus-yellow hover:shadow-[3px_3px_0px_0px_#121212] transition-all flex items-center justify-between"
              >
                <span>SBI SimplyCLICK Statement</span>
                <span className="text-[10px] font-mono font-bold text-bauhaus-blue">5 TXNS</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

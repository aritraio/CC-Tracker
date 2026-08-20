'use client';

import React, { useState } from 'react';
import { Category } from '@/types';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Tag, Check, Repeat, ChevronDown } from 'lucide-react';

export const ALL_CATEGORIES: { name: Category; color: string }[] = [
  { name: 'Food & Dining', color: '#D02020' },
  { name: 'Shopping', color: '#1040C0' },
  { name: 'Groceries & Quick-Commerce', color: '#F0C020' },
  { name: 'Transport & Fuel', color: '#121212' },
  { name: 'Travel & Lodging', color: '#008844' },
  { name: 'Bills & Utilities', color: '#8E44AD' },
  { name: 'Entertainment & OTT', color: '#E67E22' },
  { name: 'Subscriptions', color: '#2980B9' },
  { name: 'Healthcare & Fitness', color: '#27AE60' },
  { name: 'Education', color: '#34495E' },
  { name: 'Rent & Housing', color: '#D35400' },
  { name: 'Fees & Charges', color: '#C0392B' },
  { name: 'Cash Withdrawal', color: '#7F8C8D' },
  { name: 'Other / Uncategorized', color: '#95A5A6' },
];

export interface CategorySelectPopoverProps {
  currentCategory: Category;
  isRecurring?: boolean;
  onSelectCategory: (category: Category) => void;
  onToggleRecurring?: (isRecurring: boolean) => void;
}

export const CategorySelectPopover: React.FC<CategorySelectPopoverProps> = ({
  currentCategory,
  isRecurring = false,
  onSelectCategory,
  onToggleRecurring,
}) => {
  const [open, setOpen] = useState(false);

  const handleSelect = (cat: Category) => {
    onSelectCategory(cat);
    setOpen(false);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          type="button"
          className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-muted hover:bg-bauhaus-yellow-light text-ink border-2 border-black font-mono text-xs font-bold uppercase transition-colors shadow-bauhaus-xs group text-left cursor-pointer"
          title="Click to reclassify category"
        >
          <span
            className="w-2.5 h-2.5 border border-black shrink-0"
            style={{
              backgroundColor:
                ALL_CATEGORIES.find((c) => c.name === currentCategory)?.color ||
                '#121212',
            }}
          />
          <span className="truncate max-w-[120px] sm:max-w-[150px]">
            {currentCategory}
          </span>
          <ChevronDown className="w-3 h-3 text-ink/70 group-hover:text-ink shrink-0 ml-0.5" />
        </button>
      </PopoverTrigger>

      <PopoverContent align="start" className="w-64 p-3">
        <div className="flex items-center justify-between pb-2 mb-2 border-b border-black/20 font-mono text-xs">
          <div className="flex items-center gap-1.5 font-bold uppercase text-ink">
            <Tag className="w-3.5 h-3.5 text-bauhaus-blue" />
            <span>Reclassify Category</span>
          </div>
        </div>

        {/* Categories List */}
        <div className="max-h-56 overflow-y-auto space-y-1 pr-1 font-mono text-xs">
          {ALL_CATEGORIES.map((cat) => {
            const isSelected = cat.name === currentCategory;
            return (
              <button
                key={cat.name}
                type="button"
                onClick={() => handleSelect(cat.name)}
                className={`w-full flex items-center justify-between px-2.5 py-1.5 text-left border transition-all ${
                  isSelected
                    ? 'bg-bauhaus-yellow border-black font-bold text-ink shadow-bauhaus-xs'
                    : 'bg-canvas hover:bg-white border-transparent text-ink/80 hover:text-ink'
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <span
                    className="w-3 h-3 border border-black shrink-0"
                    style={{ backgroundColor: cat.color }}
                  />
                  <span className="truncate">{cat.name}</span>
                </div>
                {isSelected && <Check className="w-3.5 h-3.5 text-ink shrink-0" />}
              </button>
            );
          })}
        </div>

        {/* Toggle Recurring Subscription Flag */}
        {onToggleRecurring && (
          <div className="pt-2.5 mt-2.5 border-t border-black/20">
            <button
              type="button"
              onClick={() => onToggleRecurring(!isRecurring)}
              className={`w-full flex items-center justify-between px-2.5 py-1.5 border border-black text-xs font-mono font-bold transition-all ${
                isRecurring
                  ? 'bg-bauhaus-blue text-white shadow-bauhaus-xs'
                  : 'bg-canvas hover:bg-white text-ink'
              }`}
            >
              <div className="flex items-center gap-1.5">
                <Repeat className="w-3.5 h-3.5" />
                <span>Mark as Subscription</span>
              </div>
              <span className="text-[10px] font-bold">
                {isRecurring ? 'ACTIVE' : 'OFF'}
              </span>
            </button>
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
};

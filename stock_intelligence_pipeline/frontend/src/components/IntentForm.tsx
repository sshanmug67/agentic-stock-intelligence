import { useState } from 'react';

interface IntentFormProps {
  onExecute: (intentType: string, symbol: string) => void;
  loading: boolean;
}

const IntentForm = ({ onExecute, loading }: IntentFormProps) => {
  const [intentType, setIntentType] = useState('analyze_stock');
  const [symbol, setSymbol] = useState('AAPL');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onExecute(intentType, symbol.toUpperCase());
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Execute Intent
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Intent Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Intent Type
          </label>
          <select
            value={intentType}
            onChange={(e) => setIntentType(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="analyze_stock">Analyze Stock</option>
            <option value="compare_stocks" disabled>Compare Stocks (Soon)</option>
            <option value="market_scan" disabled>Market Scan (Soon)</option>
          </select>
        </div>

        {/* Stock Symbol */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Stock Symbol
          </label>
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            placeholder="e.g., AAPL, MSFT, GOOGL"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 uppercase"
            required
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Executing...
            </span>
          ) : (
            '🚀 Execute Intent'
          )}
        </button>
      </form>

      {/* Quick Examples */}
      <div className="mt-4 pt-4 border-t">
        <p className="text-xs text-gray-500 mb-2">Quick Examples:</p>
        <div className="flex flex-wrap gap-2">
          {['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'].map((sym) => (
            <button
              key={sym}
              onClick={() => setSymbol(sym)}
              className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
            >
              {sym}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default IntentForm;
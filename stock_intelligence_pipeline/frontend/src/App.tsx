import { useState, useEffect } from 'react';
import { executeIntent, getExecution, listExecutions, type ExecutionRecord } from './services/api';
import IntentForm from './components/IntentForm';
import ExecutionDetails from './components/ExecutionDetails';
import ExecutionList from './components/ExecutionList';
import './App.css';

function App() {
  const [currentExecution, setCurrentExecution] = useState<ExecutionRecord | null>(null);
  const [executions, setExecutions] = useState<ExecutionRecord[]>([]);
  const [isPolling, setIsPolling] = useState(false);
  const [loading, setLoading] = useState(false);

  // Load executions list
  const loadExecutions = async () => {
    try {
      const data = await listExecutions(20);
      setExecutions(data);
    } catch (error) {
      console.error('Failed to load executions:', error);
    }
  };

  // Poll for execution updates
  useEffect(() => {
    if (!currentExecution || !isPolling) return;

    const interval = setInterval(async () => {
      try {
        const updated = await getExecution(currentExecution.execution_id);
        setCurrentExecution(updated);
        
        // Stop polling if execution is complete
        if (updated.status === 'success' || updated.status === 'failed') {
          setIsPolling(false);
          loadExecutions(); // Refresh list
        }
      } catch (error) {
        console.error('Failed to poll execution:', error);
        setIsPolling(false);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [currentExecution, isPolling]);

  // Load executions on mount
  useEffect(() => {
    loadExecutions();
  }, []);

  const handleExecuteIntent = async (intentType: string, symbol: string) => {
    setLoading(true);
    try {
      const response = await executeIntent({
        intent_type: intentType,
        parameters: { symbol },
        priority: 5
      });

      // Start polling for updates
      setIsPolling(true);
      
      // Fetch initial execution state
      const execution = await getExecution(response.execution_id);
      setCurrentExecution(execution);
      
    } catch (error) {
      console.error('Failed to execute intent:', error);
      alert('Failed to execute intent');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectExecution = async (executionId: string) => {
    try {
      const execution = await getExecution(executionId);
      setCurrentExecution(execution);
      setIsPolling(false); // Don't auto-poll when viewing history
    } catch (error) {
      console.error('Failed to load execution:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            📈 Stock Intelligence Pipeline
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Intent-driven stock analysis with AI agents
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column - Intent Form */}
          <div className="lg:col-span-1">
            <IntentForm 
              onExecute={handleExecuteIntent}
              loading={loading}
            />
            
            <div className="mt-6">
              <ExecutionList 
                executions={executions}
                onSelect={handleSelectExecution}
                selectedId={currentExecution?.execution_id}
              />
            </div>
          </div>

          {/* Right Column - Execution Details */}
          <div className="lg:col-span-2">
            {currentExecution ? (
              <ExecutionDetails 
                execution={currentExecution}
                isPolling={isPolling}
              />
            ) : (
              <div className="bg-white rounded-lg shadow-sm border p-8 text-center text-gray-500">
                <p>Execute an intent or select from history to view details</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
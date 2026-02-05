import type { ExecutionRecord } from '../services/api';

interface ExecutionDetailsProps {
  execution: ExecutionRecord;
  isPolling: boolean;
}

const ExecutionDetails = ({ execution, isPolling }: ExecutionDetailsProps) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-600 bg-green-50 border-green-200';
      case 'running': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'failed': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return '✅';
      case 'running': return '⏳';
      case 'failed': return '❌';
      default: return '⚪';
    }
  };

  return (
    <div className="space-y-4">
      {/* Execution Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Execution Details
          </h2>
          {isPolling && (
            <span className="flex items-center text-sm text-blue-600">
              <span className="animate-pulse mr-2">●</span>
              Live updates
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Execution ID</p>
            <p className="font-mono text-sm">{execution.execution_id}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Intent Type</p>
            <p className="font-medium">{execution.intent_type}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Status</p>
            <span className={`inline-flex items-center px-2 py-1 rounded text-sm font-medium border ${getStatusColor(execution.status)}`}>
              {getStatusIcon(execution.status)} {execution.status.toUpperCase()}
            </span>
          </div>
          <div>
            <p className="text-sm text-gray-500">Duration</p>
            <p className="font-medium">
              {execution.duration_seconds 
                ? `${execution.duration_seconds.toFixed(2)}s` 
                : 'In progress...'}
            </p>
          </div>
        </div>

        {/* Parameters */}
        <div className="mt-4 pt-4 border-t">
          <p className="text-sm text-gray-500 mb-2">Parameters</p>
          <pre className="bg-gray-50 p-2 rounded text-xs overflow-auto">
            {JSON.stringify(execution.parameters, null, 2)}
          </pre>
        </div>
      </div>

      {/* Agent Executions */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Agent Executions ({execution.agents.length})
        </h3>

        <div className="space-y-3">
          {execution.agents.length === 0 ? (
            <p className="text-sm text-gray-500">No agents executed yet...</p>
          ) : (
            execution.agents.map((agent, index) => (
              <div key={index} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{getStatusIcon(agent.status)}</span>
                    <span className="font-medium text-gray-900">{agent.agent_name}</span>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded ${getStatusColor(agent.status)}`}>
                    {agent.status}
                  </span>
                </div>

                {agent.duration_seconds && (
                  <p className="text-sm text-gray-600 mb-2">
                    Duration: {agent.duration_seconds.toFixed(2)}s
                  </p>
                )}

                {agent.error && (
                  <div className="bg-red-50 border border-red-200 rounded p-2 mt-2">
                    <p className="text-xs text-red-600">{agent.error}</p>
                  </div>
                )}

                {agent.result && agent.status === 'success' && (
                  <details className="mt-2">
                    <summary className="text-sm text-blue-600 cursor-pointer hover:text-blue-700">
                      View Result
                    </summary>
                    <pre className="bg-gray-50 p-2 rounded text-xs overflow-auto mt-2">
                      {JSON.stringify(agent.result, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Final Result */}
      {execution.result && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Final Result
          </h3>
          <pre className="bg-gray-50 p-4 rounded text-sm overflow-auto">
            {JSON.stringify(execution.result, null, 2)}
          </pre>
        </div>
      )}

      {/* Error Message */}
      {execution.error_message && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-red-900 mb-2">Error</h3>
          <p className="text-sm text-red-700">{execution.error_message}</p>
        </div>
      )}
    </div>
  );
};

export default ExecutionDetails;
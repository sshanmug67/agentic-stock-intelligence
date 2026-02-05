import type { ExecutionRecord } from '../services/api';

interface ExecutionListProps {
  executions: ExecutionRecord[];
  onSelect: (executionId: string) => void;
  selectedId?: string;
}

const ExecutionList = ({ executions, onSelect, selectedId }: ExecutionListProps) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return '✅';
      case 'running': return '⏳';
      case 'failed': return '❌';
      default: return '⚪';
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-4">
      <h3 className="text-sm font-semibold text-gray-900 mb-3">
        Recent Executions
      </h3>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {executions.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-4">
            No executions yet
          </p>
        ) : (
          executions.map((execution) => (
            <button
              key={execution.execution_id}
              onClick={() => onSelect(execution.execution_id)}
              className={`w-full text-left p-3 rounded-lg border transition-all hover:shadow-sm ${
                selectedId === execution.execution_id
                  ? 'bg-blue-50 border-blue-300'
                  : 'bg-white border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-gray-900">
                  {execution.parameters.symbol || 'N/A'}
                </span>
                <span className="text-lg">
                  {getStatusIcon(execution.status)}
                </span>
              </div>
              <div className="text-xs text-gray-500">
                {execution.intent_type}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {formatTime(execution.started_at)}
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
};

export default ExecutionList;
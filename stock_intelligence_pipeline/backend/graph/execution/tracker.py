"""
Execution tracker - stores execution records
"""
from datetime import datetime
from uuid import uuid4
from typing import Dict, Optional
from ...models.execution import ExecutionRecord, ExecutionStatus, AgentExecution


class ExecutionTracker:
    """Track graph execution status (in-memory for now)"""
    
    def __init__(self):
        self._executions: Dict[str, ExecutionRecord] = {}
    
    def start_execution(self, intent_type: str, parameters: dict) -> str:
        """Start tracking a new execution"""
        execution_id = str(uuid4())
        
        record = ExecutionRecord(
            execution_id=execution_id,
            intent_type=intent_type,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.utcnow(),
            parameters=parameters,
            retry_count=0,
            agents=[]
        )
        
        self._executions[execution_id] = record
        return execution_id
    
    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Get execution by ID"""
        return self._executions.get(execution_id)
    
    def list_executions(self, limit: int = 50) -> list[ExecutionRecord]:
        """List recent executions"""
        executions = list(self._executions.values())
        executions.sort(key=lambda x: x.started_at, reverse=True)
        return executions[:limit]
    
    def update_status(self, execution_id: str, status: ExecutionStatus):
        """Update execution status"""
        if execution_id in self._executions:
            self._executions[execution_id].status = status
    
    def start_agent(self, execution_id: str, agent_name: str):
        """Record agent start"""
        if execution_id in self._executions:
            agent_exec = AgentExecution(
                agent_name=agent_name,
                status=ExecutionStatus.RUNNING,
                started_at=datetime.utcnow()
            )
            self._executions[execution_id].agents.append(agent_exec)
    
    def complete_agent(self, execution_id: str, agent_name: str, 
                      success: bool, result: Optional[dict] = None, 
                      error: Optional[str] = None):
        """Record agent completion"""
        if execution_id in self._executions:
            record = self._executions[execution_id]
            for agent in record.agents:
                if agent.agent_name == agent_name and agent.status == ExecutionStatus.RUNNING:
                    agent.completed_at = datetime.utcnow()
                    agent.duration_seconds = (agent.completed_at - agent.started_at).total_seconds()
                    agent.status = ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED
                    agent.result = result
                    agent.error = error
                    break
    
    def complete_execution(self, execution_id: str, success: bool, 
                          result: Optional[dict] = None, 
                          error: Optional[str] = None):
        """Mark execution as complete"""
        if execution_id in self._executions:
            record = self._executions[execution_id]
            record.completed_at = datetime.utcnow()
            record.duration_seconds = (record.completed_at - record.started_at).total_seconds()
            record.status = ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED
            record.result = result
            record.error_message = error


# Global tracker instance
execution_tracker = ExecutionTracker()
"""
Execution tracker - stores execution records in Redis
"""
from datetime import datetime
from uuid import uuid4
from typing import Dict, Optional
import json
import redis
from ...models.execution import ExecutionRecord, ExecutionStatus, AgentExecution
from ...config.settings import settings


class ExecutionTracker:
    """Track graph execution status using Redis backend"""
    
    def __init__(self):
        # Connect to Redis
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True
        )
    
    def _get_key(self, execution_id: str) -> str:
        """Get Redis key for execution"""
        return f"execution:{execution_id}"
    
    def _serialize_record(self, record: ExecutionRecord) -> str:
        """Serialize ExecutionRecord to JSON"""
        # Convert to dict, handling datetime serialization
        data = record.model_dump()
        
        # Convert datetime objects to ISO format strings
        if data.get('started_at'):
            data['started_at'] = data['started_at'].isoformat()
        if data.get('completed_at'):
            data['completed_at'] = data['completed_at'].isoformat()
        
        # Convert agent datetimes
        for agent in data.get('agents', []):
            if agent.get('started_at'):
                agent['started_at'] = agent['started_at'].isoformat()
            if agent.get('completed_at'):
                agent['completed_at'] = agent['completed_at'].isoformat()
        
        return json.dumps(data)
    
    def _deserialize_record(self, data: str) -> ExecutionRecord:
        """Deserialize JSON to ExecutionRecord"""
        record_dict = json.loads(data)
        
        # Convert ISO strings back to datetime
        if record_dict.get('started_at'):
            record_dict['started_at'] = datetime.fromisoformat(record_dict['started_at'])
        if record_dict.get('completed_at'):
            record_dict['completed_at'] = datetime.fromisoformat(record_dict['completed_at'])
        
        # Convert agent datetimes
        for agent in record_dict.get('agents', []):
            if agent.get('started_at'):
                agent['started_at'] = datetime.fromisoformat(agent['started_at'])
            if agent.get('completed_at'):
                agent['completed_at'] = datetime.fromisoformat(agent['completed_at'])
        
        return ExecutionRecord(**record_dict)
    
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
        
        # Store in Redis with 24 hour expiration
        key = self._get_key(execution_id)
        self.redis_client.setex(key, 86400, self._serialize_record(record))
        
        # Add to execution list (for listing)
        self.redis_client.zadd('executions:list', {execution_id: datetime.utcnow().timestamp()})
        
        return execution_id
    
    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Get execution by ID"""
        key = self._get_key(execution_id)
        data = self.redis_client.get(key)
        
        if not data:
            return None
        
        return self._deserialize_record(data)
    
    def list_executions(self, limit: int = 50) -> list[ExecutionRecord]:
        """List recent executions"""
        # Get most recent execution IDs from sorted set
        execution_ids = self.redis_client.zrevrange('executions:list', 0, limit - 1)
        
        executions = []
        for exec_id in execution_ids:
            record = self.get_execution(exec_id)
            if record:
                executions.append(record)
        
        return executions
    
    def update_status(self, execution_id: str, status: ExecutionStatus):
        """Update execution status"""
        record = self.get_execution(execution_id)
        if record:
            record.status = status
            key = self._get_key(execution_id)
            self.redis_client.setex(key, 86400, self._serialize_record(record))
    
    def start_agent(self, execution_id: str, agent_name: str):
        """Record agent start"""
        record = self.get_execution(execution_id)
        if record:
            agent_exec = AgentExecution(
                agent_name=agent_name,
                status=ExecutionStatus.RUNNING,
                started_at=datetime.utcnow()
            )
            record.agents.append(agent_exec)
            
            key = self._get_key(execution_id)
            self.redis_client.setex(key, 86400, self._serialize_record(record))
    
    def complete_agent(self, execution_id: str, agent_name: str, 
                      success: bool, result: Optional[dict] = None, 
                      error: Optional[str] = None):
        """Record agent completion"""
        record = self.get_execution(execution_id)
        if record:
            for agent in record.agents:
                if agent.agent_name == agent_name and agent.status == ExecutionStatus.RUNNING:
                    agent.completed_at = datetime.utcnow()
                    agent.duration_seconds = (agent.completed_at - agent.started_at).total_seconds()
                    agent.status = ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED
                    agent.result = result
                    agent.error = error
                    break
            
            key = self._get_key(execution_id)
            self.redis_client.setex(key, 86400, self._serialize_record(record))
    
    def complete_execution(self, execution_id: str, success: bool, 
                          result: Optional[dict] = None, 
                          error: Optional[str] = None):
        """Mark execution as complete"""
        record = self.get_execution(execution_id)
        if record:
            record.completed_at = datetime.utcnow()
            record.duration_seconds = (record.completed_at - record.started_at).total_seconds()
            record.status = ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED
            record.result = result
            record.error_message = error
            
            key = self._get_key(execution_id)
            self.redis_client.setex(key, 86400, self._serialize_record(record))


# Global tracker instance
execution_tracker = ExecutionTracker()
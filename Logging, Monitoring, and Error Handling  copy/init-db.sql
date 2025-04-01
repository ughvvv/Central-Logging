-- Create tables for the orchestrator database

-- Task states table
CREATE TABLE IF NOT EXISTS task_states (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL UNIQUE,
    task_type VARCHAR(100) NOT NULL,
    agent_name VARCHAR(100),
    state VARCHAR(50) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    metadata JSONB
);

-- Create index on task_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_task_states_task_id ON task_states(task_id);

-- Create index on state for filtering by state
CREATE INDEX IF NOT EXISTS idx_task_states_state ON task_states(state);

-- Create index on agent_name for filtering by agent
CREATE INDEX IF NOT EXISTS idx_task_states_agent_name ON task_states(agent_name);

-- Agent registry table
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL UNIQUE,
    agent_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    last_heartbeat TIMESTAMP,
    capabilities JSONB,
    metadata JSONB
);

-- Create index on agent_name for faster lookups
CREATE INDEX IF NOT EXISTS idx_agents_agent_name ON agents(agent_name);

-- Create index on status for filtering by status
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);

-- Task history table for completed tasks
CREATE TABLE IF NOT EXISTS task_history (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL UNIQUE,
    task_type VARCHAR(100) NOT NULL,
    agent_name VARCHAR(100),
    state VARCHAR(50) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP NOT NULL,
    duration_ms INTEGER,
    success BOOLEAN NOT NULL,
    error_type VARCHAR(100),
    error_message TEXT,
    metadata JSONB
);

-- Create index on task_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_task_history_task_id ON task_history(task_id);

-- Create index on task_type for analytics
CREATE INDEX IF NOT EXISTS idx_task_history_task_type ON task_history(task_type);

-- Create index on agent_name for filtering by agent
CREATE INDEX IF NOT EXISTS idx_task_history_agent_name ON task_history(agent_name);

-- Create index on success for filtering by success/failure
CREATE INDEX IF NOT EXISTS idx_task_history_success ON task_history(success);

-- System configuration table
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP NOT NULL
);

-- Create index on config_key for faster lookups
CREATE INDEX IF NOT EXISTS idx_system_config_config_key ON system_config(config_key);

-- Insert some sample configuration
INSERT INTO system_config (config_key, config_value, description, updated_at)
VALUES 
    ('retry_policy', '{"max_retries": 3, "backoff_factor": 0.5, "max_backoff": 10}', 'Global retry policy for transient errors', NOW()),
    ('logging_levels', '{"default": "INFO", "orchestrator": "INFO", "agents": "INFO"}', 'Logging levels for different components', NOW()),
    ('agent_timeout', '{"heartbeat_interval": 60, "timeout_seconds": 300}', 'Agent heartbeat and timeout settings', NOW())
ON CONFLICT (config_key) DO NOTHING;

-- Insert sample agent types
INSERT INTO agents (agent_name, agent_type, status, last_heartbeat, capabilities, metadata)
VALUES 
    ('research_agent_1', 'research_agent', 'active', NOW(), '{"skills": ["web_search", "data_analysis"]}', '{"version": "1.0.0"}'),
    ('writing_agent_1', 'writing_agent', 'active', NOW(), '{"skills": ["content_generation", "editing"]}', '{"version": "1.0.0"}'),
    ('editing_agent_1', 'editing_agent', 'active', NOW(), '{"skills": ["grammar_check", "style_improvement"]}', '{"version": "1.0.0"}'),
    ('fact_checking_agent_1', 'fact_checking_agent', 'active', NOW(), '{"skills": ["verification", "source_analysis"]}', '{"version": "1.0.0"}')
ON CONFLICT (agent_name) DO NOTHING;

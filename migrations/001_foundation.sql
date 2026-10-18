CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    settings JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, slug),
    UNIQUE (tenant_id, id)
);

CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    project_id UUID,
    provider TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    external_id TEXT,
    canonical_url TEXT NOT NULL,
    display_name TEXT NOT NULL DEFAULT '',
    default_branch TEXT,
    state TEXT NOT NULL DEFAULT 'registered',
    desired_sha TEXT,
    indexed_sha TEXT,
    history_from TIMESTAMPTZ,
    last_full_scan_at TIMESTAMPTZ,
    last_incremental_sync_at TIMESTAMPTZ,
    last_error_category TEXT,
    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, provider, source_kind, external_id),
    UNIQUE (tenant_id, id),
    FOREIGN KEY (tenant_id, project_id)
        REFERENCES projects(tenant_id, id) ON DELETE SET NULL (project_id)
);
CREATE INDEX IF NOT EXISTS sources_tenant_project_idx ON sources(tenant_id, project_id);
CREATE INDEX IF NOT EXISTS sources_state_idx ON sources(state);

CREATE TABLE IF NOT EXISTS sync_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_id UUID NOT NULL,
    job_kind TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'queued',
    stage TEXT NOT NULL DEFAULT 'queued',
    idempotency_key TEXT NOT NULL UNIQUE,
    target_sha TEXT,
    start_cursor JSONB,
    end_cursor JSONB,
    checkpoint JSONB NOT NULL DEFAULT '{}'::jsonb,
    lease_owner TEXT,
    lease_expires_at TIMESTAMPTZ,
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    next_retry_at TIMESTAMPTZ,
    error_category TEXT,
    safe_error_message TEXT,
    correlation_id UUID NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    FOREIGN KEY (tenant_id, source_id) REFERENCES sources(tenant_id, id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS sync_jobs_ready_idx ON sync_jobs(state, next_retry_at, created_at);
CREATE INDEX IF NOT EXISTS sync_jobs_source_idx ON sync_jobs(source_id, created_at DESC);

CREATE TABLE IF NOT EXISTS sync_checkpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_id UUID NOT NULL,
    checkpoint_name TEXT NOT NULL,
    checkpoint_value JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_id, checkpoint_name),
    FOREIGN KEY (tenant_id, source_id) REFERENCES sources(tenant_id, id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS webhook_inbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    installation_id TEXT NOT NULL DEFAULT '',
    delivery_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    source_id UUID,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    processed_at TIMESTAMPTZ,
    processing_error_category TEXT,
    UNIQUE (provider, installation_id, delivery_id),
    FOREIGN KEY (tenant_id, source_id)
        REFERENCES sources(tenant_id, id) ON DELETE SET NULL (source_id)
);
CREATE INDEX IF NOT EXISTS webhook_inbox_pending_idx ON webhook_inbox(received_at) WHERE processed_at IS NULL;

CREATE TABLE IF NOT EXISTS activity_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_id UUID NOT NULL,
    provider TEXT NOT NULL,
    external_event_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    actor_external_id TEXT,
    actor_display_name TEXT,
    occurred_at TIMESTAMPTZ,
    source_url TEXT,
    commit_sha TEXT,
    related_external_id TEXT,
    summary TEXT NOT NULL DEFAULT '',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_id, provider, external_event_id),
    FOREIGN KEY (tenant_id, source_id) REFERENCES sources(tenant_id, id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS activity_events_time_idx ON activity_events(tenant_id, source_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS activity_events_type_idx ON activity_events(tenant_id, event_type, occurred_at DESC);

CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_id UUID NOT NULL,
    platform TEXT NOT NULL,
    external_channel_id TEXT NOT NULL,
    external_message_id TEXT NOT NULL,
    external_author_id TEXT,
    author_display_name TEXT,
    body TEXT NOT NULL DEFAULT '',
    thread_id TEXT,
    reply_to_message_id TEXT,
    source_url TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    edited_at TIMESTAMPTZ,
    is_bot BOOLEAN NOT NULL DEFAULT false,
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    is_redacted BOOLEAN NOT NULL DEFAULT false,
    retention_until TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_id, platform, external_message_id),
    FOREIGN KEY (tenant_id, source_id) REFERENCES sources(tenant_id, id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS conversation_time_idx ON conversation_messages(tenant_id, source_id, created_at DESC);
CREATE INDEX IF NOT EXISTS conversation_thread_idx ON conversation_messages(source_id, thread_id, created_at);

CREATE TABLE IF NOT EXISTS repository_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_id UUID NOT NULL,
    commit_sha TEXT NOT NULL,
    path TEXT NOT NULL,
    language TEXT,
    size_bytes BIGINT NOT NULL DEFAULT 0 CHECK (size_bytes >= 0),
    content_sha256 TEXT NOT NULL,
    is_binary BOOLEAN NOT NULL DEFAULT false,
    is_excluded BOOLEAN NOT NULL DEFAULT false,
    exclusion_reason TEXT,
    indexed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_id, commit_sha, path),
    UNIQUE (tenant_id, source_id, id),
    FOREIGN KEY (tenant_id, source_id) REFERENCES sources(tenant_id, id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS repository_files_path_idx ON repository_files(source_id, path);

CREATE TABLE IF NOT EXISTS code_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_id UUID NOT NULL,
    file_id UUID NOT NULL,
    commit_sha TEXT NOT NULL,
    path TEXT NOT NULL,
    chunk_key TEXT NOT NULL,
    symbol_name TEXT,
    language TEXT,
    start_line INTEGER,
    end_line INTEGER,
    content TEXT NOT NULL,
    content_sha256 TEXT NOT NULL,
    chunker_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_id, commit_sha, path, chunk_key, chunker_version),
    UNIQUE (tenant_id, id),
    FOREIGN KEY (tenant_id, source_id) REFERENCES sources(tenant_id, id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id, source_id, file_id)
        REFERENCES repository_files(tenant_id, source_id, id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS code_chunks_source_path_idx ON code_chunks(source_id, path);

CREATE TABLE IF NOT EXISTS code_symbols (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_id UUID NOT NULL,
    commit_sha TEXT NOT NULL,
    symbol_key TEXT NOT NULL,
    symbol_name TEXT NOT NULL,
    qualified_name TEXT,
    symbol_kind TEXT NOT NULL,
    path TEXT NOT NULL,
    start_line INTEGER,
    end_line INTEGER,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (source_id, commit_sha, symbol_key),
    FOREIGN KEY (tenant_id, source_id) REFERENCES sources(tenant_id, id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS code_symbols_name_idx ON code_symbols(tenant_id, symbol_name);

CREATE TABLE IF NOT EXISTS graph_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_id UUID NOT NULL,
    commit_sha TEXT NOT NULL,
    from_key TEXT NOT NULL,
    edge_type TEXT NOT NULL,
    to_key TEXT NOT NULL,
    confidence DOUBLE PRECISION NOT NULL DEFAULT 1.0 CHECK (confidence >= 0 AND confidence <= 1),
    evidence_path TEXT,
    evidence_line INTEGER,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (source_id, commit_sha, from_key, edge_type, to_key),
    FOREIGN KEY (tenant_id, source_id) REFERENCES sources(tenant_id, id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS graph_edges_from_idx ON graph_edges(source_id, commit_sha, from_key);
CREATE INDEX IF NOT EXISTS graph_edges_to_idx ON graph_edges(source_id, commit_sha, to_key);

CREATE TABLE IF NOT EXISTS embedding_spaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    model_id TEXT NOT NULL,
    model_revision TEXT,
    dimensions INTEGER NOT NULL CHECK (dimensions > 0 AND dimensions <= 16000),
    distance_metric TEXT NOT NULL DEFAULT 'cosine',
    normalization TEXT NOT NULL DEFAULT 'provider_default',
    chunker_version TEXT NOT NULL,
    license_review_ref TEXT,
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    is_promoted BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, name, model_id, model_revision, dimensions),
    UNIQUE (tenant_id, id)
);

CREATE TABLE IF NOT EXISTS chunk_embeddings (
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    chunk_id UUID NOT NULL,
    embedding_space_id UUID NOT NULL,
    dimensions INTEGER NOT NULL CHECK (dimensions > 0 AND dimensions <= 16000),
    embedding vector NOT NULL,
    input_sha256 TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (chunk_id, embedding_space_id),
    CHECK (vector_dims(embedding) = dimensions),
    FOREIGN KEY (tenant_id, chunk_id) REFERENCES code_chunks(tenant_id, id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id, embedding_space_id)
        REFERENCES embedding_spaces(tenant_id, id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS chunk_embeddings_space_idx ON chunk_embeddings(tenant_id, embedding_space_id, dimensions);

CREATE TABLE IF NOT EXISTS knowledge_facts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    project_id UUID,
    fact_type TEXT NOT NULL,
    claim TEXT NOT NULL,
    verification_state TEXT NOT NULL DEFAULT 'hypothesis',
    confidence DOUBLE PRECISION CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
    source_evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
    valid_from TEXT,
    valid_until TEXT,
    superseded_by UUID,
    owner_external_id TEXT,
    model_provenance JSONB NOT NULL DEFAULT '{}'::jsonb,
    last_verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, id),
    FOREIGN KEY (tenant_id, project_id) REFERENCES projects(tenant_id, id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id, superseded_by)
        REFERENCES knowledge_facts(tenant_id, id) ON DELETE SET NULL (superseded_by)
);
CREATE INDEX IF NOT EXISTS knowledge_facts_project_idx ON knowledge_facts(tenant_id, project_id, fact_type);

CREATE TABLE IF NOT EXISTS source_access_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_id UUID NOT NULL,
    principal_type TEXT NOT NULL,
    principal_id TEXT NOT NULL,
    permission TEXT NOT NULL,
    granted_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_id, principal_type, principal_id, permission),
    FOREIGN KEY (tenant_id, source_id) REFERENCES sources(tenant_id, id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT,
    correlation_id UUID,
    result TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS audit_events_time_idx ON audit_events(tenant_id, occurred_at DESC);

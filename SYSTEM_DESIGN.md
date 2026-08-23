# RAG Knowledge Assistant - System Design

## 1. Project Overview
A comprehensive, **cost-free, fully open-source** system to ingest documents, create text embeddings, store vectors in a database, and build a retrieval-augmented query pipeline that enhances LLM responses with contextual information.

**Key Principles:**
- 💰 **100% Free** - All components are open-source
- 📊 **Observable** - Built-in metrics, logging, and dashboards
- 🔐 **Self-Hosted** - Complete control, no vendor lock-in
- ⚡ **Production-Ready** - Kubernetes-native architecture

---

## 2. Architecture Components

### 2.1 Document Ingestion Layer
```
┌─────────────────────────┐
│   Document Sources      │
│ - PDFs                  │
│ - Text Files            │
│ - Web URLs              │
│ - Markdown              │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Document Parser/        │
│ Preprocessor            │
│ - Extract text          │
│ - Clean & normalize     │
│ - Chunk documents       │
│ - Deduplication         │
└────────┬────────────────┘
         │
    ┌────┴─────────────┐
    │                  │
    ▼                  ▼
[Metrics]          [Logging]
```

**Key Features:**
- Multi-format support (PDF, DOCX, TXT, Markdown)
- Fixed-size sliding-window chunking with overlap (see 6. Configuration)
- Metadata extraction and preservation
- Duplicate detection with fingerprinting

---

### 2.2 Embedding Generation Layer (Local)
```
┌─────────────────────────────────────┐
│   Text Chunks                       │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Local Embedding Model              │
│  - Sentence-Transformers            │
│  - all-mpnet-base-v2 (768-dim)     │
│  - Running in Docker/Kubernetes     │
└────────┬────────────────────────────┘
         │
    ┌────┴──────────────┐
    │                   │
    ▼                   ▼
[Metrics]           [Logging]
- Embedding time   - Processing logs
- Batch size       - Error tracking
- Cache hits       - Embedding quality
```

**Key Features:**
- Locally hosted embedding service (Sentence-Transformers)
- Batch processing for efficiency
- In-memory + Redis caching
- Quality metrics tracking
- ZERO external API calls

---

### 2.3 Vector Storage Layer
```
┌──────────────────────────────────┐
│   Vector Database                │
│   - ChromaDB (Default)           │
│   - FAISS (Alternative)          │
│   - Local Storage                │
│   - Persistent Volumes           │
└────────┬─────────────────────────┘
         │
    ┌────┴─────────────────┐
    │                      │
    ▼                      ▼
[Metrics]              [Logging]
- Query latency       - Index updates
- Index size          - Storage usage
- Search performance  - Error logs
```

**Key Features:**
- Hybrid search (vector + metadata)
- Similarity-based retrieval
- Scalable indexing
- No external dependencies

---

### 2.4 Retrieval Pipeline Layer
```
┌─────────────────────────┐
│   User Query            │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Query Embedding       │
│   (Local Service)       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Vector Search         │
│   (Top-K retrieval)     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Re-ranking (optional) │
│   - Cross-encoder score │
│   - BM25 keyword score  │
│   - In-memory BM25 index│
│     (rank-bm25, rebuilt │
│     from Postgres text) │
└────────┬────────────────┘
         │
    ┌────┴────────────────┐
    │                     │
    ▼                     ▼
[Metrics]            [Logging]
- Retrieval time    - Retrieved chunks
- Relevance scores  - Similarity scores
- Cache hits        - Query metadata
```

---

### 2.5 LLM Integration Layer (Local Llama 3)
```
┌──────────────────────────────────┐
│   Retrieved Context              │
│   +                              │
│   User Query                     │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│   Prompt Construction            │
│ - Context formatting             │
│ - Token counting                 │
│ - Chain-of-thought              │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│   Local LLM (Llama 3)            │
│   - Ollama Runtime               │
│   - Running in Container         │
│   - 8B/70B model sizes          │
└────────┬─────────────────────────┘
         │
    ┌────┴──────────────────────┐
    │                           │
    ▼                           ▼
[Metrics]                  [Logging]
- Generation time          - Prompt/response
- Token counts             - Confidence scores
- Model performance        - Source citations
- Cache hits               - Errors/retries
```

---

### 2.6 Observability Stack
```
┌──────────────────────────────────────────────┐
│     Application Metrics                      │
│   (Prometheus format from all services)      │
└────────┬─────────────────────────────────────┘
         │
    ┌────┴────────────────┬─────────────┐
    │                     │             │
    ▼                     ▼             ▼
[Prometheus]       [Loki]         [Jaeger]
(Metrics DB)       (Logs DB)       (Tracing)
    │                  │               │
    └──────────┬───────┴───────┬──────┘
               │               │
               ▼               ▼
           [Grafana] ← Dashboards & Alerts
```

**Components:**
- **Prometheus**: Metrics collection & storage (FREE)
- **Loki**: Log aggregation (FREE)
- **Jaeger**: Distributed tracing (FREE)
- **Grafana**: Dashboards & visualization (FREE)

---

## 3. Technology Stack (100% Open Source & Free)

### Core Libraries
```
Python 3.11+
├── Document Processing
│   ├── pypdf
│   ├── pdf2image
│   ├── python-docx
│   ├── beautifulsoup4
│   └── markdown
├── Local Embeddings
│   ├── sentence-transformers
│   ├── torch (CPU/GPU optimized)
│   └── numpy
├── Vector Database
│   ├── chromadb (Primary)
│   └── faiss-cpu (Alternative)
├── Keyword Search / Reranking
│   ├── rank-bm25 (BM25 index, in-memory)
│   └── sentence-transformers cross-encoder (reranker)
├── Local LLM
│   ├── ollama (inference server)
│   └── llama-cpp-python (optional)
├── API & Web
│   ├── fastapi
│   ├── uvicorn
│   └── python-multipart
├── Observability
│   ├── prometheus-client
│   ├── python-json-logger
│   ├── opentelemetry
│   ├── opentelemetry-exporter-prometheus
│   ├── opentelemetry-instrumentation-fastapi
│   └── opentelemetry-instrumentation-sqlalchemy
├── Caching & Queues
│   ├── redis
│   ├── celery
│   └── kombu
├── Database
│   ├── sqlalchemy
│   ├── alembic
│   └── psycopg2-binary
└── Utilities
    ├── pydantic
    ├── python-dotenv
    └── pytest
```

### Infrastructure (All Open Source)
```
Docker
├── Ollama (Llama 3 Runtime)
├── Embedding Service (Sentence-Transformers)
├── RAG Application (FastAPI)
├── PostgreSQL (Metadata)
├── Redis (Caching & Queues)
├── ChromaDB (Vector DB)
├── Prometheus (Metrics)
├── Loki (Logs)
├── Jaeger (Tracing)
└── Grafana (Dashboards)
```

---

## 4. Database Schema

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  api_key_hash VARCHAR(255) UNIQUE NOT NULL,  -- hashed, never store raw keys
  role VARCHAR(20) DEFAULT 'user',            -- 'user' | 'admin', for RBAC
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP,
  last_login_at TIMESTAMP
);
```
`queries.user_id` and the structured logs' `user_id` field reference this
table. With `security.enable_auth: true`, `api/auth.py` verifies the API
key/JWT on every request and resolves it to a `users.id`.

### Document Table
```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  original_filename VARCHAR(255) NOT NULL,
  file_hash VARCHAR(64) UNIQUE,  -- For deduplication
  doc_type VARCHAR(20),
  source_url VARCHAR(2048),
  total_chunks INT,
  total_tokens INT,
  status ENUM('processing', 'completed', 'failed'),
  error_message TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  processed_at TIMESTAMP
);
```

### Chunks Table
```sql
CREATE TABLE chunks (
  id UUID PRIMARY KEY,
  document_id UUID REFERENCES documents(id),
  chunk_index INT,
  content TEXT,
  char_start INT,
  char_end INT,
  token_count INT,
  embedding_model VARCHAR(255),
  embedding_dimension INT,
  created_at TIMESTAMP
);
```

### Embeddings Table (ChromaDB)
```
chromadb/
├── documents/
│   ├── chunk_id (ID)            -- same UUID as chunks.id in Postgres
│   ├── content (Text)           -- denormalized copy for retrieval speed
│   ├── embedding (Vector 768-dim)
│   ├── document_id (Metadata)
│   ├── filename (Metadata)
│   ├── chunk_index (Metadata)
│   └── timestamp (Metadata)
└── chroma.sqlite
```
**Postgres is the source of truth for chunk text; ChromaDB is a derived,
rebuildable index.** Write order: insert into `chunks` (Postgres) first,
then upsert into ChromaDB using `chunks.id` as the ChromaDB `chunk_id`.
If the ChromaDB upsert fails, the chunk is left `status='processing'` and
a retry job re-syncs it — never write to ChromaDB first, since a failed
Postgres write would leave an orphaned vector with no citation record.

### Queries Table (for tracking)
```sql
CREATE TABLE queries (
  id UUID PRIMARY KEY,
  user_id VARCHAR(255),
  query_text TEXT,
  retrieved_chunks INT,
  response TEXT,
  response_tokens INT,
  generation_time_ms INT,
  retrieval_time_ms INT,
  total_time_ms INT,
  confidence_score FLOAT,  -- NOT the LLM's self-reported confidence (LLMs
                            -- can't reliably report that). Computed as the
                            -- average vector-similarity score of the chunks
                            -- actually cited in the answer — a proxy for
                            -- "how well the source material matched the
                            -- question," not "how correct the answer is."
  model_version VARCHAR(50),
  created_at TIMESTAMP
);
```

---

## 5. API Endpoints

### Auth
```
POST   /api/v1/auth/register             Create a user, returns an API key (shown once)
POST   /api/v1/auth/rotate-key           Invalidate old key, issue a new one
```
All endpoints below require `Authorization: Bearer <api_key>` when
`security.enable_auth: true`, verified by `api/auth.py` against `users.api_key_hash`.

### Document Management
```
POST   /api/v1/documents/upload          Upload document(s)
GET    /api/v1/documents                 List all documents
GET    /api/v1/documents/{id}            Get document details
DELETE /api/v1/documents/{id}            Delete document
POST   /api/v1/documents/{id}/reprocess  Reprocess document
GET    /api/v1/documents/health/status   Ingestion status
```

### Query & Retrieval
```
POST   /api/v1/query                     Submit RAG query
GET    /api/v1/query/{id}                Get query result
POST   /api/v1/retrieve                  Raw vector search (top-k)
```

### Observability
```
GET    /metrics                          Prometheus metrics
GET    /api/v1/health                    Health check
GET    /api/v1/stats                     System statistics
GET    /api/v1/logs                      Recent logs (JSON)
```

---

## 6. Configuration Management

```yaml
# config.yaml

app:
  name: "RAG Knowledge Assistant"
  version: "1.0.0"
  environment: "production"
  debug: false

# Local Embedding Configuration
embedding:
  provider: "sentence-transformers"
  model: "all-mpnet-base-v2"
  dimension: 768
  device: "cpu"  # set to "cuda" only if a GPU is confirmed available
  batch_size: 32
  cache_enabled: true
  cache_ttl_seconds: 86400

# Local LLM Configuration (Llama 3)
llm:
  provider: "ollama"
  model: "llama3:8b"  # or "llama3:70b" for higher quality (needs ~40GB+ RAM/VRAM)
  base_url: "http://ollama:11434"
  temperature: 0.7
  top_p: 0.9
  top_k: 40
  max_tokens: 2048
  num_predict: 2048
  stream: true
  timeout_seconds: 300
  request_timeout: 60

# Chunking Configuration
# Sizes are in CHARACTERS, not tokens (roughly chars / 4 ≈ tokens).
# Fixed-size sliding window — simple and predictable, but can cut
# mid-sentence. A semantic/recursive chunker is a future upgrade.
chunking:
  strategy: "sliding_window"
  chunk_size_chars: 512
  overlap_chars: 100
  min_chunk_size_chars: 50

# Vector Database Configuration
vector_db:
  provider: "chromadb"
  host: "chromadb"
  port: 8000
  persist_directory: "/data/chromadb"
  distance_metric: "cosine"

# Retrieval Configuration
retrieval:
  top_k: 5
  similarity_threshold: 0.5
  enable_reranking: true
  reranker_model: "cross-encoder/ms-marco-MiniLM-L-12-v2"

# Caching Configuration
# Redis DB indices are separated so a cache flush/eviction never touches
# the Celery task queue: db 0 = app cache, db 1 = Celery broker/results.
cache:
  backend: "redis"
  redis_url: "${REDIS_CACHE_URL}"  # e.g. redis://redis:6379/0, from .env
  ttl_seconds: 3600
  max_size_mb: 1024
  eviction_policy: "allkeys-lru"

celery:
  broker_url: "${CELERY_BROKER_URL}"  # e.g. redis://redis:6379/1

# PostgreSQL Configuration
database:
  url: "${DATABASE_URL}"  # e.g. postgresql://user:pass@postgres:5432/rag_db, from .env — never commit real credentials
  pool_size: 20
  max_overflow: 10
  echo: false

# Observability Configuration
observability:
  # Prometheus Metrics
  prometheus:
    enabled: true
    port: 8001
    path: "/metrics"
  
  # Structured Logging with Loki
  logging:
    level: "INFO"
    format: "json"
    loki_enabled: true
    loki_url: "http://loki:3100"
    batch_size: 100
    flush_interval: 5
  
  # Distributed Tracing with Jaeger
  tracing:
    enabled: true
    jaeger_enabled: true
    jaeger_agent_host: "jaeger"
    jaeger_agent_port: 6831
    trace_sample_rate: 1.0  # Sample all traces
  
  # Grafana Dashboards
  grafana:
    enabled: true
    url: "http://grafana:3000"
    admin_password: "${GRAFANA_ADMIN_PASSWORD}"  # from .env, never a default like "admin"

# File Upload Configuration
file_upload:
  max_size_mb: 100
  allowed_types: ["pdf", "txt", "docx", "md"]
  upload_directory: "/data/uploads"
  scan_for_duplicates: true

# Security Configuration
security:
  enable_auth: true   # false is fine for local dev only — never in production
  cors_origins: ["http://localhost:3000", "http://localhost:8000"]
  rate_limit_enabled: true
  rate_limit_per_minute: 60
```

---

## 7. Project Structure

```
rag-knowledge-assistant/
├── docs/
│   ├── SYSTEM_DESIGN.md
│   ├── API_DOCUMENTATION.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── OBSERVABILITY_GUIDE.md
│   └── TROUBLESHOOTING.md
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── config.yaml
│   ├── document_ingestion/
│   │   ├── __init__.py
│   │   ├── parsers.py
│   │   ├── chunker.py
│   │   ├── preprocessor.py
│   │   └── deduplicator.py
│   ├── embeddings/
│   │   ├── __init__.py
│   │   ├── embedding_models.py
│   │   ├── cache.py
│   │   ├── embedding_service.py
│   │   └── metrics.py
│   ├── vector_db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── chromadb_client.py
│   │   ├── faiss_client.py
│   │   └── metrics.py
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── retriever.py
│   │   ├── bm25_index.py       # Builds/queries in-memory BM25 index
│   │   ├── reranker.py
│   │   ├── query_processor.py
│   │   └── metrics.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── ollama_client.py
│   │   ├── prompt_builder.py
│   │   ├── response_formatter.py
│   │   └── metrics.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── crud.py
│   │   └── connection.py
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── metrics.py          # Prometheus metrics
│   │   ├── logging.py          # Loki logging
│   │   ├── tracing.py          # Jaeger tracing
│   │   └── dashboards/
│   │       ├── rag_metrics.json
│   │       ├── embedding_metrics.json
│   │       ├── llm_metrics.json
│   │       └── system_health.json
│   └── api/
│       ├── __init__.py
│       ├── app.py
│       ├── auth.py             # API-key/JWT verification dependency
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── documents.py
│       │   ├── query.py
│       │   ├── health.py
│       │   └── metrics.py
│       └── schemas.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── notebooks/
│   ├── 01_exploration.ipynb
│   └── 02_evaluation.ipynb
├── scripts/
│   ├── setup_db.py
│   ├── seed_documents.py
│   ├── benchmark.py
│   └── generate_dashboards.py
├── kubernetes/
│   ├── namespace.yaml
│   ├── postgres.yaml
│   ├── redis.yaml
│   ├── chromadb.yaml
│   ├── ollama.yaml
│   ├── embedding-service.yaml
│   ├── rag-app.yaml
│   ├── prometheus.yaml
│   ├── loki.yaml
│   ├── jaeger.yaml
│   ├── grafana.yaml
│   ├── ingress.yaml
│   ├── backup-cronjob.yaml    # pg_dump + ChromaDB PV snapshot on a schedule
│   └── kustomization.yaml
├── docker/
│   ├── Dockerfile.embedding-service
│   ├── Dockerfile.rag-app
│   ├── prometheus.yml
│   ├── loki-config.yml
│   └── jaeger-config.yml
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .dockerignore
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py
└── CONTRIBUTING.md
```

---

## 8. Observability & Monitoring

### Metrics Collection (Prometheus)
```python
# Key metrics to track:

Application Metrics:
  - rag_documents_total              # Total documents ingested
  - rag_chunks_total                 # Total chunks created
  - rag_query_duration_ms            # Query latency
  - rag_retrieval_duration_ms        # Retrieval latency
  - rag_llm_generation_duration_ms   # LLM generation time
  - rag_token_count                  # Tokens used by LLM
  - rag_documents_ingested_total     # Count of ingested docs
  - rag_embedding_cache_hits_total   # Cache hit rate
  - rag_queries_total                # Total queries processed

Embedding Service Metrics:
  - embedding_request_duration_ms    # Embedding computation time
  - embedding_cache_hit_rate         # Cache effectiveness
  - embedding_batch_size             # Batch processing size
  - embedding_model_load_time_ms     # Model loading time

LLM Metrics:
  - llm_generation_duration_ms       # Token generation time
  - llm_tokens_total                 # Total tokens generated
  - llm_prompt_tokens                # Prompt tokens
  - llm_completion_tokens            # Completion tokens
  - llm_model_load_time_ms           # Model loading

Retrieval Metrics:
  - retrieval_top_k_duration_ms      # Vector search time
  - retrieval_rerank_duration_ms     # Reranking time
  - retrieval_chunks_retrieved       # Chunks returned

System Metrics:
  - system_memory_usage_bytes        # Memory consumption
  - system_cpu_usage_percent         # CPU usage
  - disk_usage_bytes                 # Storage usage
  - cache_size_bytes                 # Cache size
```

### Structured Logging (Loki)
```json
{
  "timestamp": "2024-01-20T10:30:45.123Z",
  "level": "INFO",
  "service": "rag-app",
  "component": "retrieval",
  "request_id": "uuid-xxx",
  "user_id": "user-123",
  "event": "query_processed",
  "query": "What are the key findings?",
  "retrieved_chunks": 5,
  "retrieval_time_ms": 45,
  "generation_time_ms": 2300,
  "total_time_ms": 2450,
  "tokens_used": 450,
  "confidence_score": 0.92,
  "metadata": {
    "model_version": "llama2-13b",
    "embedding_model": "all-mpnet-base-v2"
  }
}
```

### Distributed Tracing (Jaeger)
```
Trace spans for each request:
  ├── query_ingestion
  ├── query_embedding
  │   └── embedding_model_inference
  ├── vector_search
  │   ├── chromadb_query
  │   └── reranking
  ├── prompt_construction
  ├── llm_inference
  │   └── ollama_generation
  └── response_formatting
```

### Grafana Dashboards
```
Available Dashboards:
1. RAG System Overview
   - Total queries, average latency
   - Documents ingested, chunk stats
   - Cache hit rate, error rate

2. Embedding Service Health
   - Embedding latency distribution
   - Cache performance
   - Model resource usage

3. LLM Performance
   - Generation time by model
   - Token usage trends
   - Error rate and retry attempts

4. Vector Database
   - Search latency percentiles
   - Index size and memory
   - Query volume

5. System Resources
   - CPU, Memory, Disk usage
   - Network I/O
   - Container health

6. Query Analytics
   - Queries by type/user
   - Success/failure rates
   - Latency trends
```

---

## 9. Implementation Phases

### Phase 1: Core Infrastructure + Observability (Week 1-2)
- [x] Project setup and structure
- [x] System design documentation
- [ ] Database schema and migrations
- [ ] Document parsers (PDF, DOCX, TXT, MD)
- [ ] Text chunking with deduplication
- [ ] Prometheus metrics setup
- [ ] Structured logging with Loki
- [ ] Unit tests for core components

### Phase 2: Local Embedding Service (Week 2-3)
- [ ] Sentence-Transformers service setup
- [ ] Embedding generation pipeline
- [ ] Redis caching layer
- [ ] Embedding quality metrics
- [ ] Docker containerization
- [ ] Integration tests

### Phase 3: Vector Database & Retrieval (Week 3-4)
- [ ] ChromaDB integration
- [ ] Similarity search implementation
- [ ] BM25 reranking
- [ ] Query processing and validation
- [ ] Retrieval metrics tracking
- [ ] Integration tests

### Phase 4: Local Llama 3 LLM Integration (Week 4-5)
- [ ] Ollama setup with Llama 3
- [ ] LLM client implementation
- [ ] Prompt engineering and templates
- [ ] Response formatting with citations
- [ ] LLM metrics and monitoring
- [ ] Error handling and retries

### Phase 5: FastAPI & Web Service (Week 5-6)
- [ ] FastAPI application setup
- [ ] Document upload endpoints
- [ ] Query API with streaming
- [ ] Health checks and monitoring
- [ ] Error handling and validation
- [ ] API documentation (OpenAPI/Swagger)

### Phase 6: Kubernetes Deployment (Week 6-7)
- [ ] Kubernetes manifests creation
- [ ] ConfigMaps and Secrets setup
- [ ] Persistent volumes configuration
- [ ] Service mesh (optional)
- [ ] Horizontal Pod Autoscaling

### Phase 7: Observability & Dashboards (Week 7-8)
- [ ] Jaeger distributed tracing setup
- [ ] Grafana dashboard creation
- [ ] Alert rules configuration
- [ ] Log aggregation and querying
- [ ] Performance optimization based on metrics

---

## 10. Data Flow Example

```
User uploads "research.pdf"
    ↓
[Parser] Extracts text, metadata → Logs event
    ↓
[Deduplicator] Checks file hash → Prometheus metric
    ↓
[Chunker] Splits into 512-char overlapping chunks → Logs chunks count
    ↓
[Embedder (Local)] Generates 768-dim vectors → Tracks latency in Prometheus
    ↓
[ChromaDB] Stores vectors with metadata → Logs storage metrics
    ↓
User submits query: "What are the key findings?"
    ↓
[Query Logger] Logs query with timestamp, user_id → Loki ingestion
    ↓
[Embedder (Local)] Encodes query to 768-dim vector → Tracks cache hit/miss
    ↓
[ChromaDB Search] Finds top-5 similar chunks → Records search latency
    ↓
[Reranker] Re-scores for relevance → Prometheus metric
    ↓
[Prompt Builder] Creates context-aware prompt → Logs token count
    ↓
[Llama 3 (Local)] Generates answer via Ollama → Tracks generation time
    ↓
[Response Formatter] Adds citations and confidence → Jaeger trace span
    ↓
[Response] Returns answer + sources + metrics → Traces complete
```

---

## 11. Cost & Infrastructure Analysis

### **Monthly Cost: $0 (Self-Hosted)**

| Component | Cost | Alternative |
|-----------|------|-------------|
| Ollama (Llama 3) | Free | - |
| Sentence-Transformers | Free | - |
| ChromaDB | Free | - |
| PostgreSQL | Free | - |
| Redis | Free | - |
| Prometheus | Free | - |
| Loki | Free | - |
| Jaeger | Free | - |
| Grafana | Free | - |
| **Total** | **$0** | **100% Open Source** |

### **Resource Requirements (Kubernetes)**

```
CPU: 4-8 cores
Memory: 16-32 GB
Storage: 50-100 GB (depending on documents)
GPU: Optional (4-8GB for faster inference)

Can run on:
- Laptop/Desktop
- Single bare-metal server
- Kubernetes cluster
- Docker Swarm
```

### Backup & Disaster Recovery
Postgres (documents/chunks/users metadata) and ChromaDB (vectors) are both
stateful and are the only copies of ingested knowledge — losing them means
re-ingesting every document. `kubernetes/backup-cronjob.yaml` runs a nightly
`pg_dump` and a ChromaDB persistent-volume snapshot to external storage.
Uploaded source files in `/data/uploads` should be backed up the same way,
since chunks can't be regenerated without the originals.

---

## 12. Security & Best Practices

### Security Implementation
Status reflects the design, not a finished build (see Section 9 for what's
actually implemented so far).
- [ ] Input validation & sanitization (Pydantic schemas — planned)
- [ ] File upload malware scanning (e.g. ClamAV) — hash-based dedup only so far, NOT a security scan
- [ ] API authentication (API key/JWT via `api/auth.py` + `users` table — planned)
- [ ] Rate limiting
- [ ] Secrets via environment variables / secret store (no plaintext credentials in config — see Section 6)
- [ ] Audit logging with Loki
- [ ] RBAC (`users.role` column exists in schema — enforcement not yet built)

### Performance Optimization
- [x] Batch embedding generation
- [x] Vector DB indexing optimization
- [x] Redis caching layer
- [x] Horizontal pod autoscaling
- [x] Query result caching
- [x] Local model inference (no API latency)

### Monitoring & Alerting
- [x] Prometheus metrics collection
- [x] Grafana dashboards
- [x] Loki log aggregation
- [x] Jaeger distributed tracing
- [x] Alert rules for critical metrics
- [x] Health check endpoints

---

## 13. Evaluation Metrics

### Retrieval Quality
- **NDCG (Normalized Discounted Cumulative Gain)**: 0.75+
- **MRR (Mean Reciprocal Rank)**: 0.80+
- **Hit Rate@5**: 0.85+
- **F1 Score**: 0.80+

### Response Quality
BLEU/ROUGE are reference-translation/summarization metrics and a poor fit
for open-ended QA, where many correct phrasings exist. Use RAG-specific,
LLM-judged metrics instead (e.g. via the RAGAS framework):
- **Faithfulness** (is the answer actually supported by the retrieved chunks, not hallucinated?): 0.90+
- **Answer Relevancy** (does the answer address the question asked?): 0.85+
- **Context Precision** (are the retrieved chunks actually relevant?): 0.80+
- **Human Evaluation**: 4/5 stars

### System Performance
- **P50 Latency**: < 500ms
- **P95 Latency**: < 2s
- **P99 Latency**: < 5s
- **Throughput**: 10+ concurrent queries

### Cost Efficiency
- **Per-query cost**: $0
- **Monthly cost**: $0
- **ROI**: Infinite (Free infrastructure)

---

## 14. Open Source Dependencies

All dependencies are free and open source. Most are permissively licensed
(Apache 2.0, MIT, BSD); Loki and Grafana are AGPLv3, which is still free
to self-host but has stricter terms if you ever modify and redistribute
them as a service — irrelevant for this project's internal, self-hosted use:

```
Core:
  ✓ FastAPI (MIT)
  ✓ Pydantic (MIT)
  ✓ SQLAlchemy (MIT)
  ✓ ChromaDB (Apache 2.0)

ML/AI:
  ✓ Sentence-Transformers (Apache 2.0)
  ✓ Torch (BSD)
  ✓ Transformers (Apache 2.0)
  ✓ Ollama (MIT)

Observability:
  ✓ Prometheus (Apache 2.0)
  ✓ Loki (AGPL - but can self-host)
  ✓ Jaeger (Apache 2.0)
  ✓ Grafana (AGPL - but can self-host)

Database:
  ✓ PostgreSQL (PostgreSQL License - free)
  ✓ Redis (BSD)

Testing:
  ✓ Pytest (MIT)
  ✓ Pytest-cov (MIT)
```

---

## 15. Quick Start (Self-Hosted)

```bash
# Clone repository
git clone https://github.com/ankitagadage/rag-knowledge-assistant.git
cd rag-knowledge-assistant

# Copy environment
cp .env.example .env

# Start everything with Docker Compose
docker-compose up -d

# Verify services
docker-compose ps

# Access dashboards
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
# - Jaeger: http://localhost:16686
# - API Docs: http://localhost:8000/docs
```

---

**No vendor lock-in. No API costs. Complete observability. Full control. 100% Open Source. 🚀**

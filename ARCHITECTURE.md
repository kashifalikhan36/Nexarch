# Nexarch — Architecture Intelligence Platform

**Technical Design and Implementation Document**

---

## 1. Vision and Core Problem

### 1.1 The Problem: Architecture Drift and Invisible Complexity

Production systems evolve organically. Microservices multiply. Dependencies entangle. Performance degrades. Errors cascade. Yet most teams lack runtime visibility into their actual architecture.

Traditional observability tools provide logs, metrics, and traces but stop short of architectural intelligence. They answer "what happened?" but not "what is the structure?" or "where are the systemic bottlenecks?"

Engineering teams face several critical gaps:

1. **Static documentation becomes stale immediately** - Architecture diagrams drawn in the design phase bear little resemblance to the runtime system six months later.

2. **No automated dependency mapping** - Teams manually maintain service catalogs that are perpetually outdated.

3. **Issue detection is reactive** - Problems surface as incidents rather than being predicted through structural analysis.

4. **Migration planning is guesswork** - Without runtime dependency data, refactoring proposals are based on assumptions rather than evidence.

5. **No comparison of remediation strategies** - Teams lack tooling to evaluate multiple architectural changes and their tradeoffs.

### 1.2 Why Nexarch Exists

Nexarch solves architecture visibility by reconstructing the runtime dependency graph from production telemetry. It goes beyond traditional APM by:

- **Automatic discovery**: Infers services, databases, and external dependencies from actual call patterns
- **Structural analysis**: Applies graph algorithms to detect anti-patterns (deep call chains, high fan-out, single points of failure)
- **Evidence-based issue detection**: Every detected issue is backed by quantitative metrics (latency, error rates, call volume)
- **Multi-strategy workflow generation**: Produces multiple remediation plans with complexity/risk/impact scoring
- **Non-linear reasoning**: Uses LangGraph to reason through issue categorization, strategy selection, and workflow generation with conditional branching logic

Nexarch makes the invisible architecture visible and provides actionable intelligence for refactoring decisions.

---

## 2. System Overview

### 2.1 Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                   CLIENT APPLICATIONS                        │
│            (AI Agents, CLIs, Dashboards)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ MCP Protocol
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastMCP SERVER                            │
│     (Stateless read-only interface to core services)       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Function Calls
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   NEXARCH BACKEND                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Ingestion  │  │   Graph      │  │   Issue      │     │
│  │   Service    │  │   Service    │  │   Detector   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │   Metrics    │  │   Workflow   │                        │
│  │   Service    │  │   Generator  │                        │
│  └──────────────┘  └──────────────┘                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          LangGraph Reasoning Pipeline                │  │
│  │  (Non-linear issue classification and strategy       │  │
│  │   selection with conditional branching)              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ SQL
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE LAYER                             │
│        (Raw spans, architecture snapshots)                  │
└─────────────────────────────────────────────────────────────┘
                     ▲
                     │
                     │ HTTP POST /api/v1/ingest
                     │
┌─────────────────────────────────────────────────────────────┐
│              NEXARCH PYTHON SDK                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Middleware  │  │  Tracing     │  │  Queue &     │     │
│  │  (Request    │  │  Context     │  │  Exporters   │     │
│  │  Intercept)  │  │  Propagation │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  HTTP Library Instrumentation (requests, httpx)      │  │
│  │  (Monkey-patching for downstream call detection)     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                     ▲
                     │
                     │ Installed via pip
                     │
┌─────────────────────────────────────────────────────────────┐
│               USER'S FASTAPI APPLICATION                     │
│          (Production services with Nexarch SDK)             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

1. **Telemetry Collection**: User's FastAPI application includes Nexarch SDK → Middleware intercepts all HTTP requests → Instrumentation patches capture outbound calls → Spans generated with trace context
2. **Local Buffering**: Spans queued in thread-safe async queue → Background worker batches and flushes to local JSON or HTTP endpoint
3. **Ingestion**: Backend receives spans via POST /api/v1/ingest → Validates and stores raw spans in database
4. **Graph Construction**: Graph Service reads all spans → Builds NetworkX directed graph (nodes = services, edges = dependencies) → Aggregates metrics per edge
5. **Issue Detection**: Rule Engine runs deterministic checks on graph → Detects latency issues, deep chains, error rates, fan-out, single points of failure
6. **Workflow Reasoning**: LangGraph pipeline runs non-linear reasoning → Classifies issues → Selects strategies → Generates 3 workflow alternatives (minimal, performance, cost)
7. **MCP Interface**: FastMCP exposes read-only tools → AI agents query architecture, issues, workflows → No side effects

### 2.3 Separation of Concerns

| Layer | Responsibility | State |
|-------|---------------|-------|
| SDK | Transparent telemetry capture | Stateless (context-aware) |
| Backend Services | Business logic (graph construction, metrics, issue detection) | Stateful (database-backed) |
| Reasoning Pipeline | Non-linear decision logic | Stateless (pure functions) |
| MCP Server | Protocol adapter for AI agents | Stateless (read-only) |
| Database | Persistent storage of raw telemetry | Stateful |

---

## 3. Design Principles

### 3.1 Runtime-First Analysis

Nexarch does not rely on static code analysis, annotations, or manual configuration. It reconstructs architecture from actual production behavior. This principle ensures:

- **Accuracy**: The graph reflects reality, not intent
- **No maintenance burden**: No manual service registry to update
- **Production fidelity**: Captures actual call patterns, not hypothetical ones

### 3.2 Deterministic Core Logic

Issue detection and metric computation are deterministic. Given the same graph, the same issues will be detected. This is critical for:

- **Reproducibility**: Engineers can trust results
- **Testability**: Rules can be unit tested
- **Debugging**: No black-box AI decisions

AI enhancement is layered on top (LangGraph reasoning, optional LLM-based explanations) but the core logic is rule-based.

### 3.3 SDK Invisibility

The SDK operates with near-zero performance overhead and zero code changes in user applications. Principles:

- **Async logging**: Telemetry export happens in background threads
- **Sampling support**: Drop spans probabilistically to reduce load
- **Graceful degradation**: If export fails, application continues
- **No blocking I/O in hot path**: Middleware adds <1ms overhead per request

### 3.4 Layered Architecture

Each layer has a single responsibility and communicates through well-defined interfaces:

- **SDK → Backend**: HTTP POST with span JSON (can be replaced with gRPC, Kafka, etc.)
- **Services → Database**: SQLAlchemy ORM (can swap database engines)
- **MCP → Services**: Direct Python function calls (MCP is a thin wrapper)
- **LangGraph → Services**: Graph algorithms and rule outputs fed into reasoning pipeline

### 3.5 MCP as Adapter, Not Core

FastMCP is an interface layer, not the system itself. Nexarch's services exist independently. MCP provides:

- **Standardized protocol**: AI agents use MCP tools to query architecture
- **Read-only safety**: MCP tools have no side effects
- **Decoupling**: MCP can be removed without affecting core functionality

This design allows Nexarch to serve multiple clients (REST API, GraphQL, gRPC, CLI) without rewriting core logic.

### 3.6 AI as Enhancement, Not Dependency

LangGraph reasoning enhances workflow generation but is not required for the system to function. Core capabilities (ingestion, graph construction, issue detection, metrics) work without AI. AI adds:

- **Sophisticated workflow generation**: Multi-strategy comparison
- **Natural language explanations**: Via optional LLM integration
- **Adaptive reasoning**: Conditional branching based on issue types

If AI components fail, the system degrades gracefully to rule-based outputs.

---

## 4. Nexarch Python SDK

### 4.1 Purpose of the SDK

The SDK's mission is to capture runtime telemetry from user applications without requiring code instrumentation. It achieves this by:

1. **Intercepting HTTP requests** at the FastAPI middleware layer
2. **Propagating trace context** through the application call stack
3. **Detecting downstream calls** via monkey-patching of HTTP libraries
4. **Exporting telemetry** to local files or remote endpoints

The SDK is designed to be invisible. User applications add two lines:

```python
from nexarch import NexarchSDK

NexarchSDK.start(app, api_key="...")
```

### 4.2 SDK Architecture

#### Components

1. **NexarchMiddleware**: ASGI middleware that wraps every incoming HTTP request
2. **Tracing Context**: `contextvars`-based trace ID and span ID propagation across async boundaries
3. **Span**: OpenTelemetry-inspired data structure for representing operations
4. **Instrumentation Patches**: Monkey-patching of `requests` and `httpx` to intercept outbound calls
5. **LogQueue**: Thread-safe async queue for buffering telemetry
6. **Exporters**: Pluggable backends for telemetry export (local JSON, HTTP POST)
7. **Router**: Optional internal endpoints for health checks and telemetry introspection

#### Internal Flow

```
Incoming Request
    ↓
NexarchMiddleware.dispatch()
    ├─ Generate trace_id, span_id
    ├─ Set trace context (contextvars)
    ├─ Create server span
    ├─ Measure latency
    ├─ Capture status code / errors
    ├─ Finish span
    └─ Enqueue span to LogQueue
        ↓
LogQueue (background thread)
    ├─ Batch spans (up to 100 or 1 second timeout)
    └─ Flush to Exporter
        ↓
Exporter
    ├─ LocalJSONExporter → Append to file
    └─ HttpExporter → POST to backend
```

### 4.3 Request Lifecycle

#### Step-by-step execution:

1. **Request arrives** at FastAPI application
2. **Middleware intercepts** via `dispatch()`
3. **Sampling decision** made (probabilistic, configurable rate)
4. **Trace context established**:
   - `trace_id` = UUID v4 (unique per request)
   - `span_id` = UUID v4 (unique per operation)
   - Context set via `contextvars` (async-safe)
5. **Server span created**:
   - `kind = "server"`
   - `operation = "GET /api/users"`
   - `start_time = utcnow()`
6. **Request processed** by application handler
7. **Downstream calls detected**:
   - If handler calls `requests.get()` or `httpx.get()`
   - Instrumentation patch intercepts call
   - Creates **client span** with `parent_span_id = server span_id`
   - Links child span to parent trace
8. **Response returned** to client
9. **Span finalized**:
   - `end_time = utcnow()`
   - `latency_ms = (end_time - start_time) * 1000`
   - `status_code` and `error` captured
10. **Span enqueued** to `LogQueue`
11. **Background worker** batches and exports span
12. **Trace context cleared** (cleanup for next request)

#### Error Handling

If an exception occurs:
- Span marked with `status = "error"`, `status_code = 500`
- Error message and traceback captured in `ErrorData`
- Exception re-raised (SDK does not suppress errors)
- Partial span still exported (important for failure analysis)

### 4.4 Dependency Instrumentation

#### Why Monkey-Patching?

Python's HTTP libraries (`requests`, `httpx`) do not natively support tracing hooks. To detect downstream calls, Nexarch replaces their internal methods with wrapped versions.

#### Implementation

```python
# Original function stored
_original_request = requests.Session.request

# Wrapper installed
def _instrumented_request(self, method, url, **kwargs):
    trace_id = get_trace_id()  # From contextvars
    parent_span_id = get_span_id()
    
    if not trace_id:
        return _original_request(self, method, url, **kwargs)
    
    # Create client span
    span_id = str(uuid.uuid4())
    span = Span.create_client_span(
        trace_id=trace_id,
        span_id=span_id,
        parent_span_id=parent_span_id,
        service="downstream",
        operation=f"{method} {url}"
    )
    
    # Execute actual request
    response = _original_request(self, method, url, **kwargs)
    
    # Finish and export span
    span.finish(status_code=response.status_code)
    get_log_queue().enqueue(span.to_dict())
    
    return response
```

#### Why This Approach?

1. **Zero code changes** in user applications
2. **Automatic propagation** of trace context to all outbound calls
3. **Captures real dependency topology** (not guessed from static analysis)

#### Tradeoffs

- **Fragility**: Monkey-patching can break if library internals change
- **Coverage**: Only patches `requests` and `httpx` (not `urllib3`, `aiohttp`, etc.)
- **Performance**: Small overhead per outbound call (~0.5ms)

Mitigation: SDK includes fallback logic if patching fails. Core telemetry still works without downstream span capture.

### 4.5 Data Model

#### Span Structure

```python
@dataclass
class Span:
    trace_id: str              # UUID linking all spans in a request
    span_id: str               # UUID for this operation
    parent_span_id: Optional[str]  # Parent span (None for root)
    service_name: str          # e.g., "production"
    operation: str             # e.g., "GET /api/users"
    kind: str                  # "server", "client", "internal"
    start_time: str            # ISO 8601 timestamp
    end_time: Optional[str]    # ISO 8601 timestamp
    latency_ms: Optional[float]  # Computed from start/end
    status_code: Optional[int]   # HTTP status (200, 500, etc.)
    error: Optional[str]         # Error message if failed
    tags: Dict[str, Any]         # Custom metadata
```

#### Error Structure

```python
@dataclass
class ErrorData:
    trace_id: str
    span_id: str
    timestamp: str
    error_type: str            # Exception class name
    error_message: str         # Exception message
    traceback: str             # Full Python traceback
    service: str
    operation: str
    method: str
    path: str
    query_params: Dict[str, Any]
```

#### Why These Fields?

- `trace_id`: Enables correlation of all spans in a distributed request
- `parent_span_id`: Reconstructs call hierarchy (parent → child relationships)
- `kind`: Distinguishes incoming requests ("server") from outgoing calls ("client")
- `downstream`: Identifies target service for graph edge construction
- `latency_ms`: Core metric for performance analysis
- `status_code` + `error`: Distinguishes success from failure

### 4.6 Why These Choices Were Made

#### OpenTelemetry Conceptual Alignment

Nexarch's span model mirrors OpenTelemetry (trace ID, span ID, parent relationships, span kinds) for three reasons:

1. **Industry standard**: Engineers familiar with OTel concepts can understand Nexarch immediately
2. **Interoperability potential**: Future support for OTel Collector as an export target
3. **Proven model**: OTel's design has been battle-tested across thousands of systems

Nexarch does NOT implement full OTel protocol (too heavy), but reuses its vocabulary.

#### Local-First Logging

SDK defaults to writing telemetry to local JSON files because:

1. **Zero dependencies**: No external services required to start using Nexarch
2. **Debugging aid**: Engineers can inspect `nexarch_telemetry.json` directly
3. **Data ownership**: Telemetry stays in user's infrastructure
4. **Batch ingestion**: Users can process local files at their own pace

HTTP export is optional for real-time streaming to Nexarch backend.

#### Async Logging Queue

Telemetry export runs in a background thread with batching to:

1. **Minimize latency impact**: No synchronous I/O in request hot path
2. **Handle bursts**: Queue buffers spans during traffic spikes
3. **Graceful degradation**: If queue fills, new spans are dropped silently (better than crashing production)

Tradeoff: Telemetry may be delayed by up to 1 second (flush interval). This is acceptable for architecture intelligence (not real-time alerting).

#### Sampling Support

Sampling rate (default 100%, configurable down to 1%) allows users to:

1. **Reduce overhead** in ultra-high-throughput systems
2. **Control costs** if using external backend
3. **Focus on representative traffic** (statistical sampling gives accurate architecture graph)

Sampling is head-based (decision at trace start) to avoid partial traces.

---

## 5. Telemetry Ingestion Backend

### 5.1 Ingestion API

#### Endpoint Design

```
POST /api/v1/ingest
Content-Type: application/json

{
  "trace_id": "a1b2c3...",
  "span_id": "x7y8z9...",
  "parent_span_id": null,
  "service_name": "production",
  "operation": "GET /api/users",
  "kind": "server",
  "start_time": "2026-01-16T10:30:00.000Z",
  "end_time": "2026-01-16T10:30:00.123Z",
  "latency_ms": 123.45,
  "status_code": 200,
  "error": null,
  "downstream": "postgres://users-db"
}
```

Response: `202 Accepted` with `span_id` acknowledgment

#### Validation Strategy

Ingestion uses Pydantic models for validation:

```python
class Span(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    service_name: str
    operation: str
    kind: str
    start_time: datetime
    end_time: datetime
    latency_ms: float
    status_code: Optional[int]
    error: Optional[str]
    downstream: Optional[str]
```

Invalid spans are rejected with `400 Bad Request`. This ensures database integrity.

#### Why 202 Accepted?

Ingestion is async-safe. The API returns immediately after validation, queuing span for storage. This decouples ingestion from database write latency.

### 5.2 Data Storage

#### Raw Span Persistence

All spans are stored in relational database (SQLite by default, PostgreSQL/MySQL for production):

```sql
CREATE TABLE spans (
    id INTEGER PRIMARY KEY,
    trace_id VARCHAR(64) NOT NULL,
    span_id VARCHAR(32) UNIQUE NOT NULL,
    parent_span_id VARCHAR(32),
    service_name VARCHAR(255) NOT NULL,
    operation VARCHAR(255) NOT NULL,
    kind VARCHAR(32) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    latency_ms FLOAT NOT NULL,
    status_code INTEGER,
    error TEXT,
    downstream VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_trace_start (trace_id, start_time),
    INDEX idx_service_time (service_name, start_time)
);
```

#### Why Raw Data is Preserved

Nexarch stores spans in their original form (no aggregation, no rollup) for:

1. **Flexible queries**: Graph can be reconstructed with different time windows or filters
2. **Audit trail**: Full history of system behavior is retained
3. **Retroactive analysis**: New rules can be applied to historical data
4. **Debugging**: Engineers can inspect individual spans for deep investigations

#### Tradeoffs

- **Storage growth**: Spans accumulate over time (mitigated by retention policies, time-based partitioning)
- **Query performance**: Full table scans for graph reconstruction (mitigated by indexes, materialized views)

For high-scale deployments, consider:
- Time-series database (InfluxDB, TimescaleDB)
- Stream processing (Kafka → Flink → aggregated views)
- Archival to object storage (S3/GCS for cold data)

---

## 6. Architecture Reconstruction Engine

### 6.1 Dependency Graph Model

#### Nodes

A **node** represents a service, database, or external system. Node types:

- `service`: Internal application services (identified by `service_name`)
- `database`: Databases (inferred from downstream strings containing "postgres", "mysql", "redis", "mongo", "dynamodb", "cosmosdb")
- `external`: External APIs (inferred from downstream strings containing "http://", "https://", "api.", "external")

Node attributes:
- `id`: Unique identifier (e.g., "production", "postgres://users-db")
- `type`: service | database | external
- `metrics`: Aggregated stats (avg latency, error rate, call count)

#### Edges

An **edge** represents a dependency relationship (caller → callee). Edges are directed.

Edge attributes:
- `source`: Calling service
- `target`: Called service/database/external
- `call_count`: Total number of calls observed
- `avg_latency_ms`: Mean latency across all calls
- `error_rate`: Fraction of calls that failed (status_code >= 500 or error present)

#### Why NetworkX?

NetworkX is Python's standard graph library. It provides:

- **Graph algorithms**: Shortest paths, centrality, cycle detection, topological sorting
- **Flexible data model**: Arbitrary attributes on nodes and edges
- **Visualization**: Integration with Matplotlib, Graphviz
- **Mature ecosystem**: Well-documented, stable API

### 6.2 Graph Construction

#### Algorithm

```
1. Query all spans from database
2. Extract unique service names → nodes
3. Extract unique downstream targets → nodes
4. Classify each node type (service / database / external)
5. Group spans by (source, target) pair
6. For each pair:
   - Create edge
   - Compute call_count = len(spans)
   - Compute avg_latency_ms = mean(span.latency_ms)
   - Compute error_rate = count(span.error or span.status_code >= 500) / call_count
7. Add nodes and edges to NetworkX DiGraph
8. Attach metrics to nodes and edges
```

#### How Services, Databases, and Externals Are Identified

**Service**: Default classification. If downstream is not a database or external, it's treated as an internal service.

**Database**: Heuristic matching on downstream string:
- Contains "postgres", "mysql", "mongo", "redis", "dynamodb", "cosmosdb"
- Example: `"postgres://users-db"` → type = "database"

**External**: Heuristic matching on downstream string:
- Contains "http://", "https://", "api."
- Example: `"https://api.stripe.com"` → type = "external"

These heuristics are pragmatic. They work for 90% of systems. For edge cases, users can override node types via configuration (future enhancement).

#### Why This Matters

Distinguishing databases from services enables:
- **Targeted issue detection**: Different rules for database latency vs. service latency
- **Visualization**: Different icons/colors in architecture diagrams
- **Migration planning**: Workflows can propose database replication separately from service scaling

### 6.3 Why NetworkX

#### Benefits

1. **Rich algorithm library**: Nexarch uses shortest path length (for deep chain detection), in/out degree (for fan-out detection), betweenness centrality (for bottleneck detection), cycle detection (for circular dependencies)
2. **Pythonic API**: Integrates naturally with FastAPI backend
3. **No external dependencies**: Pure Python, no graph database required
4. **Fast for small/medium graphs**: <1000 nodes handled efficiently in-memory

#### Tradeoffs

1. **In-memory only**: NetworkX cannot handle million-node graphs (not Nexarch's target use case)
2. **No persistence**: Graph must be rebuilt from spans on every query (mitigated by caching, materialized views)
3. **Single-threaded**: No parallelism for graph algorithms (acceptable for <1000 nodes)

For ultra-scale (>10,000 services), consider Neo4j or TigerGraph. Nexarch's current design prioritizes simplicity over scale.

---

## 7. Metrics Aggregation

### 7.1 Computation Logic

#### Latency Aggregation

```python
avg_latency_ms = sum(span.latency_ms for span in spans) / len(spans)
```

Why mean (not median/p99)? Mean is simpler and sufficient for architecture-level analysis. Nexarch is not replacing APM tools (which need percentiles). If an edge has mean latency >1000ms, it's a problem regardless of p99.

#### Error Rate Calculation

```python
error_count = count(span for span in spans if span.error or span.status_code >= 500)
error_rate = error_count / len(spans)
```

Errors defined as: `status_code >= 500` OR `error field is not null`.

Why >=500? HTTP 4xx are client errors (bad requests). HTTP 5xx are server errors (system failures). Nexarch focuses on system-level issues.

#### Call Volume Computation

```python
call_count = len(spans)
```

Simple count of observed calls. Used for:
- Identifying hotspots (edges with high traffic)
- Filtering noise (edges with <10 calls may be spurious)
- Weighting issues (a latency issue on 10,000 calls/day is more critical than on 10 calls/day)

### 7.2 Why These Metrics Were Chosen

These three metrics (latency, error rate, call volume) form the minimal set for architectural decisions:

1. **Latency**: Indicates performance bottlenecks
2. **Error rate**: Indicates reliability issues
3. **Call volume**: Indicates load distribution and dependency strength

Additional metrics (CPU, memory, disk I/O) are valuable but require agent-based collection (out of scope for SDK-based approach).

---

## 8. Issue Detection Engine

### 8.1 Rule-Based Detection

#### Why Rules Come Before AI

Deterministic rules are the foundation of Nexarch's issue detection. Rules are:

1. **Explainable**: Engineers can trace why an issue was flagged
2. **Testable**: Rules can be unit tested with synthetic graphs
3. **Fast**: No LLM latency, no API costs
4. **Reliable**: Same graph → same issues (no non-determinism)

AI-based detection (LLMs analyzing logs) can augment rules but cannot replace them. Without rules, the system is a black box.

### 8.2 Implemented Rules

#### Rule 1: High Latency Edges

```python
def detect_high_latency_edges(G: nx.DiGraph) -> List[Issue]:
    threshold = 1000  # ms (configurable)
    issues = []
    
    for source, target, data in G.edges(data=True):
        latency = data.get("avg_latency_ms", 0)
        if latency > threshold:
            issues.append(Issue(
                severity="high",
                type="high_latency_edge",
                description=f"Edge {source} → {target} has high latency ({latency:.0f}ms)",
                affected_nodes=[source, target],
                metric_value=latency,
                evidence={
                    "threshold": threshold,
                    "actual": latency,
                    "call_count": data.get("call_count", 0)
                }
            ))
    
    return issues
```

**Why this rule?** Latency directly impacts user experience. If service A → service B takes >1 second, it's a bottleneck.

**Threshold rationale**: 1000ms is aggressive for modern systems. Configurable via `HIGH_LATENCY_THRESHOLD_MS`.

#### Rule 2: Deep Synchronous Call Chains

```python
def detect_deep_sync_chains(G: nx.DiGraph) -> List[Issue]:
    max_depth = 5  # configurable
    issues = []
    
    for node in G.nodes():
        paths = nx.single_source_shortest_path_length(G, node)
        max_path = max(paths.values()) if paths else 0
        
        if max_path > max_depth:
            issues.append(Issue(
                severity="medium",
                type="deep_sync_chain",
                description=f"Service {node} has deep sync chain (depth={max_path})",
                affected_nodes=[node],
                metric_value=float(max_path),
                evidence={"threshold": max_depth, "actual_depth": max_path}
            ))
    
    return issues
```

**Why this rule?** Deep chains amplify latency. If A → B → C → D → E → F, and each hop adds 100ms, total latency is 500ms. Chains also increase failure risk (cascade errors).

**Threshold rationale**: Depth >5 indicates poor decomposition (too many synchronous hops).

#### Rule 3: High Error Rate Nodes

```python
def detect_high_error_nodes(G: nx.DiGraph) -> List[Issue]:
    threshold = 0.05  # 5% error rate
    issues = []
    
    for node, data in G.nodes(data=True):
        metrics = data.get("metrics", {})
        error_rate = metrics.get("error_rate", 0)
        
        if error_rate > threshold:
            issues.append(Issue(
                severity="critical",
                type="high_error_rate",
                description=f"Service {node} has high error rate ({error_rate*100:.1f}%)",
                affected_nodes=[node],
                metric_value=error_rate,
                evidence={
                    "threshold": threshold,
                    "actual": error_rate,
                    "call_count": metrics.get("call_count", 0)
                }
            ))
    
    return issues
```

**Why this rule?** Error rate >5% indicates systemic reliability issues (not transient failures).

**Severity justification**: Critical because errors directly impact availability.

#### Rule 4: Fan-Out Overload

```python
def detect_fan_out_overload(G: nx.DiGraph) -> List[Issue]:
    max_fan_out = 10
    issues = []
    
    for node in G.nodes():
        out_degree = G.out_degree(node)
        
        if out_degree > max_fan_out:
            issues.append(Issue(
                severity="medium",
                type="fan_out_overload",
                description=f"Service {node} calls too many services ({out_degree})",
                affected_nodes=[node],
                metric_value=float(out_degree),
                evidence={
                    "threshold": max_fan_out,
                    "actual": out_degree,
                    "targets": list(G.successors(node))
                }
            ))
    
    return issues
```

**Why this rule?** Excessive fan-out indicates:
- Poor service boundaries (doing too many things)
- Potential for scatter-gather latency (sequential calls to many services)
- Increased coupling (changes in any downstream break this service)

**Threshold rationale**: >10 outbound calls is a code smell.

#### Rule 5: Single Point of Failure

```python
def detect_single_point_of_failure(G: nx.DiGraph) -> List[Issue]:
    issues = []
    
    for node in G.nodes():
        in_degree = G.in_degree(node)
        
        if in_degree > 5:
            issues.append(Issue(
                severity="high",
                type="single_point_of_failure",
                description=f"Service {node} is SPOF with {in_degree} dependencies",
                affected_nodes=[node],
                metric_value=float(in_degree),
                evidence={
                    "dependent_services": list(G.predecessors(node)),
                    "in_degree": in_degree
                }
            ))
    
    return issues
```

**Why this rule?** If many services depend on one service, its failure cascades. This is a structural risk.

**Threshold rationale**: >5 incoming edges indicates critical service (requires redundancy, circuit breakers, fallbacks).

### 8.3 Evidence Generation

Every issue includes:

1. **Quantitative metric**: The actual value that triggered the rule (e.g., latency = 1250ms)
2. **Threshold**: The configured limit (e.g., threshold = 1000ms)
3. **Context**: Additional data (e.g., call_count, affected services)

Example:

```json
{
  "id": "latency-a7f3e2d1",
  "severity": "high",
  "type": "high_latency_edge",
  "description": "Edge production → postgres://users-db has high latency (1250ms)",
  "affected_nodes": ["production", "postgres://users-db"],
  "metric_value": 1250.0,
  "evidence": {
    "threshold": 1000,
    "actual": 1250.0,
    "call_count": 4523
  }
}
```

#### Why Evidence is Critical for Trust

Without evidence, issue detection is magic. With evidence, it's transparent. Engineers can:

- Verify the issue by querying raw spans
- Adjust thresholds if false positive
- Understand issue severity from metrics

---

## 9. Workflow Generation System

### 9.1 Purpose

Nexarch generates **multiple workflow alternatives** for remediating detected issues. Each workflow proposes a different strategy with tradeoffs:

1. **Minimal Migration**: Quick fixes, low risk, low impact
2. **Performance Optimized**: Maximize throughput, higher cost/complexity
3. **Cost Optimized**: Reduce operational costs, may sacrifice peak performance

#### Why Multiple Workflows?

Different teams have different priorities:
- Startups: Minimize risk, ship fast (choose Minimal)
- High-traffic SaaS: Maximize performance (choose Performance)
- Mature systems: Reduce costs (choose Cost)

Generating all three allows **comparison**. Teams can see tradeoffs explicitly (complexity score, risk score, expected impact).

### 9.2 Workflow Types

#### Minimal Migration Workflow

**Philosophy**: Address top 3 issues with simplest possible changes.

Example changes:
- Add Redis cache for high-latency database queries
- Add circuit breaker for unreliable external API
- Enhance logging for error-prone service

**Scores**:
- Complexity: 2/10 (low)
- Risk: 1/10 (minimal)

**Expected Impact**:
- Latency improvement: 10-20%
- Error reduction: 20-30%
- Cost increase: 5-10%

#### Performance Optimized Workflow

**Philosophy**: Maximize throughput and reduce latency, even if it requires significant changes.

Example changes:
- Implement distributed cache (Redis cluster)
- Convert synchronous chains to async (message queue)
- Add CDN for static assets
- Database read replicas

**Scores**:
- Complexity: 6/10 (moderate-high)
- Risk: 4/10 (moderate)

**Expected Impact**:
- Latency improvement: 50-70%
- Error reduction: 10-20%
- Cost increase: 30-50%

#### Cost Optimized Workflow

**Philosophy**: Reduce operational costs while maintaining reliability.

Example changes:
- Consolidate downstream calls (batch requests)
- Optimize retry logic (exponential backoff with jitter)
- Right-size service instances (reduce over-provisioning)
- Database connection pooling

**Scores**:
- Complexity: 4/10 (moderate)
- Risk: 3/10 (low-moderate)

**Expected Impact**:
- Latency improvement: 5-10%
- Error reduction: 15-25%
- Cost increase: -20% to -30% (cost reduction)

### 9.3 Workflow Structure

```python
@dataclass
class WorkflowChange:
    type: str              # "caching", "async_pattern", "circuit_breaker", etc.
    target: str            # Which service/component to change
    description: str       # Human-readable explanation
    impact: str            # Expected effect (e.g., "Reduce latency by 40%")

@dataclass
class Workflow:
    id: str
    name: str
    description: str
    proposed_changes: List[WorkflowChange]
    pros: List[str]
    cons: List[str]
    complexity_score: int  # 1-10 (1=simple, 10=complex)
    risk_score: int        # 1-10 (1=safe, 10=risky)
    expected_impact: Dict[str, str]  # {"latency_improvement": "30%", ...}
```

### 9.4 Scoring Methodology

#### Complexity Score (1-10)

Measures implementation difficulty:

- **1-3**: Configuration changes, feature flags, simple code edits
- **4-6**: New infrastructure (cache, queue), moderate refactoring
- **7-10**: Architectural overhaul (service splitting, database migration)

Scoring factors:
- Number of services touched
- New infrastructure components
- Lines of code changed
- Team coordination required

#### Risk Score (1-10)

Measures potential for disruption:

- **1-3**: Easy rollback, no downtime, isolated changes
- **4-6**: Requires testing, potential for transient errors, careful deployment
- **7-10**: High chance of outages, data migration, no rollback

Scoring factors:
- Can change be rolled back?
- Does it touch critical path?
- Requires data migration?
- Affects multiple services simultaneously?

#### Why Subjective Scores Are Bounded

Complexity and risk are subjective. Different teams may assess them differently. Nexarch bounds scores (1-10) to force relative comparison. The goal is not precision but clarity: "Workflow A is simpler and safer than Workflow B."

Scores are calculated heuristically:
- Minimal: Low scores by definition
- Performance: Higher complexity (new infrastructure), moderate risk (well-tested patterns)
- Cost: Moderate complexity (optimization, not overhaul), low-moderate risk (no new dependencies)

Future enhancement: Allow users to provide weights (e.g., "prioritize low risk over low complexity").

---

## 10. LangGraph Reasoning Pipeline

### 10.1 Why LangGraph

Traditional workflow generation is linear: detect issues → generate workflow. But real reasoning is non-linear:

- Issues should be **classified** (performance vs. reliability vs. scalability)
- Strategies should be **selected conditionally** (if high latency → consider caching; if deep chains → consider async)
- Workflow generation should **branch** (different paths for different issue types)
- Analysis may need to **loop back** (if new issues discovered, re-classify)

LangGraph enables this by representing reasoning as a **state graph** with conditional edges.

#### Benefits Over Linear Pipelines

1. **Conditional branching**: Generate workflows only if issues exist (skip empty case)
2. **Parallel generation**: Minimal, Performance, and Cost workflows can be generated in parallel (future optimization)
3. **Re-entrant logic**: Can add loops for iterative refinement
4. **Stateful reasoning**: Intermediate results (issue classification, strategy selection) are preserved in state

### 10.2 Pipeline Structure

#### State Definition

```python
class ReasoningState(TypedDict):
    graph: nx.DiGraph                  # Input: dependency graph
    issues: List[Issue]                # Detected issues (accumulated)
    issue_categories: dict             # Classified issues by type
    strategy_selection: dict           # Which strategies to apply
    workflows: List[Workflow]          # Generated workflows (accumulated)
    analysis_complete: bool            # Termination flag
```

#### Nodes (Pure Functions)

1. **detect_issues**: Runs rule engine on graph → outputs issues
2. **classify_issues**: Groups issues by category (performance, reliability, scalability, complexity)
3. **analyze_graph**: Runs graph algorithms (centrality, paths, cycles) → outputs analysis
4. **select_strategies**: Based on issue types, decides which strategies to apply (caching, async, circuit breaker, consolidation)
5. **generate_minimal**: Produces Minimal Migration workflow
6. **generate_performance**: Produces Performance Optimized workflow
7. **generate_cost**: Produces Cost Optimized workflow
8. **finalize**: Sets `analysis_complete = True`

#### Edges (Control Flow)

```
detect_issues → classify_issues
classify_issues → analyze_graph
analyze_graph → select_strategies
select_strategies → [conditional routing]
    If no issues: → END
    If issues: → [generate_minimal, generate_performance, generate_cost]
generate_* → finalize
finalize → END
```

#### Conditional Routing Logic

```python
def _route_generation(state: ReasoningState) -> str:
    if not state.get("issues"):
        return "end"  # No issues, skip workflow generation
    return "all"      # Generate all 3 workflows
```

This is deterministic routing (not AI-based). LangGraph supports LLM-based routing, but Nexarch keeps routing logic rule-based for predictability.

### 10.3 Determinism Guarantees

#### Where AI is NOT Allowed

1. **Issue detection**: Rules only (no LLMs analyzing spans)
2. **Metric computation**: Pure math (averages, counts)
3. **Graph construction**: Direct transformation of spans to edges
4. **Routing logic**: Conditional statements (if/else, not LLM decisions)

#### Where AI IS Allowed (Optional)

1. **Workflow change descriptions**: LLM can rephrase technical changes into business language
2. **Explanation generation**: LLM can synthesize why a workflow was chosen
3. **Future: Issue prioritization**: LLM can rank issues by business impact (requires context)

#### Why This Separation?

Core logic must be deterministic for:
- **Reproducibility**: Same telemetry → same architecture graph → same issues
- **Debugging**: Engineers can trace decisions
- **Testing**: Unit tests with mock graphs verify correctness

AI enhancement is additive. If LLM fails, the system still produces workflows (just with less polished descriptions).

---

## 11. FastMCP Server

### 11.1 Purpose of MCP in Nexarch

FastMCP (Model Context Protocol) is a standardized interface for AI agents to interact with tools. Nexarch includes an MCP server to enable:

1. **AI-assisted architecture reviews**: LLMs can query current architecture, issues, and workflows
2. **Natural language queries**: Instead of REST APIs, users can ask "What are the current bottlenecks?"
3. **Integration with AI coding assistants**: Claude, ChatGPT, etc. can call Nexarch tools to inform refactoring suggestions

MCP is an **adapter layer**, not the core system. Nexarch's services (graph, metrics, issue detection) exist independently. MCP wraps them for AI consumption.

### 11.2 MCP Tool Design

#### Exposed Tools

1. **get_current_architecture**
   - Returns: Nodes, edges, metrics summary
   - Use case: "Show me the current service dependencies"

2. **get_detected_issues**
   - Returns: List of issues, categorized by severity
   - Use case: "What architectural problems exist?"

3. **generate_workflows**
   - Returns: 3 workflow alternatives (Minimal, Performance, Cost)
   - Use case: "Propose migration strategies"

4. **compare_workflows**
   - Returns: Comparison matrix + recommendation
   - Use case: "Which workflow should I choose?"

5. **explain_decision**
   - Input: workflow_id
   - Returns: Detailed reasoning for why workflow was generated
   - Use case: "Why does Workflow X propose caching?"

6. **get_graph_analysis**
   - Returns: Advanced graph metrics (centrality, bottlenecks, cycles)
   - Use case: "Are there circular dependencies?"

#### Why MCP Wraps Services Instead of Duplicating Logic

Each MCP tool is a thin wrapper:

```python
@mcp.tool()
def get_detected_issues() -> Dict[str, Any]:
    return tools.get_detected_issues()

# tools.get_detected_issues() calls:
class MCPTools:
    def get_detected_issues(self):
        db = SessionLocal()
        issues = IssueDetector.detect_issues(db)  # Core service
        db.close()
        return {"issues": [i.model_dump() for i in issues]}
```

**Why this design?**

1. **Single source of truth**: Core services contain all logic. MCP is just a protocol adapter.
2. **Testability**: Core services can be tested without MCP dependency.
3. **Flexibility**: Core services can be exposed via REST, GraphQL, gRPC, or CLI without code duplication.
4. **Maintainability**: Changes to issue detection logic automatically reflect in MCP, REST API, and any other interface.

### 11.3 Statelessness and Safety

#### Why MCP Has No Side Effects

All MCP tools are **read-only**:
- `get_current_architecture`: Query database
- `get_detected_issues`: Run rules on graph (no mutation)
- `generate_workflows`: Generate workflows (no storage)
- `compare_workflows`: Compare workflows (no storage)
- `explain_decision`: Provide explanation (no mutation)
- `get_graph_analysis`: Run graph algorithms (no mutation)

No tool writes to database, modifies configuration, or triggers deployments.

#### Security Implications

Read-only MCP tools are safe to expose to AI agents:
- **No accidental damage**: AI cannot delete data or misconfigure system
- **No authentication bypass**: Even if agent is compromised, it cannot modify state
- **Auditable**: All queries are logged, no hidden side effects

Future enhancement: If write operations are needed (e.g., "Apply workflow X"), implement explicit approval flow (human-in-the-loop).

---

## 12. API Surface

### 12.1 REST Endpoints

#### Ingestion

```
POST /api/v1/ingest
Body: SpanData JSON
Response: 202 Accepted
```

#### Architecture

```
GET /api/v1/architecture
Response: { nodes: [...], edges: [...], metrics: {...} }
```

#### Issues

```
GET /api/v1/issues
Response: { issues: [...], by_severity: {...} }
```

#### Workflows

```
GET /api/v1/workflows
Response: { workflows: [...], count: 3 }
```

### 12.2 MCP Tools

```
get_current_architecture() -> Dict
get_detected_issues() -> Dict
generate_workflows() -> Dict
compare_workflows() -> Dict
explain_decision(workflow_id: str) -> Dict
get_graph_analysis() -> Dict
```

### 12.3 Output Formats

All endpoints return JSON. Structure example:

```json
{
  "nodes": [
    {
      "id": "production",
      "type": "service",
      "metrics": {
        "avg_latency_ms": 234.5,
        "error_rate": 0.02,
        "call_count": 15234
      }
    }
  ],
  "edges": [
    {
      "source": "production",
      "target": "postgres://users-db",
      "call_count": 8234,
      "avg_latency_ms": 123.4,
      "error_rate": 0.01
    }
  ],
  "metrics_summary": {
    "total_spans": 15234,
    "unique_services": 3,
    "avg_latency_ms": 234.5,
    "error_rate": 0.02
  }
}
```

All timestamps are ISO 8601 UTC. All latencies are in milliseconds. All error rates are floats (0.0 to 1.0).

---

## 13. Security and Privacy

### 13.1 What is Collected

Nexarch SDK collects:
- Service names (e.g., "production", "staging")
- HTTP methods and paths (e.g., "GET /api/users")
- Query parameters (e.g., `{"page": 1}`)
- Response status codes (e.g., 200, 500)
- Latencies (e.g., 234.5ms)
- Error types and messages (e.g., "ConnectionError")
- Downstream targets (e.g., "postgres://users-db")

### 13.2 What is NEVER Collected

Nexarch does NOT collect:
- Request bodies (no PII, no credentials)
- Response bodies (no data payloads)
- HTTP headers (no auth tokens)
- Environment variables (no secrets)
- Database query results (no customer data)

### 13.3 Data Isolation Principles

1. **Telemetry stays in user's infrastructure**: Default exporter writes to local filesystem. HTTP export is optional and user-controlled.
2. **No phone home**: SDK does not send telemetry to Nexarch-owned servers.
3. **Self-hosted backend**: Nexarch backend runs in user's environment (not SaaS).
4. **Open source transparency**: All SDK and backend code is auditable (planned open source release).

---

## 14. Scalability and Future Extensions

### 14.1 Multi-Tenant Support

Current implementation: Single-tenant (one database per deployment).

Future: Add `tenant_id` to spans table, partition by tenant, enforce row-level security.

### 14.2 Streaming Ingestion

Current implementation: HTTP POST per span (batched by SDK queue).

Future: Support streaming protocols (Kafka, Kinesis, NATS) for high-throughput systems (>100k spans/sec).

### 14.3 Advanced AI Reasoning

Current implementation: LangGraph with deterministic routing.

Future enhancements:
- LLM-based issue prioritization (use business context, historical incidents)
- Predictive analytics (forecast when latency will exceed threshold)
- Anomaly detection (ML-based, not just rule-based)
- Natural language workflow descriptions (LLM rewrites technical changes for stakeholders)

### 14.4 Visualization Layers

Current implementation: JSON API for graph data.

Future: Build web UI with interactive graph visualization (D3.js, Cytoscape.js), timeline view, issue dashboard, workflow comparison matrix.

---

## 15. What Nexarch Is NOT

### 15.1 Clear Non-Goals

1. **Not an APM tool**: Nexarch does not replace Datadog, New Relic, or Prometheus. It complements them by focusing on architecture-level intelligence, not request-level observability.

2. **Not a monitoring system**: No alerting, no dashboards, no real-time metrics. Nexarch analyzes historical telemetry to inform refactoring decisions.

3. **Not a deployment tool**: Nexarch generates workflows but does not execute them. It does not apply Terraform, Kubernetes manifests, or code changes.

4. **Not a service mesh**: Nexarch does not control traffic, route requests, or enforce policies. It observes traffic patterns passively.

5. **Not a full observability platform**: No logs aggregation, no distributed tracing UI, no metric visualization. Nexarch is architecture-first, not operations-first.

### 15.2 Boundaries of Responsibility

Nexarch's scope:
- Telemetry collection (SDK)
- Dependency graph reconstruction (Backend)
- Issue detection (Rules)
- Workflow generation (LangGraph)
- AI-agent interface (MCP)

Outside Nexarch's scope:
- Log aggregation (use ELK, Loki)
- Metric storage (use Prometheus, InfluxDB)
- Alerting (use PagerDuty, Opsgenie)
- Visualization (use Grafana, custom UIs)
- Code generation (use Copilot, Cursor)
- CI/CD (use GitHub Actions, Jenkins)

Nexarch integrates with these tools but does not replace them.

---

## 16. Summary: How All Components Fit Together

### 16.1 End-to-End Flow

1. **User installs Nexarch SDK** in their FastAPI application (2 lines of code)
2. **SDK intercepts requests** via middleware, captures latency, status codes, errors
3. **SDK patches HTTP libraries** (requests, httpx) to detect downstream calls
4. **Spans generated** with trace IDs, parent relationships, timestamps
5. **Telemetry queued** in background thread, batched, exported to local JSON or HTTP endpoint
6. **Backend ingests spans** via REST API, validates, stores in database
7. **Graph Service queries spans**, builds NetworkX directed graph (nodes = services, edges = dependencies), aggregates metrics
8. **Metrics Service computes** latency, error rate, call volume per node and edge
9. **Issue Detector runs rules** on graph (latency, chains, errors, fan-out, SPOF), generates issues with evidence
10. **LangGraph Pipeline reasons** about issues, classifies by type, selects strategies, generates 3 workflows (Minimal, Performance, Cost)
11. **MCP Server exposes tools** for AI agents to query architecture, issues, workflows
12. **AI agents** (Claude, ChatGPT, custom bots) call MCP tools to assist engineers in refactoring decisions

### 16.2 Why This Architecture is Future-Proof

1. **Modularity**: Each component (SDK, backend, reasoning, MCP) is independently replaceable
2. **Extensibility**: New rules, metrics, workflow types, exporters can be added without rewriting core logic
3. **Technology-agnostic**: SDK principles apply to any language (Python today, Go/Java/Node.js tomorrow)
4. **AI-ready**: MCP interface enables any LLM to consume Nexarch intelligence
5. **Open-source potential**: All components are self-contained, no proprietary dependencies
6. **Scalable foundations**: NetworkX can be swapped for graph database, SQLite can be swapped for Postgres/TimescaleDB, local files can be swapped for object storage

Nexarch's core insight — **runtime dependency graphs enable architectural intelligence** — remains valid regardless of technology evolution.

---

**End of Document**

This document is the single source of truth for Nexarch. All design decisions, implementation details, and architectural principles are captured here. Use this document to onboard engineers, justify technical choices, pass architecture reviews, and guide future development.

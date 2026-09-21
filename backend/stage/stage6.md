Implement **Stage 6 — RAG + pgvector** for the existing FinPilot backend.

IMPORTANT:

Stages 1–5 already exist and must continue working.

Do NOT redesign the existing architecture.

Do NOT implement Stage 7 yet.

Do NOT add an LLM.

Do NOT add an AI agent.

Do NOT add tool calling.

Do NOT add API LLM fallback.

Do NOT modify the financial calculation engine.

The purpose of this stage is ONLY to build a secure document retrieval layer using PostgreSQL + pgvector.

==================================================

1. GOAL
   ==================================================

Build this pipeline:

Document
→ text extraction
→ cleaning
→ chunking
→ embeddings
→ pgvector
→ semantic retrieval
→ source evidence

The retrieval layer will later be consumed by the Stage 7 agent.

==================================================
2. EXISTING ARCHITECTURE
========================

Continue using the existing modular monolith:

backend/
└── app/
├── api/
├── core/
├── models/
├── repositories/
├── services/
├── engine/
└── schemas/

Keep the existing authentication, financial engine, ingestion, and chat architecture.

==================================================
3. EXISTING DOCUMENT MODEL
==========================

Stage 3 already contains a documents table/model.

Reuse it.

Do not create a duplicate document table.

The existing document should contain information such as:

id
user_id
filename
mime_type
storage_key
status
created_at

Respect the existing schema instead of recreating it.

==================================================
4. ADD document_chunks
======================

Create a new document_chunks model/table.

Fields:

id UUID PRIMARY KEY

document_id UUID NOT NULL
FOREIGN KEY → documents.id

user_id UUID NOT NULL
FOREIGN KEY → users.id

chunk_index INTEGER NOT NULL

content TEXT NOT NULL

embedding VECTOR(<configured_dimension>)

metadata JSONB NULL

created_at TIMESTAMPTZ NOT NULL

Do not hard-code the embedding dimension throughout the codebase.

The embedding dimension must come from the configured embedding provider/model.

Add appropriate indexes.

At minimum support efficient:

user_id filtering
document_id filtering
chunk ordering

Add a pgvector similarity index if appropriate for the selected pgvector configuration.

==================================================
5. PGVECTOR
===========

Enable the PostgreSQL pgvector extension through an Alembic migration.

Do not use Pinecone, Chroma, FAISS, or another external vector database.

PostgreSQL + pgvector is the vector store for this stage.

Keep structured financial data and vector data in the same PostgreSQL database.

==================================================
6. EMBEDDING ABSTRACTION
========================

Create an embedding abstraction.

Example:

EmbeddingProvider

Methods:

embed_text(text)
embed_texts(texts)

Create a local embedding implementation.

The exact model must be configurable through environment/configuration.

Do not scatter model-specific code throughout the application.

The architecture should allow another embedding provider to be added later without rewriting retrieval logic.

If using a Sentence Transformers based provider, keep model loading centralized and avoid loading the model once per request.

Reuse the loaded model.

==================================================
7. DOCUMENT PROCESSING
======================

Build a reusable document processing pipeline.

Pipeline:

document
→ extract text
→ normalize text
→ chunk text
→ generate embeddings
→ persist chunks

Reuse the existing Stage 3 extraction functionality where possible.

Do not duplicate PDF extraction unnecessarily.

Support the document types already supported by Stage 3.

At minimum preserve support for the existing PDF/text ingestion flow.

If DOCX support already exists, reuse it.

==================================================
8. TEXT CLEANING
================

Normalize extracted text.

Handle:

excessive whitespace
empty lines
broken spacing
obvious extraction artifacts

Do not aggressively rewrite the source text.

The stored chunk content should remain faithful to the original document.

==================================================
9. CHUNKING
===========

Create a dedicated chunking component.

Example abstraction:

TextChunker

Configuration:

chunk_size
chunk_overlap

Make these values configurable.

Do not scatter magic numbers through the code.

Chunks must have deterministic ordering using:

chunk_index

Do not create chunks containing only whitespace.

Preserve enough surrounding context through overlap.

==================================================
10. METADATA
============

Store useful metadata for each chunk.

Example:

{
"page": 4,
"source": "statement_august.pdf",
"document_type": "bank_statement",
"section": "fees"
}

Only store metadata that is actually available.

Do not invent page numbers or document information.

Metadata must remain JSON serializable.

==================================================
11. RETRIEVAL SERVICE
=====================

Create:

app/services/retrieval_service.py

or an equivalent clean service.

Expose a method similar to:

search_documents(
user_id,
query,
top_k=5,
similarity_threshold=<configured value>,
filters=None
)

The retrieval process must:

1. Validate query
2. Generate query embedding
3. Apply user_id filter
4. Apply optional metadata/document filters
5. Calculate vector similarity
6. Order by similarity
7. Apply similarity threshold
8. Return top-K results
9. Include source metadata

==================================================
12. CRITICAL USER ISOLATION
===========================

This requirement is mandatory.

Every retrieval query MUST be scoped to the authenticated user.

Never perform:

SELECT chunks
ORDER BY similarity

without user filtering.

Correct conceptual behavior:

SELECT chunks
WHERE user_id = authenticated_user_id
ORDER BY similarity
LIMIT K

The frontend must never control the user_id used for retrieval.

The backend must obtain it from the authenticated JWT/current_user.

User A must NEVER retrieve User B's document chunks.

Add explicit tests for this.

==================================================
13. RETRIEVAL RESULT SCHEMA
===========================

Create a structured response model.

Example:

{
"chunk_id": "...",
"document_id": "...",
"content": "...",
"score": 0.91,
"metadata": {
"page": 4
}
}

Also include enough source information for a future agent to cite the source.

Do not generate natural-language answers in the retrieval service.

The retrieval service returns evidence only.

==================================================
14. SEARCH API
==============

Create:

POST /api/v1/documents/search

Request:

{
"query": "late payment charges",
"top_k": 5
}

Optional filters can include document_id or metadata filters if the existing architecture supports them cleanly.

Do not expose arbitrary SQL filters.

Response:

{
"query": "late payment charges",
"results": [
{
"chunk_id": "...",
"document_id": "...",
"content": "...",
"score": 0.91,
"metadata": {
"page": 4
}
}
]
}

Require authentication.

Never accept user_id from the request body.

==================================================
15. CONFIGURATION
=================

Add configuration for:

embedding provider
embedding model
embedding dimension
chunk size
chunk overlap
retrieval top_k
similarity threshold

Use environment variables where appropriate.

Do not hard-code secrets.

==================================================
16. DOCUMENT REPROCESSING
=========================

Make processing idempotent.

If a document is processed again, avoid blindly creating duplicate chunks.

Use one of these approaches:

delete existing chunks for the document before rebuilding

OR

use a versioning strategy.

Prefer the simpler safe approach unless the existing architecture already has versioning.

==================================================
17. ERROR HANDLING
==================

Handle:

unsupported document type
empty extracted text
embedding failure
database failure
invalid query
invalid top_k
invalid chunk configuration

Do not leave partially processed data silently.

Use the existing application error-handling conventions.

==================================================
18. ASYNC / PERFORMANCE
=======================

Do not load the embedding model repeatedly.

Reuse the embedding provider.

Avoid embedding one tiny string with a separate model initialization.

Prefer batch embedding:

embed_texts([...])

when processing multiple chunks.

Do not block API requests unnecessarily if the existing ingestion architecture already supports background processing.

Integrate with the existing Stage 3 processing lifecycle where practical.

==================================================
19. IMPORTANT FINANCIAL DATA RULE
=================================

RAG must NOT be used for financial calculations.

Do not calculate:

monthly expenses
income
budget percentage
balances
cash flow
goal progress
purchase affordability

from retrieved chunks.

Those operations remain in the Stage 4 financial engine using structured SQL data and deterministic Python.

RAG is only for retrieving relevant document evidence.

==================================================
20. FUTURE AGENT INTERFACE
==========================

Create a clean retrieval interface that Stage 7 can call.

For example:

retrieval_service.search_documents(...)

The future agent should be able to call:

search_financial_documents(query)

without knowing pgvector implementation details.

Do not implement the future agent now.

==================================================
21. SOURCE EVIDENCE
===================

Every retrieval result should preserve:

document_id
chunk_id
content
similarity score
metadata/source information

This will later allow the Stage 7 agent to produce answers such as:

"According to your uploaded statement..."

Do not generate citations using an LLM yet.

==================================================
22. TESTS
=========

Add comprehensive tests.

Test:

1. pgvector extension migration

2. document chunk creation

3. chunk ordering

4. chunking behavior

5. chunk overlap

6. empty document handling

7. embedding provider

8. batch embedding

9. semantic retrieval

10. top_k

11. similarity threshold

12. metadata filtering

13. authenticated retrieval

14. user isolation

Example:

User A has:

document_A
chunk_A1
chunk_A2

User B has:

document_B
chunk_B1
chunk_B2

Search as User A.

Results MUST NOT contain:

chunk_B1
chunk_B2

15. nonexistent document

16. reprocessing the same document

17. invalid query

18. invalid top_k

19. embedding failure

20. database failure

21. Stage 1 tests still pass

22. Stage 2 tests still pass

23. Stage 3 tests still pass

24. Stage 4 tests still pass

25. Stage 5 tests still pass

==================================================
23. API DOCUMENTATION
=====================

Ensure FastAPI OpenAPI documentation clearly describes:

POST /api/v1/documents/search

Request schema

Response schema

Authentication requirement

==================================================
24. CODE QUALITY
================

Follow the existing project's conventions.

Use:

Pydantic schemas
repository pattern
service layer
dependency injection
typed Python
structured logging
centralized configuration

Avoid:

global database connections
global request state
hard-coded user IDs
hard-coded secrets
duplicate document models
duplicate extraction pipelines
LLM calls
agent frameworks
unnecessary microservices

==================================================
25. FINAL EXPECTED STRUCTURE
============================

Add something similar to:

backend/
└── app/
├── api/
│   └── v1/
│       └── documents.py
│
├── models/
│   └── document_chunk.py
│
├── repositories/
│   └── document_chunk_repository.py
│
├── services/
│   ├── embedding_service.py
│   ├── chunking_service.py
│   ├── document_processing_service.py
│   └── retrieval_service.py
│
├── schemas/
│   └── retrieval.py
│
└── tests/
├── test_chunking.py
├── test_embeddings.py
├── test_retrieval.py
└── test_document_isolation.py

Adapt the exact structure to the existing project rather than blindly creating duplicate modules.

==================================================
26. MIGRATION
=============

Create an Alembic migration that:

1. Enables pgvector
2. Creates document_chunks
3. Creates required indexes

Do NOT use Base.metadata.create_all() to bypass migrations.

==================================================
27. DEFINITION OF DONE
======================

Stage 6 is complete only when:

[ ] pgvector enabled
[ ] document_chunks table exists
[ ] Alembic migration works
[ ] embedding provider works
[ ] chunking works
[ ] document processing works
[ ] embeddings stored in PostgreSQL
[ ] semantic retrieval works
[ ] top-k works
[ ] similarity threshold works
[ ] metadata supported
[ ] source evidence returned
[ ] authenticated search works
[ ] user isolation verified
[ ] duplicate processing handled
[ ] retrieval API works
[ ] OpenAPI documentation works
[ ] tests pass
[ ] Stage 1 tests pass
[ ] Stage 2 tests pass
[ ] Stage 3 tests pass
[ ] Stage 4 tests pass
[ ] Stage 5 tests pass

==================================================
FINAL RULE
==========

STOP after implementing Stage 6.

Do not implement:

LLM
agent
tool calling
RAG-generated answers
API LLM fallback
frontend integration

Those belong to later stages.
***do not hardcode any logic***
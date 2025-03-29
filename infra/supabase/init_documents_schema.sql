"""adapted for documents from  https://github.com/coleam00/ottomator-agents/blob/main/crawl4AI-agent/site_pages.sql"""

-- Enable pgvector for similarity search
create extension if not exists vector;

-- Create the table for parsed textbook chunks
create table documents (
    id bigserial primary key,

    file_name varchar not null,               -- e.g. leerboek_kgt_1.pdf
    page_number integer not null,             -- Actual page in the book
    chapter varchar not null,                 -- Human-readable section name
    content text not null,                    -- Markdown content of the chunk
    metadata jsonb not null default '{}'::jsonb,

    embedding vector(384),                    -- Assuming you're using MiniLM
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Prevent duplicate pages from being inserted twice
create unique index unique_page_per_file on documents (file_name, page_number);

-- Optional: Index for chapter filtering
create index idx_documents_chapter on documents (chapter);

-- Index for metadata filtering
create index idx_documents_metadata on documents using gin (metadata);

-- Index for vector similarity search
create index on documents using ivfflat (embedding vector_cosine_ops);

-- Similarity search function
create function match_documents (
  query_embedding vector(384),
  match_count int default 10,
  filter jsonb DEFAULT '{}'::jsonb
) returns table (
  id bigint,
  file_name varchar,
  page_number integer,
  chapter varchar,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
  return query
  select
    id,
    file_name,
    page_number,
    chapter,
    content,
    metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where metadata @> filter
  order by documents.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Supabase row-level security setup
alter table documents enable row level security;

-- Allow public read access (adjust later for user-based filtering)
create policy "Public Read Access"
  on documents
  for select
  to public
  using (true);

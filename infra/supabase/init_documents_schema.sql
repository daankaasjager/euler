-- Enable pgvector for similarity search
create extension if not exists vector;

-- Create the table for your processed textbook chunks
create table documents (
    id bigserial primary key,

    -- from "ProcessedChunk"
    file_name varchar not null,
    chunk_nummer integer not null,
    thema varchar not null,
    omschrijving varchar not null,
    inhoud text not null,
    metadata jsonb not null default '{}'::jsonb,

    embedding vector(384),  -- Assuming you're using a 384-dim embedding
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Optional: Prevent duplicates of (file_name, chunk_nummer)
create unique index unique_chunk_per_file
on documents (file_name, chunk_nummer);

-- Index for metadata filtering
create index idx_documents_metadata on documents using gin (metadata);

-- Index for vector similarity search
create index on documents using ivfflat (embedding vector_cosine_ops);

-- Example similarity search function, if you want it:
create function match_documents (
  query_embedding vector(384),
  match_count int default 10,
  filter jsonb default '{}'::jsonb
)
returns table (
  id bigint,
  file_name varchar,
  chunk_nummer integer,
  thema varchar,
  omschrijving varchar,
  inhoud text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
  return query
  select
    d.id,
    d.file_name,
    d.chunk_nummer,
    d.thema,
    d.omschrijving,
    d.inhoud,
    d.metadata,
    1 - (d.embedding <=> query_embedding) as similarity
  from documents d
  where d.metadata @> filter
  order by d.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Enable row-level security
alter table documents enable row level security;



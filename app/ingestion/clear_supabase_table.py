from ..utils.supabase_client import get_supabase_client

def clear_supabase_table(subject_filter: str = "wiskunde"):
    supabase = get_supabase_client()
    try:
        response = supabase.table("documents") \
            .delete() \
            .eq("metadata->>subject", subject_filter) \
            .execute()
        print(f"🧹 Deleted {len(response.data)} documents.")
    except Exception as e:
        print(f"❌ Failed to clear documents: {e}")

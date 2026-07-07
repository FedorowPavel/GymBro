import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const url = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

export function getSupabase(): SupabaseClient | null {
  if (!url || !anonKey) {
    return null;
  }
  return createClient(url, anonKey);
}

export function supabaseConfigured(): boolean {
  return Boolean(url && anonKey);
}

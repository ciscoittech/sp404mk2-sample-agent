import { createClient } from '@supabase/supabase-js';

const supabaseUrl: string | any = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey: string | any = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseKey);

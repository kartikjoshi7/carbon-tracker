-- Run this in your Supabase SQL Editor to create the necessary tables for the Carbon Tracker

-- 1. Create the Footprint Logs Table
CREATE TABLE IF NOT EXISTS public.footprint_logs (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id text NOT NULL,
    category text NOT NULL,
    metric_value numeric NOT NULL,
    calculated_co2 numeric NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

-- 2. Create the AI Insights Table
CREATE TABLE IF NOT EXISTS public.footprint_insights (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id text NOT NULL,
    category text NOT NULL,
    insight_text text NOT NULL,
    related_co2 numeric NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

-- Note: Since we are using the service_role key for the backend API,
-- Row Level Security (RLS) policies are automatically bypassed by the backend.
-- However, if you plan to access Supabase directly from the Vite frontend later,
-- you will need to enable RLS and add public policies.

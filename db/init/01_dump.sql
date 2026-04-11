--
-- PostgreSQL database dump
--

\restrict ilgELRPMkp0oEF7yaoETlizCfTuV3SJKZyiKEE2WoL0iMi72GbRG36kR5MMjsGK

-- Dumped from database version 17.8 (Debian 17.8-1.pgdg13+1)
-- Dumped by pg_dump version 17.8 (Debian 17.8-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: audit_trigger_func(); Type: FUNCTION; Schema: public; Owner: recipe_user
--

CREATE FUNCTION public.audit_trigger_func() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            INSERT INTO audit_logs (
                tenant_id, actor_type, actor_id, action, entity, entity_id,
                old_data, new_data
            ) VALUES (
                COALESCE(
                    current_setting('app.current_tenant_id', true)::uuid,
                    '00000000-0000-0000-0000-000000000000'::uuid
                ),
                COALESCE(current_setting('app.current_actor_type', true), 'system'),
                COALESCE(
                    current_setting('app.current_actor_id', true)::uuid,
                    '00000000-0000-0000-0000-000000000000'::uuid
                ),
                TG_OP,
                TG_TABLE_NAME,
                CASE TG_OP
                    WHEN 'DELETE' THEN (OLD).id
                    ELSE (NEW).id
                END,
                CASE TG_OP
                    WHEN 'INSERT' THEN NULL
                    ELSE to_jsonb(OLD)
                END,
                CASE TG_OP
                    WHEN 'DELETE' THEN NULL
                    ELSE to_jsonb(NEW)
                END
            );
            RETURN COALESCE(NEW, OLD);
        END;
        $$;


ALTER FUNCTION public.audit_trigger_func() OWNER TO recipe_user;

--
-- Name: set_updated_at(); Type: FUNCTION; Schema: public; Owner: recipe_user
--

CREATE FUNCTION public.set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$;


ALTER FUNCTION public.set_updated_at() OWNER TO recipe_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: additives; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.additives (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code integer NOT NULL,
    name_de character varying(255) NOT NULL,
    name_en character varying(255)
);


ALTER TABLE public.additives OWNER TO recipe_user;

--
-- Name: agent_interactions; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.agent_interactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    agent_id uuid NOT NULL,
    source character varying(50) NOT NULL,
    raw_input text NOT NULL,
    parsed_intent character varying(255),
    confidence_score numeric(3,2),
    tool_calls jsonb DEFAULT '[]'::jsonb,
    response_text text,
    latency_ms integer,
    error text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.agent_interactions OWNER TO recipe_user;

--
-- Name: agents; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.agents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    agent_type character varying(50) NOT NULL,
    name character varying(255) NOT NULL,
    capabilities jsonb DEFAULT '[]'::jsonb NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.agents OWNER TO recipe_user;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO recipe_user;

--
-- Name: allergens; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.allergens (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code integer NOT NULL,
    name_de character varying(255) NOT NULL,
    name_en character varying(255),
    parent_code integer
);


ALTER TABLE public.allergens OWNER TO recipe_user;

--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.audit_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    actor_type character varying(50) NOT NULL,
    actor_id uuid NOT NULL,
    action character varying(50) NOT NULL,
    entity character varying(100) NOT NULL,
    entity_id uuid,
    old_data jsonb,
    new_data jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO recipe_user;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.categories (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid,
    name character varying(255) NOT NULL
);


ALTER TABLE public.categories OWNER TO recipe_user;

--
-- Name: ingredient_additives; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.ingredient_additives (
    ingredient_id uuid NOT NULL,
    additive_id uuid NOT NULL
);


ALTER TABLE public.ingredient_additives OWNER TO recipe_user;

--
-- Name: ingredient_allergens; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.ingredient_allergens (
    ingredient_id uuid NOT NULL,
    allergen_id uuid NOT NULL
);


ALTER TABLE public.ingredient_allergens OWNER TO recipe_user;

--
-- Name: ingredient_nutrition; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.ingredient_nutrition (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ingredient_id uuid NOT NULL,
    energy_kj numeric,
    energy_kcal numeric,
    fat numeric,
    saturates numeric,
    carbs numeric,
    sugars numeric,
    protein numeric,
    fiber numeric,
    salt numeric,
    alcohol numeric,
    water numeric,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.ingredient_nutrition OWNER TO recipe_user;

--
-- Name: ingredient_prices; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.ingredient_prices (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ingredient_id uuid NOT NULL,
    price_per_unit numeric(10,4),
    currency character varying(10) DEFAULT 'EUR'::character varying NOT NULL,
    unit character varying(50),
    supplier_name character varying(255),
    supplier_id character varying(100),
    article_number character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    price_per_gram numeric(14,8),
    CONSTRAINT ingredient_prices_price_per_gram_positive CHECK (((price_per_gram IS NULL) OR (price_per_gram > (0)::numeric))),
    CONSTRAINT positive_price CHECK ((price_per_unit > (0)::numeric))
);


ALTER TABLE public.ingredient_prices OWNER TO recipe_user;

--
-- Name: ingredient_prices_latest; Type: VIEW; Schema: public; Owner: recipe_user
--

CREATE VIEW public.ingredient_prices_latest AS
 SELECT DISTINCT ON (ingredient_id, COALESCE(unit, ''::character varying)) id,
    ingredient_id,
    price_per_unit,
    price_per_gram,
    currency,
    unit,
    supplier_name,
    supplier_id,
    article_number,
    created_at,
    updated_at
   FROM public.ingredient_prices ip
  ORDER BY ingredient_id, COALESCE(unit, ''::character varying), updated_at DESC NULLS LAST, created_at DESC NULLS LAST, id DESC;


ALTER VIEW public.ingredient_prices_latest OWNER TO recipe_user;

--
-- Name: ingredient_units; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.ingredient_units (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ingredient_id uuid NOT NULL,
    unit_code character varying(20) NOT NULL,
    grams_per_unit numeric NOT NULL,
    label character varying(100),
    CONSTRAINT ingredient_units_grams_per_unit_positive CHECK ((grams_per_unit > (0)::numeric))
);


ALTER TABLE public.ingredient_units OWNER TO recipe_user;

--
-- Name: ingredients; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.ingredients (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid,
    name character varying(255) NOT NULL,
    name_english character varying(255),
    source character varying(50) DEFAULT 'standard'::character varying NOT NULL,
    bls_key character varying(50),
    default_unit character varying(50),
    is_custom boolean DEFAULT false NOT NULL,
    parent_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.ingredients OWNER TO recipe_user;

--
-- Name: recipe_categories; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.recipe_categories (
    recipe_id uuid NOT NULL,
    category_id uuid NOT NULL
);


ALTER TABLE public.recipe_categories OWNER TO recipe_user;

--
-- Name: recipe_ingredients; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.recipe_ingredients (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    recipe_id uuid NOT NULL,
    ingredient_id uuid NOT NULL,
    quantity numeric,
    unit character varying(50),
    preparation character varying(255),
    sort_order integer DEFAULT 0 NOT NULL,
    quid_percent numeric,
    is_organic boolean DEFAULT false,
    item_type character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    quantity_grams numeric,
    CONSTRAINT recipe_ingredients_quantity_grams_non_negative CHECK (((quantity_grams IS NULL) OR (quantity_grams >= (0)::numeric)))
);


ALTER TABLE public.recipe_ingredients OWNER TO recipe_user;

--
-- Name: recipe_nutrition_cache; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.recipe_nutrition_cache (
    recipe_id uuid NOT NULL,
    energy_kj numeric,
    energy_kcal numeric,
    fat numeric,
    saturates numeric,
    carbs numeric,
    sugars numeric,
    protein numeric,
    salt numeric,
    fiber numeric,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.recipe_nutrition_cache OWNER TO recipe_user;

--
-- Name: recipe_tags; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.recipe_tags (
    recipe_id uuid NOT NULL,
    tag_id uuid NOT NULL
);


ALTER TABLE public.recipe_tags OWNER TO recipe_user;

--
-- Name: recipe_versions; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.recipe_versions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    recipe_id uuid NOT NULL,
    version integer NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.recipe_versions OWNER TO recipe_user;

--
-- Name: recipes; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.recipes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    instructions text,
    yield_amount numeric,
    yield_unit character varying(50),
    reduction_factor numeric DEFAULT 1.0,
    status character varying(50) DEFAULT 'draft'::character varying NOT NULL,
    is_component boolean DEFAULT false NOT NULL,
    recipe_number character varying(100),
    preparation_time_minutes integer,
    cooking_time_minutes integer,
    shelf_life_text text,
    storage_temperature character varying(50),
    notes text,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    yield_mode character varying(20) DEFAULT 'count'::character varying NOT NULL,
    portion_size_grams numeric,
    total_raw_weight_grams numeric,
    total_cooked_weight_grams numeric,
    portions_count_resolved numeric,
    CONSTRAINT positive_portion_size_grams CHECK (((portion_size_grams IS NULL) OR (portion_size_grams > (0)::numeric))),
    CONSTRAINT positive_portions_count_resolved CHECK (((portions_count_resolved IS NULL) OR (portions_count_resolved > (0)::numeric))),
    CONSTRAINT positive_total_cooked_weight_grams CHECK (((total_cooked_weight_grams IS NULL) OR (total_cooked_weight_grams >= (0)::numeric))),
    CONSTRAINT positive_total_raw_weight_grams CHECK (((total_raw_weight_grams IS NULL) OR (total_raw_weight_grams >= (0)::numeric))),
    CONSTRAINT valid_status CHECK (((status)::text = ANY ((ARRAY['draft'::character varying, 'active'::character varying, 'archived'::character varying])::text[]))),
    CONSTRAINT valid_yield_mode CHECK (((yield_mode)::text = ANY ((ARRAY['count'::character varying, 'weight'::character varying])::text[]))),
    CONSTRAINT weight_mode_requires_portion_size_when_active CHECK ((((status)::text <> 'active'::text) OR ((yield_mode)::text <> 'weight'::text) OR ((portion_size_grams IS NOT NULL) AND (portion_size_grams > (0)::numeric))))
);


ALTER TABLE public.recipes OWNER TO recipe_user;

--
-- Name: shopping_list_items; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.shopping_list_items (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    list_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    quantity numeric,
    unit character varying(50),
    is_checked boolean DEFAULT false NOT NULL,
    sort_order integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    quantity_grams numeric,
    CONSTRAINT shopping_list_items_quantity_grams_non_negative CHECK (((quantity_grams IS NULL) OR (quantity_grams >= (0)::numeric)))
);


ALTER TABLE public.shopping_list_items OWNER TO recipe_user;

--
-- Name: shopping_lists; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.shopping_lists (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    name character varying(255) DEFAULT 'Shopping List'::character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.shopping_lists OWNER TO recipe_user;

--
-- Name: tags; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.tags (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid,
    name character varying(255) NOT NULL
);


ALTER TABLE public.tags OWNER TO recipe_user;

--
-- Name: task_items; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.task_items (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    list_id uuid NOT NULL,
    title character varying(500) NOT NULL,
    status character varying(50) DEFAULT 'pending'::character varying NOT NULL,
    sort_order integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT valid_task_status CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'done'::character varying])::text[])))
);


ALTER TABLE public.task_items OWNER TO recipe_user;

--
-- Name: task_lists; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.task_lists (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    name character varying(255) DEFAULT 'Prep List'::character varying NOT NULL,
    date date DEFAULT CURRENT_DATE NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.task_lists OWNER TO recipe_user;

--
-- Name: tenants; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.tenants (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    slug character varying(100) NOT NULL,
    settings jsonb DEFAULT '{}'::jsonb,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tenants OWNER TO recipe_user;

--
-- Name: units; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.units (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(20) NOT NULL,
    name_de character varying(100) NOT NULL,
    name_en character varying(100),
    grams_per_unit numeric,
    unit_type character varying(20) NOT NULL,
    is_base boolean DEFAULT false NOT NULL,
    CONSTRAINT valid_unit_type CHECK (((unit_type)::text = ANY ((ARRAY['weight'::character varying, 'volume'::character varying, 'piece'::character varying, 'custom'::character varying])::text[])))
);


ALTER TABLE public.units OWNER TO recipe_user;

--
-- Name: users; Type: TABLE; Schema: public; Owner: recipe_user
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    email character varying(320) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(50) DEFAULT 'editor'::character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO recipe_user;

--
-- Name: additives additives_code_key; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.additives
    ADD CONSTRAINT additives_code_key UNIQUE (code);


--
-- Name: additives additives_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.additives
    ADD CONSTRAINT additives_pkey PRIMARY KEY (id);


--
-- Name: agent_interactions agent_interactions_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.agent_interactions
    ADD CONSTRAINT agent_interactions_pkey PRIMARY KEY (id);


--
-- Name: agents agents_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: allergens allergens_code_key; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.allergens
    ADD CONSTRAINT allergens_code_key UNIQUE (code);


--
-- Name: allergens allergens_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.allergens
    ADD CONSTRAINT allergens_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: ingredient_additives ingredient_additives_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredient_additives
    ADD CONSTRAINT ingredient_additives_pkey PRIMARY KEY (ingredient_id, additive_id);


--
-- Name: ingredient_allergens ingredient_allergens_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredient_allergens
    ADD CONSTRAINT ingredient_allergens_pkey PRIMARY KEY (ingredient_id, allergen_id);


--
-- Name: ingredient_nutrition ingredient_nutrition_ingredient_id_key; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredient_nutrition
    ADD CONSTRAINT ingredient_nutrition_ingredient_id_key UNIQUE (ingredient_id);


--
-- Name: ingredient_nutrition ingredient_nutrition_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredient_nutrition
    ADD CONSTRAINT ingredient_nutrition_pkey PRIMARY KEY (id);


--
-- Name: ingredient_prices ingredient_prices_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredient_prices
    ADD CONSTRAINT ingredient_prices_pkey PRIMARY KEY (id);


--
-- Name: ingredient_units ingredient_units_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredient_units
    ADD CONSTRAINT ingredient_units_pkey PRIMARY KEY (id);


--
-- Name: ingredients ingredients_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredients
    ADD CONSTRAINT ingredients_pkey PRIMARY KEY (id);


--
-- Name: recipe_categories recipe_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipe_categories
    ADD CONSTRAINT recipe_categories_pkey PRIMARY KEY (recipe_id, category_id);


--
-- Name: recipe_ingredients recipe_ingredients_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT recipe_ingredients_pkey PRIMARY KEY (id);


--
-- Name: recipe_nutrition_cache recipe_nutrition_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipe_nutrition_cache
    ADD CONSTRAINT recipe_nutrition_cache_pkey PRIMARY KEY (recipe_id);


--
-- Name: recipe_tags recipe_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipe_tags
    ADD CONSTRAINT recipe_tags_pkey PRIMARY KEY (recipe_id, tag_id);


--
-- Name: recipe_versions recipe_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipe_versions
    ADD CONSTRAINT recipe_versions_pkey PRIMARY KEY (id);


--
-- Name: recipes recipes_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_pkey PRIMARY KEY (id);


--
-- Name: shopping_list_items shopping_list_items_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.shopping_list_items
    ADD CONSTRAINT shopping_list_items_pkey PRIMARY KEY (id);


--
-- Name: shopping_lists shopping_lists_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.shopping_lists
    ADD CONSTRAINT shopping_lists_pkey PRIMARY KEY (id);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (id);


--
-- Name: task_items task_items_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.task_items
    ADD CONSTRAINT task_items_pkey PRIMARY KEY (id);


--
-- Name: task_lists task_lists_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.task_lists
    ADD CONSTRAINT task_lists_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_slug_key; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_slug_key UNIQUE (slug);


--
-- Name: units units_code_key; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.units
    ADD CONSTRAINT units_code_key UNIQUE (code);


--
-- Name: units units_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.units
    ADD CONSTRAINT units_pkey PRIMARY KEY (id);


--
-- Name: ingredient_units uq_ingredient_unit; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredient_units
    ADD CONSTRAINT uq_ingredient_unit UNIQUE (ingredient_id, unit_code);


--
-- Name: recipe_ingredients uq_recipe_ingredient_order; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT uq_recipe_ingredient_order UNIQUE (recipe_id, ingredient_id, sort_order);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_agent_interactions_agent; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_agent_interactions_agent ON public.agent_interactions USING btree (agent_id, created_at DESC);


--
-- Name: idx_agent_interactions_tenant; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_agent_interactions_tenant ON public.agent_interactions USING btree (tenant_id, created_at DESC);


--
-- Name: idx_audit_logs_entity; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_audit_logs_entity ON public.audit_logs USING btree (entity, entity_id);


--
-- Name: idx_audit_logs_tenant; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_audit_logs_tenant ON public.audit_logs USING btree (tenant_id, created_at DESC);


--
-- Name: idx_ing_additives_additive; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_ing_additives_additive ON public.ingredient_additives USING btree (additive_id);


--
-- Name: idx_ing_allergens_allergen; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_ing_allergens_allergen ON public.ingredient_allergens USING btree (allergen_id);


--
-- Name: idx_ingredient_prices_ing; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_ingredient_prices_ing ON public.ingredient_prices USING btree (ingredient_id);


--
-- Name: idx_ingredient_prices_latest_lookup; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_ingredient_prices_latest_lookup ON public.ingredient_prices USING btree (ingredient_id, unit, updated_at DESC, created_at DESC, id DESC);


--
-- Name: idx_ingredient_units_ingredient; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_ingredient_units_ingredient ON public.ingredient_units USING btree (ingredient_id);


--
-- Name: idx_ingredients_name; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_ingredients_name ON public.ingredients USING btree (name);


--
-- Name: idx_ingredients_parent; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_ingredients_parent ON public.ingredients USING btree (parent_id);


--
-- Name: idx_ingredients_tenant; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_ingredients_tenant ON public.ingredients USING btree (tenant_id);


--
-- Name: idx_recipe_categories_cat; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_recipe_categories_cat ON public.recipe_categories USING btree (category_id);


--
-- Name: idx_recipe_ingredients_ingredient; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_recipe_ingredients_ingredient ON public.recipe_ingredients USING btree (ingredient_id);


--
-- Name: idx_recipe_ingredients_recipe; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_recipe_ingredients_recipe ON public.recipe_ingredients USING btree (recipe_id);


--
-- Name: idx_recipe_tags_tag; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_recipe_tags_tag ON public.recipe_tags USING btree (tag_id);


--
-- Name: idx_recipe_versions_recipe; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_recipe_versions_recipe ON public.recipe_versions USING btree (recipe_id);


--
-- Name: idx_recipes_component; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_recipes_component ON public.recipes USING btree (tenant_id, is_component);


--
-- Name: idx_recipes_name; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_recipes_name ON public.recipes USING btree (name);


--
-- Name: idx_recipes_status; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_recipes_status ON public.recipes USING btree (tenant_id, status);


--
-- Name: idx_recipes_tenant; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_recipes_tenant ON public.recipes USING btree (tenant_id);


--
-- Name: idx_recipes_yield_mode; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_recipes_yield_mode ON public.recipes USING btree (yield_mode);


--
-- Name: idx_shopping_items_list; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_shopping_items_list ON public.shopping_list_items USING btree (list_id);


--
-- Name: idx_task_items_list; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE INDEX idx_task_items_list ON public.task_items USING btree (list_id);


--
-- Name: uq_ingredient_no_supplier; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE UNIQUE INDEX uq_ingredient_no_supplier ON public.ingredient_prices USING btree (ingredient_id) WHERE (supplier_id IS NULL);


--
-- Name: uq_ingredient_supplier; Type: INDEX; Schema: public; Owner: recipe_user
--

CREATE UNIQUE INDEX uq_ingredient_supplier ON public.ingredient_prices USING btree (ingredient_id, supplier_id) WHERE (supplier_id IS NOT NULL);


--
-- Name: ingredients audit_ingredients; Type: TRIGGER; Schema: public; Owner: recipe_user
--

CREATE TRIGGER audit_ingredients AFTER INSERT OR DELETE OR UPDATE ON public.ingredients FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_func();


--
-- Name: recipe_ingredients audit_recipe_ingredients; Type: TRIGGER; Schema: public; Owner: recipe_user
--

CREATE TRIGGER audit_recipe_ingredients AFTER INSERT OR DELETE OR UPDATE ON public.recipe_ingredients FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_func();


--
-- Name: recipes audit_recipes; Type: TRIGGER; Schema: public; Owner: recipe_user
--

CREATE TRIGGER audit_recipes AFTER INSERT OR DELETE OR UPDATE ON public.recipes FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_func();


--
-- Name: ingredient_nutrition set_ingredient_nutrition_updated_at; Type: TRIGGER; Schema: public; Owner: recipe_user
--

CREATE TRIGGER set_ingredient_nutrition_updated_at BEFORE UPDATE ON public.ingredient_nutrition FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: ingredient_prices set_ingredient_prices_updated_at; Type: TRIGGER; Schema: public; Owner: recipe_user
--

CREATE TRIGGER set_ingredient_prices_updated_at BEFORE UPDATE ON public.ingredient_prices FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: ingredients set_ingredients_updated_at; Type: TRIGGER; Schema: public; Owner: recipe_user
--

CREATE TRIGGER set_ingredients_updated_at BEFORE UPDATE ON public.ingredients FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: recipes set_recipes_updated_at; Type: TRIGGER; Schema: public; Owner: recipe_user
--

CREATE TRIGGER set_recipes_updated_at BEFORE UPDATE ON public.recipes FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: tenants set_tenants_updated_at; Type: TRIGGER; Schema: public; Owner: recipe_user
--

CREATE TRIGGER set_tenants_updated_at BEFORE UPDATE ON public.tenants FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: users set_users_updated_at; Type: TRIGGER; Schema: public; Owner: recipe_user
--

CREATE TRIGGER set_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: agent_interactions agent_interactions_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.agent_interactions
    ADD CONSTRAINT agent_interactions_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(id);


--
-- Name: agent_interactions agent_interactions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.agent_interactions
    ADD CONSTRAINT agent_interactions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: agents agents_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: categories categories_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: ingredient_additives ingredient_additives_additive_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredient_additives
    ADD CONSTRAINT ingredient_additives_additive_id_fkey FOREIGN KEY (additive_id) REFERENCES public.additives(id) ON DELETE CASCADE;


--
-- Name: ingredient_additives ingredient_additives_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredient_additives
    ADD CONSTRAINT ingredient_additives_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id) ON DELETE CASCADE;


--
-- Name: ingredient_allergens ingredient_allergens_allergen_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredient_allergens
    ADD CONSTRAINT ingredient_allergens_allergen_id_fkey FOREIGN KEY (allergen_id) REFERENCES public.allergens(id) ON DELETE CASCADE;


--
-- Name: ingredient_allergens ingredient_allergens_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredient_allergens
    ADD CONSTRAINT ingredient_allergens_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id) ON DELETE CASCADE;


--
-- Name: ingredient_nutrition ingredient_nutrition_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredient_nutrition
    ADD CONSTRAINT ingredient_nutrition_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id) ON DELETE CASCADE;


--
-- Name: ingredient_prices ingredient_prices_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredient_prices
    ADD CONSTRAINT ingredient_prices_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id) ON DELETE CASCADE;


--
-- Name: ingredient_units ingredient_units_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredient_units
    ADD CONSTRAINT ingredient_units_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id) ON DELETE CASCADE;


--
-- Name: ingredients ingredients_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredients
    ADD CONSTRAINT ingredients_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.ingredients(id);


--
-- Name: ingredients ingredients_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.ingredients
    ADD CONSTRAINT ingredients_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: recipe_categories recipe_categories_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipe_categories
    ADD CONSTRAINT recipe_categories_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE CASCADE;


--
-- Name: recipe_categories recipe_categories_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipe_categories
    ADD CONSTRAINT recipe_categories_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: recipe_ingredients recipe_ingredients_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT recipe_ingredients_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id) ON DELETE CASCADE;


--
-- Name: recipe_ingredients recipe_ingredients_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT recipe_ingredients_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: recipe_nutrition_cache recipe_nutrition_cache_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipe_nutrition_cache
    ADD CONSTRAINT recipe_nutrition_cache_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: recipe_tags recipe_tags_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipe_tags
    ADD CONSTRAINT recipe_tags_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: recipe_tags recipe_tags_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipe_tags
    ADD CONSTRAINT recipe_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id) ON DELETE CASCADE;


--
-- Name: recipe_versions recipe_versions_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipe_versions
    ADD CONSTRAINT recipe_versions_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: recipes recipes_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: recipes recipes_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: shopping_list_items shopping_list_items_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.shopping_list_items
    ADD CONSTRAINT shopping_list_items_list_id_fkey FOREIGN KEY (list_id) REFERENCES public.shopping_lists(id) ON DELETE CASCADE;


--
-- Name: shopping_lists shopping_lists_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.shopping_lists
    ADD CONSTRAINT shopping_lists_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: tags tags_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: task_items task_items_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.task_items
    ADD CONSTRAINT task_items_list_id_fkey FOREIGN KEY (list_id) REFERENCES public.task_lists(id) ON DELETE CASCADE;


--
-- Name: task_lists task_lists_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.task_lists
    ADD CONSTRAINT task_lists_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: users users_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipe_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: agent_interactions; Type: ROW SECURITY; Schema: public; Owner: recipe_user
--

ALTER TABLE public.agent_interactions ENABLE ROW LEVEL SECURITY;

--
-- Name: audit_logs; Type: ROW SECURITY; Schema: public; Owner: recipe_user
--

ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

--
-- Name: ingredients ingredient_access; Type: POLICY; Schema: public; Owner: recipe_user
--

CREATE POLICY ingredient_access ON public.ingredients USING (((tenant_id IS NULL) OR (tenant_id = (current_setting('app.current_tenant_id'::text, true))::uuid)));


--
-- Name: ingredient_nutrition; Type: ROW SECURITY; Schema: public; Owner: recipe_user
--

ALTER TABLE public.ingredient_nutrition ENABLE ROW LEVEL SECURITY;

--
-- Name: ingredients; Type: ROW SECURITY; Schema: public; Owner: recipe_user
--

ALTER TABLE public.ingredients ENABLE ROW LEVEL SECURITY;

--
-- Name: ingredient_nutrition nutrition_access; Type: POLICY; Schema: public; Owner: recipe_user
--

CREATE POLICY nutrition_access ON public.ingredient_nutrition USING ((ingredient_id IN ( SELECT ingredients.id
   FROM public.ingredients
  WHERE ((ingredients.tenant_id IS NULL) OR (ingredients.tenant_id = (current_setting('app.current_tenant_id'::text, true))::uuid)))));


--
-- Name: recipe_ingredients; Type: ROW SECURITY; Schema: public; Owner: recipe_user
--

ALTER TABLE public.recipe_ingredients ENABLE ROW LEVEL SECURITY;

--
-- Name: recipes; Type: ROW SECURITY; Schema: public; Owner: recipe_user
--

ALTER TABLE public.recipes ENABLE ROW LEVEL SECURITY;

--
-- Name: shopping_list_items; Type: ROW SECURITY; Schema: public; Owner: recipe_user
--

ALTER TABLE public.shopping_list_items ENABLE ROW LEVEL SECURITY;

--
-- Name: shopping_lists; Type: ROW SECURITY; Schema: public; Owner: recipe_user
--

ALTER TABLE public.shopping_lists ENABLE ROW LEVEL SECURITY;

--
-- Name: task_items; Type: ROW SECURITY; Schema: public; Owner: recipe_user
--

ALTER TABLE public.task_items ENABLE ROW LEVEL SECURITY;

--
-- Name: task_lists; Type: ROW SECURITY; Schema: public; Owner: recipe_user
--

ALTER TABLE public.task_lists ENABLE ROW LEVEL SECURITY;

--
-- Name: agent_interactions tenant_isolation; Type: POLICY; Schema: public; Owner: recipe_user
--

CREATE POLICY tenant_isolation ON public.agent_interactions USING ((tenant_id = (current_setting('app.current_tenant_id'::text, true))::uuid));


--
-- Name: audit_logs tenant_isolation; Type: POLICY; Schema: public; Owner: recipe_user
--

CREATE POLICY tenant_isolation ON public.audit_logs USING ((tenant_id = (current_setting('app.current_tenant_id'::text, true))::uuid));


--
-- Name: recipe_ingredients tenant_isolation; Type: POLICY; Schema: public; Owner: recipe_user
--

CREATE POLICY tenant_isolation ON public.recipe_ingredients USING ((recipe_id IN ( SELECT recipes.id
   FROM public.recipes
  WHERE (recipes.tenant_id = (current_setting('app.current_tenant_id'::text, true))::uuid))));


--
-- Name: recipes tenant_isolation; Type: POLICY; Schema: public; Owner: recipe_user
--

CREATE POLICY tenant_isolation ON public.recipes USING ((tenant_id = (current_setting('app.current_tenant_id'::text, true))::uuid));


--
-- Name: shopping_list_items tenant_isolation; Type: POLICY; Schema: public; Owner: recipe_user
--

CREATE POLICY tenant_isolation ON public.shopping_list_items USING ((list_id IN ( SELECT shopping_lists.id
   FROM public.shopping_lists
  WHERE (shopping_lists.tenant_id = (current_setting('app.current_tenant_id'::text, true))::uuid))));


--
-- Name: shopping_lists tenant_isolation; Type: POLICY; Schema: public; Owner: recipe_user
--

CREATE POLICY tenant_isolation ON public.shopping_lists USING ((tenant_id = (current_setting('app.current_tenant_id'::text, true))::uuid));


--
-- Name: task_items tenant_isolation; Type: POLICY; Schema: public; Owner: recipe_user
--

CREATE POLICY tenant_isolation ON public.task_items USING ((list_id IN ( SELECT task_lists.id
   FROM public.task_lists
  WHERE (task_lists.tenant_id = (current_setting('app.current_tenant_id'::text, true))::uuid))));


--
-- Name: task_lists tenant_isolation; Type: POLICY; Schema: public; Owner: recipe_user
--

CREATE POLICY tenant_isolation ON public.task_lists USING ((tenant_id = (current_setting('app.current_tenant_id'::text, true))::uuid));


--
-- PostgreSQL database dump complete
--

\unrestrict ilgELRPMkp0oEF7yaoETlizCfTuV3SJKZyiKEE2WoL0iMi72GbRG36kR5MMjsGK


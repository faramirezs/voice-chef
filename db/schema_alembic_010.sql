--
-- PostgreSQL database dump
--

\restrict f4s03rGRdBd4efNw1QelQwhPcl0QXdkGShaGo4NzZxjaqrdMcIvokfd7IKZQVSK

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
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: additives; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.additives (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code text NOT NULL,
    name text NOT NULL
);


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: allergens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.allergens (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code text NOT NULL,
    name text NOT NULL
);


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_logs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid,
    action text NOT NULL,
    entity text NOT NULL,
    entity_id uuid,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categories (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name text NOT NULL
);


--
-- Name: files; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.files (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    recipe_id uuid,
    file_type text NOT NULL,
    uri text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: ingredient_additives; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ingredient_additives (
    ingredient_id uuid NOT NULL,
    additive_id uuid NOT NULL
);


--
-- Name: ingredient_allergens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ingredient_allergens (
    ingredient_id uuid NOT NULL,
    allergen_id uuid NOT NULL
);


--
-- Name: ingredient_merge_audit; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ingredient_merge_audit (
    id bigint NOT NULL,
    merged_at timestamp with time zone DEFAULT now() NOT NULL,
    normalized_name text NOT NULL,
    keep_id uuid NOT NULL,
    drop_id uuid NOT NULL,
    table_name text NOT NULL,
    row_data jsonb NOT NULL
);


--
-- Name: ingredient_merge_audit_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ingredient_merge_audit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ingredient_merge_audit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ingredient_merge_audit_id_seq OWNED BY public.ingredient_merge_audit.id;


--
-- Name: ingredient_nutrition; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ingredient_nutrition (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ingredient_id uuid NOT NULL,
    energy_kj numeric(10,2),
    energy_kcal numeric(10,2),
    carbs numeric(10,2),
    protein numeric(10,2),
    fat numeric(10,2),
    sugars numeric(10,2),
    fiber numeric(10,2),
    saturates numeric(10,2),
    salt numeric(10,2),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    alcohol numeric(10,3),
    water numeric(10,3)
);


--
-- Name: ingredient_prices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ingredient_prices (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    ingredient_id uuid NOT NULL,
    price_per_unit numeric(10,2),
    currency character varying(3) DEFAULT 'EUR'::character varying,
    unit character varying(50),
    supplier_id character varying(100),
    supplier_name character varying(255),
    article_number character varying(100),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    price_per_gram numeric(14,8),
    CONSTRAINT ingredient_prices_price_per_gram_positive CHECK (((price_per_gram IS NULL) OR (price_per_gram > (0)::numeric)))
);


--
-- Name: ingredient_prices_latest; Type: VIEW; Schema: public; Owner: -
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


--
-- Name: ingredient_units; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ingredient_units (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    ingredient_id uuid NOT NULL,
    unit_code character varying(20) NOT NULL,
    grams_per_unit numeric NOT NULL,
    label character varying(100),
    CONSTRAINT ingredient_units_grams_per_unit_positive CHECK ((grams_per_unit > (0)::numeric))
);


--
-- Name: ingredients; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ingredients (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    tenant_id uuid,
    name character varying(255) NOT NULL,
    default_unit character varying(50),
    nutrition_id uuid,
    usage_count integer DEFAULT 0,
    recipe_count integer DEFAULT 0,
    ingredient_type character varying(50),
    bls_key character varying(100),
    is_custom boolean DEFAULT false,
    has_parent boolean DEFAULT false,
    parent_id uuid,
    initial_recipe_id uuid
);


--
-- Name: nutrition_facts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.nutrition_facts (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    energy_kj numeric,
    energy_kcal numeric,
    fat numeric,
    saturates numeric,
    carbs numeric,
    sugars numeric,
    protein numeric,
    salt numeric
);


--
-- Name: recipe_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recipe_categories (
    recipe_id uuid NOT NULL,
    category_id uuid NOT NULL
);


--
-- Name: recipe_ingredients; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recipe_ingredients (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    recipe_id uuid NOT NULL,
    ingredient_id uuid NOT NULL,
    quantity numeric(10,4),
    unit character varying(50),
    preparation character varying(255),
    sort_order integer DEFAULT 0 NOT NULL,
    quid numeric(10,4),
    item_type character varying(50),
    quantity_grams numeric,
    CONSTRAINT recipe_ingredients_quantity_grams_non_negative CHECK (((quantity_grams IS NULL) OR (quantity_grams >= (0)::numeric)))
);


--
-- Name: recipe_nutrition; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recipe_nutrition (
    recipe_id uuid NOT NULL,
    nutrition_id uuid,
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: recipe_photos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recipe_photos (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    recipe_id uuid NOT NULL,
    photo_url text,
    photo_data bytea,
    photo_type character varying(50),
    is_primary boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: recipe_tags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recipe_tags (
    recipe_id uuid NOT NULL,
    tag_id uuid NOT NULL
);


--
-- Name: recipe_versions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recipe_versions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    recipe_id uuid,
    version integer NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: recipes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recipes (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    tenant_id uuid,
    name character varying(255) NOT NULL,
    description text,
    yield_amount numeric(10,2),
    yield_unit character varying(50),
    instructions text,
    status character varying(50) DEFAULT 'draft'::character varying NOT NULL,
    created_by uuid,
    description_short text,
    serving_recommendation text,
    side_dishes text,
    notes text,
    preparation_time text,
    waiting_time text,
    cooking_time text,
    shelf_life text,
    reduction_factor numeric(10,4),
    eigene_menge numeric(10,2),
    recipe_number character varying(100),
    packaging text,
    packaging_material text,
    net_weight numeric(10,2),
    fill_weight numeric(10,2),
    fill_quantity numeric(10,2),
    drained_weight numeric(10,2),
    total_weight numeric(10,2),
    portion_by_weight boolean DEFAULT false,
    portion_weight numeric(10,2),
    batch_number character varying(100),
    production_date date,
    use_by_date date,
    expiry_date date,
    storage_text text,
    storage_temperature character varying(50),
    bio_label_eu boolean,
    origin_fish text,
    origin_location text,
    devices text,
    utensils text,
    labor_effort character varying(50),
    margin numeric(10,2),
    sales_price_points numeric(10,2),
    vat_rate numeric(5,2),
    nutri_score_category character varying(10),
    nutri_score_veg_fruits numeric(5,2),
    layout_id character varying(50),
    row_height integer,
    rezeptblatt_image_width integer,
    mise_en_place_display boolean DEFAULT true,
    notes_instructions text,
    is_component boolean DEFAULT false,
    branch_ids text,
    ingredient_list_custom text,
    ingredient_list_product_pass text,
    allergene_source text,
    unit_measure character varying(50),
    unit_serving character varying(50),
    preference_allergens text,
    preference_price numeric(10,2),
    preference_nutri_value numeric(10,2),
    yield_mode character varying(20) DEFAULT 'count'::character varying NOT NULL,
    portion_size_grams numeric,
    total_raw_weight_grams numeric,
    total_cooked_weight_grams numeric,
    portions_count_resolved numeric,
    CONSTRAINT positive_portion_size_grams CHECK (((portion_size_grams IS NULL) OR (portion_size_grams > (0)::numeric))),
    CONSTRAINT positive_portions_count_resolved CHECK (((portions_count_resolved IS NULL) OR (portions_count_resolved > (0)::numeric))),
    CONSTRAINT positive_total_cooked_weight_grams CHECK (((total_cooked_weight_grams IS NULL) OR (total_cooked_weight_grams >= (0)::numeric))),
    CONSTRAINT positive_total_raw_weight_grams CHECK (((total_raw_weight_grams IS NULL) OR (total_raw_weight_grams >= (0)::numeric))),
    CONSTRAINT valid_yield_mode CHECK (((yield_mode)::text = ANY ((ARRAY['count'::character varying, 'weight'::character varying])::text[]))),
    CONSTRAINT weight_mode_requires_portion_size_when_active CHECK ((((status)::text <> 'active'::text) OR ((yield_mode)::text <> 'weight'::text) OR ((portion_size_grams IS NOT NULL) AND (portion_size_grams > (0)::numeric))))
);


--
-- Name: tags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tags (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name text NOT NULL
);


--
-- Name: tenants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenants (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    name character varying(255) NOT NULL,
    slug character varying(100) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    settings character varying
);


--
-- Name: units; Type: TABLE; Schema: public; Owner: -
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


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(50) DEFAULT 'editor'::character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    tenant_id uuid
);


--
-- Name: ingredient_merge_audit id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_merge_audit ALTER COLUMN id SET DEFAULT nextval('public.ingredient_merge_audit_id_seq'::regclass);


--
-- Name: additives additives_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.additives
    ADD CONSTRAINT additives_code_key UNIQUE (code);


--
-- Name: additives additives_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.additives
    ADD CONSTRAINT additives_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: allergens allergens_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.allergens
    ADD CONSTRAINT allergens_code_key UNIQUE (code);


--
-- Name: allergens allergens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.allergens
    ADD CONSTRAINT allergens_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);


--
-- Name: ingredient_additives ingredient_additives_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_additives
    ADD CONSTRAINT ingredient_additives_pkey PRIMARY KEY (ingredient_id, additive_id);


--
-- Name: ingredient_allergens ingredient_allergens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_allergens
    ADD CONSTRAINT ingredient_allergens_pkey PRIMARY KEY (ingredient_id, allergen_id);


--
-- Name: ingredient_merge_audit ingredient_merge_audit_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_merge_audit
    ADD CONSTRAINT ingredient_merge_audit_pkey PRIMARY KEY (id);


--
-- Name: ingredient_nutrition ingredient_nutrition_ingredient_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_nutrition
    ADD CONSTRAINT ingredient_nutrition_ingredient_id_key UNIQUE (ingredient_id);


--
-- Name: ingredient_nutrition ingredient_nutrition_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_nutrition
    ADD CONSTRAINT ingredient_nutrition_pkey PRIMARY KEY (id);


--
-- Name: ingredient_prices ingredient_prices_ingredient_id_supplier_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_prices
    ADD CONSTRAINT ingredient_prices_ingredient_id_supplier_id_key UNIQUE (ingredient_id, supplier_id);


--
-- Name: ingredient_prices ingredient_prices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_prices
    ADD CONSTRAINT ingredient_prices_pkey PRIMARY KEY (id);


--
-- Name: ingredient_units ingredient_units_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_units
    ADD CONSTRAINT ingredient_units_pkey PRIMARY KEY (id);


--
-- Name: ingredients ingredients_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredients
    ADD CONSTRAINT ingredients_pkey PRIMARY KEY (id);


--
-- Name: nutrition_facts nutrition_facts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nutrition_facts
    ADD CONSTRAINT nutrition_facts_pkey PRIMARY KEY (id);


--
-- Name: recipe_categories recipe_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipe_categories
    ADD CONSTRAINT recipe_categories_pkey PRIMARY KEY (recipe_id, category_id);


--
-- Name: recipe_ingredients recipe_ingredients_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT recipe_ingredients_pkey PRIMARY KEY (id);


--
-- Name: recipe_nutrition recipe_nutrition_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipe_nutrition
    ADD CONSTRAINT recipe_nutrition_pkey PRIMARY KEY (recipe_id);


--
-- Name: recipe_photos recipe_photos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipe_photos
    ADD CONSTRAINT recipe_photos_pkey PRIMARY KEY (id);


--
-- Name: recipe_tags recipe_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipe_tags
    ADD CONSTRAINT recipe_tags_pkey PRIMARY KEY (recipe_id, tag_id);


--
-- Name: recipe_versions recipe_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipe_versions
    ADD CONSTRAINT recipe_versions_pkey PRIMARY KEY (id);


--
-- Name: recipes recipes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_pkey PRIMARY KEY (id);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_slug_key UNIQUE (slug);


--
-- Name: units units_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.units
    ADD CONSTRAINT units_code_key UNIQUE (code);


--
-- Name: units units_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.units
    ADD CONSTRAINT units_pkey PRIMARY KEY (id);


--
-- Name: ingredient_units uq_ingredient_unit; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_units
    ADD CONSTRAINT uq_ingredient_unit UNIQUE (ingredient_id, unit_code);


--
-- Name: recipe_ingredients uq_recipe_ingredient_order; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT uq_recipe_ingredient_order UNIQUE (recipe_id, ingredient_id, sort_order);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_additives_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_additives_code ON public.additives USING btree (code);


--
-- Name: idx_allergens_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_allergens_code ON public.allergens USING btree (code);


--
-- Name: idx_audit_logs_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_logs_created ON public.audit_logs USING btree (created_at);


--
-- Name: idx_audit_logs_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_logs_entity ON public.audit_logs USING btree (entity, entity_id);


--
-- Name: idx_audit_logs_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_logs_user ON public.audit_logs USING btree (user_id);


--
-- Name: idx_categories_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_categories_name ON public.categories USING btree (name);


--
-- Name: idx_files_recipe; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_files_recipe ON public.files USING btree (recipe_id);


--
-- Name: idx_ing_additives_additive; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ing_additives_additive ON public.ingredient_additives USING btree (additive_id);


--
-- Name: idx_ing_allergens_allergen; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ing_allergens_allergen ON public.ingredient_allergens USING btree (allergen_id);


--
-- Name: idx_ingredient_prices_ingredient; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ingredient_prices_ingredient ON public.ingredient_prices USING btree (ingredient_id);


--
-- Name: idx_ingredient_prices_latest_lookup; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ingredient_prices_latest_lookup ON public.ingredient_prices USING btree (ingredient_id, unit, updated_at DESC, created_at DESC, id DESC);


--
-- Name: idx_ingredient_units_ingredient; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ingredient_units_ingredient ON public.ingredient_units USING btree (ingredient_id);


--
-- Name: idx_ingredients_parent_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ingredients_parent_id ON public.ingredients USING btree (parent_id);


--
-- Name: idx_ingredients_usage_count; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ingredients_usage_count ON public.ingredients USING btree (usage_count);


--
-- Name: idx_recipe_cat_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_recipe_cat_category ON public.recipe_categories USING btree (category_id);


--
-- Name: idx_recipe_nutrition_nutrition; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_recipe_nutrition_nutrition ON public.recipe_nutrition USING btree (nutrition_id);


--
-- Name: idx_recipe_photos_recipe; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_recipe_photos_recipe ON public.recipe_photos USING btree (recipe_id);


--
-- Name: idx_recipe_tags_tag; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_recipe_tags_tag ON public.recipe_tags USING btree (tag_id);


--
-- Name: idx_recipe_versions_data; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_recipe_versions_data ON public.recipe_versions USING gin (data);


--
-- Name: idx_recipe_versions_recipe; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_recipe_versions_recipe ON public.recipe_versions USING btree (recipe_id);


--
-- Name: idx_recipes_batch_number; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_recipes_batch_number ON public.recipes USING btree (batch_number);


--
-- Name: idx_recipes_is_component; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_recipes_is_component ON public.recipes USING btree (is_component);


--
-- Name: idx_recipes_reduction_factor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_recipes_reduction_factor ON public.recipes USING btree (reduction_factor);


--
-- Name: idx_recipes_yield_mode; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_recipes_yield_mode ON public.recipes USING btree (yield_mode);


--
-- Name: idx_tags_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tags_name ON public.tags USING btree (name);


--
-- Name: ix_ingredients_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ingredients_name ON public.ingredients USING btree (name);


--
-- Name: ix_recipe_ingredients_ingredient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_recipe_ingredients_ingredient_id ON public.recipe_ingredients USING btree (ingredient_id);


--
-- Name: ix_recipe_ingredients_recipe_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_recipe_ingredients_recipe_id ON public.recipe_ingredients USING btree (recipe_id);


--
-- Name: ix_recipe_ingredients_sort_order; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_recipe_ingredients_sort_order ON public.recipe_ingredients USING btree (sort_order);


--
-- Name: ix_recipes_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_recipes_name ON public.recipes USING btree (name);


--
-- Name: ix_tenants_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_tenants_name ON public.tenants USING btree (name);


--
-- Name: ix_tenants_slug; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_tenants_slug ON public.tenants USING btree (slug);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: recipe_nutrition update_recipe_nutrition_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_recipe_nutrition_updated_at BEFORE UPDATE ON public.recipe_nutrition FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: ingredient_additives ingredient_additives_additive_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_additives
    ADD CONSTRAINT ingredient_additives_additive_id_fkey FOREIGN KEY (additive_id) REFERENCES public.additives(id) ON DELETE CASCADE;


--
-- Name: ingredient_allergens ingredient_allergens_allergen_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_allergens
    ADD CONSTRAINT ingredient_allergens_allergen_id_fkey FOREIGN KEY (allergen_id) REFERENCES public.allergens(id) ON DELETE CASCADE;


--
-- Name: ingredient_nutrition ingredient_nutrition_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_nutrition
    ADD CONSTRAINT ingredient_nutrition_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id) ON DELETE CASCADE;


--
-- Name: ingredient_prices ingredient_prices_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_prices
    ADD CONSTRAINT ingredient_prices_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id) ON DELETE CASCADE;


--
-- Name: ingredient_units ingredient_units_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredient_units
    ADD CONSTRAINT ingredient_units_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id) ON DELETE CASCADE;


--
-- Name: ingredients ingredients_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredients
    ADD CONSTRAINT ingredients_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.ingredients(id);


--
-- Name: ingredients ingredients_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ingredients
    ADD CONSTRAINT ingredients_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: recipe_categories recipe_categories_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipe_categories
    ADD CONSTRAINT recipe_categories_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE CASCADE;


--
-- Name: recipe_ingredients recipe_ingredients_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT recipe_ingredients_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id) ON DELETE CASCADE;


--
-- Name: recipe_ingredients recipe_ingredients_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT recipe_ingredients_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: recipe_nutrition recipe_nutrition_nutrition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipe_nutrition
    ADD CONSTRAINT recipe_nutrition_nutrition_id_fkey FOREIGN KEY (nutrition_id) REFERENCES public.nutrition_facts(id) ON DELETE CASCADE;


--
-- Name: recipe_photos recipe_photos_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipe_photos
    ADD CONSTRAINT recipe_photos_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: recipe_tags recipe_tags_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipe_tags
    ADD CONSTRAINT recipe_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id) ON DELETE CASCADE;


--
-- Name: recipes recipes_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: recipes recipes_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: users users_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- PostgreSQL database dump complete
--

\unrestrict f4s03rGRdBd4efNw1QelQwhPcl0QXdkGShaGo4NzZxjaqrdMcIvokfd7IKZQVSK


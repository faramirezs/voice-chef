"""Initial schema for Voice Chef

Revision ID: 001
Revises: -
Create Date: 2026-03-12

Creates all 26 tables, indexes, constraints, RLS policies, and audit trigger.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    #  Extensions                                                         #
    # ------------------------------------------------------------------ #
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # ------------------------------------------------------------------ #
    #  1. tenants                                                         #
    # ------------------------------------------------------------------ #
    op.create_table(
        "tenants",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("settings", JSONB, server_default=sa.text("'{}'")),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ------------------------------------------------------------------ #
    #  2. users                                                           #
    # ------------------------------------------------------------------ #
    op.create_table(
        "users",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default=sa.text("'editor'")),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ------------------------------------------------------------------ #
    #  3. agents                                                          #
    # ------------------------------------------------------------------ #
    op.create_table(
        "agents",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("agent_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("capabilities", JSONB, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ------------------------------------------------------------------ #
    #  4. ingredients  (before recipes — recipes.created_by -> users,     #
    #     but recipe_ingredients needs both)                              #
    # ------------------------------------------------------------------ #
    op.create_table(
        "ingredients",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, sa.ForeignKey("tenants.id"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("name_english", sa.String(255), nullable=True),
        sa.Column("source", sa.String(50), nullable=False, server_default=sa.text("'standard'")),
        sa.Column("bls_key", sa.String(50), nullable=True),
        sa.Column("default_unit", sa.String(50), nullable=True),
        sa.Column("is_custom", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("parent_id", UUID, sa.ForeignKey("ingredients.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ------------------------------------------------------------------ #
    #  5. ingredient_nutrition                                            #
    # ------------------------------------------------------------------ #
    op.create_table(
        "ingredient_nutrition",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("ingredient_id", UUID, sa.ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("energy_kj", sa.Numeric, nullable=True),
        sa.Column("energy_kcal", sa.Numeric, nullable=True),
        sa.Column("fat", sa.Numeric, nullable=True),
        sa.Column("saturates", sa.Numeric, nullable=True),
        sa.Column("carbs", sa.Numeric, nullable=True),
        sa.Column("sugars", sa.Numeric, nullable=True),
        sa.Column("protein", sa.Numeric, nullable=True),
        sa.Column("fiber", sa.Numeric, nullable=True),
        sa.Column("salt", sa.Numeric, nullable=True),
        sa.Column("alcohol", sa.Numeric, nullable=True),
        sa.Column("water", sa.Numeric, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ------------------------------------------------------------------ #
    #  6. recipes                                                         #
    # ------------------------------------------------------------------ #
    op.create_table(
        "recipes",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("instructions", sa.Text, nullable=True),
        sa.Column("yield_amount", sa.Numeric, nullable=True),
        sa.Column("yield_unit", sa.String(50), nullable=True),
        sa.Column("reduction_factor", sa.Numeric, nullable=True, server_default=sa.text("1.0")),
        sa.Column("status", sa.String(50), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("is_component", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("recipe_number", sa.String(100), nullable=True),
        sa.Column("preparation_time_minutes", sa.Integer, nullable=True),
        sa.Column("cooking_time_minutes", sa.Integer, nullable=True),
        sa.Column("shelf_life_text", sa.Text, nullable=True),
        sa.Column("storage_temperature", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_by", UUID, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('draft', 'active', 'archived')", name="valid_status"),
    )

    # ------------------------------------------------------------------ #
    #  7. recipe_ingredients                                              #
    # ------------------------------------------------------------------ #
    op.create_table(
        "recipe_ingredients",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("recipe_id", UUID, sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ingredient_id", UUID, sa.ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Numeric, nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("preparation", sa.String(255), nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("quid_percent", sa.Numeric, nullable=True),
        sa.Column("is_organic", sa.Boolean, nullable=True, server_default=sa.text("false")),
        sa.Column("item_type", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("recipe_id", "ingredient_id", "sort_order", name="uq_recipe_ingredient_order"),
    )

    # ------------------------------------------------------------------ #
    #  8. allergens                                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "allergens",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.Integer, nullable=False, unique=True),
        sa.Column("name_de", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=True),
        sa.Column("parent_code", sa.Integer, nullable=True),
    )

    # ------------------------------------------------------------------ #
    #  9. additives                                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "additives",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.Integer, nullable=False, unique=True),
        sa.Column("name_de", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=True),
    )

    # ------------------------------------------------------------------ #
    #  10. ingredient_allergens (M2M)                                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        "ingredient_allergens",
        sa.Column("ingredient_id", UUID, sa.ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("allergen_id", UUID, sa.ForeignKey("allergens.id", ondelete="CASCADE"), primary_key=True),
    )

    # ------------------------------------------------------------------ #
    #  11. ingredient_additives (M2M)                                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        "ingredient_additives",
        sa.Column("ingredient_id", UUID, sa.ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("additive_id", UUID, sa.ForeignKey("additives.id", ondelete="CASCADE"), primary_key=True),
    )

    # ------------------------------------------------------------------ #
    #  12. ingredient_prices                                              #
    # ------------------------------------------------------------------ #
    op.create_table(
        "ingredient_prices",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("ingredient_id", UUID, sa.ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("price_per_unit", sa.Numeric(10, 4), nullable=True),
        sa.Column("currency", sa.String(10), nullable=False, server_default=sa.text("'EUR'")),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("supplier_name", sa.String(255), nullable=True),
        sa.Column("supplier_id", sa.String(100), nullable=True),
        sa.Column("article_number", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("price_per_unit > 0", name="positive_price"),
    )

    # ------------------------------------------------------------------ #
    #  13. categories                                                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        "categories",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, sa.ForeignKey("tenants.id"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
    )

    # ------------------------------------------------------------------ #
    #  14. tags                                                           #
    # ------------------------------------------------------------------ #
    op.create_table(
        "tags",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, sa.ForeignKey("tenants.id"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
    )

    # ------------------------------------------------------------------ #
    #  15. recipe_categories (M2M)                                        #
    # ------------------------------------------------------------------ #
    op.create_table(
        "recipe_categories",
        sa.Column("recipe_id", UUID, sa.ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("category_id", UUID, sa.ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
    )

    # ------------------------------------------------------------------ #
    #  16. recipe_tags (M2M)                                              #
    # ------------------------------------------------------------------ #
    op.create_table(
        "recipe_tags",
        sa.Column("recipe_id", UUID, sa.ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", UUID, sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )

    # ------------------------------------------------------------------ #
    #  17. recipe_nutrition_cache                                         #
    # ------------------------------------------------------------------ #
    op.create_table(
        "recipe_nutrition_cache",
        sa.Column("recipe_id", UUID, sa.ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("energy_kj", sa.Numeric, nullable=True),
        sa.Column("energy_kcal", sa.Numeric, nullable=True),
        sa.Column("fat", sa.Numeric, nullable=True),
        sa.Column("saturates", sa.Numeric, nullable=True),
        sa.Column("carbs", sa.Numeric, nullable=True),
        sa.Column("sugars", sa.Numeric, nullable=True),
        sa.Column("protein", sa.Numeric, nullable=True),
        sa.Column("salt", sa.Numeric, nullable=True),
        sa.Column("fiber", sa.Numeric, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ------------------------------------------------------------------ #
    #  18. recipe_versions                                                #
    # ------------------------------------------------------------------ #
    op.create_table(
        "recipe_versions",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("recipe_id", UUID, sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("data", JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ------------------------------------------------------------------ #
    #  19. agent_interactions                                             #
    # ------------------------------------------------------------------ #
    op.create_table(
        "agent_interactions",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("agent_id", UUID, sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("raw_input", sa.Text, nullable=False),
        sa.Column("parsed_intent", sa.String(255), nullable=True),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=True),
        sa.Column("tool_calls", JSONB, nullable=True, server_default=sa.text("'[]'")),
        sa.Column("response_text", sa.Text, nullable=True),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ------------------------------------------------------------------ #
    #  20. audit_logs                                                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, nullable=False),
        sa.Column("actor_type", sa.String(50), nullable=False),
        sa.Column("actor_id", UUID, nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("entity", sa.String(100), nullable=False),
        sa.Column("entity_id", UUID, nullable=True),
        sa.Column("old_data", JSONB, nullable=True),
        sa.Column("new_data", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ------------------------------------------------------------------ #
    #  21. shopping_lists                                                  #
    # ------------------------------------------------------------------ #
    op.create_table(
        "shopping_lists",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False, server_default=sa.text("'Shopping List'")),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ------------------------------------------------------------------ #
    #  22. shopping_list_items                                             #
    # ------------------------------------------------------------------ #
    op.create_table(
        "shopping_list_items",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("list_id", UUID, sa.ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Numeric, nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("is_checked", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ------------------------------------------------------------------ #
    #  23. task_lists                                                      #
    # ------------------------------------------------------------------ #
    op.create_table(
        "task_lists",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False, server_default=sa.text("'Prep List'")),
        sa.Column("date", sa.Date, nullable=False, server_default=sa.text("CURRENT_DATE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ------------------------------------------------------------------ #
    #  24. task_items                                                      #
    # ------------------------------------------------------------------ #
    op.create_table(
        "task_items",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("list_id", UUID, sa.ForeignKey("task_lists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('pending', 'done')", name="valid_task_status"),
    )

    # ================================================================== #
    #  INDEXES                                                            #
    # ================================================================== #

    # Recipes
    op.create_index("idx_recipes_tenant", "recipes", ["tenant_id"])
    op.create_index("idx_recipes_name", "recipes", ["name"])
    op.create_index("idx_recipes_status", "recipes", ["tenant_id", "status"])
    op.create_index("idx_recipes_component", "recipes", ["tenant_id", "is_component"])

    # Ingredients
    op.create_index("idx_ingredients_name", "ingredients", ["name"])
    op.create_index("idx_ingredients_tenant", "ingredients", ["tenant_id"])
    op.create_index("idx_ingredients_parent", "ingredients", ["parent_id"])

    # Recipe ingredients
    op.create_index("idx_recipe_ingredients_recipe", "recipe_ingredients", ["recipe_id"])
    op.create_index("idx_recipe_ingredients_ingredient", "recipe_ingredients", ["ingredient_id"])

    # Recipe versions
    op.create_index("idx_recipe_versions_recipe", "recipe_versions", ["recipe_id"])

    # Agent interactions
    op.create_index("idx_agent_interactions_tenant", "agent_interactions", ["tenant_id", sa.text("created_at DESC")])
    op.create_index("idx_agent_interactions_agent", "agent_interactions", ["agent_id", sa.text("created_at DESC")])

    # Audit logs
    op.create_index("idx_audit_logs_tenant", "audit_logs", ["tenant_id", sa.text("created_at DESC")])
    op.create_index("idx_audit_logs_entity", "audit_logs", ["entity", "entity_id"])

    # Shopping & Tasks
    op.create_index("idx_shopping_items_list", "shopping_list_items", ["list_id"])
    op.create_index("idx_task_items_list", "task_items", ["list_id"])

    # FK indexes on junction tables
    op.create_index("idx_ing_allergens_allergen", "ingredient_allergens", ["allergen_id"])
    op.create_index("idx_ing_additives_additive", "ingredient_additives", ["additive_id"])
    op.create_index("idx_recipe_categories_cat", "recipe_categories", ["category_id"])
    op.create_index("idx_recipe_tags_tag", "recipe_tags", ["tag_id"])
    op.create_index("idx_ingredient_prices_ing", "ingredient_prices", ["ingredient_id"])

    # Partial unique indexes for ingredient_prices (NULL-safe supplier_id)
    op.execute("""
        CREATE UNIQUE INDEX uq_ingredient_supplier
        ON ingredient_prices (ingredient_id, supplier_id)
        WHERE supplier_id IS NOT NULL
    """)
    op.execute("""
        CREATE UNIQUE INDEX uq_ingredient_no_supplier
        ON ingredient_prices (ingredient_id)
        WHERE supplier_id IS NULL
    """)

    # ================================================================== #
    #  ROW LEVEL SECURITY                                                 #
    # ================================================================== #

    tenant_scoped_tables = [
        "recipes",
        "recipe_ingredients",
        "shopping_lists",
        "shopping_list_items",
        "task_lists",
        "task_items",
        "audit_logs",
        "agent_interactions",
    ]

    for table in tenant_scoped_tables:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")

        if table in ("shopping_list_items", "task_items"):
            op.execute(f"""
                CREATE POLICY tenant_isolation ON {table}
                FOR ALL USING (
                    list_id IN (
                        SELECT id FROM {"shopping_lists" if "shopping" in table else "task_lists"}
                        WHERE tenant_id = current_setting('app.current_tenant_id', true)::uuid
                    )
                )
            """)
        else:
            op.execute(f"""
                CREATE POLICY tenant_isolation ON {table}
                FOR ALL USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
            """)

    # Ingredients: tenant-owned OR shared (NULL tenant_id)
    op.execute("ALTER TABLE ingredients ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY ingredient_access ON ingredients
        FOR ALL USING (
            tenant_id IS NULL
            OR tenant_id = current_setting('app.current_tenant_id', true)::uuid
        )
    """)

    # ingredient_nutrition inherits access through the ingredient FK
    op.execute("ALTER TABLE ingredient_nutrition ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY nutrition_access ON ingredient_nutrition
        FOR ALL USING (
            ingredient_id IN (
                SELECT id FROM ingredients
                WHERE tenant_id IS NULL
                   OR tenant_id = current_setting('app.current_tenant_id', true)::uuid
            )
        )
    """)

    # ================================================================== #
    #  AUDIT TRIGGER FUNCTION                                             #
    # ================================================================== #
    op.execute("""
        CREATE OR REPLACE FUNCTION audit_trigger_func()
        RETURNS trigger
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
    """)

    audited_tables = ["recipes", "ingredients", "recipe_ingredients"]
    for table in audited_tables:
        op.execute(f"""
            CREATE TRIGGER audit_{table}
            AFTER INSERT OR UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION audit_trigger_func()
        """)

    # ================================================================== #
    #  updated_at AUTO-REFRESH TRIGGER                                    #
    # ================================================================== #
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$;
    """)

    tables_with_updated_at = [
        "tenants", "users", "ingredients", "ingredient_nutrition",
        "recipes", "ingredient_prices",
    ]
    for table in tables_with_updated_at:
        op.execute(f"""
            CREATE TRIGGER set_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION set_updated_at()
        """)


def downgrade() -> None:
    audited_tables = ["recipes", "ingredients", "recipe_ingredients"]
    for table in audited_tables:
        op.execute(f"DROP TRIGGER IF EXISTS audit_{table} ON {table}")

    tables_with_updated_at = [
        "tenants", "users", "ingredients", "ingredient_nutrition",
        "recipes", "ingredient_prices",
    ]
    for table in tables_with_updated_at:
        op.execute(f"DROP TRIGGER IF EXISTS set_{table}_updated_at ON {table}")

    op.execute("DROP FUNCTION IF EXISTS audit_trigger_func() CASCADE")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at() CASCADE")

    tables_to_drop = [
        "task_items", "task_lists",
        "shopping_list_items", "shopping_lists",
        "audit_logs", "agent_interactions",
        "recipe_versions", "recipe_nutrition_cache",
        "recipe_tags", "recipe_categories",
        "tags", "categories",
        "ingredient_prices",
        "ingredient_additives", "ingredient_allergens",
        "additives", "allergens",
        "recipe_ingredients",
        "recipes",
        "ingredient_nutrition",
        "ingredients",
        "agents", "users", "tenants",
    ]
    for table in tables_to_drop:
        op.drop_table(table, if_exists=True)

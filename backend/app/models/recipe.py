from typing import Optional, TYPE_CHECKING
import datetime
import decimal
import uuid

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Text, Uuid, text
from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from app.models.users import Users, Tenants
    from app.models.recipe_ingredients import RecipeIngredient
    from app.models.tmp_draft import Categories, Tags, RecipeVersions


class Recipe(SQLModel, table=True):
    __tablename__ = 'recipes'
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'active', 'archived')", name='valid_status'),
        CheckConstraint('portion_size_grams IS NULL OR portion_size_grams > 0::numeric', name='positive_portion_size_grams'),
        CheckConstraint('portions_count_resolved IS NULL OR portions_count_resolved > 0::numeric', name='positive_portions_count_resolved'),
        CheckConstraint("status::text <> 'active'::text OR yield_mode::text <> 'weight'::text OR portion_size_grams IS NOT NULL AND portion_size_grams > 0::numeric", name='weight_mode_requires_portion_size_when_active'),
        CheckConstraint('total_cooked_weight_grams IS NULL OR total_cooked_weight_grams >= 0::numeric', name='positive_total_cooked_weight_grams'),
        CheckConstraint('total_raw_weight_grams IS NULL OR total_raw_weight_grams >= 0::numeric', name='positive_total_raw_weight_grams'),
        CheckConstraint("yield_mode::text = ANY (ARRAY['count'::character varying, 'weight'::character varying]::text[])", name='valid_yield_mode'),
        ForeignKeyConstraint(['created_by'], ['users.id'], name='recipes_created_by_fkey'),
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='recipes_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='recipes_pkey'),
        Index('idx_recipes_component', 'tenant_id', 'is_component'),
        Index('idx_recipes_name', 'name'),
        Index('idx_recipes_status', 'tenant_id', 'status'),
        Index('idx_recipes_tenant', 'tenant_id'),
        Index('idx_recipes_yield_mode', 'yield_mode'),
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    tenant_id: uuid.UUID = Field(sa_column=Column('tenant_id', Uuid, nullable=False))
    name: str = Field(sa_column=Column('name', String(255), nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column('description', Text))
    yield_amount: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('yield_amount', Numeric))
    yield_unit: Optional[str] = Field(default=None, sa_column=Column('yield_unit', String(50)))
    instructions: Optional[str] = Field(default=None, sa_column=Column('instructions', Text))
    reduction_factor: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('reduction_factor', Numeric, server_default=text('1.0')))
    status: str = Field(sa_column=Column('status', String(50), nullable=False, server_default=text("'draft'::character varying")))
    is_component: bool = Field(sa_column=Column('is_component', Boolean, nullable=False, server_default=text('false')))
    recipe_number: Optional[str] = Field(default=None, sa_column=Column('recipe_number', String(100)))
    preparation_time_minutes: Optional[int] = Field(default=None, sa_column=Column('preparation_time_minutes', Integer, nullable=True))
    cooking_time_minutes: Optional[int] = Field(default=None, sa_column=Column('cooking_time_minutes', Integer, nullable=True))
    shelf_life_text: Optional[str] = Field(default=None, sa_column=Column('shelf_life_text', Text))
    storage_temperature: Optional[str] = Field(default=None, sa_column=Column('storage_temperature', String(50)))
    notes: Optional[str] = Field(default=None, sa_column=Column('notes', Text))
    photo_url: Optional[str] = Field(default=None, sa_column=Column('photo_url', Text))
    created_by: Optional[uuid.UUID] = Field(default=None, sa_column=Column('created_by', Uuid))
    yield_mode: str = Field(sa_column=Column('yield_mode', String(20), nullable=False, server_default=text("'count'::character varying")))
    portion_size_grams: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('portion_size_grams', Numeric))
    total_raw_weight_grams: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('total_raw_weight_grams', Numeric))
    total_cooked_weight_grams: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('total_cooked_weight_grams', Numeric))
    portions_count_resolved: Optional[decimal.Decimal] = Field(default=None, sa_column=Column('portions_count_resolved', Numeric))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))

<<<<<<< HEAD
    # Text fields
    description: str | None = Field(default=None, sa_column=Column(Text))
    description_short: str | None = Field(default=None, sa_column=Column(Text))
    instructions: str | None = Field(default=None, sa_column=Column(Text))
    notes: str | None = Field(default=None, sa_column=Column(Text))
    notes_instructions: str | None = Field(default=None, sa_column=Column(Text))
    serving_recommendation: str | None = Field(default=None, sa_column=Column(Text))
    side_dishes: str | None = Field(default=None, sa_column=Column(Text))
    storage_text: str | None = Field(default=None, sa_column=Column(Text))
    origin_fish: str | None = Field(default=None, sa_column=Column(Text))
    origin_location: str | None = Field(default=None, sa_column=Column(Text))
    devices: str | None = Field(default=None, sa_column=Column(Text))
    utensils: str | None = Field(default=None, sa_column=Column(Text))
    packaging: str | None = Field(default=None, sa_column=Column(Text))
    packaging_material: str | None = Field(default=None, sa_column=Column(Text))
    ingredient_list_custom: str | None = Field(default=None, sa_column=Column(Text))
    allergene_source: str | None = Field(default=None, sa_column=Column(Text))
    preparation_time: str | None = Field(default=None, sa_column=Column(Text))
    waiting_time: str | None = Field(default=None, sa_column=Column(Text))
    cooking_time: str | None = Field(default=None, sa_column=Column(Text))
    shelf_life: str | None = Field(default=None, sa_column=Column(Text))

    # Varying character fields
    yield_unit: str | None = Field(default=None, max_length=50)
    recipe_number: str | None = Field(default=None, max_length=100)
    batch_number: str | None = Field(default=None, max_length=100)
    storage_temperature: str | None = Field(default=None, max_length=50)
    labor_effort: str | None = Field(default=None, max_length=50)
    nutri_score_category: str | None = Field(default=None, max_length=10)
    unit_measure: str | None = Field(default=None, max_length=50)
    unit_serving: str | None = Field(default=None, max_length=50)
    yield_mode: str = Field(default="count", max_length=20)

    # Numeric fields
    yield_amount: Decimal | None = Field(sa_column=Column(Numeric(10, 2)))
    reduction_factor: Decimal | None = Field(sa_column=Column(Numeric(10, 4)))
    eigene_menge: Decimal | None = Field(sa_column=Column(Numeric(10, 2)))
    net_weight: Decimal | None = Field(sa_column=Column(Numeric(10, 2)))
    fill_weight: Decimal | None = Field(sa_column=Column(Numeric(10, 2)))
    fill_quantity: Decimal | None = Field(sa_column=Column(Numeric(10, 2)))
    drained_weight: Decimal | None = Field(sa_column=Column(Numeric(10, 2)))
    total_weight: Decimal | None = Field(sa_column=Column(Numeric(10, 2)))
    portion_weight: Decimal | None = Field(sa_column=Column(Numeric(10, 2)))
    margin: Decimal | None = Field(sa_column=Column(Numeric(10, 2)))
    nutri_score_veg_fruits: Decimal | None = Field(sa_column=Column(Numeric(5, 2)))
    preference_nutri_value: Decimal | None = Field(sa_column=Column(Numeric(10, 2)))
    portion_size_grams: Decimal | None = Field(sa_column=Column(Numeric))
    total_raw_weight_grams: Decimal | None = Field(sa_column=Column(Numeric))
    total_cooked_weight_grams: Decimal | None = Field(sa_column=Column(Numeric))
    portions_count_resolved: Decimal | None = Field(sa_column=Column(Numeric))

    # Booleans
    portion_by_weight: bool = Field(default=False, sa_column=Column(Boolean, server_default=text("false")))
    mise_en_place_display: bool = Field(default=True, sa_column=Column(Boolean, server_default=text("true")))
    is_component: bool = Field(default=False, sa_column=Column(Boolean, server_default=text("false")))

    # Dates
    production_date: date | None = Field(sa_column=Column(DATE))
    use_by_date: date | None = Field(sa_column=Column(DATE))
    expiry_date: date | None = Field(sa_column=Column(DATE))

    # Foreign keys
    tenant_id: UUID | None = Field(default=None, foreign_key="tenants.id")
    created_by: UUID | None = Field(default=None, foreign_key="users.id")

    # Relationship attributes
    recipe_ingredients: list["RecipeIngredient"] = Relationship(back_populates="recipe", sa_relationship_kwargs={"passive_deletes": True})
    recipe_photos: list["RecipePhoto"] = Relationship(back_populates="recipe")
    created_by_user: Optional["Users"] = Relationship(back_populates="recipes")
    tenant: Optional["Tenants"] = Relationship(back_populates="recipes")
=======
    category: list['Categories'] = Relationship(back_populates='recipe', sa_relationship_kwargs={'secondary': 'recipe_categories'})
    created_by_user: Optional['Users'] = Relationship(back_populates='recipes')
    tenant: 'Tenants' = Relationship(back_populates='recipes')
    tag: list['Tags'] = Relationship(back_populates='recipe', sa_relationship_kwargs={'secondary': 'recipe_tags'})
    recipe_ingredients: list['RecipeIngredient'] = Relationship(back_populates='recipe', sa_relationship_kwargs={'foreign_keys': '[RecipeIngredient.recipe_id]', 'passive_deletes': True})
    recipe_versions: list['RecipeVersions'] = Relationship(back_populates='recipe')
>>>>>>> main


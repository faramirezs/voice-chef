from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Index, CheckConstraint, Column, Text, text, Boolean, DateTime, Numeric

if TYPE_CHECKING:
    from app.models.users import Users, Tenants

class Recipe(SQLModel, table=True):
    __tablename__ = "recipes"
    __table_args__ = (
        Index("idx_recipes_batch_number", "batch_number"),
        Index("idx_recipes_is_component", "is_component"),
        Index("idx_recipes_reduction_factor", "reduction_factor"),
        Index("idx_recipes_yield_mode", "yield_mode"),
        Index("ix_recipes_name", "name"),
        CheckConstraint("portion_size_grams IS NULL OR portion_size_grams > 0", 
                        name="positive_portion_size_grams"),
        CheckConstraint("portions_count_resolved IS NULL OR portions_count_resolved > 0", 
                        name="positive_portions_count_resolved"),
        CheckConstraint("total_cooked_weight_grams IS NULL OR total_cooked_weight_grams >= 0", 
                        name="positive_total_cooked_weight_grams"),
        CheckConstraint("total_raw_weight_grams IS NULL OR total_raw_weight_grams >= 0", 
                        name="positive_total_raw_weight_grams"),
        CheckConstraint("yield_mode::text = ANY (ARRAY['count'::character varying, 'weight'::character varying]::text[])", 
                        name="valid_yield_mode",),
        CheckConstraint("(status)::text <> 'active'::text OR (yield_mode)::text <> 'weight'::text OR (portion_size_grams IS NOT NULL AND portion_size_grams > 0::numeric)",
                        name="weight_mode_requires_portion_size_when_active")
    )

    # Primary key, Core fields, Timestamps
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    status: str = Field(default="draft", max_length=50)
    created_at: datetime | None = Field(sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")))
    updated_at: datetime | None = Field(sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=text("now()")))

    # Text fields
    description: str | None = Field(sa_column=Column(Text))
    description_short: str | None = Field(sa_column=Column(Text))
    instructions: str | None = Field(sa_column=Column(Text))
    notes: str | None = Field(sa_column=Column(Text))
    notes_instructions: str | None = Field(sa_column=Column(Text))
    serving_recommendation: str | None = Field(sa_column=Column(Text))
    side_dishes: str | None = Field(sa_column=Column(Text))
    storage_text: str | None = Field(sa_column=Column(Text))
    origin_fish: str | None = Field(sa_column=Column(Text))
    origin_location: str | None = Field(sa_column=Column(Text))
    devices: str | None = Field(sa_column=Column(Text))
    utensils: str | None = Field(sa_column=Column(Text))
    packaging: str | None = Field(sa_column=Column(Text))
    packaging_material: str | None = Field(sa_column=Column(Text))
    ingredient_list_custom: str | None = Field(sa_column=Column(Text))
    allergene_source: str | None = Field(sa_column=Column(Text))
    preparation_time: str | None = Field(sa_column=Column(Text))
    waiting_time: str | None = Field(sa_column=Column(Text))
    cooking_time: str | None = Field(sa_column=Column(Text))
    shelf_life: str | None = Field(sa_column=Column(Text))

    # Varying character fields
    yield_unit: str | None = Field(max_length=50)
    recipe_number: str | None = Field(max_length=100)
    batch_number: str | None = Field(max_length=100)
    storage_temperature: str | None = Field(max_length=50)
    labor_effort: str | None = Field(max_length=50)
    nutri_score_category: str | None = Field(max_length=10)
    unit_measure: str | None = Field(max_length=50)
    unit_serving: str | None = Field(max_length=50)
    yield_mode: str = Field(default="count", max_length=20, nullable=False)

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
    production_date: datetime | None = Field(sa_column=Column(DateTime(timezone=True)))
    use_by_date: datetime | None = Field(sa_column=Column(DateTime(timezone=True)))
    expiry_date: datetime | None = Field(sa_column=Column(DateTime(timezone=True)))

    # Foreign keys
    tenant_id: UUID | None = Field(foreign_key="tenants.id")
    created_by: UUID | None = Field(foreign_key="users.id")

    # Relationship attributes
    created_by_user: Optional["Users"] = Relationship(back_populates="recipes")
    tenant: Optional["Tenants"] = Relationship(back_populates="recipes")
    # created_by: Optional["Users"] = Relationship(back_populates="recipes")

    # recipe_ingredients: list["RecipeIngredient"] = Relationship(
    #     back_populates="recipe"
    # )

    # recipe_photos: list["RecipePhoto"] = Relationship(
    #     back_populates="recipe"
    # )

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import text, DateTime, Column, Numeric, CheckConstraint
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user_models import Users, Tenants


class Recipe(SQLModel, table=True):
    # NOTE MP "type: ignore" tells Pylance to suppress the type error for this specific line
    __tablename__ = "recipes"  # type: ignore

    # For this table, the `__table_args__` block is required
    # The reason is complex constraints known as CHECK constraints: 
    # database-level data validation rules (for example, “the ‘weight’ mode requires that a portion size be specified”)
    __table_args__ = (
        CheckConstraint("portion_size_grams IS NULL OR portion_size_grams > 0", name="positive_portion_size_grams"),
        CheckConstraint("yield_mode IN ('count', 'weight')", name="valid_yield_mode"),
        CheckConstraint(
            "status <> 'active' OR yield_mode <> 'weight' OR (portion_size_grams IS NOT NULL AND portion_size_grams > 0)",
            name="weight_mode_requires_portion_size_when_active"
        ),
        CheckConstraint("portions_count_resolved IS NULL OR portions_count_resolved > 0", name="positive_portions_count_resolved"),
        CheckConstraint("total_cooked_weight_grams IS NULL OR total_cooked_weight_grams >= 0", name="positive_total_cooked_weight_grams"),
        CheckConstraint("total_raw_weight_grams IS NULL OR total_raw_weight_grams >= 0", name="positive_total_raw_weight_grams"),
    )

    id: UUID = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")}
    )
    name: str = Field(max_length=255, index=True, nullable=False)
    status: str = Field(default="draft", max_length=50)
    created_at: datetime = Field(
        default=None, # Python should not generate a value
        sa_column=Column(
            DateTime(timezone=True), 
            nullable=False, 
            server_default=text("now()"),
        )
    )
    updated_at: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
            onupdate=text("now()"),
        )
    )
    # Foreign keys
    tenant_id: UUID | None = Field(default=None, foreign_key="tenants.id")
    created_by: UUID | None = Field(default=None, foreign_key="users.id")

    # Text fields
    description: str | None = None
    description_short: str | None = None
    instructions: str | None = None
    notes: str | None = None
    notes_instructions: str | None = None
    serving_recommendation: str | None = None
    side_dishes: str | None = None
    storage_text: str | None = None
    origin_fish: str | None = None
    origin_location: str | None = None
    devices: str | None = None
    utensils: str | None = None
    packaging: str | None = None
    packaging_material: str | None = None
    ingredient_list_custom: str | None = None
    allergene_source: str | None = None
    preparation_time: str | None = None
    waiting_time: str | None = None
    cooking_time: str | None = None
    shelf_life: str | None = None

    # Numeric fields
    yield_amount: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 2)))
    reduction_factor: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(10, 4), index=True)
    )
    eigene_menge: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 2)))
    net_weight: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 2)))
    fill_weight: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 2)))
    fill_quantity: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 2)))
    drained_weight: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 2)))
    total_weight: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 2)))
    portion_weight: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 2)))
    margin: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 2)))
    nutri_score_veg_fruits: Decimal | None = Field(default=None, sa_column=Column(Numeric(5, 2)))
    preference_nutri_value: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 2)))
    portion_size_grams: Decimal | None = Field(default=None, sa_column=Column(Numeric))
    total_raw_weight_grams: Decimal | None = Field(default=None, sa_column=Column(Numeric))
    total_cooked_weight_grams: Decimal | None = Field(default=None, sa_column=Column(Numeric))
    portions_count_resolved: Decimal | None = Field(default=None, sa_column=Column(Numeric))

    # Strings
    yield_unit: str | None = Field(default=None, max_length=50)
    recipe_number: str | None = Field(default=None, max_length=100)
    batch_number: str | None = Field(default=None, max_length=100, index=True)
    storage_temperature: str | None = Field(default=None, max_length=50)
    labor_effort: str | None = Field(default=None, max_length=50)
    nutri_score_category: str | None = Field(default=None, max_length=10)
    unit_measure: str | None = Field(default=None, max_length=50)
    unit_serving: str | None = Field(default=None, max_length=50)
    yield_mode: str = Field(default='count', max_length=20, index=True)

    # Booleans
    portion_by_weight: bool = Field(default=False)
    mise_en_place_display: bool = Field(default=True)
    is_component: bool = Field(default=False, index=True)

    # Dates
    production_date: date | None = None
    use_by_date: date | None = None
    expiry_date: date | None = None

    # Relationship attributes
    tenant: 'Tenants | None' = Relationship(back_populates="recipes")
    created_by_user: 'Users | None' = Relationship(back_populates="recipes")

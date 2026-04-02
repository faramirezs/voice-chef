from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import text, Text, Column, Numeric
from sqlalchemy import CheckConstraint, Index, Boolean
import uuid
from uuid import UUID
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime     # database column type: `timestamp with time zone`
from datetime import date, datetime # Python type: type hints and runtime values
from decimal import Decimal


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
        CheckConstraint("yield_mode::text = ANY (ARRAY['count'::text, 'weight'::text])", name="valid_yield_mode"),
        CheckConstraint(
            "(status)::text <> 'active'::text OR (yield_mode)::text <> 'weight'::text OR (portion_size_grams IS NOT NULL AND portion_size_grams > 0::numeric)",
            name="weight_mode_requires_portion_size_when_active"
        ),
        CheckConstraint("portions_count_resolved IS NULL OR portions_count_resolved > 0", name="positive_portions_count_resolved"),
        CheckConstraint("total_cooked_weight_grams IS NULL OR total_cooked_weight_grams >= 0", name="positive_total_cooked_weight_grams"),
        CheckConstraint("total_raw_weight_grams IS NULL OR total_raw_weight_grams >= 0", name="positive_total_raw_weight_grams"),
        Index('idx_recipes_batch_number', 'batch_number'),
        Index('idx_recipes_is_component', 'is_component'),
        Index('idx_recipes_reduction_factor', 'reduction_factor'),
        Index('idx_recipes_yield_mode', 'yield_mode'),
    )

    id: UUID = Field(
        # app-side UUID generation for MVP delivery
        default_factory=uuid.uuid4,
        # scheduling DB-enforced UUID defaults as post-MVP hardening
        # sa_column_kwargs={"server_default": text("gen_random_uuid()")}
        primary_key=True,
    )
    name: str = Field(max_length=255, index=True, nullable=False)
    status: str = Field(
        default="draft",
        max_length=50,
        nullable=False,
        sa_column_kwargs={"server_default": text("'draft'::character varying")},
    )
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

    # Numeric fields
    yield_amount: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 2)))
    reduction_factor: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(10, 4))
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
    batch_number: str | None = Field(default=None, max_length=100)
    storage_temperature: str | None = Field(default=None, max_length=50)
    labor_effort: str | None = Field(default=None, max_length=50)
    nutri_score_category: str | None = Field(default=None, max_length=10)
    unit_measure: str | None = Field(default=None, max_length=50)
    unit_serving: str | None = Field(default=None, max_length=50)
    yield_mode: str = Field(
        default='count', # default is for Python
        max_length=20,
        nullable=False,
        sa_column_kwargs={"server_default": text("'count'::character varying")} # server_default is for the database
    )

    # Booleans
    portion_by_weight: bool | None = Field(
        default=False,
        sa_column=Column(Boolean, server_default=text('false'))
    )
    mise_en_place_display: bool | None = Field(
        default=True, 
        sa_column=Column(Boolean, server_default=text('true'))
    )
    is_component: bool | None = Field(
        default=False, 
        sa_column=Column(Boolean, server_default=text('false'))
    )

    # Dates
    production_date: date | None = None
    use_by_date: date | None = None
    expiry_date: date | None = None

    # Relationship attributes
    tenant: Optional["Tenants"] = Relationship(back_populates="recipes")
    created_by_user: Optional["Users"] = Relationship(back_populates="recipes")

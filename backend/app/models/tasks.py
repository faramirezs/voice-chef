from typing import TYPE_CHECKING
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import (
    CheckConstraint, ForeignKeyConstraint, PrimaryKeyConstraint, Index,
    Column, Date, DateTime, String, text, Integer, Boolean
)
from datetime import datetime, date as date_type
from uuid import UUID
from decimal import Decimal

if TYPE_CHECKING:
    from app.models.users import Tenants


# ─── ORM SQLMOdel model for task_lists ─────────────────────────────────────────────────

class TaskLists(SQLModel, table=True):
    __tablename__ = 'task_lists'
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='task_lists_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='task_lists_pkey')
    )

    # Primary key, Core fields, Timestamps
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    name: str = Field(sa_column=Column('name', String(255), nullable=False, server_default=text("'Prep List'")))
    created_at: datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    date: date_type = Field(sa_column=Column('date', Date, nullable=False, server_default=text('CURRENT_DATE')))
    # Foreign keys
    tenant_id: UUID = Field(nullable=False)
    # Relationship attributes
    tenant: 'Tenants' = Relationship(back_populates='task_lists')
    task_items: list['TaskItems'] = Relationship(back_populates='list')


# ─── ORM SQLMOdel model for task_items ─────────────────────────────────────────────────

class TaskItems(SQLModel, table=True):
    __tablename__ = 'task_items'
    __table_args__ = (
        CheckConstraint("status::text = ANY (ARRAY['pending', 'done']::text[])", name='valid_task_status'),
        ForeignKeyConstraint(['list_id'], ['task_lists.id'], ondelete='CASCADE', name='task_items_list_id_fkey'),
        PrimaryKeyConstraint('id', name='task_items_pkey'),
        Index('idx_task_items_list', 'list_id')
    )

    # Primary key, Core fields, Timestamps
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    title: str = Field(max_length=500, nullable=False)
    created_at: datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))

    status: str = Field(sa_column=Column('status', String(50), nullable=False, server_default=text("'pending'")))
    sort_order: int = Field(sa_column=Column('sort_order', Integer, nullable=False, server_default=text('0')))
    
    # Foreign keys
    list_id: UUID = Field(nullable=False)
    # Relationship attributes
    list: 'TaskLists' = Relationship(back_populates='task_items')


# ─── ORM SQLMOdel model for shopping_lists ─────────────────────────────────────────────────

class ShoppingLists(SQLModel, table=True):
    __tablename__ = 'shopping_lists'
    __table_args__ = (
        ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='shopping_lists_tenant_id_fkey'),
        PrimaryKeyConstraint('id', name='shopping_lists_pkey')
    )
    # Primary key, Core fields, Timestamps
    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    name: str = Field(
        sa_column=Column('name', String(255), nullable=False, server_default=text("'Shopping List'")))
    is_active: bool = Field(nullable=False, sa_column_kwargs={"server_default": text("true")})
    created_at: datetime = Field(
        sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    # Foreign keys
    tenant_id: UUID = Field(nullable=False)
    # Relationship attributes
    tenant: 'Tenants' = Relationship(back_populates='shopping_lists')
    shopping_list_items: list['ShoppingListItems'] = Relationship(back_populates='list')


# ─── ORM SQLMOdel model for shopping_lists ─────────────────────────────────────────────────

class ShoppingListItems(SQLModel, table=True):
    __tablename__ = 'shopping_list_items'
    __table_args__ = (
        CheckConstraint('quantity_grams IS NULL OR quantity_grams >= 0::numeric', name='shopping_list_items_quantity_grams_non_negative'),
        ForeignKeyConstraint(['list_id'], ['shopping_lists.id'], ondelete='CASCADE', name='shopping_list_items_list_id_fkey'),
        PrimaryKeyConstraint('id', name='shopping_list_items_pkey'),
        Index('idx_shopping_items_list', 'list_id')
    )

    id: UUID = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": text("gen_random_uuid()")})
    name: str = Field(max_length=255, nullable=False)
    is_checked: bool = Field(nullable=False, sa_column_kwargs={"server_default": text("false")})
    sort_order: int = Field(sa_column=Column('sort_order', Integer, nullable=False, server_default=text('0')))
    created_at: datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    quantity: Decimal | None = Field(default=None)
    unit: str | None = Field(default=None, max_length=50)
    quantity_grams: Decimal | None = Field(default=None)
    # Foreign keys
    list_id: UUID = Field(nullable=False)
    # Relationship attributes
    list: 'ShoppingLists' = Relationship(back_populates='shopping_list_items')

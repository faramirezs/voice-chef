from typing import Optional
import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, Index, PrimaryKeyConstraint, String, UniqueConstraint, Uuid, text
from sqlmodel import Field, Relationship, SQLModel


class Tenants(SQLModel, table=True):
    __table_args__ = (
        Index('ix_tenants_name', 'name'),
        Index('ix_tenants_slug', 'slug', unique=True),
        PrimaryKeyConstraint('id', name='tenants_pkey'),
        UniqueConstraint('slug', name='tenants_slug_key')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True))
    name: str = Field(sa_column=Column('name', String(255), nullable=False))
    slug: str = Field(sa_column=Column('slug', String(100), nullable=False))
    is_active: bool = Field(sa_column=Column('is_active', Boolean, nullable=False, server_default=text('true')))
    created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
    updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))
    settings: Optional[str] = Field(default=None, sa_column=Column('settings', String))

    agents: list['Agents'] = Relationship(back_populates='tenant')
    categories: list['Categories'] = Relationship(back_populates='tenant')
    ingredients: list['Ingredients'] = Relationship(back_populates='tenant')
    shopping_lists: list['ShoppingLists'] = Relationship(back_populates='tenant')
    tags: list['Tags'] = Relationship(back_populates='tenant')
    task_lists: list['TaskLists'] = Relationship(back_populates='tenant')
    users: list['Users'] = Relationship(back_populates='tenant')
    agent_interactions: list['AgentInteractions'] = Relationship(back_populates='tenant')
    recipes: list['Recipes'] = Relationship(back_populates='tenant')

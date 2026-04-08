from typing import Optional
import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKeyConstraint, PrimaryKeyConstraint, String, UniqueConstraint, Uuid, text
from sqlmodel import Field, Relationship, SQLModel


class Users(SQLModel, table=True):
	__table_args__ = (
		ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='users_tenant_id_fkey'),
		PrimaryKeyConstraint('id', name='users_pkey'),
		UniqueConstraint('email', name='users_email_key')
	)

	id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
	tenant_id: uuid.UUID = Field(sa_column=Column('tenant_id', Uuid, nullable=False))
	email: str = Field(sa_column=Column('email', String(320), nullable=False))
	password_hash: str = Field(sa_column=Column('password_hash', String(255), nullable=False))
	role: str = Field(sa_column=Column('role', String(50), nullable=False, server_default=text("'editor'::character varying")))
	is_active: bool = Field(sa_column=Column('is_active', Boolean, nullable=False, server_default=text('true')))
	created_at: datetime.datetime = Field(sa_column=Column('created_at', DateTime(True), nullable=False, server_default=text('now()')))
	updated_at: datetime.datetime = Field(sa_column=Column('updated_at', DateTime(True), nullable=False, server_default=text('now()')))

	tenant: 'Tenants' = Relationship(back_populates='users')
	recipes: list['Recipes'] = Relationship(back_populates='users')

"""Seed reference lookup tables from JSON

Revision ID: 012
Revises: 011
Create Date: 2026-04-11
"""

import json
from pathlib import Path

from alembic import op

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def _reference_data_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "scripts" / "reference_data"


def _sql_str(value: object) -> str:
    if value is None:
        return "NULL"
    s = str(value)
    return "'" + s.replace("'", "''") + "'"


def _sql_int(value: object) -> str:
    if value is None:
        return "NULL"
    return str(int(value))


def _sql_numeric(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        raise TypeError("unexpected bool for numeric column")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    return str(value)


def _sql_bool(value: object) -> str:
    return "TRUE" if value else "FALSE"


def upgrade() -> None:
    ref = _reference_data_dir()

    with open(ref / "units.json", encoding="utf-8") as fh:
        units_rows = json.load(fh)
    unit_values = ", ".join(
        (
            "(gen_random_uuid(), "
            f"{_sql_str(row['code'])}, "
            f"{_sql_str(row['name_de'])}, "
            f"{_sql_str(row.get('name_en'))}, "
            f"{_sql_numeric(row.get('grams_per_unit'))}, "
            f"{_sql_str(row['unit_type'])}, "
            f"{_sql_bool(row['is_base'])})"
        )
        for row in units_rows
    )
    op.execute(
        "INSERT INTO public.units (id, code, name_de, name_en, grams_per_unit, unit_type, is_base) "
        f"VALUES {unit_values} "
        "ON CONFLICT (code) DO UPDATE SET "
        "name_de = EXCLUDED.name_de, "
        "name_en = EXCLUDED.name_en, "
        "grams_per_unit = EXCLUDED.grams_per_unit, "
        "unit_type = EXCLUDED.unit_type, "
        "is_base = EXCLUDED.is_base;"
    )

    with open(ref / "allergens.json", encoding="utf-8") as fh:
        allergen_rows = json.load(fh)
    allergen_values = ", ".join(
        (
            "(gen_random_uuid(), "
            f"{_sql_int(row['code'])}, "
            f"{_sql_str(row['name_de'])}, "
            f"{_sql_str(row.get('name_en'))}, "
            f"{_sql_int(row.get('parent_code'))})"
        )
        for row in allergen_rows
    )
    op.execute(
        "INSERT INTO public.allergens (id, code, name_de, name_en, parent_code) "
        f"VALUES {allergen_values} "
        "ON CONFLICT (code) DO UPDATE SET "
        "name_de = EXCLUDED.name_de, "
        "name_en = EXCLUDED.name_en, "
        "parent_code = EXCLUDED.parent_code;"
    )

    with open(ref / "additives.json", encoding="utf-8") as fh:
        additive_rows = json.load(fh)
    additive_values = ", ".join(
        (
            "(gen_random_uuid(), "
            f"{_sql_int(row['code'])}, "
            f"{_sql_str(row['name_de'])}, "
            f"{_sql_str(row.get('name_en'))})"
        )
        for row in additive_rows
    )
    op.execute(
        "INSERT INTO public.additives (id, code, name_de, name_en) "
        f"VALUES {additive_values} "
        "ON CONFLICT (code) DO UPDATE SET "
        "name_de = EXCLUDED.name_de, "
        "name_en = EXCLUDED.name_en;"
    )


def downgrade() -> None:
    pass

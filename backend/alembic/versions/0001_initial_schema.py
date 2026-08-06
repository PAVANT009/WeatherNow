"""Create cities, districts, and weather_records tables.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-03 22:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "country_code", name="uq_cities_name_country_code"),
    )

    op.create_table(
        "districts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("city_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=10, scale=7), nullable=False),
        sa.Column("longitude", sa.Numeric(precision=10, scale=7), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["city_id"], ["cities.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("city_id", "name", name="uq_districts_city_id_name"),
    )
    op.create_index("ix_districts_city_id", "districts", ["city_id"], unique=False)

    op.create_table(
        "weather_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("district_id", sa.Integer(), nullable=False),
        sa.Column("temperature", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("feels_like", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("humidity", sa.Integer(), nullable=False),
        sa.Column("wind_speed", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("weather_status", sa.String(length=80), nullable=False),
        sa.Column("weather_description", sa.String(length=255), nullable=True),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["districts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "district_id",
            "observed_at",
            name="uq_weather_records_district_observed_at",
        ),
    )
    op.create_index(
        "ix_weather_records_district_id",
        "weather_records",
        ["district_id"],
        unique=False,
    )
    op.create_index(
        "ix_weather_records_observed_at",
        "weather_records",
        ["observed_at"],
        unique=False,
    )
    op.create_index(
        "ix_weather_records_district_id_observed_at",
        "weather_records",
        ["district_id", "observed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_weather_records_district_id_observed_at",
        table_name="weather_records",
    )
    op.drop_index("ix_weather_records_observed_at", table_name="weather_records")
    op.drop_index("ix_weather_records_district_id", table_name="weather_records")
    op.drop_table("weather_records")
    op.drop_index("ix_districts_city_id", table_name="districts")
    op.drop_table("districts")
    op.drop_table("cities")

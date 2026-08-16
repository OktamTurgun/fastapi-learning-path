"""seed initial roles

Revision ID: 26f928deb23b
Revises: c74572d0bb05
Create Date: 2026-08-16 09:27:13.499890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26f928deb23b'
down_revision: Union[str, Sequence[str], None] = 'c74572d0bb05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    roles_table = sa.table(
        "roles",
        sa.column("name", sa.String),
    )
    op.bulk_insert(
        roles_table,
        [
            {"name": "customer"},
            {"name": "courier"},
            {"name": "admin"},
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM roles WHERE name IN ('customer', 'courier', 'admin')")

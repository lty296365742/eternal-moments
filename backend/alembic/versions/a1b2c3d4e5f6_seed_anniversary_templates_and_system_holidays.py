"""seed anniversary templates and system holidays

Revision ID: a1b2c3d4e5f6
Revises: ffbc7185d0c3
Create Date: 2026-09-16 14:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ffbc7185d0c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ALL_RELATIONSHIPS = ["父亲", "母亲", "配偶", "子女", "朋友", "同事", "兄弟姐妹", "老师", "其他"]

TEMPLATES = [
    ("birthday", "生日", "yearly"),
    ("wedding", "结婚纪念日", "yearly"),
    ("memorial", "忌日", "yearly"),
    ("love_start", "相恋纪念日", "yearly"),
    ("work_start", "入职纪念日", "yearly"),
    ("graduation", "毕业纪念日", "yearly"),
    ("move_in", "搬家纪念日", "once"),
    ("baby_born", "宝宝出生", "yearly"),
    ("adoption", "领养纪念日", "yearly"),
    ("other", "其他", "yearly"),
]

HOLIDAYS = [
    ("H0001", "元旦", "01-01", ALL_RELATIONSHIPS, "每年1月1日"),
    ("H0002", "情人节", "02-14", ["配偶"], "每年2月14日"),
    ("H0003", "妇女节", "03-08", ["母亲", "配偶"], "每年3月8日"),
    ("H0004", "母亲节", "05-SUN-2", ["母亲"], "每年5月第2个星期日"),
    ("H0005", "父亲节", "06-SUN-3", ["父亲"], "每年6月第3个星期日"),
    ("H0006", "儿童节", "06-01", ["子女"], "每年6月1日"),
    ("H0007", "教师节", "09-10", ["老师"], "每年9月10日"),
    ("H0008", "国庆节", "10-01", ALL_RELATIONSHIPS, "每年10月1日"),
    ("H0009", "圣诞节", "12-25", ["配偶", "子女", "朋友"], "每年12月25日"),
]


def upgrade() -> None:
    template_table = sa.table(
        "t_anniversary_template",
        sa.column("title_key", sa.String),
        sa.column("label", sa.String),
        sa.column("default_repeat", sa.String),
        sa.column("sort_order", sa.BigInteger),
        sa.column("status", sa.SmallInteger),
    )
    op.bulk_insert(template_table, [
        {"title_key": key, "label": label, "default_repeat": repeat,
         "sort_order": i + 1, "status": 1}
        for i, (key, label, repeat) in enumerate(TEMPLATES)
    ])

    holiday_table = sa.table(
        "t_system_holiday",
        sa.column("holiday_id", sa.String),
        sa.column("name", sa.String),
        sa.column("date_rule", sa.String),
        sa.column("applicable_relationships", sa.JSON),
        sa.column("description", sa.String),
        sa.column("status", sa.SmallInteger),
    )
    op.bulk_insert(holiday_table, [
        {"holiday_id": hid, "name": name, "date_rule": rule,
         "applicable_relationships": rels, "description": desc, "status": 1}
        for hid, name, rule, rels, desc in HOLIDAYS
    ])


def downgrade() -> None:
    keys = ", ".join(f"'{key}'" for key, _, _ in TEMPLATES)
    op.execute(f"DELETE FROM t_anniversary_template WHERE title_key IN ({keys})")
    ids = ", ".join(f"'{hid}'" for hid, _, _, _, _ in HOLIDAYS)
    op.execute(f"DELETE FROM t_system_holiday WHERE holiday_id IN ({ids})")

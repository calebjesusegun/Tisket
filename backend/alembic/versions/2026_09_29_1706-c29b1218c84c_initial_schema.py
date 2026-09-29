"""initial schema: tasks, notes, tags

Revision ID: c29b1218c84c
Revises:
Create Date: 2026-09-29 17:06:55

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c29b1218c84c"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Expressions must match app/repositories/search.py so PostgreSQL can use the indexes.
# Title words weigh more (A) than body words (B) when ranking.
TASKS_TSV = (
    "(setweight(to_tsvector('english'::regconfig, coalesce(title, '')), 'A') || "
    "setweight(to_tsvector('english'::regconfig, coalesce(description, '')), 'B'))"
)
NOTES_TSV = (
    "(setweight(to_tsvector('english'::regconfig, coalesce(title, '')), 'A') || "
    "setweight(to_tsvector('english'::regconfig, coalesce(content, '')), 'B'))"
)


def upgrade() -> None:
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tags")),
        sa.UniqueConstraint("name", name=op.f("uq_tags_name")),
    )
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("todo", "in_progress", "done", name="task_status",
                    native_enum=False, create_constraint=True, length=20),
            nullable=False,
        ),
        sa.Column(
            "priority",
            sa.Enum("low", "medium", "high", name="task_priority",
                    native_enum=False, create_constraint=True, length=20),
            nullable=False,
        ),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reminder_dismissed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tasks")),
    )
    op.create_index(op.f("ix_tasks_due_at"), "tasks", ["due_at"])
    op.create_index(op.f("ix_tasks_priority"), "tasks", ["priority"])
    op.create_index(op.f("ix_tasks_status"), "tasks", ["status"])

    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("pinned", sa.Boolean(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], name=op.f("fk_notes_task_id_tasks"),
                                ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notes")),
    )
    op.create_index(op.f("ix_notes_pinned"), "notes", ["pinned"])
    op.create_index(op.f("ix_notes_task_id"), "notes", ["task_id"])

    op.create_table(
        "task_tags",
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], name=op.f("fk_task_tags_tag_id_tags"),
                                ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"],
                                name=op.f("fk_task_tags_task_id_tasks"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("task_id", "tag_id", name=op.f("pk_task_tags")),
    )
    op.create_index(op.f("ix_task_tags_tag_id"), "task_tags", ["tag_id"])

    op.create_table(
        "note_tags",
        sa.Column("note_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["note_id"], ["notes.id"],
                                name=op.f("fk_note_tags_note_id_notes"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], name=op.f("fk_note_tags_tag_id_tags"),
                                ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("note_id", "tag_id", name=op.f("pk_note_tags")),
    )
    op.create_index(op.f("ix_note_tags_tag_id"), "note_tags", ["tag_id"])

    if op.get_bind().dialect.name == "postgresql":
        op.execute(f"CREATE INDEX ix_tasks_fts ON tasks USING gin ({TASKS_TSV})")
        op.execute(f"CREATE INDEX ix_notes_fts ON notes USING gin ({NOTES_TSV})")


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP INDEX IF EXISTS ix_notes_fts")
        op.execute("DROP INDEX IF EXISTS ix_tasks_fts")
    op.drop_index(op.f("ix_note_tags_tag_id"), table_name="note_tags")
    op.drop_table("note_tags")
    op.drop_index(op.f("ix_task_tags_tag_id"), table_name="task_tags")
    op.drop_table("task_tags")
    op.drop_index(op.f("ix_notes_task_id"), table_name="notes")
    op.drop_index(op.f("ix_notes_pinned"), table_name="notes")
    op.drop_table("notes")
    op.drop_index(op.f("ix_tasks_status"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_priority"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_due_at"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_table("tags")

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'xxxx_fix_events_sports'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None

def upgrade():
    # Add sport_type to events
    op.add_column('events', sa.Column('sport_type', sa.Text(), nullable=True))

    # Set NOT NULL for sports_id and tour_year_id in events
    op.alter_column('events', 'sports_id', nullable=False)
    op.alter_column('events', 'tour_year_id', nullable=False)

    # Drop info column from sports if it exists
    with op.get_bind().connect() as conn:
        result = conn.execute("SELECT column_name FROM information_schema.columns WHERE table_name='sports' AND column_name='info';")
        if result.fetchone():
            op.drop_column('sports', 'info')


def downgrade():
    # Reverse upgrade if needed
    op.drop_column('events', 'sport_type')
    op.alter_column('events', 'sports_id', nullable=True)
    op.alter_column('events', 'tour_year_id', nullable=True)
    op.add_column('sports', sa.Column('info', sa.JSON))

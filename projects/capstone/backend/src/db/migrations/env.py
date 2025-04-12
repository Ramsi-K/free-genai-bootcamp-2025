from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlmodel import SQLModel

# Import all models needed for migrations
from src.models.associations import word_group_map
from src.models.word import Word
from src.models.group import WordGroup
from src.models.sample_sentence import SampleSentence
from src.models.activity_log import ActivityLog
from src.models.study_session import StudySession
from src.models.session_stats import SessionStats, session_words_shown
from src.models.word_stats import WordStats
from src.models.wrong_input import WrongInput
from src.models.study_activity import StudyActivity
from src.models.word_review_item import WordReviewItem

from src.config import SQLITE_DB_PATH

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set SQLModel metadata for migrations
target_metadata = SQLModel.metadata


def get_url():
    return f"sqlite:///{SQLITE_DB_PATH}"


def run_migrations_offline():
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

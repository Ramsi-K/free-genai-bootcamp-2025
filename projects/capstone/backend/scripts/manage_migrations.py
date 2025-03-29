import os
import sys
from pathlib import Path
import alembic.config


def main():
    """Manage database migrations"""
    # Ensure we're in the project root
    os.chdir(Path(__file__).parent.parent)

    if len(sys.argv) < 2:
        print("Available commands:")
        print("  migrate       Create a new migration")
        print("  upgrade      Apply migrations")
        print("  downgrade   Revert migrations")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "migrate":
        # Create new migration
        message = args[0] if args else "Migration"
        alembic.config.main(argv=["revision", "--autogenerate", "-m", message])
    elif command == "upgrade":
        # Apply migrations
        revision = args[0] if args else "head"
        alembic.config.main(argv=["upgrade", revision])
    elif command == "downgrade":
        # Revert migrations
        revision = args[0] if args else "-1"
        alembic.config.main(argv=["downgrade", revision])
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

import sys
import alembic.config


def main():
    """Manage database migrations"""
    # Removed os.chdir to avoid path conflicts with Alembic

    if len(sys.argv) < 2:
        print("Available commands:")
        print("  migrate       Create a new migration")
        print("  upgrade      Apply migrations")
        print("  downgrade   Revert migrations")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    # Define the path to the alembic.ini file relative to the project root
    # (where this script is expected to be run from within Docker)
    alembic_cfg_path = "src/db/migrations/alembic.ini"

    if command == "migrate":
        # Create new migration
        message = args[0] if args else "Migration"
        alembic.config.main(
            argv=[
                "-c",
                alembic_cfg_path,
                "revision",
                "--autogenerate",
                "-m",
                message,
            ]
        )
    elif command == "upgrade":
        # Apply migrations
        revision = args[0] if args else "head"
        alembic.config.main(argv=["-c", alembic_cfg_path, "upgrade", revision])
    elif command == "downgrade":
        # Revert migrations
        revision = args[0] if args else "-1"
        alembic.config.main(
            argv=["-c", alembic_cfg_path, "downgrade", revision]
        )
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

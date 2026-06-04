from sqlalchemy import text

from apso_backend.db.session import create_session_factory


def main() -> None:
    factory = create_session_factory()
    with factory() as session:
        result = session.execute(text("select current_database(), current_user")).one()
        vector = session.execute(
            text("select exists(select 1 from pg_extension where extname = 'vector')")
        ).scalar()
    print({"database": result[0], "user": result[1], "pgvector_enabled": bool(vector)})


if __name__ == "__main__":
    main()


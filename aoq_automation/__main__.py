from . import start, db
import asyncio
import argparse


async def main() -> None:
    parser = argparse.ArgumentParser(prog="aoq-automation")
    parser.add_argument(
        "--create-tables",
        help="create tables in database (use this when database is new)",
        action="store_true",
    )
    parser.add_argument(
        "--verbose-sql",
        help="show all sql expressions, that are sent into database",
        action="store_true",
    )
    args = parser.parse_args()
    
    db.connect(echo=args.verbose_sql)
    print("connected to database")
    if args.create_tables:
        await db.create_tables()
        print("tables created")
    print("starting polling")
    await start()


if __name__ == "__main__":
    asyncio.run(main())

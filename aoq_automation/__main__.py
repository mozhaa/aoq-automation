import argparse
import asyncio

from aoq_automation.database.database import db
from aoq_automation.telegram.start import start


async def main() -> None:
    parser = argparse.ArgumentParser(prog="aoq-automation")
    parser.add_argument(
        "--recreate-tables",
        help="recreate tables in database",
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
    if args.recreate_tables:
        await db.recreate_tables()
        print("tables created")
    print("starting polling")
    await start()


if __name__ == "__main__":
    asyncio.run(main())

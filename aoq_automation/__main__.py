from . import start, create_tables, connect
import asyncio
import argparse


async def main() -> None:
    parser = argparse.ArgumentParser(prog="aoq-automation")
    parser.add_argument(
        "--create-tables",
        help="create tables in database (use this when database is new)",
        action="store_true",
    )
    args = parser.parse_args()
    connect()
    if args.create_tables:
        await create_tables()
        print("tables created")
    print("starting polling")
    await start()


if __name__ == "__main__":
    asyncio.run(main())

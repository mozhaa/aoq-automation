from argparse import ArgumentParser
import aoq

def main():
    parser = ArgumentParser(
        prog='Anime Opening Quiz Automation',
        description='Tools for automatically create anime opening quizzes',
    )
    
    parser.add_argument('--token-file', default='files/token.hidden')
    parser.add_argument('--db-init-file', default='files/start.sql')
    parser.add_argument('--db-file', default='files/database.db')
    
    args = parser.parse_args()
    
    database = aoq.database.Database(fp=args.db_file, init_fp=args.db_init_file)
    telegram_bot = aoq.telegram.Bot(token_fp=args.token_file, db=database)
    telegram_bot.start()

if __name__ == '__main__':
    main()
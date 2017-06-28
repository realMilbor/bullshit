from Database import *
from UI import *


def main(argv):
    # with Database(username='DB_USER_1', password='ORACLE', host='192.168.56.101', port=1521, listener='orcl') as db:
    db = Database(schema='DB_USER_1', username='DB_USER_1', password='oracle', host='127.0.0.1', port=1521, listener='orcl')

    architect = Architect(db)
    sys.exit(architect.run())

if __name__ == '__main__':
    main(sys.argv)

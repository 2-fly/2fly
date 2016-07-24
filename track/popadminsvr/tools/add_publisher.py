import sys

import init_env
import settings
import utils
from db_client import Publisher, DBClient

if __name__ == "__main__":
    try:
        assert len(sys.argv) == 4
    except:
        print "usage : %s [username] [password] [email]"%sys.argv[0]
        exit(-1)

    name = sys.argv[1]
    pwd = utils.gen_secret(sys.argv[2])
    email = sys.argv[3]
    db = DBClient(settings.db_user, settings.db_password,
        settings.db_host, settings.db_name)

    l = len(db.select_all(Publisher))
    user = Publisher(name=name, password=pwd, email=email)
    db.do_save(user)
    assert len(db.select_all(Publisher)) == l + 1

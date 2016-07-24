import sys

import init_env
import settings
import utils
from db_client import Advertiser, DBClient, Publisher

if __name__ == "__main__":
    try:
        assert len(sys.argv) == 5
    except:
        print "usage : %s [username] [password] [email]"%sys.argv[0]
        exit(-1)

    name = sys.argv[2]
    pwd = utils.gen_secret(sys.argv[3])
    email = sys.argv[4]

    if sys.argv[1] == "advertiser":
        cls = Advertiser
    else:
        cls = Publisher
    db = DBClient(settings.db_user, settings.db_password,
        settings.db_host, settings.db_name)
    user = db.select_one(cls, name=name)

    user.password=pwd
    user.email=email
    db.do_save(user)

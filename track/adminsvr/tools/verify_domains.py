import init_env
import route53
import ujson
import datetime
from dns.route53_helper import key_id, key_secret, compare_domains_by_zones, get_all_host_zones, get_conn
from commlib.db.db_tabledef import verify_domains_key
from adminsvr import settings
from adminsvr.db_client import User
from adminsvr.global_vars import global_db_set as DBSet

def get_domains(domains_str):
    return [d.split(";")[0] for d in domains_str.split(",")]

def get_all_domains():
    domains = {}
    dset = []
    users = DBSet.get_db_client().iter_all(User)
    for user in users:
        domains[user.id] = []
        for d in get_domains(user.lander_domains):
            if d in dset:
                continue
            domains[user.id].append(d)
            dset.append(d)
        for d in get_domains(user.track_domains):
            if d in dset:
                continue
            domains[user.id].append(d)
            dset.append(d)
    return domains

def get_verify_domains():
    uid_domains_map = get_all_domains()


    conn = get_conn()
    zones = get_all_host_zones(conn)
    for uid, domains in uid_domains_map.items():
        print "------------uid:%s------------"%uid
        verify_domains(conn, zones, uid, domains)

def verify_domains(conn, zones, uid, domains, n=3):
    ret = compare_domains_by_zones(domains, uid, '/root/massival/dns/tmp', zones, conn)
    suc = {}
    fail = {}
    for domain, res in ret.items():
        if res['ret'] == -1:
            fail[domain] = res
        else:
            suc[domain] = res
    for domain, res in suc.items():
        print "***************add domain********************"
        print domain, res
        redis_cli.add_one(verify_domains_key, domain, ujson.dumps(res))
    if n:
        return verify_domains(conn, zones, uid, fail.keys(), n=n-1)
    else:
        for domain, res in fail.items():
            print "***************error domain********************"
            print domain, res
            redis_cli.add_one(verify_domains_key, domain, ujson.dumps(res))

redis_cli = None

if __name__ == "__main__":
    ds = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    print "############### %s ###############"%ds
    DBSet.set_init(True)
    redis_cli = DBSet.get_redis_db()
    get_verify_domains()
    ds = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    print "############### %s ###############"%ds

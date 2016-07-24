#!/usr/bin/env python
# -*- coding:utf-8 -*-
import ujson

import init_env
from adminsvr.db_client import DBClient, User
from commlib.db.redis_helper import RedisHashTable2
from commlib.db.db_tabledef import virusdomains_table, virus_domains_key, virusdomain_report_table
import adminsvr.settings as settings

def main_func():
    db_client = DBClient(settings.db_user, settings.db_password, settings.db_host, settings.db_name)
    redis_cli = RedisHashTable2(host=settings.redis_host, port=settings.redis_port)
    new = []

    for user in db_client.select_all(User):
        [new.append(i.split(";")[0]) for i in user.lander_domains.split(",") if i]
        [new.append(i) for i in user.track_domains.split(",") if i]

    domains = redis_cli.get_one(virusdomains_table, virus_domains_key)
    domains = ujson.loads(domains) if domains else []
    for domain in new:
        if domain in domains:
            continue
        domains.append(domain)
    redis_cli.add_one(virusdomains_table, virus_domains_key, ujson.dumps(domains))

if __name__ == "__main__":
    main_func()

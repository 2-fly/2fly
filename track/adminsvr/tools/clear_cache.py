import sys
import redis
import init_env

import adminsvr.settings

if __name__ == '__main__':
    host = 'localhost'
    if len(sys.argv) >  1:
        host = sys.argv[1]

    cli = redis.Redis(host, port=settings.redis_port)
    items = cli.scan(0, 'mss_*', 1000000)[1]
    if items:
        print cli.delete(*items)


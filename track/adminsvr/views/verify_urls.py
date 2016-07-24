import random
import copy


#from dns.route53_helper import compare_domains

def verify_all(domains, username):
    #return compare_domains(domains, username, '/root/massival/dns/tmp')

    ret1 = {'ret' : 0, 'ns' : ['domain1.com', 'domain2.com', 'domain3.com', 'domain4.com']}
    ret2 = {'ret' : 0, 'ns' : []}
    ret3 = {'ret' : -1, 'ns' : []}
    ret4 = {'ret' : -1, 'ns' : ['domain1.com', 'domain2.com', 'domain3.com', 'domain4.com']}
    ret = [ret1, ret2, ret3, ret4]
    d = { }
    for domain in domains:
        d[domain] = copy.deepcopy(random.choice(ret))
    return d

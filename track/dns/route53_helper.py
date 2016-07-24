#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import datetime
import copy
import ujson as json
from os import path as osp

import route53



key_id = 'AKIAIAQW37AJGIKM6JAA'
key_secret = 'MQ0t/NP4X3II/H2Muhk9Ncyyj0h5eKEtSZzwKrNd'


sample_dict = {
    'Comment': 'A new record set for the zone.',
    'Changes': [],
}


sample_record = {
    'Action': 'CREATE',
    'ResourceRecordSet':{
        'Name':'Name',
        'Type':'A',
        'SetIdentifier':'SetIdentifier',
        'Region':'Region',
        'AliasTarget':{
            'HostedZoneId':'HostedZoneId',
            'DNSName':'DNSName',
            'EvaluateTargetHealth':False,
        }
    }
}

regions = [
    ('france', 'eu-central-1', 'alpha-massival-176504631.eu-central-1.elb.amazonaws.com', 'Z215JYRZR1TBD5'),
    ('brazil', 'sa-east-1', 'alpha-massival-146227615.sa-east-1.elb.amazonaws.com', 'Z2ES78Y61JGQKS'),
    ('california', 'us-west-1', 'alpha-massival-231557346.us-west-1.elb.amazonaws.com', 'Z1M58G0W56PQJA'),
    ('virginia', 'us-east-1', 'alpha-massival-73847199.us-east-1.elb.amazonaws.com', 'Z3DZXE0Q79N41H'),
    ('japan', 'ap-northeast-1', 'alpha-massival-2117648168.ap-northeast-1.elb.amazonaws.com', 'Z2YN17T5R711GT'),
    ('singapore', 'ap-southeast-1', 'alpha-massival-1679653588.ap-southeast-1.elb.amazonaws.com', 'Z1WI8VXHPB1R38'),
    ('ireland', 'eu-west-1', 'alpha-massival-818600649.eu-west-1.elb.amazonaws.com', 'Z3NF1Z3NOM5OY2'),
    ('oregon', 'us-west-2', 'alpha-massival-1468186311.us-west-2.elb.amazonaws.com', 'Z33MTJ483KN6FU'),
    ('sydney', 'ap-southeast-2', 'alpha-massival-288057044.ap-southeast-2.elb.amazonaws.com', 'Z2999QAZ9SRTIC'),
    #('mumbai', 'ap-south-1', 'dualstack.alpha-massival-29461675.ap-south-1.elb.amazonaws.com.', 'ZP97RAFLXTNZK'),
]



def new_domain_dict(domain, hosted_zone_id):
    ret_dict = copy.deepcopy(sample_dict)
    for _region in regions:
        record = new_sample_record('%s.'%domain, _region[0],
                _region[1], _region[2], _region[3])
        ret_dict['Changes'].append(record)

        record = new_sample_record('\\052.%s.'%domain, _region[0],
                _region[1], _region[2], _region[3])
        ret_dict['Changes'].append(record)

    return ret_dict



def new_sample_record(domain, region_name, region, dns_name, region_hosted_zone_id):
    tmp_record = copy.deepcopy(sample_record)
    tmp_record['ResourceRecordSet']['Name'] = domain
    tmp_record['ResourceRecordSet']['AliasTarget']['HostedZoneId'] = region_hosted_zone_id
    tmp_record['ResourceRecordSet']['SetIdentifier'] = region_name
    tmp_record['ResourceRecordSet']['Region'] = region
    tmp_record['ResourceRecordSet']['AliasTarget']['DNSName'] = dns_name
    return tmp_record




def find_host_zone(conn, domain):
    domain = domain.lower().strip()
    if not domain:
        return None
    ret_zones = find_host_zones(conn, {domain:1})
    return ret_zones.get(domain)



def find_host_zones(conn, domains):
    ret_zones = {}
    for zone in conn.list_hosted_zones():
        zone_name = zone.name.rstrip('.')
        if zone_name in domains:
            ret_zones[zone_name] = zone
            if len(domains) == len(ret_zones):
                break

    return ret_zones



def create_host_zone(conn, domain, uid, domain_output_dir):
    ds = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    new_zone, change_info = conn.create_hosted_zone(
            name=domain,
            caller_reference=ds,
            comment='%s-%s'%(uid, ds))

    #<route53.hosted_zone.HostedZone object at 0x7f85555ec790>
    #{'request_status': 'PENDING', 'request_submitted_at': datetime.datetime(2015, 9, 5, 3, 19, 48, 985000, tzinfo=<UTC>), 'request_id': '/change/C1QU9C3X2W1MXS'}
    msg = 'create_host_zone %s %s %s %s'%(domain, new_zone.id, new_zone.nameservers, change_info)
    write_domain_log(domain, msg, domain_output_dir)

    #print 'new_zone %s  %s'%(new_zone, change_info)
    #['ns-1836.awsdns-37.co.uk', 'ns-189.awsdns-23.com', 'ns-1452.awsdns-53.org', 'ns-547.awsdns-04.net']
    #for i in z.record_sets:
    #<AResourceRecordSet: \052.wouai.com.>
    return new_zone.id, new_zone.nameservers


def write_domain_log(domain, log, domain_output_dir):
    log_file = osp.join(domain_output_dir, '%s.log'%domain)
    f = open(log_file, 'a')
    ds = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    f.write('%s\t%s\n'%(ds, log))
    f.close()


def get_dns_file(domain):
    temp_file = 'tmp/%s.tmp'%domain
    return temp_file


def create_dns(domain, uid):
    temp_file = get_dns_file(domain)
    ds = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    cmd = 'aws route53 create-hosted-zone --name %s --caller-reference %s --hosted-zone-config Comment="%s-%s" > %s '%(domain, ds, uid, ds, temp_file)
    s = os.popen(cmd).read()
    try:
        obj = json.loads(s)
    except Exception, ex:
        raise ex

    host_zone_id = obj['HostedZone']['Id']


def create_record_sets(host_zone_id, domain, domain_output_dir):
    domain_dict = new_domain_dict(domain, host_zone_id)
    sample_json = json.dumps(domain_dict)
    temp_json_file = osp.join(domain_output_dir, '%s.json'%domain)
    f = open(temp_json_file, 'w')
    f.write(sample_json)
    f.close()

    cmd = 'aws route53 change-resource-record-sets --hosted-zone-id %s --change-batch file://%s'%(host_zone_id, temp_json_file)
    s = os.popen(cmd).read()

    msg = 'create_record_sets %s %s %s'%(domain, host_zone_id, s.replace('\n', ' '))
    write_domain_log(domain, msg, domain_output_dir)
    return s


def do_nslookup(domain):
    s = os.popen('nslookup -q=ns -timeout=1 -retry=1 %s 8.8.8.8'%domain).read()
    lines = s.split('\n')
    all_ns = []
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if domain in line and 'nameserver' in line:
            parts = line.split('=')
            if len(parts) < 2:
                continue
            ns = parts[1]
            ns = ns.strip()
            ns = ns.strip(' ')
            ns = ns.strip('.')
            if ns:
                all_ns.append(ns)

    return all_ns


def get_alias_records(zone):
    records = []
    try:
        for rec in zone.record_sets:
            if rec.is_alias_record_set():
                records.append(rec)
    except Exception, e:
        print "-----------", zone.name
        print  Exception, e
    return records

def get_conn():
    return route53.connect(aws_access_key_id=key_id, aws_secret_access_key=key_secret,)


def compare_nameservers(ns_a, ns_b):
    set_a = set(ns_a)
    set_b = set(ns_b)
    return len(set_a) == len(set_b) and len(set_a - set_b) == 0

def get_all_host_zones(conn):
    ret_zones = {}
    for zone in conn.list_hosted_zones():
        zone_name = zone.name.rstrip('.')
        ret_zones[zone_name] = zone
    return ret_zones

def compare_domains_by_zones(domains, uid, domain_output_dir, zones, conn):

    results = {}
    domains = handle_domains(domains)
    for domain in domains:
        try:
            zone = zones.get(domain)
            if zone is None:
                print 'domain zone not found: %s'%domain
                hosted_zone_id, nameservers = create_host_zone(conn, domain, uid, domain_output_dir)
                create_record_sets(hosted_zone_id, domain, domain_output_dir)
                actual_nameservers = do_nslookup(domain)
                res = compare_nameservers(nameservers, actual_nameservers)
                ret_code = 0 if res else -1
                results[domain] = dict(ret=ret_code, ns=nameservers)
                continue

            if 1:
                records = get_alias_records(zone)
                if len(records) < len(regions)*2:
                    print 'records not enough(%d): %s'%(len(records), domain)
                    results[domain] = dict(ret=-1, ns=['alias_records not enough'])
                    continue

            route53_nameservers = zone.nameservers
            actual_nameservers = do_nslookup(domain)

            res = compare_nameservers(route53_nameservers, actual_nameservers)
            if not res:
                print "#############"
                print domain, res, route53_nameservers, actual_nameservers
                print "#############"

            ret_code = 0 if res else -1
            results[domain] = dict(ret=ret_code, ns=route53_nameservers)
        except Exception, e:
            print domain, Exception, e

    return results

def handle_domains(domains):
    ret = []
    for d in domains:
        d = d.strip().lower()
        if d:
            ret.append(d)
    return ret

def compare_domains(domains, uid, domain_output_dir):
    conn = route53.connect(aws_access_key_id=key_id, aws_secret_access_key=key_secret,)

    results = {}
    domains = handle_domains(domains)
    zones = find_host_zones(conn, domains)
    for domain in domains:
        zone = zones.get(domain)
        if zone is None:
            print 'domain zone not found: %s'%domain
            hosted_zone_id, nameservers = create_host_zone(conn, domain, uid, domain_output_dir)
            create_record_sets(hosted_zone_id, domain, domain_output_dir)
            actual_nameservers = do_nslookup(domain)
            res = compare_nameservers(nameservers, actual_nameservers)
            ret_code = 0 if res else -1
            results[domain] = dict(ret=ret_code, ns=nameservers)
            continue

        if 1:
            records = get_alias_records(zone)
            if len(records) < len(regions)*2:
                print 'records not enough(%d): %s'%(len(records), domain)
                results[domain] = dict(ret=-1, ns=['alias_records not enough'])
                continue

        route53_nameservers = zone.nameservers
        actual_nameservers = do_nslookup(domain)

        res = compare_nameservers(route53_nameservers, actual_nameservers)
        print domain, res, route53_nameservers

        ret_code = 0 if res else -1
        results[domain] = dict(ret=ret_code, ns=route53_nameservers)

    return results


def delete_hostzones(domains, domain_output_dir):
    conn = route53.connect(aws_access_key_id=key_id, aws_secret_access_key=key_secret,)

    domains = handle_domains(domains)
    zones = find_host_zones(conn, domains)
    for domain in domains:
        zone = zones.get(domain)
        if zone:
            #for rec in zone.record_sets:
            #    rec.delete()
            zone.delete(force=True)

            msg = 'delete_hostzones %s %s'%(domain, zone.id)
            write_domain_log(domain, msg, domain_output_dir)


if __name__ == '__main__':
    #from pprint import pprint as pp
    #print pp(new_domain_dict('aa.com', 'x3123ssd'))

    all_domains = set()
    with open(sys.argv[1], 'r') as f:
        for line in f:
            all_domains.add(line.strip())

    uid = 10
    import init_env
    domain_output_dir = osp.join(init_env.cur_path, 'tmp')
    compare_domains(all_domains, uid, domain_output_dir)




#!/usr/bin/env python
# -*-coding:utf-8 -*-
from view import ModelView, Render
from utils import get_model_uri
from mako.template import Template
from db_client import Offer, LandingPage, Path, SwapRotation, Flow
from config.rule_config import rule, rule_type

import ujson
import global_vars
import view_util

REFERRER_TYPE = 4
ISP_TYPE = 5

class FlowView(ModelView):
    def __init__(self, session_info):
        self.__tablename__ = Flow
        self.db_client = global_vars.global_db_set.get_db_client()
        self.my_uid = view_util.username2uid(session_info['username'], self.db_client)
        self.check_relative_uid(self.my_uid)
        self.args = view_util.get_request_args()
        self.args['uid'] = self.my_uid

    def save_path(self, p):
        try:
            if p.get('id'):
                p_model = self.paths[p['id']]
            else:
                p_model = Path(uid=self.my_uid)
            p['lander'] = ",".join([";".join([str(l['val']), str(l.get('weight', 0))]) for l in p['lander']])
            p['offer'] = ",".join([str(o['val']) for o in p['offer']])
            if not p['lander'] or not p['offer']:
                return "error"
            p_model.name = p['name']
            p_model.offers = p['offer']
            p_model.landing_pages = p['lander']
            p_model.direct_linking = p['direct_linking']
            if p_model.id:
                self.db_client.do_save(p_model)
            else:
                self.db_client.add_one(p_model)
                assert p_model.id
            p['id'] = p_model.id
        except AssertionError:
            print "add path id error", p
            return {'res':False, 'msg': "path id error"}
        except Exception, ex:
            print ex
            print "path error", p
            return {'res':False, 'msg': "path error"}
        return {'res':True}

    def handle_rule(self, rules):
        remove_rules = []
        for rule in rules:
            if rule['type'] in [REFERRER_TYPE, ISP_TYPE]:
                r_str = rule['rules']
                r_str = "\n".join([r.strip() for r in r_str.split("\n") if r])
                rule['rules'] = r_str.encode("utf8")
                if not r_str:
                    remove_rules.append(rule)
        [rules.remove(r) for r in remove_rules]

    def save_swap(self, swap):
        try:
            for p in swap['paths']:
                res = self.save_path(p)
                if not res['res']:
                    return res

            paths = ",".join([";".join([str(p['id']), str(p['weight'])]) for p in swap['paths']])
            swap['paths'] = paths
            if swap.get('id'):
                model = self.swaps[swap['id']]
            else:
                model = SwapRotation(uid=self.my_uid)
            model.paths = swap['paths']
            if swap.get('condition'):
                model.name = swap['name']
                self.handle_rule(swap['condition'])
                model.rules = ujson.dumps(swap['condition']).encode("utf8")
            else:
                model.name = "default"
            if model.id:
                self.db_client.do_save(model)
            else:
                self.db_client.add_one(model)
                assert model.id
            swap['id'] = model.id
        except AssertionError:
            print "add swap id error", swap
            return {'res':False, 'msg': "swap id error"}
        except:
            print "add swap error", swaps
            return {'res':False, 'msg': "swap error"}
        return {'res':True}

    def parse_sql_seq2dict(self, sql_seq):
        ret = {}
        for i in sql_seq:
            ret[i.id] = i
        return ret

    def check_flow(self, flow):
        try:
            if flow.get("id"):
                assert self.flow
                assert flow['default_swap']['id'] in self.swaps
                assert isinstance(flow['rules'], list)
                for r in flow['rules']:
                    if r.get('id'):
                        assert r['id'] in self.swaps
            for p in flow['default_swap']['paths']:
                assert self.check_path(p)
            for r in flow['rules']:
                assert r['condition']
                for p in r['paths']:
                    assert self.check_path(p)
                for c in r['condition']:
                    assert c['rules']
                    if type(c['rules']) == str or type(c['rules']) == unicode:
                        c['rules'] = c['rules']
                        assert c['rules']
                        assert c.get('type')
                        flag = False
                        for rt in rule_type:
                            if rt['id'] == c['type']:
                                flag = True
                                break
                        assert flag
                        continue
                    assert rule.get(c['type'])
                    for rid in c['rules']:
                        assert rule[c['type']].get(rid)
                    if c['type'] != 3:
                        c['rules'] = [rule[c['type']][rid]['value'] for rid in c['rules'] if rule[c['type']].get(rid)]
        except Exception, ex:
            print Exception, ex
            return False
        return True


    def check_path(self, p):
        try:
            if p.get('id'):
                assert p['id'] in self.paths
            assert p['weight'] >= 0
            for l in p['lander']:
                assert l['val'] in self.landers
            for o in p['offer']:
                assert o['val'] in self.offers
        except Exception, ex:
            print ex
            return False
        return True


    def save_flow(self):
        try:
            flow = ujson.loads(self.args['flow'])

            self.landers =  self.parse_sql_seq2dict(self.db_client.iter_all(LandingPage, uid=self.my_uid))
            self.offers = self.parse_sql_seq2dict(self.db_client.iter_all(Offer, uid=self.my_uid))
            self.paths = self.parse_sql_seq2dict(self.db_client.iter_all(Path, uid=self.my_uid))
            self.flow = self.db_client.select_one(Flow, id=flow.get("id", -1))
            self.swaps = self.parse_sql_seq2dict(self.db_client.iter_all(SwapRotation, uid=self.my_uid))

            if not self.check_flow(flow):
                return '{"err":"error"}'
            res = self.save_swap(flow['default_swap'])
            if not res['res']:
                return '{"err": "%s"}'%res['msg']
            swap_ids = [str(flow['default_swap']['id'])]
            for r in flow['rules']:
                res = self.save_swap(r)
                if not res['res']:
                    return '{"err": "%s"}'%res["msg"]
                swap_ids.append(str(r['id']))
            swap_ids = ",".join(swap_ids)
            if flow.get('id'):
                model = self.flow
            else:
                model = Flow(uid=self.my_uid)
            model.name = flow['name']
            model.swaps = swap_ids

            if flow.get('id'):
                self.db_client.do_save(model)
            else:
                self.db_client.add_one(model)
                assert model.id
            return ujson.dumps({'name':model.name, 'id':model.id})
        except AssertionError:
            print "flow id error", flow
            return '{"err":"flow id error"}'


    def get_flow(self):
        if not self.args['id'].isdigit():
            return '{"err":"id must be int"}'

        flow_id = int(self.args['id'])
        self.landers =  self.parse_sql_seq2dict(self.db_client.iter_all(LandingPage, uid=self.my_uid))
        self.offers = self.parse_sql_seq2dict(self.db_client.iter_all(Offer, uid=self.my_uid))
        self.paths = self.parse_sql_seq2dict(self.db_client.iter_all(Path, uid=self.my_uid))
        self.swaps = self.parse_sql_seq2dict(self.db_client.iter_all(SwapRotation, uid=self.my_uid))


        flow = self.db_client.select_one(Flow, id=flow_id)
        if not flow:
            return '{"err":"flow is not existed"}'
        swap_ids = [int(sid) for sid in flow.swaps.split(",")]
        ret = {"rules": []}
        for sid in swap_ids:
            swap = self.get_swap(sid)
            if not swap.get("condition"):
                ret['default_swap'] = swap
            else:
                ret['rules'].append(swap)
        ret['id'] = flow.id
        ret['name'] = flow.name

        ret = ujson.dumps(ret)
        return ret

    def get_swap(self, sid):
        ret = {'paths':[]}
        model = self.swaps[sid]
        paths = model.paths.split(",") if model.paths else []
        for path in paths:
            sp = path.split(";")
            pid = sp[0]
            weight = sp[1] if len(sp) >= 2 else 100
            if not pid: continue
            pid = int(pid)
            p = self.get_path(pid)
            p['weight'] = weight
            ret['paths'].append(p)
        ret['id'] = model.id
        if model.rules:
            condition = ujson.loads(model.rules)
            for c in condition:
                c['rule_type_name'] = self.get_rule_type_name(c)
                if c['type'] == 3: #国家略过
                    continue
                if rule.get(c['type']):
                    c['rules'] = [self.get_rule_id(c['type'], r) for r in c['rules']]


            ret['condition'] = condition
            ret['name'] = model.name
        return ret

    def get_path(self, pid):
        ret = {}
        model = self.paths[pid]
        ret['lander'] = [lander.split(";") for lander in model.landing_pages.split(",")]
        #ret['lander'] = [{"val":int(lid), "weight":int(lw)} for lid, lw in ret['lander']]
        ret['lander'] = [{"val":int(lid)} for lid, lw in ret['lander']]
        ret['offer'] = [{"val":int(oid)} for oid in model.offers.split(",")]
        ret['id'] = model.id
        ret['name'] = model.name
        ret['direct_linking'] = model.direct_linking
        return ret

    def get_rule_type_name(self, c):
        for rt in rule_type:
            if rt['id'] == c['type']:
                return rt['name']

    def get_rule_id(self, rule_type, rule_val):
        rules = rule[rule_type]
        for k, v in rules.items():
            if rule_val == v['value']:
                return k
        return -1

#!/usr/bin/env python
# -*- coding:utf-8 -*-


class StatResult(object):
    def __init__(self):
        self.views = 0
        self.visits = 0
        self.clicks = 0
        self.convs = 0

        self.cost = 0.0
        self.revenue = 0.0
        self.profit = 0.0

        self.CPV = 0.0
        self.CTR = 0.0
        self.CR = 0.0
        self.CV = 0.0
        self.ROI = 0.0
        self.EPV = 0.0
        self.EPC = 0.0
        self.AP = 0.0
        self.CPC = 0.0
        self.WR = 0.68
        self.bids = 0

        self.rid_errors = 0
        self.cid_errors = 0
        self.postback_errors = 0

        self.warns = 0
        self.track_domain = 0
        self.lander_domain = 0
        self.cloak_ts = 0
        self.cloak = 0
        self.android = 0
        self.websiteid_typo = 0
        self.websiteid_digit = 0
        self.blackIps = 0

    def to_raw_items(self):
        self.recalc()
        s = []
        s.append(self.views)
        s.append(self.visits)
        s.append(self.clicks)
        s.append(self.convs)
        s.append(self.profit)
        s.append(self.revenue)
        s.append(self.cost)

        s.append(self.CPV*1000)
        s.append(self.CTR*0.01)
        s.append(self.CR*0.01)
        s.append(self.CV*0.01)
        s.append(self.ROI*0.01)
        s.append(self.EPV*1000)
        s.append(self.EPC*1000)
        s.append(self.AP)
        s.append(self.CPC)
        s.append(self.WR)

        #s.append(format(self.rid_errors, ','))
        #s.append(format(self.cid_errors, ','))
        #s.append(format(self.postback_errors, ','))

        s.append(self.warns)
        s.append(self.cloak_ts)
        s.append(self.cloak)
        s.append(self.track_domain)
        s.append(self.lander_domain)
        s.append(self.android)
        s.append(self.websiteid_typo)
        s.append(self.websiteid_digit)
        #s.append(self.blackIps)


        #s.append(str(self.rid_errors))
        #s.append(str(self.cid_errors))
        #s.append(str(self.postback_errors))
        errors = self.rid_errors + self.cid_errors + self.postback_errors
        s.append(errors)
        s.append(self.bids)
        return s

    def to_items(self):
        self.recalc()
        s = []
        s.append(format(self.views, ","))
        s.append(format(self.visits, ","))
        s.append(format(self.clicks, ","))
        s.append(format(self.convs, ","))
        s.append('$%s'%(format(float('%0.2f'%self.profit),",")))
        s.append('$%s'%(format(float('%0.2f'%self.revenue),",")))
        s.append('$%s'%(format(float('%0.2f'%self.cost),",")))

        s.append('$%0.2f'%(self.CPV*1000))
        s.append('%0.2f%%'%self.CTR)
        s.append('%0.2f%%'%self.CR)
        s.append('%0.2f%%'%self.CV)
        s.append('%0.2f%%'%self.ROI)
        s.append('$%0.2f'%(self.EPV*1000))
        s.append('$%0.2f'%(self.EPC*1000))
        s.append('$%0.2f'%self.AP)
        s.append('0.2f'%self.CPC)

        #s.append(format(self.rid_errors, ','))
        #s.append(format(self.cid_errors, ','))
        #s.append(format(self.postback_errors, ','))

        s.append(format(self.warns, ","))
        s.append(format(self.cloak_ts, ","))
        s.append(format(self.cloak, ","))
        s.append(format(self.track_domain, ","))
        s.append(format(self.lander_domain, ","))
        s.append(format(self.android, ","))
        s.append(format(self.websiteid_typo, ","))
        s.append(format(self.websiteid_digit, ","))
        #s.append(str(self.blackIps))

        errors = self.rid_errors + self.cid_errors + self.postback_errors
        s.append(str(errors))
        s.append(self.bids)
        #s.append(str(self.rid_errors))
        #s.append(str(self.cid_errors))
        #s.append(str(self.postback_errors))
        return s

    def to_csv_items(self):
        self.recalc()
        s = []
        s.append(format(self.views, ""))
        s.append(format(self.visits, ""))
        s.append(format(self.clicks, ""))
        s.append(format(self.convs, ""))
        s.append('%s'%(format(float('%0.2f'%self.revenue),"")))
        s.append('%s'%(format(float('%0.2f'%self.cost),"")))
        s.append('%s'%(format(float('%0.2f'%self.profit),"")))

        s.append('%0.2f'%(self.CPV*1000))
        s.append('%0.2f'%self.CTR)
        s.append('%0.2f'%self.CR)
        s.append('%0.2f'%self.CV)
        s.append('%0.2f'%self.ROI)
        s.append('%0.2f'%(self.EPV*1000))
        s.append('%0.2f'%(self.EPC*1000))

        s.append(str(self.rid_errors))
        s.append(str(self.cid_errors))
        s.append(str(self.postback_errors))
        s.append(format(self.warns, ""))
        return s

    def add(self, other):
        self.views += other.views
        self.visits += other.visits
        self.clicks += other.clicks
        self.convs += other.convs
        self.bids += other.bids

        self.cost += other.cost
        self.revenue += other.revenue
        self.profit += other.profit

        self.rid_errors += other.rid_errors
        self.cid_errors += other.cid_errors
        self.postback_errors += other.postback_errors

        self.warns += other.warns
        self.cloak_ts += other.cloak_ts
        self.cloak += other.cloak
        self.android += other.android
        self.websiteid_typo += other.websiteid_typo
        self.websiteid_digit += other.websiteid_digit
        self.track_domain += other.track_domain
        self.lander_domain += other.lander_domain
        self.blackIps += other.blackIps
        self.recalc()

    def add_raw(self, other):
        tmp = StatResult()
        tmp.from_dict(other)
        self.add(tmp)

    def recalc(self):
        self.profit = self.revenue - self.cost
        if self.views != 0:
            self.CPV = self.cost/self.views
            self.CTR = 100.0*self.visits/self.views
            self.CV = 100.0*self.convs/self.views
            self.EPV = self.revenue/self.views
        if self.visits != 0:
            self.CR = 100.0*self.convs/self.visits
            self.CPC = self.cost/self.visits

        if self.bids != 0:
            self.WR = self.views * 1.0 / self.bids

        if self.cost != 0.0:
            self.ROI = 100.0*self.profit/self.cost

        if self.clicks != 0:
            self.EPC = self.revenue/self.clicks

        if self.convs != 0:
            self.AP = self.revenue / self.convs

    def from_dict(self, d):
        for k, v in d.iteritems():
            setattr(self, k, v)


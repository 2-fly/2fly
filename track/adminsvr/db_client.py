#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey, String, Sequence, Float, Text
from sqlalchemy import create_engine, or_, and_, event, DDL
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError


Base = declarative_base()

class methods():
    @classmethod
    def get_options(*k, **w):
        pass;

class VerifingUser(Base, methods):
    __tablename__ = 'verifing_user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    md5_name = Column(String(255), index=True, unique=True, nullable=False)
    timestamp = Column(Integer, nullable=False)

class User(Base, methods):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    timezone = Column(Integer, default=8)
    track_domains = Column(String(65536), nullable=False, default="")
    lander_domains = Column(String(65536), nullable=False, default="")
    lander_domains_dist = Column(String(65536), nullable=False, default="")
    event_email = Column(String(512), nullable=False, default="")
    permission = Column(Integer, default=6)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class TrafficSource(Base, methods):
    __tablename__ = 'traffic_source'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    postback_url = Column(String(4096), default="")
    fields = Column(String(4096), default="")
    timezone = Column(Integer, default=0)
    ad_server_domains = Column(String(65536), default="")     # domains.txt split by ,

    uid = Column(Integer(), ForeignKey(User.id), nullable=False)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class AdminTrafficSource(Base, methods):
    __tablename__ = 'admin_traffic_source'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    postback_url = Column(String(4096), default="")
    fields = Column(String(4096), default="")
    timezone = Column(Integer, default=0)
    ad_server_domains = Column(Text, default="")     # domains.txt split by ,

    uid = Column(Integer(), ForeignKey(User.id), nullable=False)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class AffiliateNetwork(Base, methods):
    __tablename__ = 'affiliate_network'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)

    uid = Column(Integer(), ForeignKey(User.id), nullable=False)

    def __unicode__(self):
        return self.name

class AdminAffiliateNetwork(Base, methods):
    __tablename__ = 'admin_affiliate_network'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)

    uid = Column(Integer(), ForeignKey(User.id), nullable=False)

    def __unicode__(self):
        return self.name

#direct type == 1, mobvista
#direct type == 2, youmi
class Offer(Base, methods):
    __tablename__ = 'offer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    url = Column(String(512), default="")
    url_direct = Column(String(512), default="")
    direct_type = Column(Integer, default=0)#0:not direct (1,2,3..):direct
    country = Column(String(512), default="")
    payout_type = Column(Float, default=0.0)

    uid = Column(Integer(), ForeignKey(User.id), nullable=False)

    #network_id = Column(Integer(), ForeignKey(AffiliateNetwork.id), nullable=False)
    network_id = Column(Integer(), default=0, nullable=False)
    hidden = Column(Integer(), default=0, nullable=True)
    direct_offer_id = Column(Integer(), default=0)
    admin_network_id = Column(Integer(), default=0, nullable=False)
    #cap = Column(String(16), default="No")

    #network = relationship(AffiliateNetwork, backref='networkds')
    introduction = Column(String(4096), default="")

    def __unicode__(self):
        return self.name

class Flow(Base, methods):
    __tablename__ = "flow"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, ForeignKey(User.id), nullable=False)
    name = Column(String(255), index=True, nullable=False)
    swaps= Column(String(4096), default="")

    def __unicode__(self):
        return self.name

class LandingPage(Base, methods):
    __tablename__ = 'landing_page'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    page_source = Column(String(65536), default="")
    source = Column(String(65536), default="")
    uid = Column(Integer(), ForeignKey(User.id), nullable=False)
    hidden = Column(Integer(), default=0, nullable=True)
    lander_mode = Column(Integer(), default=0)
    lander_link = Column(String(65536), default="")

    #offers = relationship('Offer', secondary=lp_offers_table)

    def __unicode__(self):
        return self.name

class Path(Base, methods):
    __tablename__ = 'path'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)

    direct_linking = Column(Integer, default=0)

    #landing_pages = relationship('LandingPage', secondary=path_lps_table)
    #offers = relationship('Offer', secondary=path_offers_table)

    landing_pages = Column(String(4096), default="")
    offers = Column(String(4096), default="")

    uid = Column(Integer(), ForeignKey(User.id), nullable=False)

    def __unicode__(self):
        return self.name



class SwapRotation(Base, methods):
    __tablename__ = 'swap_rotation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    #redirect_enabled = Column(Integer, default=0)
    #redirect_type = Column(Integer, default=0)

    #paths = relationship('Path', secondary=swap_paths_table)
    #campaign = relationship('Campaign', backref='swap')


    paths = Column(String(4096), default="")
    rules = Column(String(4096), default="", nullable=False)

    uid = Column(Integer(), ForeignKey(User.id), nullable=False)

    def __unicode__(self):
        return self.name



class DomainGroup(Base, methods):
    __tablename__ = 'domain_group'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    domains = Column(String(65536), default="")     # domains.txt split by ,

    uid = Column(Integer(), ForeignKey(User.id), nullable=False)


class Campaign(Base, methods):
    __tablename__ = 'campaign'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    uri = Column(String(255), index=True, unique=True, nullable=False)
    country = Column(String(512), default="")
    cost = Column(Float, default=0.0)

    uid = Column(Integer(), ForeignKey(User.id), nullable=False)

    #source_id = Column(Integer(), ForeignKey(TrafficSource.id), nullable=True)
    source_id = Column(Integer(), default=0, nullable=False)
    admin_source_id = Column(Integer(), default=0, nullable=False)

    flow_id = Column(Integer(), ForeignKey(Flow.id), nullable=False)
    #swap_id = Column(Integer(), ForeignKey(SwapRotation.id), nullable=False)
    #dg_id = Column(Integer(), ForeignKey(DomainGroup.id), nullable=False)

    ck_cloak = Column(Integer, default=0)
    ck_cloak_html = Column(String(255), default="")

    ck_touch = Column(Integer, default=0)
    ck_touch_html = Column(String(255), default="")

    ck_cloak_ts = Column(Integer, default=0)
    ck_cloak_ts_html = Column(String(255), default="")

    ck_android = Column(Integer, default=0)
    ck_android_html = Column(String(255), default="")

    ck_websiteid_digit = Column(Integer, default=0)
    ck_websiteid_typo = Column(Integer, default=0)
    ck_websiteid_html = Column(String(255), default="")

    ck_meta_refresh = Column(Integer, default=0)
    lander_domains_dist = Column(String(65536), nullable=False, default="")
    track_domain = Column(String(65536), default="")
    hidden = Column(Integer, default=0, nullable=True)

    ck_cookie = Column(Integer, default=0)
    ck_cookie_time = Column(Integer, default=0)
    ck_cookie_html = Column(String(255), default="")

    ck_cloak_ts2 = Column(Integer, default=0)
    ck_cloak_ts_html2 = Column(String(255), default="")

    def __unicode__(self):
        return self.uri


class RealCost(Base, methods):
    __tablename__ = 'real_cost'

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_ts = Column(Integer, default=0)
    end_ts = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    update_time = Column(Integer, default=0)
    cpid = Column(Integer(), ForeignKey(Campaign.id), nullable=False)
    uid = Column(Integer(), ForeignKey(User.id), nullable=False)


    def __unicode__(self):
        return '%d_%d_%d_%d'%(self.uid, self.cpid, self.start_ts, self.end_ts)


#direct type == 1, mobvista
#direct type == 2, youmi
class AdminOffer(Base, methods):
    __tablename__ = 'admin_offer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    url = Column(String(512), default="")
    direct_type = Column(Integer, default=0)#0:not direct (1,2,3..):direct
    country = Column(String(512), default="")
    payout_type = Column(Float, default=0.0)
    hidden = Column(Integer(), default=0, nullable=True)
    state = Column(Integer(), default=0)
    introduction = Column(String(4096), default="")

    #network = relationship(AffiliateNetwork, backref='networkds')

    def __unicode__(self):
        return self.name

class AdminOfferPayout(Base, methods):
    __tablename__ = 'admin_offer_payout'

    id = Column(Integer, primary_key=True, autoincrement=True)
    #admin_offer_id = Column(Integer(), ForeignKey(AdminOffer.id), nullable=False)
    admin_offer_id = Column(Integer, default=0)
    uid = Column(Integer(), ForeignKey(User.id), nullable=False)

    payout = Column(Float, default=0.0)
    start_time = Column(Integer, default=0)
    timezone = Column(Integer, default=0)

    def __unicode__(self):
        return "%s_%s_%s_%s" % (self.id, self.admin_offer_id, self.payout, self.start_time)



class CampaignCost(Base, methods):
    __tablename__ = 'campaign_cost'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer(), ForeignKey(User.id), nullable=False)
    cpid = Column(Integer, default=0)

    cost = Column(Float, default=0.0)
    start_time = Column(Integer, default=0)
    timezone = Column(Integer, default=8)

    def __unicode__(self):
        return "%s_%s_%s_%s_%s_%s" % (self.id, self.uid, self.cpid, self.payout, self.start_time, self.timezone)

class MobvistaOfferFocus(Base, methods):
    __tablename__ = 'mvoffer_focus'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, default=0)
    focus = Column(String(2048), default="")
    email = Column(String(2048), default="")

    def __unicode__(self):
        return "%s_%s_%s" % (self.id, self.uid, self.focus)

class IronSourceOfferFocus(Base, methods):
    __tablename__ = 'isoffer_focus'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, default=0)
    focus = Column(String(2048), default="")
    email = Column(String(2048), default="")

    def __unicode__(self):
        return "%s_%s_%s" % (self.id, self.uid, self.focus)

class SwitchPath(Base, methods):
    __tablename__ = 'switch_path'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, nullable=True)
    cpid = Column(Integer, nullable=True)
    flow_id = Column(Integer, nullable=True)
    rules = Column(String(2048), default="")  #swap1|master1|slave1;swap2|master2|slave2;

    def __unicode__(self):
        return "%s_%s_%s_%s_%s" % (self.id, self.uid, self.cpid, self.flow_id, self.rules)

class DBClient(object):
    def __init__(self, username, password, host, db, connect_timeout=3):
        #url = 'mysql+mysqldb://%s:%s@%s/%s'%(username, password, host, db)
        url = 'mysql+pymysql://%s:%s@%s/%s'%(username, password, host, db)
        #url = 'sqlite:///' + 'sample_db.sqlite'

        #self.engine = create_engine(url)
        self.engine = create_engine(url,
                connect_args={'connect_timeout': connect_timeout},
                pool_timeout=3,
                pool_recycle=300,
                pool_size=16,
                )

        #self.drop_all()
        self.create_all()
        self.Session = sessionmaker(bind=self.engine)

    def create_all(self):
        Base.metadata.create_all(self.engine)

    def drop_all(self):
        Base.metadata.drop_all(self.engine)

    def add_one(self, record):
        session = self.Session()
        res = True
        try:
            session.add(record)
            session.commit()
            session.refresh(record)
        except Exception, ex:
            print ex
            res = False
        finally:
            session.close()
        return res



    def do_save(self, record):
        session = self.Session()
        res = True
        try:
            res = session.merge(record)
            session.commit()
        except Exception, ex:
            print ex
            res = False
        finally:
            session.close()
        return res

    def do_update(self, table_class, filter_dict, update_dict):
        filter_list = []
        for k, v in filter_dict.iteritems():
            filter_list.append(getattr(table_class, k)==v)

        session = self.Session()
        try:
            res = session.query(table_class).filter(*filter_list).update(update_dict)
            session.commit()
        finally:
            session.close()
        return res == 1

    def iter_all(self, table_class, **kwargs):
        return self.select_all(table_class, **kwargs)
        session = self.Session()
        try:
            res = session.query(table_class).filter_by(**kwargs)
        finally:
            session.close()
        return res

    def select_all(self, table_class, **kwargs):
        session = self.Session()
        try:
            res = session.query(table_class).filter_by(**kwargs).all()
        finally:
            session.close()
        return res

    def select_all_sort(self, table_class, sort_by, **kwargs):
        session = self.Session()
        try:
            res = session.query(table_class).filter_by(**kwargs).order_by(sort_by).all()
        finally:
            session.close()
        return res

    def select_one(self, table_class, **kwargs):
        session = self.Session()
        try:
            res = session.query(table_class).filter_by(**kwargs).limit(1).all()
        finally:
            session.close()
        return res[0] if res else None

    def delete(self, table_class, **kwargs):
        session = self.Session()
        try:
            res = session.query(table_class).filter_by(**kwargs).delete()
            session.commit()
            return res
        finally:
            session.close()

    def select_filter_str(self, table_class, field, sub_str, **kwargs):
        session = self.Session()
        try:
            q = session.query(table_class).filter_by(**kwargs).filter(or_(field.like(sub_str+",%"), field.like("%,"+sub_str), field.like("%,"+sub_str+",%"), field==sub_str))
            res = q.all()
        finally:
            session.close()
        return res


# 获取所有主键
def get_primary_keys(table_class):
    return [i for i in table_class.__table__.primary_key.columns]


# 获取所有主键
def get_foreign_keys(table_class):
    columns = []
    for i in table_class.__table__.foreign_keys:
        columns.append(i.parent)
    return columns

# 获取所有主键
def get_foreign_source_keys(table_class):
    columns = []
    for i in table_class.__table__.foreign_keys:
        columns.append(i)
    return columns


# 获取所有索引
def get_indexes(table_class):
    columns = []
    for i in table_class.__table__.indexes:
        for j in i.columns:
            columns.append(j)
    return columns


# 获取所有列
def get_columns(table_class):
    return [i for i in table_class.__table__.columns]


# 获取除主键以外的列
def get_normal_columns(table_class):
    primary_keys = get_primary_keys(table_class)
    foreign_keys = get_foreign_keys(table_class)
    columns = get_columns(table_class)
    normal_columns = []
    for i in columns:
        if i in primary_keys:
            continue
        if i in foreign_keys:
            continue
        normal_columns.append(i)

    return normal_columns

def get_nonprimary_columns(table_class):
    primary_keys = get_primary_keys(table_class)
    columns = get_columns(table_class)
    ret_columns = []
    for i in columns:
        if i in primary_keys:
            continue
        ret_columns.append(i)

    return ret_columns


if __name__ == '__main__':
    db = DBClient('admin', '123456', 'db', 'massival')

    assert len(db.select_all(User)) == 0
    user = User(name='Season', password='123456', email='myonlylee@gmail.com')
    db.do_save(user)
    assert len(db.select_all(User)) == 1

    user = User(name='Season', password='123456', email='myonlylee@gmail.com')
    try:
        db.do_save(user)
    except IntegrityError, ex:
        pass

    assert len(db.select_all(User)) == 1
    user = db.select_all(User)[0]


    source = TrafficSource(name='discuz.org', postback_url='baidu.com', uid=user.id, fields="rid={rid}")
    assert len(db.select_all(TrafficSource)) == 0
    db.do_save(source)
    assert len(db.select_all(TrafficSource)) == 1
    source = db.select_all(TrafficSource)[0]


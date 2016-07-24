#!/usr/bin/env python
# -*- coding:utf-8 -*-


from sqlalchemy import Table, Column, Integer, ForeignKey, String, Sequence, Float, Text, SmallInteger
from sqlalchemy import create_engine, or_, and_, event, DDL
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

class methods():
    @classmethod
    def get_options(*k, **w):
        pass;


class Publisher(Base, methods):
    __tablename__ = 'rtb_publisher'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)



class Website(Base, methods):
    __tablename__ = 'rtb_website'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    #uri = Column(String(255), index=True, unique=True, nullable=False)
    uid = Column(Integer(), ForeignKey(Publisher.id), nullable=False)


class WebsiteBid(Base, methods):
    __tablename__ = 'rtb_website_bid'
    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(4096), default="")      # ALL or countries
    os = Column(String(512), default="")
    browser = Column(String(4096), default="")
    max_bid = Column(Float, default=0.0)
    status = Column(Integer(), default=0)
    wid = Column(Integer(), ForeignKey(Website.id), nullable=False)

class Advertiser(Base, methods):
    __tablename__ = 'rtb_advertiser'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)

# os: iOS   Android     Desktop
# Windows Phone OS      Windows Mobile OS
class Campaign(Base, methods):
    __tablename__ = 'rtb_campaign'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    url = Column(Text, nullable=False)
    country = Column(Text, nullable=False)
    os = Column(String(512), nullable=False)
    browser = Column(Text, nullable=False)
    include_websites = Column(Text, default="", nullable=False)
    exclude_websites = Column(Text, default="", nullable=False)
    status = Column(Integer(), default=0)
    max_bid = Column(Float, default=0.0)
    total_budget = Column(Float, default=0.0)
    daily_budget = Column(Float, default=0.0)
    daily_website_budget = Column(Float, default=0.0)
    exchange = Column(SmallInteger, default=0)

    start_ts = Column(Integer, default=0)
    end_ts = Column(Integer, default=0)
    timezone = Column(SmallInteger, default=0)
    isp = Column(Text, default="")
    device_type = Column(Integer, default=0)
    connection_type = Column(Integer, default=0)
    ip_range = Column(Text, default="")
    beacon_urls = Column(Text, default="")

    uid = Column(Integer(), ForeignKey(Advertiser.id), nullable=False)

    a_domain = Column(Text, default="")
    image_urls = Column(Text, default="")
    image_width_heights = Column(Text)
    sample_image_url = Column(String(255), default="")

    source_type = Column(Integer, default=0)
    jc_js_url = Column(String(255), default="")
    jc_js_camp_url = Column(String(255), default="")

    adm = Column(Text, default="")
    category = Column(Text, default="", nullable=False)
    website_info_list = Column(Text, default="")
    cap_per_ip_ua = Column(Integer, default=0)
    duration_per_ip_ua = Column(Integer, default=0)
    cap_per_did = Column(Integer, default=0)
    duration_per_did = Column(Integer, default=0)

class JsSpy(Base, methods):
    __tablename__ = 'rtb_jsspy'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    uid = Column(Integer(), ForeignKey(Advertiser.id), nullable=False)
    url = Column(Text, nullable=False)
    ck_ip_ua = Column(Integer, default=0)
    ck_ref = Column(Integer, default=0)
    ck_anonip = Column(Integer, default=0)
    ck_cookie = Column(Integer, default=0)
    default_type = Column(Integer, default=0)
    default_js = Column(Text, nullable=True, default="")
    spy_type = Column(Integer, default=0)
    spy_js = Column(Text, nullable=True, default="")

class DBClient(object):
    def __init__(self, username, password, host, db, connect_timeout=3):
        #url = 'mysql+mysqldb://%s:%s@%s/%s'%(username, password, host, db)
        url = 'mysql+pymysql://%s:%s@%s/%s'%(username, password, host, db)
        #url = 'sqlite:///' + 'sample_db.sqlite'

        #self.engine = create_engine(url)
        self.engine = create_engine(url,
                connect_args={'connect_timeout': connect_timeout},
                pool_timeout=3,
                pool_recycle=7200,
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
            #print ex
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
            #print ex
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

    def select_all_left_join_filter_by_right_col(self, left_cls, right_cls, left_col, right_col, filter_col, filter_val):
        session = self.Session()
        try:
            res = session.query(left_cls).outerjoin(right_cls, left_col==right_col).filter(filter_col==filter_val).all();
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
    db = DBClient('admin', '123456', 'db', 'poponads')

    assert len(db.select_all(Publisher)) == 0
    publisher = Publisher(name='Season', password='123456', email='myonlylee@gmail.com')
    db.do_save(publisher)
    assert len(db.select_all(Publisher)) == 1

    publisher = Publisher(name='Season', password='123456', email='myonlylee@gmail.com')

    res = db.do_save(publisher)
    assert res == False

    assert len(db.select_all(Publisher)) == 1
    publisher = db.select_all(Publisher)[0]

    website = Website(name='sina.com', cost=0.5, uid=publisher.id)
    db.do_save(website)
    assert len(db.select_all(Website)) == 1



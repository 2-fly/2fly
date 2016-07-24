#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey, String, Sequence, Float
from sqlalchemy import create_engine, or_, and_, event, DDL
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError


Base = declarative_base()

class methods():
    @classmethod
    def get_options(*k, **w):
        pass;

class Mail(Base, methods):
    __tablename__ = 'mail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(2048), nullable=False)
    title = Column(String(255), nullable=False)
    type = Column(Integer, nullable=False)
    create_time = Column(Integer, nullable=False)
    sender = Column(String(255), nullable=False)

    def __unicode__(self):
        return

class UserMail(Base, methods):
    __tablename__ = 'user_mail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mid = Column(Integer, ForeignKey(Mail.id), nullable=False)
    read = Column(Integer, nullable=False)
    uid = Column(Integer, nullable=False)

    def __unicode__(self):
        return


class Invoice(Base, methods):
    __tablename__ = 'invoice'

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_date = Column(String(255), nullable=False)
    end_date = Column(String(255), nullable=False)
    status = Column(Integer(), default=0, nullable=False)
    amount = Column(String(255), nullable=False)
    uid = Column(Integer(), nullable=False)

    def __unicode__(self):
        return

class FlowEvent(Base, methods):
    __tablename__ = 'flow_event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, nullable=False)
    profit = Column(String(255), default="")
    ctr = Column(String(255), default="")
    cr = Column(String(255), default="")
    warn = Column(String(255), default="")
    cloak_ts = Column(String(255), default="")
    cloak = Column(String(255), default="")
    track_domain = Column(String(255), default="")
    lander_domain = Column(String(255), default="")
    wid_typo = Column(String(255), default="")
    wid_digit = Column(String(255), default="")
    roi = Column(String(255), default="")
    offers = Column(String(4096), default="")

class AdminFlowEvent(Base, methods):
    __tablename__ = 'admin_flow_event'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, nullable=False)
    profit = Column(String(255), default="")
    ctr = Column(String(255), default="")
    cr = Column(String(255), default="")
    warn = Column(String(255), default="")
    cloak_ts = Column(String(255), default="")
    cloak = Column(String(255), default="")
    track_domain = Column(String(255), default="")
    lander_domain = Column(String(255), default="")
    wid_typo = Column(String(255), default="")
    wid_digit = Column(String(255), default="")
    roi = Column(String(255), default="")
    offers = Column(String(4096), default="")

class UserDBClient(object):
    def __init__(self, username, password, host, db, connect_timeout=3):
        #url = 'mysql+mysqldb://%s:%s@%s/%s'%(username, password, host, db)
        url = 'mysql+pymysql://%s:%s@%s/%s'%(username, password, host, db)
        #url = 'sqlite:///' + 'sample_db.sqlite'

        #self.engine = create_engine(url)
        self.engine = create_engine(url,
                connect_args={'connect_timeout': connect_timeout},
                pool_timeout=3
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

    def select_all(self, table_class, **kwargs):
        session = self.Session()
        try:
            res = session.query(table_class).filter_by(**kwargs).all()
        finally:
            session.close()
        return res

    def iter_all(self, table_class, **kwargs):
        session = self.Session()
        try:
            res = session.query(table_class).filter_by(**kwargs)
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



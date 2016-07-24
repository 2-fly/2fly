#!/usr/bin/env python
# -*- coding:utf-8 -*-

STATIC_DATA_BY_DAY = 0
STATIC_DATA_BY_HOUR = 1
IGNORE_RULE_ID = -1

FORMAT_INT = "n0"
FORMAT_DOLLAR_TWO = "c2"
FORMAT_DOLLAR_THREE = "c3"
FORMAT_PERCENT = "p2"


CAMPAIGN_TAG = 'campaign'
CAMPAIGN_DATE_TAG = 'campaign_date'
CAMPAIGN_HOUR_TAG = 'campaign_hour'
WEBSITE_TAG = 'website'
BANNER_TAG = 'banner'
OS_TAG = 'os'
COUNTRY_TAG = 'country'
BROWSER_TAG = 'browser'
TOTAL_TAG = 'total'

RULES_NO_LENGTH_LIMIT = -1

TABLE_TAG = [
    CAMPAIGN_TAG, CAMPAIGN_DATE_TAG, CAMPAIGN_HOUR_TAG, WEBSITE_TAG, BANNER_TAG, OS_TAG, BROWSER_TAG, COUNTRY_TAG
]

ALL_TAGS = [
    CAMPAIGN_TAG
]

def _make_tag(tag):
    title = tag
    table = "datatable_%s" % tag
    table_tag = "datatable_%s_tag" % tag
    return (table_tag, table, title)

def _make_table_tag(tag):
    return  "datatable_%s" % tag

def _make_all_tags():
    result = {}
    for tag in TABLE_TAG:
        result[tag] = _make_tag(tag)
    return result

def _make_all_table_tags():
    result = {}
    for tag in TABLE_TAG:
        result[tag] = _make_table_tag(tag)
    return result

table_config = _make_all_tags()

table_tag_config = _make_all_table_tags()





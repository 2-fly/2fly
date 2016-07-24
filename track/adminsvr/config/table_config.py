#!/usr/bin/env python
# -*- coding:utf-8 -*-

TOTAL_TAG = 'total'
CAMPAIGN_TAG = 'campaign'
PATH_TAG = 'path'
LANDPAGE_TAG = 'landpage'
OFFER_TAG = 'offer'
NETWORK_TAG = 'network'
SOURCE_TAG = 'source'
BROWSER_TAG = 'browser'
ISP_TAG = 'isp'
CAMPAIGN_DATE_TAG = 'campaign_date'
OS_TAG = 'os'
COUNTRY_TAG = 'country'
DOMAIN_TAG = 'domain'
REF_TAG = 'referrer'
LANDERREF_TAG = 'lander_referrer'
TSREF_TAG = 'ts_referrer'
CAMPAIGN_HOUR_TAG = 'campaign_hour'
BILLING_TAG = 'billing'
WEBSITE_TAG = 'website'
COUNTRY_ISP_TAG = 'country_isp'
ADMIN_OFFER_TAG = 'admin_offer'
ADMIN_OFFER_USER_TAG = 'admin_offer_user'
USER_OFFER_TAG = 'user_offer'
ADMIN_DIRECT_PB_TAG = 'admin_direct_pb'
USER_DIRECT_PB_TAG = 'user_direct_pb'
ADMIN_BILL_TAG = 'admin_bill'
EVENT_CAMPAIGN_REPORT_TAG = "event_campaign_report"
EVENT_OFFER_REPORT_TAG = "event_offer_report"
EVENT_VALVE_OFFER_REPORT_TAG = "event_valve_offer_report"
RELATIVE_EVENT_OFFER_REPORT_TAG = "relative_event_offer_report"
RELATIVE_EVENT_VALVE_OFFER_REPORT_TAG = "relative_event_valve_offer_report"
TOK1_TAG = 'tok1'
TOK2_TAG = 'tok2'
TOK3_TAG = 'tok3'
MV_OFFER_TAG = 'mv_offer'
IS_OFFER_TAG = 'is_offer'
ZEROPARK_CAMP_TAG = 'zeropark_camp'
ZEROPARK_CAMP_DATE_TAG = 'zeropark_camp_date'
ZEROPARK_TARGET_TAG = 'zeropark_target'
ZEROPARK_API_OP_TAG = 'zeropark_api_op'
ZEROPARK_WARN_TARGET_TAG = 'zeropark_warn_target'
PROPELLER_CAMP_TAG = 'propeller_camp'
PROPELLER_CAMP_DATE_TAG = 'propeller_camp_date'
PROPELLER_ZONE_TAG = 'propeller_zone'

TABLE_TAG = [
    TOTAL_TAG, CAMPAIGN_TAG, PATH_TAG, LANDPAGE_TAG, OFFER_TAG, NETWORK_TAG, SOURCE_TAG, BROWSER_TAG,
    ISP_TAG, CAMPAIGN_DATE_TAG, OS_TAG, COUNTRY_TAG, DOMAIN_TAG, REF_TAG, LANDERREF_TAG, TSREF_TAG,
    CAMPAIGN_HOUR_TAG, BILLING_TAG, WEBSITE_TAG, COUNTRY_ISP_TAG, ADMIN_OFFER_TAG, ADMIN_OFFER_USER_TAG,
    USER_OFFER_TAG, ADMIN_DIRECT_PB_TAG, USER_DIRECT_PB_TAG, ADMIN_BILL_TAG, EVENT_CAMPAIGN_REPORT_TAG, EVENT_OFFER_REPORT_TAG,
    EVENT_VALVE_OFFER_REPORT_TAG, TOK1_TAG, TOK2_TAG, TOK3_TAG, MV_OFFER_TAG, IS_OFFER_TAG, ZEROPARK_CAMP_TAG, ZEROPARK_TARGET_TAG, ZEROPARK_CAMP_DATE_TAG, ZEROPARK_WARN_TARGET_TAG, RELATIVE_EVENT_OFFER_REPORT_TAG, RELATIVE_EVENT_VALVE_OFFER_REPORT_TAG, ZEROPARK_API_OP_TAG, PROPELLER_CAMP_TAG, PROPELLER_CAMP_DATE_TAG, PROPELLER_ZONE_TAG
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





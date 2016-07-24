#!/usr/bin/env python
# -*- coding:utf-8 -*-

import settings
import user_db_client
from db_client import *
from utils import get_model_uri, make_url, TemplateReader, get_normal_uri
from commlib.db.db_set import DBClientSet
from config.permission_config import *

all_tables = [User, TrafficSource, AffiliateNetwork,
        Offer, LandingPage, Path,
        SwapRotation, Campaign, DomainGroup, Flow, user_db_client.FlowEvent, AdminOffer, AdminAffiliateNetwork, AdminTrafficSource, user_db_client.AdminFlowEvent]


URL_BASIC_INFO_EDIT = get_model_uri(User, 'edit')
URL_BASIC_INFO_VERIFY_URL = get_model_uri(User, 'verify')
URL_BASIC_INFO_VIRUS_URL = get_model_uri(User, 'virus')

URL_TS_LIST = get_model_uri(TrafficSource, 'list')
URL_TS_CREATE = get_model_uri(TrafficSource, 'create')
URL_TS_EDIT = get_model_uri(TrafficSource, 'edit')
URL_TS_DEL = get_model_uri(TrafficSource, 'del')
URL_TS_FIELD = get_model_uri(TrafficSource, 'field')

URL_DG_LIST = get_model_uri(DomainGroup, 'list')
URL_DG_CREATE = get_model_uri(DomainGroup, 'create')
URL_DG_EDIT = get_model_uri(DomainGroup, 'edit')
URL_DG_DEL = get_model_uri(DomainGroup, 'del')

URL_AFFNET_LIST = get_model_uri(AffiliateNetwork, 'list')
URL_AFFNET_CREATE = get_model_uri(AffiliateNetwork, 'create')
URL_AFFNET_EDIT = get_model_uri(AffiliateNetwork, 'edit')
URL_AFFNET_DEL = get_model_uri(AffiliateNetwork, 'del')

URL_OFFER_LIST = get_model_uri(Offer, 'list')
URL_OFFER_CREATE = get_model_uri(Offer, 'create')
URL_OFFER_CREATE_JSON = get_model_uri(Offer, 'create/json')
URL_OFFER_EDIT = get_model_uri(Offer, 'edit')
URL_OFFER_DEL = get_model_uri(Offer, 'del')
URL_OFFER_SET_HIDDEN = get_model_uri(Offer, 'hide')

URL_LP_LIST = get_model_uri(LandingPage, 'list')
URL_LP_CREATE = get_model_uri(LandingPage, 'create')
URL_LP_CREATE_JSON = get_model_uri(LandingPage, 'create/json')
URL_LP_EDIT = get_model_uri(LandingPage, 'edit')
URL_LP_DEL = get_model_uri(LandingPage, 'del')
URL_LP_SET_HIDDEN = get_model_uri(LandingPage, 'hide')
URL_LP_BATCH_UPLOAD = get_model_uri(LandingPage, 'batchupload')

URL_PATH_LIST = get_model_uri(Path, 'list')
URL_PATH_CREATE = get_model_uri(Path, 'create')
URL_PATH_EDIT = get_model_uri(Path, 'edit')
URL_PATH_DEL = get_model_uri(Path, 'del')

URL_SWAP_LIST = get_model_uri(SwapRotation, 'list')
URL_SWAP_CREATE = get_model_uri(SwapRotation, 'create')
URL_SWAP_EDIT = get_model_uri(SwapRotation, 'edit')
URL_SWAP_DEL = get_model_uri(SwapRotation, 'del')

URL_FLOW_SAVE = get_model_uri(Flow, 'create');
URL_FLOW_GET = get_model_uri(Flow, 'get');

URL_CAMP_LIST = get_model_uri(Campaign, 'list')
URL_CAMP_CREATE = get_model_uri(Campaign, 'create')
URL_CAMP_EDIT = get_model_uri(Campaign, 'edit')
URL_CAMP_DEL = get_model_uri(Campaign, 'del')
URL_CAMP_RULE_SEC_CATE = get_model_uri(Campaign, 'sec_cate_config');
URL_CAMP_GET_RULE = get_model_uri(Campaign, 'get_rule');
URL_CAMP_SET_HIDDEN = get_model_uri(Campaign, 'hide');
URL_CAMP_CHECK_OFFER = get_model_uri(Campaign, 'check_offer');

URL_SWITCH_PATH_GET = get_model_uri(SwitchPath, "get")
URL_SWITCH_PATH_SAVE = get_model_uri(SwitchPath, "save")

URL_ADMIN_OFFER_LIST = get_model_uri(AdminOffer, 'list')
URL_ADMIN_OFFER_CREATE = get_model_uri(AdminOffer, 'create')
URL_ADMIN_OFFER_CREATE_JSON = get_model_uri(AdminOffer, 'create/json')
URL_ADMIN_OFFER_EDIT = get_model_uri(AdminOffer, 'edit')
URL_ADMIN_OFFER_DEL = get_model_uri(AdminOffer, 'del')
URL_ADMIN_OFFER_SET_HIDDEN = get_model_uri(AdminOffer, 'hide')

URL_ADMIN_TS_LIST= get_model_uri(AdminTrafficSource, 'list')
URL_ADMIN_TS_CREATE = get_model_uri(AdminTrafficSource, 'create')
URL_ADMIN_TS_EDIT = get_model_uri(AdminTrafficSource, 'edit')
URL_ADMIN_TS_FIELD = get_model_uri(AdminTrafficSource, 'field')

URL_ADMIN_AFFNET_LIST = get_model_uri(AdminAffiliateNetwork, 'list')
URL_ADMIN_AFFNET_CREATE = get_model_uri(AdminAffiliateNetwork, 'create')
URL_ADMIN_AFFNET_EDIT = get_model_uri(AdminAffiliateNetwork, 'edit')

URL_REPORTS_ALL = get_normal_uri('/reports/all')
URL_REPORTS_CAMPAIGN = get_normal_uri('/reports/campaign')
URL_REPORTS_CAMPAIGN_DATESTR = get_normal_uri('/reports/campaign/<date_str>')
URL_REPORTS_PATH = get_normal_uri('/reports/path')
URL_REPORTS_LANDPAGE = get_normal_uri('/reports/landpage')
URL_REPORTS_OFFER = get_normal_uri('/reports/offer')
URL_REPORTS_NETWORK = get_normal_uri('/reports/network')
URL_REPORTS_TRAFFICSOURCE = get_normal_uri('/reports/trafficsource')
URL_REPORTS_BROWSER = get_normal_uri('/reports/browser')
URL_REPORTS_ISP = get_normal_uri('/reports/isp')
URL_REPORTS_CAMPAIGN_DATE= get_normal_uri('/reports/campaign_date')
URL_REPORTS_OS = get_normal_uri('/reports/os')
URL_REPORTS_COUNTRY = get_normal_uri('/reports/country')
URL_REPORTS_DOMAIN = get_normal_uri('/reports/domain')

URL_CHECK_CAMPAIGN = get_normal_uri('/check/campaign')
URL_HELP = get_model_uri('/help')

URL_CHANGE_PWD = get_model_uri(User, 'change_pwd')

URL_EVENTS_EDIT = get_model_uri(user_db_client.FlowEvent, 'edit')
URL_EVENTS_CREATE = get_model_uri(user_db_client.FlowEvent, 'create')
URL_EVENTS_LIST = get_model_uri(user_db_client.FlowEvent, 'list')
URL_EVENTS_REPORT = get_normal_uri("/reports/event_report")
URL_EVENTS_CONFIG = get_model_uri(user_db_client.FlowEvent, 'config')

URL_RELATIVE_EVENTS_EDIT = get_model_uri(user_db_client.AdminFlowEvent, 'edit')
URL_RELATIVE_EVENTS_CREATE = get_model_uri(user_db_client.AdminFlowEvent, 'create')
URL_RELATIVE_EVENTS_REPORT = get_normal_uri("/reports/relative_event_report")
URL_TOOLS_DECRYPT_EDIT = get_normal_uri("/decrypt/edit")

URL_VIRUS_SYNC = get_normal_uri("/virus/sync")
URL_GSB_SYNC = get_normal_uri("/gsb/sync")

DEFAULT_INDEX_PAGE = URL_CAMP_LIST

tmpl_reader = TemplateReader(settings.template_dir)

global_db_set = DBClientSet()

APP_KEY = "2fly2016"

DOMAIN_INFO = "Domain Info"
TRAFFIC_SOURCE = "Traffic Source"
OFFER = "Offer"
AFF_NETWORK = "Affiliate Network"
LANDER_PAGE = "Landing Page"
CAMPAIGN = "Campaign"
ADMIN_OFFER = "AdminOffer"
ADMIN_AFFILIATE_NETWORK = "Admin AffiliateNetwork"
ADMIN_TRAFFIC_SOURCE = "Admin TrafficSource"

REP_TOTAL = "Total"
REP_CAMP = "Campaign"
REP_OFFER = "Offer"
REP_NETWORK = "Network"
REP_TS = "TrafficSource"

EVENTS = "Events"
GLOBAL_EVENTS = "GlobalEvents"
DECRYPT = "Decrypt"

vm_links = [
    (DOMAIN_INFO, URL_BASIC_INFO_EDIT, PERMISSION_CONFIGURE_DOMIAN_INFO),
    (TRAFFIC_SOURCE, URL_TS_LIST, PERMISSION_CONFIGURE_TRAFFIC_SOURCE),
    (AFF_NETWORK, URL_AFFNET_LIST, PERMISSION_CONFIGURE_NETWORK),
    (OFFER, URL_OFFER_LIST, PERMISSION_CONFIGURE_DIRECT_OFFER|PERMISSION_CONFIGURE_CUSTOM_OFFER|PERMISSION_CONFIGURE_MASSIVAL_OFFER),
    (LANDER_PAGE, URL_LP_LIST, PERMISSION_CONFIGURE_LANDPAGE),
    (CAMPAIGN, URL_CAMP_LIST, PERMISSION_CONFIGURE_CAMPAIGN),
    (ADMIN_OFFER, URL_ADMIN_OFFER_LIST, PERMISSION_CONFIGURE_ADMIN_OFFER),
    (ADMIN_TRAFFIC_SOURCE, URL_ADMIN_TS_LIST, PERMISSION_CONFIGURE_ADMIN_TRAFFIC_SOURCE),
    (ADMIN_AFFILIATE_NETWORK, URL_ADMIN_AFFNET_LIST, PERMISSION_CONFIGURE_ADMIN_AFFILIATE_NETWORK),
]

report_links = [
    (REP_TOTAL, URL_REPORTS_ALL, PERMISSION_REPORT_NORMAL),
    (REP_CAMP, URL_REPORTS_CAMPAIGN, PERMISSION_REPORT_NORMAL),
    (REP_OFFER, URL_REPORTS_OFFER, PERMISSION_REPORT_NORMAL),
    (REP_NETWORK, URL_REPORTS_NETWORK, PERMISSION_REPORT_NORMAL),
    (REP_TS, URL_REPORTS_TRAFFICSOURCE, PERMISSION_REPORT_NORMAL),
]

account_links = [
    #('Base Info', '#'),
    ('Change Password', URL_CHANGE_PWD, PERMISSION_IGNORE),
    ('Help', '/help', PERMISSION_IGNORE),
]

tools_links = [
    (EVENTS, URL_EVENTS_EDIT, PERMISSION_TOOLS_EVENTS),
    (GLOBAL_EVENTS, URL_RELATIVE_EVENTS_EDIT, PERMISSION_TOOLS_RELATIVE_EVENTS),
    (DECRYPT, URL_TOOLS_DECRYPT_EDIT, PERMISSION_TOOLS_DECRYPT),
]

total_links = [
    {'name':'Configure', 'items':vm_links, 'img':"/assets/image/nav-configure-icon.png", 'permission':PERMISSION_CONFIGURE},
    #{'name':'Report', 'items':report_links, 'img':"/assets/image/nav-report-icon.png", 'permission':PERMISSION_REPORT},
    {'name':'Tools', 'items':tools_links, 'img':"/assets/image/nav-configure-icon.png", 'permission':PERMISSION_TOOLS},
    {'name':'Account', 'items':account_links, 'img':"", 'permission':PERMISSION_IGNORE},
]



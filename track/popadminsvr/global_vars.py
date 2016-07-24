from db_client import *

from utils import get_model_uri, make_url, TemplateReader, get_normal_uri, get_model_name
import settings
from commlib.db.db_set import DBClientSet


URL_DEFAULT = get_normal_uri('/')
URL_LOGOUT = get_normal_uri("/logout")
URL_MODIFY_USER = get_normal_uri("/pwd")

URL_WEBSITE_LIST = get_model_uri(Website, "list")
URL_WEBSITE_EDIT = get_model_uri(Website, "edit")
URL_WEBSITE_ADD = get_model_uri(Website, "create")

URL_WEBSITE_BID_LIST = get_model_uri(WebsiteBid, "list")
URL_WEBSITE_BID_EDIT = get_model_uri(WebsiteBid, "edit")
URL_WEBSITE_BID_ADD = get_model_uri(WebsiteBid, "add")

URL_CAMP_LIST = get_model_uri(Campaign, "list")
URL_CAMP_EDIT = get_model_uri(Campaign, 'edit')
URL_CAMP_ADD = get_model_uri(Campaign, "add")
URL_UPLOAD_JS_AC = get_model_uri(Campaign, "upload_js_ac")

URL_IMG_MGR = get_normal_uri("/img/manager")
URL_IMG_OP = get_normal_uri("/img/operate")

URL_CAMP_REPORT = get_normal_uri("/report/campaign")
URL_CAMP_DATE_REPORT = get_normal_uri("/report/campaign/date")
URL_FILTER_WEBSITE_REPORT = get_normal_uri("/report/filter/website")
URL_CHANGE_CAMP_WEBSITE_LIST = get_normal_uri("/change/campaign/website")
URL_CHANGE_WEBSITE_BID = get_normal_uri("/change/website/bid")


tmpl_reader = TemplateReader(settings.template_dir)

all_tables = [Website, Campaign, Publisher, Advertiser]
PUBLISHER = 1
ADVERTISER = 2

def get_tag(cls):
    return "/%s/"%get_model_name(cls)

publisher_links = [
    {'name':'Websites', 'url':URL_WEBSITE_LIST, 'tag':get_tag(Website)},
    {'name':"WebsiteBids", 'url':URL_WEBSITE_BID_LIST, 'tag':get_tag(WebsiteBid)},
]

ads_report_links = [
    {'name':'Campaign', 'url':URL_CAMP_REPORT, 'tag':'/report/campaign'},
]

global_db_set = DBClientSet()
global_db_set.init(settings, DBClient, None)

advertiser_links = [
    {'name':"Campaigns", 'url':URL_CAMP_LIST, 'tag':get_tag(Campaign)},
]

total_links = [
    {'name':'Publisher', 'items':publisher_links, 'img':"", 'limit':PUBLISHER},
    {'name':'Advertiser', 'items':advertiser_links, 'img':"", 'limit':ADVERTISER},
    {'name':'Report', 'items':ads_report_links, 'img':"", 'limit':ADVERTISER},
]

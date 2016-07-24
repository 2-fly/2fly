#!/usr/bin/env python
# -*- coding:utf-8 -*-


# hashtable per day 'pingback_20150917'
pingback_redis_table = "pingback"

# hashtable
tspostback_table = 'ts_postback_v3'
tspostback_checked_table = 'checked_postback_v3'

# hashtable 'daystat_%d'%uid
updatecost_table = 'daystat'

# hashtable
virusdomains_table = "virus_domains"
virus_domains_key = "content"

virusdomain_scan_table = 'domain_scan'
virusdomain_report_table = 'domain_report'

virusdomains_admin_table = "admin_virus_domains"

#verify hashtable
verify_domains_key = "verify_doamin_res" #uid

# Google Safe Browsing
gsb_report_table = 'gsb_report'
gsb_admin_table = "admin_gsb_report"

#zeropark pause websiteid
zeropark_pause_wid = "zp_pause_website_info"
zeropark_website_daily_budget = "zp_wb_daily_budget"


#dsp website bid
dsp_website_bid = "dsp_website_bid_%s"
dsp_website_budget = "dsp_website_budget_%s"

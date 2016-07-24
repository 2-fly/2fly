import campaign_report as camp_rpt
import website_report as ws_rpt
import banner_report as bn_rpt
import detail_report as dt_rpt

from config import table_config

STATIC_RESULT_TYPE_CLASS = {
    table_config.table_tag_config[table_config.CAMPAIGN_TAG] : camp_rpt.CampaignResult,
    table_config.table_tag_config[table_config.CAMPAIGN_DATE_TAG] : camp_rpt.CampaignDateResult,
    table_config.table_tag_config[table_config.CAMPAIGN_HOUR_TAG] : camp_rpt.CampaignHourResult,
    table_config.table_tag_config[table_config.WEBSITE_TAG] : ws_rpt.WebsiteResult,
    table_config.table_tag_config[table_config.BANNER_TAG] : bn_rpt.BannerResult,
    table_config.table_tag_config[table_config.OS_TAG] : dt_rpt.OsResult,
    table_config.table_tag_config[table_config.COUNTRY_TAG] : dt_rpt.CountryResult,
    table_config.table_tag_config[table_config.BROWSER_TAG] : dt_rpt.BrowserResult,
}

STATIC_ON_PAGING_STATE = [table_config.CAMPAIGN_HOUR_TAG]



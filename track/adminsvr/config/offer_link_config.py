#!/usr/bin/env python
# -*- coding:utf-8 -*-

from affiliate_config import NO_AFFILIATE, MOBVISTA_AFFILIATE, YOUMI_AFFILIATE, APPFLOOD_AFFILIATE

MassivalLink = [
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105303%26click_id%3D|${transactionID}|qihoo_security_cb_tier1|cb3972%26qihoo_subid%3Dtier1_3972_${sub_channel}", "Massival_360_tier1", 0.6, "DK,AU,IT,LU,HK,SE,BE,IE,AT,FI,CH,NO"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105303%26click_id%3D|${transactionID}|qihoo_security_cb_tier2|cb3972%26qihoo_subid%3Dtier2_3972_${sub_channel}" , "Massival_360_tier2", 0.5, "PT,NZ,PL,SG,CX"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105303%26click_id%3D|${transactionID}|qihoo_security_cb_tier3|cb3972%26qihoo_subid%3Dtier3_3972_${sub_channel}" , "Massival_360_tier3", 0.3, "BG,CZ,EG,IL,PH,RO,SA,TH,TR,UA,ZA"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105303%26click_id%3D|${transactionID}|qihoo_security_cb_tier4|cb3972%26qihoo_subid%3Dtier4_3972_${sub_channel}" , "Massival_360_tier4", 0.25, "KZ,MA,PK"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105303%26click_id%3D|${transactionID}|qihoo_security_cb_tier5|cb3972%26qihoo_subid%3Dtier5_3972_${sub_channel}" , "Massival_360_tier5", 0.7, "ES,NL"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105303%26click_id%3D|${transactionID}|qihoo_security_cb_tier6|cb3972%26qihoo_subid%3Dtier6_3972_${sub_channel}" , "Massival_360_tier6", 0.4, "AE,ID,MY,VN"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105303%26click_id%3D|${transactionID}|qihoo_security_cb_tier7|cb3972%26qihoo_subid%3Dtier7_3972_${sub_channel}" , "Massival_360_tier7", 0.33, "TR"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105303%26click_id%3D|${transactionID}|qihoo_security_cb_tier8|cb3972%26qihoo_subid%3Dtier8_3972_${sub_channel}" , "Massival_360_tier8", 0.35, "TH"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105303%26click_id%3D|${transactionID}|qihoo_security_cb_us|cb3972%26qihoo_subid%3Dus_3972_${sub_channel}" , "Massival_360_us", 0.8, "US,UM,AS,VI,UK,GB,VG,IO,DE,CA"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105303%26click_id%3D|${transactionID}|qihoo_security_cb_ru|cb3972%26qihoo_subid%3Dru_3972_${sub_channel}" , "Massival_360_ru", 0.6, "RU"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105303%26click_id%3D|${transactionID}|qihoo_security_cb_uk|cb3972%26qihoo_subid%3Duk_3972_${sub_channel}" , "Massival_360_uk", 0.9, "UK,GB,VG,IO,FR,FO,PF,GF,IF,RE,MQ,GP"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105303%26click_id%3D|${transactionID}|qihoo_security_cb_kr|cb3972%26qihoo_subid%3Dkr_3972_${sub_channel}" , "Massival_360_kr", 0.6, "KR"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105303%26click_id%3D|${transactionID}|qihoo_security_cb_jp_incent|cb3972%26qihoo_subid%3Djp_incent_3972_${sub_channel}" , "Massival_360_jp_incent", 0.3,"JP"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105303%26click_id%3D|${transactionID}|qihoo_security_cb_in|cb3972%26qihoo_subid%3Djp_incent_3972_${sub_channel}" , "Massival_360_in", 0.38, "IN,MY,ID,SA"),
    ("http://url.haloapps.com/com.hola.launcher?pid=ha_mobvista_9gcb_int&c=hola_9g_cb_3972_${sub_channel}&clickid=|${transactionID}|${sub_channel}|cb3972&siteid=${sub_channel}" , "Massival_hola_9g_cb_3972", 0.25, "GLOBAL"),
    ("http://url.haloapps.com/com.hola.launcher?pid=ha_mobvista_9gcb_int&c=hola_9g_cb_4482_${sub_channel}&clickid=|${transactionID}|${sub_channel}|cb3972&siteid=${sub_channel}" , "Massival_hola_9g_cb_4482", 0.25, "GLOBAL"),
    ("market://details?id=com.qihoo.security.lite&referrer=qihoo_id%3D105347%26click_id%3D|${transactionID}|qihoo_security_lite_cb|cb3972%26qihoo_subid%3Dglobal_3972_${sub_channel}" , "Massival_360lite", 0.2, "GLOBAL"),
    ("market://details?id=com.qihoo.security.lite&referrer=qihoo_id%3D105346%26click_id%3D|${transactionID}|qihoo_security_lite_tier1_cb|cb3972%26qihoo_subid%3Dtier1_3972_${sub_channel}" , "Massival_360lite_tier1", 0.4, "AS,AT,BE,CZ,ES,FO,GF,GP,HK,IE,IL,IO,IT,KR,MQ,PF,PL,PT,RE,RU,SG,TW,UM,VG,VI,ZA,UK,GB,FR,IF"),
    ("market://details?id=com.qihoo.security.lite&referrer=qihoo_id%3D105346%26click_id%3D|${transactionID}|qihoo_security_lite_tier2_cb|cb3972%26qihoo_subid%3Dtier2_3972_${sub_channel}" , "Massival_360lite_tier2", 0.3, "AE,EG,GR,ID,IN,MY,PH,PK,RO,SA,TH,TR,VN"),
    ("market://details?id=com.qihoo.security.lite&referrer=qihoo_id%3D105346%26click_id%3D|${transactionID}|qihoo_security_lite_tier3_cb|cb3972%26qihoo_subid%3Dtier3_3972_${sub_channel}" , "Massival_360lite_tier3", 0.7, "CA,AU,US,UM,AS,VI,VG,IO,UK,GB"),
    ("market://details?id=com.qihoo.security.lite&referrer=qihoo_id%3D105346%26click_id%3D|${transactionID}|qihoo_security_lite_tier4_cb|cb3972%26qihoo_subid%3Dtier4_3972_${sub_channel}" , "Massival_360lite_tier4", 0.6, "CH,DE,DK,FO,FR,GF,GP,MQ,NL,NO,PF,RE,AF"),
    ("market://details?id=com.qihoo.security.lite&referrer=qihoo_id%3D105346%26click_id%3D|${transactionID}|qihoo_security_lite_tier5_cb|cb3972%26qihoo_subid%3Dtier5_3972_${sub_channel}" , "Massival_360lite_tier5", 0.5, "SE,NZ,FI"),
]

YoumiLink = [
    ("" , "empty" ,0)
]

NoDirectLink = [
    ("", "empty", 0)
]

AppFloodLink = [
    # 360
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D2339" , "AppFlood_360_2339", 0.9, "GB"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D782" , "AppFlood_360_782", 0.8, "US,FR,DE,CA,GB"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D2345" , "AppFlood_360_2345", 0.7, "NL,AU,SE,FI"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D1929" , "AppFlood_360_1929", 0.6, "ES,HK,BE,IE,AT,DK,CH,NO,LU,RU,NL,SE,AU"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D1930" , "AppFlood_360_1930", 0.5, "ES,LU,SE,NO,NL,IE,CH,BE,AT,HK,FI,RU,IT,PL,PT,SG,NZ"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D2261" , "AppFlood_360_2261", 0.5, "RU"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D2279" , "AppFlood_360_2279", 0.38, "IN,ID,VN"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D2026" , "AppFlood_360_2026", 0.3, "IN，AE,TH,MY,ID,SA,UA,VN,TR,CZ,PH,RO,BG,ZA,IL"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D2439" , "AppFlood_360_2439", 0.4, "MY,AE,VN,ID"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D2526" , "AppFlood_360_2526", 0.35, "TH"),
    ("market://details?id=com.qihoo.security&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D2527" , "AppFlood_360_2527", 0.33, "TR,EG"),

    # 360lite
    ("market://details?id=com.qihoo.security.lite&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D2795" , "AppFlood_360lite_2795", 0.7, ""),
    ("market://details?id=com.qihoo.security.lite&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D2796" , "AppFlood_360lite_2796", 0, ""),
    ("market://details?id=com.qihoo.security.lite&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D2797" , "AppFlood_360lite_2797", 0, ""),
    ("market://details?id=com.qihoo.security.lite&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D2798" , "AppFlood_360lite_2798", 0, ""),
    ("market://details?id=com.qihoo.security.lite&referrer=qihoo_id%3D105321%26qihoo_subid%3Dli97i%26duid%3D${transactionID}%26qihoo_subid2%3D2799" , "AppFlood_360lite_2799", 0.3, ""),
]

def _tuple2dict(data):
    result = {}
    for _info in data:
        url, nick, ap, country = _info
        result[url] = {
            "nick" : nick,
            "ap" : ap,
            "country" : country,
            "network_id" : 0,
        }
    return result

OfferLink = {
    #NO_AFFILIATE : _tuple2dict(NoDirectLink),
    MOBVISTA_AFFILIATE : _tuple2dict(MassivalLink),
    #YOUMI_AFFILIATE : _tuple2dict(YoumiLink),
    APPFLOOD_AFFILIATE : _tuple2dict(AppFloodLink),
}

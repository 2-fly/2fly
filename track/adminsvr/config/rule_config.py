#!/usr/bin/env python
# -*- coding:utf-8 -*-
from country_config import COUNTRY_NAME_LIST
from operator import itemgetter

rule_type = [
    {'id': 1, 'name':u'Browser', 'type':1, 'field':'browser'},
    {'id': 2, 'name':u'Brand', 'type':1, 'field':'brand'},
    {'id': 3, 'name':u'Country', 'type':2, 'field':'country'},
    {'id': 4, 'name':u'Referrer', 'type':3, 'field':'ref_domain'},
    {'id': 5, 'name':u'ISP', 'type':3, 'field':'isp'},
    {'id': 6, 'name':u'User Agent', 'type':4, 'field':'us'},
    {'id': 7, 'name':u'Language', 'type':5, 'field' : "browser_lan"},
]

rule = {}
rule[1] = {}
rule[1][1] = {"id":1, "name":"Chrome Mobile", "type":1, "type_name":"Browser", "first":1, "sec":1, "value":"Chrome Mobile"}
rule[1][2] = {"id":2, "name":"Android Webkit", "type":1, "type_name":"Browser", "first":1, "sec":2, "value":"Android Webkit"}
rule[1][3] = {"id":3, "name":"Chromium", "type":1, "type_name":"Browser", "first":1, "sec":3, "value":"Chromium"}
rule[1][4] = {"id":4, "name":"UCWeb", "type":1, "type_name":"Browser", "first":1, "sec":4, "value":"UCWeb"}
rule[1][5] = {"id":5, "name":"Opera Mini", "type":1, "type_name":"Browser", "first":1, "sec":5, "value":"Opera Mini"}
rule[1][6] = {"id":6, "name":"Firefox Mobile", "type":1, "type_name":"Browser", "first":1, "sec":6, "value":"Firefox Mobile"}
rule[1][7] = {"id":7, "name":"IEMobile", "type":1, "type_name":"Browser", "first":1, "sec":7, "value":"IEMobile"}
rule[1][8] = {"id":8, "name":"Safari", "type":1, "type_name":"Browser", "first":1, "sec":8, "value":"Safari"}
rule[1][9] = {"id":9, "name":"MSIE", "type":1, "type_name":"Browser", "first":1, "sec":9, "value":"MSIE"}
rule[1][10] = {"id":10, "name":"Fennec", "type":1, "type_name":"Browser", "first":1, "sec":10, "value":"Fennec"}
rule[1][11] = {"id":11, "name":"Firefox Desktop", "type":1, "type_name":"Browser", "first":1, "sec":11, "value":"Firefox Desktop"}
rule[1][12] = {"id":12, "name":"Opera Mobi", "type":1, "type_name":"Browser", "first":1, "sec":12, "value":"Opera Mobi"}
rule[1][13] = {"id":13, "name":"Opera Tablet", "type":1, "type_name":"Browser", "first":1, "sec":13, "value":"Opera Tablet"}
rule[1][14] = {"id":14, "name":"Opera", "type":1, "type_name":"Browser", "first":1, "sec":14, "value":"Opera"}
rule[1][15] = {"id":15, "name":"BlackBerry", "type":1, "type_name":"Browser", "first":1, "sec":15, "value":"BlackBerry"}
rule[1][16] = {"id":16, "name":"Nokia BrowserNG", "type":1, "type_name":"Browser", "first":1, "sec":16, "value":"Nokia BrowserNG"}
rule[1][17] = {"id":17, "name":"Nokia", "type":1, "type_name":"Browser", "first":1, "sec":17, "value":"Nokia"}
rule[1][18] = {"id":18, "name":"MQQ Browser", "type":1, "type_name":"Browser", "first":1, "sec":18, "value":"MQQ Browser"}
rule[1][19] = {"id":19, "name":"LGUPlus WebKit", "type":1, "type_name":"Browser", "first":1, "sec":19, "value":"LGUPlus WebKit"}
rule[1][20] = {"id":20, "name":"Gecko/Minimo", "type":1, "type_name":"Browser", "first":1, "sec":20, "value":"Gecko/Minimo"}
rule[1][21] = {"id":21, "name":"Nokia Proxy Browser", "type":1, "type_name":"Browser", "first":1, "sec":21, "value":"Nokia Proxy Browser"}
rule[1][22] = {"id":22, "name":"Access Netfront", "type":1, "type_name":"Browser", "first":1, "sec":22, "value":"Access Netfront"}
rule[1][23] = {"id":23, "name":"Openwave Mobile Browser", "type":1, "type_name":"Browser", "first":1, "sec":23, "value":"Openwave Mobile Browser"}
rule[1][24] = {"id":24, "name":"Microsoft Mobile Explorer", "type":1, "type_name":"Browser", "first":1, "sec":24, "value":"Microsoft Mobile Explorer"}
rule[1][25] = {"id":25, "name":"Teleca-Obigo", "type":1, "type_name":"Browser", "first":1, "sec":25, "value":"Teleca-Obigo"}
rule[1][26] = {"id":26, "name":"Presto/Opera Mini", "type":1, "type_name":"Browser", "first":1, "sec":26, "value":"Presto/Opera Mini"}
rule[1][27] = {"id":27, "name":"Dolfin/Jasmine Webkit", "type":1, "type_name":"Browser", "first":1, "sec":27, "value":"Dolfin/Jasmine Webkit"}
rule[1][28] = {"id":28, "name":"MAUI Wap Browser", "type":1, "type_name":"Browser", "first":1, "sec":28, "value":"MAUI Wap Browser"}

rule[2] = {}
rule[2][1] = {"id":1, "name":"Samsung", "type":2, "type_name":"Brand", "first":2, "sec":29, "value":"Samsung"}
rule[2][2] = {"id":2, "name":"Google", "type":2, "type_name":"Brand", "first":2, "sec":30, "value":"Google"}
rule[2][3] = {"id":3, "name":"Cubot", "type":2, "type_name":"Brand", "first":2, "sec":31, "value":"Cubot"}
rule[2][4] = {"id":4, "name":"iView", "type":2, "type_name":"Brand", "first":2, "sec":32, "value":"iView"}
rule[2][5] = {"id":5, "name":"LG", "type":2, "type_name":"Brand", "first":2, "sec":33, "value":"LG"}
rule[2][6] = {"id":6, "name":"Karbonn", "type":2, "type_name":"Brand", "first":2, "sec":34, "value":"Karbonn"}
rule[2][7] = {"id":7, "name":"Sony", "type":2, "type_name":"Brand", "first":2, "sec":35, "value":"Sony"}
rule[2][8] = {"id":8, "name":"Motorola", "type":2, "type_name":"Brand", "first":2, "sec":36, "value":"Motorola"}
rule[2][9] = {"id":9, "name":"Alcatel", "type":2, "type_name":"Brand", "first":2, "sec":37, "value":"Alcatel"}
rule[2][10] = {"id":10, "name":"Symphony", "type":2, "type_name":"Brand", "first":2, "sec":38, "value":"Symphony"}
rule[2][11] = {"id":11, "name":"Feiteng", "type":2, "type_name":"Brand", "first":2, "sec":39, "value":"Feiteng"}
rule[2][12] = {"id":12, "name":"Coby", "type":2, "type_name":"Brand", "first":2, "sec":40, "value":"Coby"}
rule[2][13] = {"id":13, "name":"Asus", "type":2, "type_name":"Brand", "first":2, "sec":41, "value":"Asus"}
rule[2][14] = {"id":14, "name":"Micromax", "type":2, "type_name":"Brand", "first":2, "sec":42, "value":"Micromax"}
rule[2][15] = {"id":15, "name":"SonyEricsson", "type":2, "type_name":"Brand", "first":2, "sec":43, "value":"SonyEricsson"}
rule[2][16] = {"id":16, "name":"AOSD", "type":2, "type_name":"Brand", "first":2, "sec":44, "value":"AOSD"}
rule[2][17] = {"id":17, "name":"HTC", "type":2, "type_name":"Brand", "first":2, "sec":45, "value":"HTC"}
rule[2][18] = {"id":18, "name":"Hisense", "type":2, "type_name":"Brand", "first":2, "sec":46, "value":"Hisense"}
rule[2][19] = {"id":19, "name":"Star", "type":2, "type_name":"Brand", "first":2, "sec":47, "value":"Star"}
rule[2][20] = {"id":20, "name":"Opera", "type":2, "type_name":"Brand", "first":2, "sec":48, "value":"Opera"}
rule[2][21] = {"id":21, "name":"Huawei", "type":2, "type_name":"Brand", "first":2, "sec":49, "value":"Huawei"}
rule[2][22] = {"id":22, "name":"KingZone", "type":2, "type_name":"Brand", "first":2, "sec":50, "value":"KingZone"}
rule[2][23] = {"id":23, "name":"Pandigital", "type":2, "type_name":"Brand", "first":2, "sec":51, "value":"Pandigital"}
rule[2][24] = {"id":24, "name":"MediaTek", "type":2, "type_name":"Brand", "first":2, "sec":52, "value":"MediaTek"}
rule[2][25] = {"id":25, "name":"Nokia", "type":2, "type_name":"Brand", "first":2, "sec":53, "value":"Nokia"}
rule[2][26] = {"id":26, "name":"generic web browser", "type":2, "type_name":"Brand", "first":2, "sec":54, "value":"generic web browser"}
rule[2][27] = {"id":27, "name":"Mozilla", "type":2, "type_name":"Brand", "first":2, "sec":55, "value":"Mozilla"}
rule[2][28] = {"id":28, "name":"OPPO", "type":2, "type_name":"Brand", "first":2, "sec":56, "value":"OPPO"}
rule[2][29] = {"id":29, "name":"Alps", "type":2, "type_name":"Brand", "first":2, "sec":57, "value":"Alps"}
rule[2][30] = {"id":30, "name":"Intex", "type":2, "type_name":"Brand", "first":2, "sec":58, "value":"Intex"}
rule[2][31] = {"id":31, "name":"ZTE", "type":2, "type_name":"Brand", "first":2, "sec":59, "value":"ZTE"}
rule[2][32] = {"id":32, "name":"Apple", "type":2, "type_name":"Brand", "first":2, "sec":60, "value":"Apple"}
rule[2][33] = {"id":33, "name":"InnJoo", "type":2, "type_name":"Brand", "first":2, "sec":61, "value":"InnJoo"}
rule[2][34] = {"id":34, "name":"Kyocera", "type":2, "type_name":"Brand", "first":2, "sec":62, "value":"Kyocera"}
rule[2][35] = {"id":35, "name":"Blu", "type":2, "type_name":"Brand", "first":2, "sec":63, "value":"Blu"}
rule[2][36] = {"id":36, "name":"Smartfren", "type":2, "type_name":"Brand", "first":2, "sec":64, "value":"Smartfren"}
rule[2][37] = {"id":37, "name":"Xolo", "type":2, "type_name":"Brand", "first":2, "sec":65, "value":"Xolo"}
rule[2][38] = {"id":38, "name":"Xiaomi", "type":2, "type_name":"Brand", "first":2, "sec":66, "value":"Xiaomi"}
rule[2][39] = {"id":39, "name":"Pantech", "type":2, "type_name":"Brand", "first":2, "sec":67, "value":"Pantech"}
rule[2][40] = {"id":40, "name":"Generic", "type":2, "type_name":"Brand", "first":2, "sec":68, "value":"Generic"}
rule[2][41] = {"id":41, "name":"Lenovo", "type":2, "type_name":"Brand", "first":2, "sec":69, "value":"Lenovo"}
rule[2][42] = {"id":42, "name":"i-mobile", "type":2, "type_name":"Brand", "first":2, "sec":70, "value":"i-mobile"}
rule[2][43] = {"id":43, "name":"Dell", "type":2, "type_name":"Brand", "first":2, "sec":71, "value":"Dell"}
rule[2][44] = {"id":44, "name":"ASK", "type":2, "type_name":"Brand", "first":2, "sec":72, "value":"ASK"}
rule[2][45] = {"id":45, "name":"Nvidia", "type":2, "type_name":"Brand", "first":2, "sec":73, "value":"Nvidia"}
rule[2][46] = {"id":46, "name":"Mediacom", "type":2, "type_name":"Brand", "first":2, "sec":74, "value":"Mediacom"}
rule[2][47] = {"id":47, "name":"Lava", "type":2, "type_name":"Brand", "first":2, "sec":75, "value":"Lava"}
rule[2][48] = {"id":48, "name":"Advan", "type":2, "type_name":"Brand", "first":2, "sec":76, "value":"Advan"}
rule[2][49] = {"id":49, "name":"Microsoft", "type":2, "type_name":"Brand", "first":2, "sec":77, "value":"Microsoft"}
rule[2][50] = {"id":50, "name":"Acer", "type":2, "type_name":"Brand", "first":2, "sec":78, "value":"Acer"}
rule[2][51] = {"id":51, "name":"iBall", "type":2, "type_name":"Brand", "first":2, "sec":79, "value":"iBall"}
rule[2][52] = {"id":52, "name":"T-Mobile", "type":2, "type_name":"Brand", "first":2, "sec":80, "value":"T-Mobile"}
rule[2][53] = {"id":53, "name":"Evercoss", "type":2, "type_name":"Brand", "first":2, "sec":81, "value":"Evercoss"}
rule[2][54] = {"id":54, "name":"Fly", "type":2, "type_name":"Brand", "first":2, "sec":82, "value":"Fly"}
rule[2][55] = {"id":55, "name":"MyPhone", "type":2, "type_name":"Brand", "first":2, "sec":83, "value":"MyPhone"}
rule[2][56] = {"id":56, "name":"Spice", "type":2, "type_name":"Brand", "first":2, "sec":84, "value":"Spice"}
rule[2][57] = {"id":57, "name":"Celkon", "type":2, "type_name":"Brand", "first":2, "sec":85, "value":"Celkon"}
rule[2][58] = {"id":58, "name":"Wiko", "type":2, "type_name":"Brand", "first":2, "sec":86, "value":"Wiko"}
rule[2][59] = {"id":59, "name":"Mobiistar", "type":2, "type_name":"Brand", "first":2, "sec":87, "value":"Mobiistar"}
rule[2][60] = {"id":60, "name":"Nuqleo", "type":2, "type_name":"Brand", "first":2, "sec":88, "value":"Nuqleo"}
rule[2][61] = {"id":61, "name":"Xtron", "type":2, "type_name":"Brand", "first":2, "sec":89, "value":"Xtron"}
rule[2][62] = {"id":62, "name":"Archos", "type":2, "type_name":"Brand", "first":2, "sec":90, "value":"Archos"}
rule[2][63] = {"id":63, "name":"Amazon", "type":2, "type_name":"Brand", "first":2, "sec":91, "value":"Amazon"}
rule[2][64] = {"id":64, "name":"OWN", "type":2, "type_name":"Brand", "first":2, "sec":92, "value":"OWN"}
rule[2][65] = {"id":65, "name":"Panasonic", "type":2, "type_name":"Brand", "first":2, "sec":93, "value":"Panasonic"}
rule[2][66] = {"id":66, "name":"NGM", "type":2, "type_name":"Brand", "first":2, "sec":94, "value":"NGM"}
rule[2][67] = {"id":67, "name":"Gionee", "type":2, "type_name":"Brand", "first":2, "sec":95, "value":"Gionee"}
rule[2][68] = {"id":68, "name":"BQ", "type":2, "type_name":"Brand", "first":2, "sec":96, "value":"BQ"}
rule[2][69] = {"id":69, "name":"RIM", "type":2, "type_name":"Brand", "first":2, "sec":97, "value":"RIM"}
rule[2][70] = {"id":70, "name":"Barnes and Noble", "type":2, "type_name":"Brand", "first":2, "sec":98, "value":"Barnes and Noble"}
rule[2][71] = {"id":71, "name":"Cherry Mobile", "type":2, "type_name":"Brand", "first":2, "sec":99, "value":"Cherry Mobile"}
rule[2][72] = {"id":72, "name":"Allview", "type":2, "type_name":"Brand", "first":2, "sec":100, "value":"Allview"}
rule[2][73] = {"id":73, "name":"Vivo", "type":2, "type_name":"Brand", "first":2, "sec":101, "value":"Vivo"}
rule[2][74] = {"id":74, "name":"iNew", "type":2, "type_name":"Brand", "first":2, "sec":102, "value":"iNew"}
rule[2][75] = {"id":75, "name":"Mito", "type":2, "type_name":"Brand", "first":2, "sec":103, "value":"Mito"}
rule[2][76] = {"id":76, "name":"Majestic", "type":2, "type_name":"Brand", "first":2, "sec":104, "value":"Majestic"}
rule[2][77] = {"id":77, "name":"HP", "type":2, "type_name":"Brand", "first":2, "sec":105, "value":"HP"}
rule[2][78] = {"id":78, "name":"Orange", "type":2, "type_name":"Brand", "first":2, "sec":106, "value":"Orange"}
rule[2][79] = {"id":79, "name":"Sprint", "type":2, "type_name":"Brand", "first":2, "sec":107, "value":"Sprint"}
rule[2][80] = {"id":80, "name":"Coolpad", "type":2, "type_name":"Brand", "first":2, "sec":108, "value":"Coolpad"}
rule[2][81] = {"id":81, "name":"Nextbook", "type":2, "type_name":"Brand", "first":2, "sec":109, "value":"Nextbook"}
rule[2][82] = {"id":82, "name":"XOLO", "type":2, "type_name":"Brand", "first":2, "sec":110, "value":"XOLO"}
rule[2][83] = {"id":83, "name":"Turkcell", "type":2, "type_name":"Brand", "first":2, "sec":111, "value":"Turkcell"}
rule[2][84] = {"id":84, "name":"Hitech", "type":2, "type_name":"Brand", "first":2, "sec":112, "value":"Hitech"}
rule[2][85] = {"id":85, "name":"Point of View", "type":2, "type_name":"Brand", "first":2, "sec":113, "value":"Point of View"}
rule[2][86] = {"id":86, "name":"DOOGEE", "type":2, "type_name":"Brand", "first":2, "sec":114, "value":"DOOGEE"}
rule[2][87] = {"id":87, "name":"Magicon", "type":2, "type_name":"Brand", "first":2, "sec":115, "value":"Magicon"}
rule[2][88] = {"id":88, "name":"Videocon", "type":2, "type_name":"Brand", "first":2, "sec":116, "value":"Videocon"}
rule[2][89] = {"id":89, "name":"Washion", "type":2, "type_name":"Brand", "first":2, "sec":117, "value":"Washion"}
rule[2][90] = {"id":90, "name":"Vodafone", "type":2, "type_name":"Brand", "first":2, "sec":118, "value":"Vodafone"}
rule[2][91] = {"id":91, "name":"Brondi", "type":2, "type_name":"Brand", "first":2, "sec":119, "value":"Brondi"}
rule[2][92] = {"id":92, "name":"Qilive", "type":2, "type_name":"Brand", "first":2, "sec":120, "value":"Qilive"}
rule[2][93] = {"id":93, "name":"Jiayu", "type":2, "type_name":"Brand", "first":2, "sec":121, "value":"Jiayu"}
rule[2][94] = {"id":94, "name":"ThL", "type":2, "type_name":"Brand", "first":2, "sec":122, "value":"ThL"}
rule[2][95] = {"id":95, "name":"Polytron", "type":2, "type_name":"Brand", "first":2, "sec":123, "value":"Polytron"}
rule[2][96] = {"id":96, "name":"inFocus", "type":2, "type_name":"Brand", "first":2, "sec":124, "value":"inFocus"}
rule[2][97] = {"id":97, "name":"BLU", "type":2, "type_name":"Brand", "first":2, "sec":125, "value":"BLU"}
rule[2][98] = {"id":98, "name":"Woxter", "type":2, "type_name":"Brand", "first":2, "sec":126, "value":"Woxter"}
rule[2][99] = {"id":99, "name":"Prestigio", "type":2, "type_name":"Brand", "first":2, "sec":127, "value":"Prestigio"}
rule[2][100] = {"id":100, "name":"RCA", "type":2, "type_name":"Brand", "first":2, "sec":128, "value":"RCA"}
rule[3] = {} #init data at last

rule[7] = {}
rule[7][1] = {"id":1, "name":"Afrikaans", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'af'}
rule[7][2] = {"id":2, "name":"Albanian", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'sq'}
rule[7][3] = {"id":3, "name":"Arabic", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'ar'}
rule[7][4] = {"id":4, "name":"Armenian", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'hy'}
rule[7][5] = {"id":5, "name":"Asturian", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'ast'}
rule[7][6] = {"id":6, "name":"Chinese", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'zh'}
rule[7][7] = {"id":7, "name":"Chinese(Hong Kong)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'zh-hk'}
rule[7][8] = {"id":8, "name":"Chinese(PRC)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'zh-cn'}
rule[7][9] = {"id":9, "name":"Chinese(Singapore)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'zh-sg'}
rule[7][10] = {"id":10, "name":"Chinese(Taiwan)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'zh-cn'}
rule[7][11] = {"id":11, "name":"Danish", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'da'}
rule[7][12] = {"id":12, "name":"Dutch(Standard)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'nl'}
rule[7][13] = {"id":13, "name":"Dutch(Belgian)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'nl-be'}
rule[7][14] = {"id":14, "name":"English", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'en'}
rule[7][15] = {"id":15, "name":"English(Australia)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'en-au'}
rule[7][16] = {"id":16, "name":"English (Belize)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'en-bz'}
rule[7][17] = {"id":17, "name":"English(Canada)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'en-ca'}
rule[7][18] = {"id":18, "name":"English(Ireland)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'en-ie'}
rule[7][19] = {"id":19, "name":"English(Jamaica)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'en-jm'}
rule[7][20] = {"id":20, "name":"English(New Zealand)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'en-nz'}
rule[7][21] = {"id":21, "name":"English(Philippines)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'en-ph'}
rule[7][22] = {"id":22, "name":"English(South Africa)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'en-za'}
rule[7][23] = {"id":23, "name":"English(Trinidad & Tobago)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'en-tt'}
rule[7][24] = {"id":24, "name":"English(United Kingdom)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'en-gb'}
rule[7][25] = {"id":25, "name":"English(United States)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'en-us'}
rule[7][26] = {"id":26, "name":"French(Standard)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'fr'}
rule[7][27] = {"id":27, "name":"French(Belgium)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'fr-be'}
rule[7][28] = {"id":28, "name":"French(Canada)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'fr-ca'}
rule[7][29] = {"id":29, "name":"French(France)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'fr-fr'}
rule[7][30] = {"id":30, "name":"French(Switzerland)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'fr-ch'}
rule[7][31] = {"id":31, "name":"German(Standard)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'de'}
rule[7][32] = {"id":32, "name":"German(Austria)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'de-at'}
rule[7][33] = {"id":33, "name":"German(Germany)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'de-de'}
rule[7][34] = {"id":34, "name":"German(Liechtenstein)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'de-li'}
rule[7][35] = {"id":35, "name":"German(Switzerland)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'de-ch'}
rule[7][36] = {"id":36, "name":"Italian(Standard)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'it'}
rule[7][37] = {"id":37, "name":"Italian(Switzerland)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'it-ch'}
rule[7][38] = {"id":38, "name":"Japanese", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'ja'}
rule[7][39] = {"id":39, "name":"Korean(North Korea)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'ko-kp'}
rule[7][40] = {"id":40, "name":"Korean(South Korea)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'ko-kr'}
rule[7][41] = {"id":41, "name":"Latin", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'la'}
rule[7][42] = {"id":42, "name":"Malay", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'ms'}
rule[7][43] = {"id":43, "name":"Norwegian", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'no'}
rule[7][44] = {"id":44, "name":"Polish", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'pl'}
rule[7][45] = {"id":45, "name":"Portuguese", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'pt'}
rule[7][46] = {"id":46, "name":"Portuguese(Brazil)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'pt-br'}
rule[7][47] = {"id":47, "name":"Punjabi", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'pa'}
rule[7][48] = {"id":48, "name":"Punjabi(India)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'pa-in'}
rule[7][49] = {"id":49, "name":"Punjabi(Pakistan)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'pa-pk'}
rule[7][50] = {"id":50, "name":"Russian", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'ru'}
rule[7][51] = {"id":51, "name":"Spanish", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'es'}
rule[7][52] = {"id":52, "name":"Spanish(Argentina)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'es-ar'}
rule[7][53] = {"id":53, "name":"Spanish(Bolivia)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'es-bo'}
rule[7][54] = {"id":54, "name":"Spanish(Chile)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'es-cl'}
rule[7][55] = {"id":55, "name":"Spanish(Colombia)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'es-co'}
rule[7][56] = {"id":56, "name":"Spanish(Costa Rica)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'es-cr'}
rule[7][57] = {"id":57, "name":"Spanish(Dominican Republic)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'es-do'}
rule[7][58] = {"id":58, "name":"Spanish(Ecuador)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'es-ec'}
rule[7][59] = {"id":59, "name":"Spanish (Mexico)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'es-mx'}
rule[7][60] = {"id":60, "name":"Spanish(Peru)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'es-pe'}
rule[7][61] = {"id":61, "name":"Spanish(Spain)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'es-ve'}
rule[7][62] = {"id":62, "name":"Spanish(Venezuela)", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'es'}
rule[7][63] = {"id":63, "name":"Swedish", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'sv'}
rule[7][64] = {"id":64, "name":"Turkish", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'tr'}
#rule[7][64] = {"id":64, "name":"Vietnamese", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'vi'}
rule[7][65] = {"id":65, "name":"Vietnamese", "type_name":'Language', "type":5, "first":7, "sec":-2, "value":'vi'}

rule_first_category = {}
rule_first_category[1] = [
    {"id":1, "name":"Chrome Mobile"},
    {"id":2, "name":"Android Webkit"},
    {"id":3, "name":"Chromium"},
    {"id":4, "name":"UCWeb"},
    {"id":5, "name":"Opera Mini"},
    {"id":6, "name":"Firefox Mobile"},
    {"id":7, "name":"IEMobile"},
    {"id":8, "name":"Safari"},
    {"id":9, "name":"MSIE"},
    {"id":10, "name":"Fennec"},
    {"id":11, "name":"Firefox Desktop"},
    {"id":12, "name":"Opera Mobi"},
    {"id":13, "name":"Opera Tablet"},
    {"id":14, "name":"Opera"},
    {"id":15, "name":"BlackBerry"},
    {"id":16, "name":"Nokia BrowserNG"},
    {"id":17, "name":"Nokia"},
    {"id":18, "name":"MQQ Browser"},
    {"id":19, "name":"LGUPlus WebKit"},
    {"id":20, "name":"Gecko/Minimo"},
    {"id":21, "name":"Nokia Proxy Browser"},
    {"id":22, "name":"Access Netfront"},
    {"id":23, "name":"Openwave Mobile Browser"},
    {"id":24, "name":"Microsoft Mobile Explorer"},
    {"id":25, "name":"Teleca-Obigo"},
    {"id":26, "name":"Presto/Opera Mini"},
    {"id":27, "name":"Dolfin/Jasmine Webkit"},
    {"id":28, "name":"MAUI Wap Browser"},
]
rule_first_category[2] = [
    {"id":29, "name":"Samsung"},
    {"id":30, "name":"Google"},
    {"id":31, "name":"Cubot"},
    {"id":32, "name":"iView"},
    {"id":33, "name":"LG"},
    {"id":34, "name":"Karbonn"},
    {"id":35, "name":"Sony"},
    {"id":36, "name":"Motorola"},
    {"id":37, "name":"Alcatel"},
    {"id":38, "name":"Symphony"},
    {"id":39, "name":"Feiteng"},
    {"id":40, "name":"Coby"},
    {"id":41, "name":"Asus"},
    {"id":42, "name":"Micromax"},
    {"id":43, "name":"SonyEricsson"},
    {"id":44, "name":"AOSD"},
    {"id":45, "name":"HTC"},
    {"id":46, "name":"Hisense"},
    {"id":47, "name":"Star"},
    {"id":48, "name":"Opera"},
    {"id":49, "name":"Huawei"},
    {"id":50, "name":"KingZone"},
    {"id":51, "name":"Pandigital"},
    {"id":52, "name":"MediaTek"},
    {"id":53, "name":"Nokia"},
    {"id":54, "name":"generic web browser"},
    {"id":55, "name":"Mozilla"},
    {"id":56, "name":"OPPO"},
    {"id":57, "name":"Alps"},
    {"id":58, "name":"Intex"},
    {"id":59, "name":"ZTE"},
    {"id":60, "name":"Apple"},
    {"id":61, "name":"InnJoo"},
    {"id":62, "name":"Kyocera"},
    {"id":63, "name":"Blu"},
    {"id":64, "name":"Smartfren"},
    {"id":65, "name":"Xolo"},
    {"id":66, "name":"Xiaomi"},
    {"id":67, "name":"Pantech"},
    {"id":68, "name":"Generic"},
    {"id":69, "name":"Lenovo"},
    {"id":70, "name":"i-mobile"},
    {"id":71, "name":"Dell"},
    {"id":72, "name":"ASK"},
    {"id":73, "name":"Nvidia"},
    {"id":74, "name":"Mediacom"},
    {"id":75, "name":"Lava"},
    {"id":76, "name":"Advan"},
    {"id":77, "name":"Microsoft"},
    {"id":78, "name":"Acer"},
    {"id":79, "name":"iBall"},
    {"id":80, "name":"T-Mobile"},
    {"id":81, "name":"Evercoss"},
    {"id":82, "name":"Fly"},
    {"id":83, "name":"MyPhone"},
    {"id":84, "name":"Spice"},
    {"id":85, "name":"Celkon"},
    {"id":86, "name":"Wiko"},
    {"id":87, "name":"Mobiistar"},
    {"id":88, "name":"Nuqleo"},
    {"id":89, "name":"Xtron"},
    {"id":90, "name":"Archos"},
    {"id":91, "name":"Amazon"},
    {"id":92, "name":"OWN"},
    {"id":93, "name":"Panasonic"},
    {"id":94, "name":"NGM"},
    {"id":95, "name":"Gionee"},
    {"id":96, "name":"BQ"},
    {"id":97, "name":"RIM"},
    {"id":98, "name":"Barnes and Noble"},
    {"id":99, "name":"Cherry Mobile"},
    {"id":100, "name":"Allview"},
    {"id":101, "name":"Vivo"},
    {"id":102, "name":"iNew"},
    {"id":103, "name":"Mito"},
    {"id":104, "name":"Majestic"},
    {"id":105, "name":"HP"},
    {"id":106, "name":"Orange"},
    {"id":107, "name":"Sprint"},
    {"id":108, "name":"Coolpad"},
    {"id":109, "name":"Nextbook"},
    {"id":110, "name":"XOLO"},
    {"id":111, "name":"Turkcell"},
    {"id":112, "name":"Hitech"},
    {"id":113, "name":"Point of View"},
    {"id":114, "name":"DOOGEE"},
    {"id":115, "name":"Magicon"},
    {"id":116, "name":"Videocon"},
    {"id":117, "name":"Washion"},
    {"id":118, "name":"Vodafone"},
    {"id":119, "name":"Brondi"},
    {"id":120, "name":"Qilive"},
    {"id":121, "name":"Jiayu"},
    {"id":122, "name":"ThL"},
    {"id":123, "name":"Polytron"},
    {"id":124, "name":"inFocus"},
    {"id":125, "name":"BLU"},
    {"id":126, "name":"Woxter"},
    {"id":127, "name":"Prestigio"},
    {"id":128, "name":"RCA"},
]

rule_first_category[3] = [
    {"id":-1}
]

rule_first_category[7] = [
    {"id":-2}
]

rule_second_category = {}
rule_second_category[1] = [rule[1][1]]
rule_second_category[2] = [rule[1][2]]
rule_second_category[3] = [rule[1][3]]
rule_second_category[4] = [rule[1][4]]
rule_second_category[5] = [rule[1][5]]
rule_second_category[6] = [rule[1][6]]
rule_second_category[7] = [rule[1][7]]
rule_second_category[8] = [rule[1][8]]
rule_second_category[9] = [rule[1][9]]
rule_second_category[10] = [rule[1][10]]
rule_second_category[11] = [rule[1][11]]
rule_second_category[12] = [rule[1][12]]
rule_second_category[13] = [rule[1][13]]
rule_second_category[14] = [rule[1][14]]
rule_second_category[15] = [rule[1][15]]
rule_second_category[16] = [rule[1][16]]
rule_second_category[17] = [rule[1][17]]
rule_second_category[18] = [rule[1][18]]
rule_second_category[19] = [rule[1][19]]
rule_second_category[20] = [rule[1][20]]
rule_second_category[21] = [rule[1][21]]
rule_second_category[22] = [rule[1][22]]
rule_second_category[23] = [rule[1][23]]
rule_second_category[24] = [rule[1][24]]
rule_second_category[25] = [rule[1][25]]
rule_second_category[26] = [rule[1][26]]
rule_second_category[27] = [rule[1][27]]
rule_second_category[28] = [rule[1][28]]
rule_second_category[29] = [rule[2][1]]
rule_second_category[30] = [rule[2][2]]
rule_second_category[31] = [rule[2][3]]
rule_second_category[32] = [rule[2][4]]
rule_second_category[33] = [rule[2][5]]
rule_second_category[34] = [rule[2][6]]
rule_second_category[35] = [rule[2][7]]
rule_second_category[36] = [rule[2][8]]
rule_second_category[37] = [rule[2][9]]
rule_second_category[38] = [rule[2][10]]
rule_second_category[39] = [rule[2][11]]
rule_second_category[40] = [rule[2][12]]
rule_second_category[41] = [rule[2][13]]
rule_second_category[42] = [rule[2][14]]
rule_second_category[43] = [rule[2][15]]
rule_second_category[44] = [rule[2][16]]
rule_second_category[45] = [rule[2][17]]
rule_second_category[46] = [rule[2][18]]
rule_second_category[47] = [rule[2][19]]
rule_second_category[48] = [rule[2][20]]
rule_second_category[49] = [rule[2][21]]
rule_second_category[50] = [rule[2][22]]
rule_second_category[51] = [rule[2][23]]
rule_second_category[52] = [rule[2][24]]
rule_second_category[53] = [rule[2][25]]
rule_second_category[54] = [rule[2][26]]
rule_second_category[55] = [rule[2][27]]
rule_second_category[56] = [rule[2][28]]
rule_second_category[57] = [rule[2][29]]
rule_second_category[58] = [rule[2][30]]
rule_second_category[59] = [rule[2][31]]
rule_second_category[60] = [rule[2][32]]
rule_second_category[61] = [rule[2][33]]
rule_second_category[62] = [rule[2][34]]
rule_second_category[63] = [rule[2][35]]
rule_second_category[64] = [rule[2][36]]
rule_second_category[65] = [rule[2][37]]
rule_second_category[66] = [rule[2][38]]
rule_second_category[67] = [rule[2][39]]
rule_second_category[68] = [rule[2][40]]
rule_second_category[69] = [rule[2][41]]
rule_second_category[70] = [rule[2][42]]
rule_second_category[71] = [rule[2][43]]
rule_second_category[72] = [rule[2][44]]
rule_second_category[73] = [rule[2][45]]
rule_second_category[74] = [rule[2][46]]
rule_second_category[75] = [rule[2][47]]
rule_second_category[76] = [rule[2][48]]
rule_second_category[77] = [rule[2][49]]
rule_second_category[78] = [rule[2][50]]
rule_second_category[79] = [rule[2][51]]
rule_second_category[80] = [rule[2][52]]
rule_second_category[81] = [rule[2][53]]
rule_second_category[82] = [rule[2][54]]
rule_second_category[83] = [rule[2][55]]
rule_second_category[84] = [rule[2][56]]
rule_second_category[85] = [rule[2][57]]
rule_second_category[86] = [rule[2][58]]
rule_second_category[87] = [rule[2][59]]
rule_second_category[88] = [rule[2][60]]
rule_second_category[89] = [rule[2][61]]
rule_second_category[90] = [rule[2][62]]
rule_second_category[91] = [rule[2][63]]
rule_second_category[92] = [rule[2][64]]
rule_second_category[93] = [rule[2][65]]
rule_second_category[94] = [rule[2][66]]
rule_second_category[95] = [rule[2][67]]
rule_second_category[96] = [rule[2][68]]
rule_second_category[97] = [rule[2][69]]
rule_second_category[98] = [rule[2][70]]
rule_second_category[99] = [rule[2][71]]
rule_second_category[100] = [rule[2][72]]
rule_second_category[101] = [rule[2][73]]
rule_second_category[102] = [rule[2][74]]
rule_second_category[103] = [rule[2][75]]
rule_second_category[104] = [rule[2][76]]
rule_second_category[105] = [rule[2][77]]
rule_second_category[106] = [rule[2][78]]
rule_second_category[107] = [rule[2][79]]
rule_second_category[108] = [rule[2][80]]
rule_second_category[109] = [rule[2][81]]
rule_second_category[110] = [rule[2][82]]
rule_second_category[111] = [rule[2][83]]
rule_second_category[112] = [rule[2][84]]
rule_second_category[113] = [rule[2][85]]
rule_second_category[114] = [rule[2][86]]
rule_second_category[115] = [rule[2][87]]
rule_second_category[116] = [rule[2][88]]
rule_second_category[117] = [rule[2][89]]
rule_second_category[118] = [rule[2][90]]
rule_second_category[119] = [rule[2][91]]
rule_second_category[120] = [rule[2][92]]
rule_second_category[121] = [rule[2][93]]
rule_second_category[122] = [rule[2][94]]
rule_second_category[123] = [rule[2][95]]
rule_second_category[124] = [rule[2][96]]
rule_second_category[125] = [rule[2][97]]
rule_second_category[126] = [rule[2][98]]
rule_second_category[127] = [rule[2][99]]
rule_second_category[128] = [rule[2][100]]

rule_second_category[-1] = [
]

rule_second_category[-2] = [
    rule[7][1],
    rule[7][2],
    rule[7][3],
    rule[7][4],
    rule[7][5],
    rule[7][6],
    rule[7][7],
    rule[7][8],
    rule[7][9],
    rule[7][10],
    rule[7][11],
    rule[7][12],
    rule[7][13],
    rule[7][14],
    rule[7][15],
    rule[7][16],
    rule[7][17],
    rule[7][18],
    rule[7][19],
    rule[7][20],
    rule[7][21],
    rule[7][22],
    rule[7][23],
    rule[7][24],
    rule[7][25],
    rule[7][26],
    rule[7][27],
    rule[7][28],
    rule[7][29],
    rule[7][30],
    rule[7][31],
    rule[7][32],
    rule[7][33],
    rule[7][34],
    rule[7][35],
    rule[7][36],
    rule[7][37],
    rule[7][38],
    rule[7][39],
    rule[7][40],
    rule[7][41],
    rule[7][42],
    rule[7][43],
    rule[7][44],
    rule[7][45],
    rule[7][46],
    rule[7][47],
    rule[7][48],
    rule[7][49],
    rule[7][50],
    rule[7][51],
    rule[7][52],
    rule[7][53],
    rule[7][54],
    rule[7][55],
    rule[7][56],
    rule[7][57],
    rule[7][58],
    rule[7][59],
    rule[7][60],
    rule[7][61],
    rule[7][62],
    rule[7][63],
    rule[7][64],
    rule[7][65],
]

if not rule_second_category[-1]:
    max_id = 0
    for name, val, indx in COUNTRY_NAME_LIST:
        max_id = max_id + 1
        rule[3][max_id] = {"id":max_id, "name":name, "type_name":'Country', "type":3, "first":3, "sec":-1, "value":val, 'index':indx}
        rule_second_category[-1].append(rule[3][max_id])
    rule_second_category[-1].sort(key=itemgetter('index', 'name'))



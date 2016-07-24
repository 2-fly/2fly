#!/usr/bin/env python
# -*- coding:utf-8 -*-

import init_env

PERMISSION_IGNORE = -1
PERMISSION_CONFIGURE = 0
PERMISSION_REPORT = 1
PERMISSION_APIOFFER = 2
PERMISSION_TOOLS = 3
PERMISSION_DASHBOARD = 4

class PermissionType(object):
    def __init__(self):
        self._pt =  {
            1 : SuperAdmin,
            2 : BDAdmin,
            3 : BD,
            4 : BDUser,
            5 : SuperUser,
            6 : NormalUser,
            7 : RelativeUser,
            8 : MBUser,
        }

    def get(self, k):
        return self._pt[k]

class BasePermission(object):
    def __init__(self):
        self.count = 0

    def add(self, k):
        v = 1 << self.count
        setattr(self, k, v)
        self.count = self.count + 1

class PermissionDashboard(BasePermission):
    def __init__(self):
        super(PermissionDashboard, self).__init__()
        self.add("PERMISSION_DASHBOARD_SHOW")

class PermissionConfigure(BasePermission):
    def __init__(self):
        super(PermissionConfigure, self).__init__()
        self.add("PERMISSION_CONFIGURE_DOMIAN_INFO")
        self.add("PERMISSION_CONFIGURE_TRAFFIC_SOURCE")
        self.add("PERMISSION_CONFIGURE_NETWORK")
        self.add("PERMISSION_CONFIGURE_DIRECT_OFFER")
        self.add("PERMISSION_CONFIGURE_MASSIVAL_OFFER")
        self.add("PERMISSION_CONFIGURE_CUSTOM_OFFER")
        self.add("PERMISSION_CONFIGURE_LANDPAGE")
        self.add("PERMISSION_CONFIGURE_CAMPAIGN")
        self.add("PERMISSION_CONFIGURE_MAIL")
        self.add("PERMISSION_CONFIGURE_ADMIN_OFFER")
        self.add("PERMISSION_CONFIGURE_ADMIN_TRAFFIC_SOURCE")
        self.add("PERMISSION_CONFIGURE_ADMIN_AFFILIATE_NETWORK")
        self.add("PERMISSION_CONFIGURE_SWITCH_PATH")

class PermissionReport(BasePermission):
    def __init__(self):
        super(PermissionReport, self).__init__()
        self.add("PERMISSION_REPORT_NORMAL")
        self.add("PERMISSION_REPORT_ADMIN")
        self.add("PERMISSION_REPORT_ENCRYPT")
        self.add("PERMISSION_REPORT_ZERO")
        self.add("PERMISSION_REPORT_ZERO_ENCRYPT")

class PermissionApiOffer(BasePermission):
    def __init__(self):
        super(PermissionApiOffer, self).__init__()
        self.add("PERMISSION_API_OFFER_MOBVISTA")
        self.add("PERMISSION_API_OFFER_IRONSOURCE")

class PermissionTool(BasePermission):
    def __init__(self):
        super(PermissionTool, self).__init__()
        self.add("PERMISSION_TOOLS_EVENTS")
        self.add("PERMISSION_TOOLS_RELATIVE_EVENTS")
        self.add("PERMISSION_TOOLS_DECRYPT")

MASSIVAL_INNER_USER = 0
MASSIVAL_NORMAL_USER = 1

class BaseUser(object):
    def __init__(self):
        self._permission = {
            PERMISSION_CONFIGURE : 0,
            PERMISSION_REPORT : 0,
            PERMISSION_APIOFFER : 0,
            PERMISSION_TOOLS : 0,
            PERMISSION_DASHBOARD : 0,
        }
        self.init()
        self._user_type = MASSIVAL_NORMAL_USER

    def set_user_type(self, user_type):
        self._user_type = user_type

    def check_is_massival_inner_user(self):
        return self._user_type == MASSIVAL_INNER_USER

    def init(self):
        self.init_configure()
        self.init_report()
        self.init_apioffer()
        self.init_tools()
        self.init_dashboard()

    def init_configure(self):
        pass

    def init_report(self):
        pass

    def init_apioffer(self):
        pass

    def init_tools(self):
        pass

    def init_dashboard(self):
        obj = PermissionDashboard()
        self.add(PERMISSION_DASHBOARD, obj.PERMISSION_DASHBOARD_SHOW)

    def add(self, k, v):
        self._permission[k] = self._permission[k] | v

    def get_permission(self, k):
        return self._permission[k]

    def check_permission(self, k, v):
        return self._permission[k] & v != 0

class SuperAdmin(BaseUser):
    def __init__(self):
        super(SuperAdmin, self).__init__()

    def init_configure(self):
        obj = PermissionConfigure()
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_DOMIAN_INFO)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_TRAFFIC_SOURCE)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_NETWORK)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_DIRECT_OFFER)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_MASSIVAL_OFFER)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_CUSTOM_OFFER)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_LANDPAGE)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_CAMPAIGN)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_MAIL)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_ADMIN_OFFER)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_ADMIN_TRAFFIC_SOURCE)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_ADMIN_AFFILIATE_NETWORK)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_SWITCH_PATH)

    def init_report(self):
        obj = PermissionReport()
        self.add(PERMISSION_REPORT, obj.PERMISSION_REPORT_NORMAL)
        self.add(PERMISSION_REPORT, obj.PERMISSION_REPORT_ADMIN)

    def init_apioffer(self):
        obj = PermissionApiOffer()
        self.add(PERMISSION_APIOFFER, obj.PERMISSION_API_OFFER_MOBVISTA)
        self.add(PERMISSION_APIOFFER, obj.PERMISSION_API_OFFER_IRONSOURCE)

    def init_tools(self):
        obj = PermissionTool()
        self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_EVENTS)
        self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_RELATIVE_EVENTS)
        self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_DECRYPT)

class BDAdmin(BaseUser):
    def __init__(self):
        super(BDAdmin, self).__init__()
        self.set_user_type(MASSIVAL_INNER_USER)

    def init_configure(self):
        obj = PermissionConfigure()
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_ADMIN_OFFER)

    def init_report(self):
        obj = PermissionReport()
        self.add(PERMISSION_REPORT, obj.PERMISSION_REPORT_NORMAL)

    def init_apioffer(self):
        obj = PermissionApiOffer()
        self.add(PERMISSION_APIOFFER, obj.PERMISSION_API_OFFER_MOBVISTA)
        self.add(PERMISSION_APIOFFER, obj.PERMISSION_API_OFFER_IRONSOURCE)

    def init_tools(self):
        obj = PermissionTool()
        self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_RELATIVE_EVENTS)

class BD(BaseUser):
    def __init__(self):
        super(BD, self).__init__()
        self.set_user_type(MASSIVAL_INNER_USER)

    def init_configure(self):
        obj = PermissionConfigure()
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_MASSIVAL_OFFER)

    def init_tools(self):
        obj = PermissionTool()
        self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_RELATIVE_EVENTS)
        #self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_EVENTS)

    def init_dashboard(self):
        pass

class BDUser(BaseUser):
    def __init__(self):
        super(BDUser, self).__init__()
        self.set_user_type(MASSIVAL_INNER_USER)

    def init_configure(self):
        obj = PermissionConfigure()
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_MASSIVAL_OFFER)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_ADMIN_OFFER)

    def init_report(self):
        obj = PermissionReport()
        self.add(PERMISSION_REPORT, obj.PERMISSION_REPORT_NORMAL)
        self.add(PERMISSION_REPORT, obj.PERMISSION_REPORT_ENCRYPT)

    def init_apioffer(self):
        obj = PermissionApiOffer()
        self.add(PERMISSION_APIOFFER, obj.PERMISSION_API_OFFER_MOBVISTA)
        self.add(PERMISSION_APIOFFER, obj.PERMISSION_API_OFFER_IRONSOURCE)

    def init_tools(self):
        obj = PermissionTool()
        #self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_EVENTS)
        self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_RELATIVE_EVENTS)
        self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_DECRYPT)

class SuperUser(BaseUser):
    def __init__(self):
        super(SuperUser, self).__init__()

    def init_configure(self):
        obj = PermissionConfigure()
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_DOMIAN_INFO)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_TRAFFIC_SOURCE)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_NETWORK)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_DIRECT_OFFER)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_MASSIVAL_OFFER)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_CUSTOM_OFFER)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_LANDPAGE)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_CAMPAIGN)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_SWITCH_PATH)

    def init_report(self):
        obj = PermissionReport()
        self.add(PERMISSION_REPORT, obj.PERMISSION_REPORT_NORMAL)
        self.add(PERMISSION_REPORT, obj.PERMISSION_REPORT_ZERO)

    def init_apioffer(self):
        obj = PermissionApiOffer()
        self.add(PERMISSION_APIOFFER, obj.PERMISSION_API_OFFER_MOBVISTA)
        self.add(PERMISSION_APIOFFER, obj.PERMISSION_API_OFFER_IRONSOURCE)

    def init_tools(self):
        obj = PermissionTool()
        self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_EVENTS)
        self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_DECRYPT)
        self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_RELATIVE_EVENTS)

class NormalUser(BaseUser):
    def __init__(self):
        super(NormalUser, self).__init__()

    def init_configure(self):
        obj = PermissionConfigure()
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_DOMIAN_INFO)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_TRAFFIC_SOURCE)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_NETWORK)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_DIRECT_OFFER)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_CUSTOM_OFFER)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_LANDPAGE)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_CAMPAIGN)

    def init_report(self):
        obj = PermissionReport()
        self.add(PERMISSION_REPORT, obj.PERMISSION_REPORT_NORMAL)

    def init_tools(self):
        obj = PermissionTool()
        self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_EVENTS)

class RelativeUser(BaseUser):
    def __init__(self):
        super(RelativeUser, self).__init__()

    def init_configure(self):
        obj = PermissionConfigure()
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_DOMIAN_INFO)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_TRAFFIC_SOURCE)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_NETWORK)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_MASSIVAL_OFFER)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_LANDPAGE)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_CAMPAIGN)

    def init_report(self):
        obj = PermissionReport()
        self.add(PERMISSION_REPORT, obj.PERMISSION_REPORT_NORMAL)
        self.add(PERMISSION_REPORT, obj.PERMISSION_REPORT_ENCRYPT)
        self.add(PERMISSION_REPORT, obj.PERMISSION_REPORT_ZERO_ENCRYPT)

    def init_tools(self):
        obj = PermissionTool()
        self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_EVENTS)

    def init_apioffer(self):
        obj = PermissionApiOffer()
        self.add(PERMISSION_APIOFFER, obj.PERMISSION_API_OFFER_MOBVISTA)
        self.add(PERMISSION_APIOFFER, obj.PERMISSION_API_OFFER_IRONSOURCE)

class MBUser(BaseUser):
    def __init__(self):
        super(MBUser, self).__init__()
        self.set_user_type(MASSIVAL_INNER_USER)

    def init_configure(self):
        obj = PermissionConfigure()
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_DOMIAN_INFO)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_MASSIVAL_OFFER)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_LANDPAGE)
        self.add(PERMISSION_CONFIGURE, obj.PERMISSION_CONFIGURE_CAMPAIGN)

    def init_report(self):
        obj = PermissionReport()
        self.add(PERMISSION_REPORT, obj.PERMISSION_REPORT_NORMAL)
        self.add(PERMISSION_REPORT, obj.PERMISSION_REPORT_ENCRYPT)
        self.add(PERMISSION_REPORT, obj.PERMISSION_REPORT_ZERO_ENCRYPT)

    def init_tools(self):
        obj = PermissionTool()
        self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_EVENTS)
        self.add(PERMISSION_TOOLS, obj.PERMISSION_TOOLS_RELATIVE_EVENTS)

def __get_permission_type():
    s = "PERMISSION_IGNORE = %s\nPERMISSION_CONFIGURE = %s\nPERMISSION_REPORT = %s\nPERMISSION_APIOFFER = %s\nPERMISSION_TOOLS = %s\nPERMISSION_DASHBOARD = %s\n\n" % (PERMISSION_IGNORE, PERMISSION_CONFIGURE, PERMISSION_REPORT, PERMISSION_APIOFFER, PERMISSION_TOOLS, PERMISSION_DASHBOARD)
    return s

def __get_permission_keyvalue():
    pt = [PermissionDashboard, PermissionConfigure, PermissionReport, PermissionApiOffer, PermissionTool]
    result = []
    for p in pt:
        ins = p()
        l = []
        for k, v in vars(ins).iteritems():
            if not k.startswith("PERMISSION"):
                continue
            s = "%s = %s\n" % (k ,v)
            l.append(s)
        s = "".join(l)
        result.append(s)
    return "\n".join(result)

def _all_offer_mask():
    pt = PermissionConfigure()
    o = pt.PERMISSION_CONFIGURE_MASSIVAL_OFFER | pt.PERMISSION_CONFIGURE_DIRECT_OFFER | pt.PERMISSION_CONFIGURE_CUSTOM_OFFER
    s = "\nPERMISSION_CONFIGURE_ALL_OFFER = %s\n" % o
    return s

def _all_report_mask():
    pt = PermissionReport()
    o = pt.PERMISSION_REPORT_NORMAL | pt.PERMISSION_REPORT_ADMIN | pt.PERMISSION_REPORT_ZERO
    s = "\nPERMISSION_REPORT_ALL = %s\n" % o
    return s

def write_permission_config():
    path = "../config/permission_config.py"
    fp = open(path, "w")
    head = "#!/usr/bin/env python\n# -*- coding:utf-8 -*-\n\n"
    fp.write(head)
    s = __get_permission_type()
    fp.write(s)
    s = __get_permission_keyvalue()
    fp.write(s)
    s = _all_offer_mask()
    fp.write(s)
    s = _all_report_mask()
    fp.write(s)
    fp.close()

if __name__ == '__main__':
    write_permission_config()

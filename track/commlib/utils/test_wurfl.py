#from pywurfl.wurfl import Wurfl
#a = Wurfl('/root/wurfl.xml''')

import time
import user_agent_parser

before = time.time()
from wurfl import devices
from pywurfl.algorithms import TwoStepAnalysis
diff = (time.time() - before)*1000
print diff, 'ms'

ua1 = u"Nokia3350/1.0 (05.01)"
ua2 = u"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36"
ua3 = u"Mozilla/5.0 (Linux; U; Android 4.1.2; es-us; SPH-M840 Build/JZO54K) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
ua4 = u'Mozilla/5.0 (Linux; Android 4.4.4; D5106 Build/18.1.A.2.25) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36'
ua5 = u'Mozilla/5.0 (Linux; ABC 4.4.4; XXXX Build/18.1.A.2.25) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36'
ua6 = u'Mozilla/5.0 (Linux; Android 4.4; Nexus 5 Build/KRT16M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36'
ua7 = u'Mozilla/5.0 (Linux; Android 4.4.2; SM701 Build/SANFRANCISCO) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36'
ua7 = u'Mozilla/5.0 (Linux; U; Android 2.3.6; pt-br; GT-I9070 Build/GINGERBREAD) AppleWebKit/533.1 (KHTML  like Gecko) Version/4.0 Mobile Safari/533.1'
ua7 = u'Mozilla/5.0 (Linux; U; Android 4.1.2; pt-br; GT-S6812B Build/JZO54K) AppleWebKit/534.30 (KHTML  like Gecko) Version/4.0 Mobile Safari/534.30'
ua7 = u'Mozilla/5.0 (Linux; U; Android 4.1.2; pt-br; GT-P3110 Build/JZO54K) AppleWebKit/534.30 (KHTML  like Gecko) Version/4.0 Safari/534.30'
search_algorithm = TwoStepAnalysis(devices)


# Print out the specialized capabilities for this device.
#print device

before = time.time()
l = [ua1, ua2, ua3, ua4, ua5, ua6, ua7]
for i in l:
    device = devices.select_ua(i, search=search_algorithm)
    print '-'*50
    print 'is_wireless_device: ', device.is_wireless_device
    print 'model_name: ', device.model_name
    print 'brand_name: ', device.brand_name
    print 'devid: ', device.devid
    print 'devua: ', device.devua

    print 'device_os: ', device.device_os
    print 'device_os_version: ', device.device_os_version

    print 'mobile_browser: ', device.mobile_browser
    print 'mobile_browser_version: ', device.mobile_browser_version
    print 'mobileoptimized: ', device.mobileoptimized

diff = (time.time() - before)*1000
print diff, 'ms'



#foo('Mozilla/5.0 (Linux; Android 4.4; Nexus 5 Build/KRT16M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36')

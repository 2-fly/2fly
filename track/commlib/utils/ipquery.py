
import geoip2.database

class IPQuery(object):
    def __init__(self, mmdb_path):
        self.db_path = mmdb_path
        self.db = geoip2.database.Reader(self.db_path)

    def get_country_name(self, ip):
        """ United States """
        try:
            result = self.db.city(ip)
            return result.country.name
        except Exception:
            return ''

    def get_country_iso(self, ip):
        """ US """
        try:
            result = self.db.city(ip)
            return result.country.iso_code
        except Exception:
            return ''

    def get_city_name(self, ip):
        """ San Francisco """
        try:
            result = self.db.city(ip)
            return result.city.name
        except Exception:
            return ''

    def get_info(self, ip):
        try:
            result = self.db.city(ip)
            return result.country.name, result.country.iso_code, result.city.name
        except Exception:
            return '', '', ''



class ISPQuery(object):
    def __init__(self, mmdb_path):
        self.db_path = mmdb_path
        self.db = geoip2.database.Reader(self.db_path)

    def get_isp(self, ip):
        """ United States """
        try:
            result = self.db.isp(ip)
            return result.isp
        except Exception:
            return ''



if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print 'usage: %s ip'%sys.argv[0]
        exit(-1)

    ip = sys.argv[1]
    #ipquery = IPQuery('GeoLite2-Country.mmdb')
    ipquery = IPQuery('GeoLite2-City.mmdb')
    print ipquery.get_info(ip)

    ipquery = ISPQuery('GeoIP2-ISP.mmdb')
    print ipquery.get_isp(ip)


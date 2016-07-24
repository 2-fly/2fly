#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urlparse


def match_domain_or_subdomain(url, domain):
    if not url.startswith('http') and not url.startswith('https'):
        url = '%s%s' % ('http://', url)

    p = urlparse.urlparse(url)
    hostname = p.netloc.lower()

    sub_domain = '.' + domain
    if hostname == domain or hostname.endswith(sub_domain):
        return True
    else:
        return False


def parse_hostname(url):
    if not url.startswith('http') and not url.startswith('https'):
        url = '%s%s' % ('http://', url)

    p = urlparse.urlparse(url)
    hostname = p.netloc.lower()

    return hostname


def is_subdomain(cur_domain, domains):
    # validate domains
    is_sub = False
    for _domain in domains:
        sub_domain = '.' + _domain
        if cur_domain == _domain or cur_domain.endswith(sub_domain):
            is_sub = True
            break

    return is_sub



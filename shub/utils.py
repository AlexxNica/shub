import sys, imp, os, netrc

from subprocess import Popen, PIPE

import requests

from shub.click_utils import log

SCRAPY_CFG_FILE = os.path.expanduser("~/.scrapy.cfg")
OS_WIN = True if os.name == 'nt' else False
NETRC_FILE = os.path.expanduser('~/_netrc') if OS_WIN else os.path.expanduser('~/.netrc')

def missing_modules(*modules):
    """Receives a list of module names and returns those which are missing"""
    missing = []
    for module_name in modules:
        try:
            imp.find_module(module_name)
        except ImportError:
            missing.append(module_name)
    return missing

def find_api_key():
    """Finds and returns the Scrapy Cloud APIKEY"""
    key = os.getenv("SHUB_APIKEY")
    if not key:
        key = get_key_netrc()
    return key

def get_key_netrc():
    """Gets the key from the netrc file"""
    try:
        info = netrc.netrc(NETRC_FILE)
    except IOError:
        return
    try:
        key, account, password = info.authenticators("scrapinghub.com")
    except TypeError:
        return
    if key:
        return key

def make_deploy_request(url, data, files, auth):
    try:
        rsp = requests.post(url=url, auth=auth, data=data, files=files,
                            stream=True, timeout=300)
        rsp.raise_for_status()
        for line in rsp.iter_lines():
            log(line)
        return True
    except requests.HTTPError as exc:
        rsp = exc.response
        log("Deploy failed ({}):".format(rsp.status_code))
        log(rsp.text)
        return False
    except requests.RequestException as exc:
        log("Deploy failed: {}".format(exc))
        return False

def pwd_git_version():
    p = Popen(['git', 'describe', '--always'], stdout=PIPE)
    d = p.communicate()[0].strip('\n')
    if p.wait() != 0:
        p = Popen(['git', 'rev-list', '--count', 'HEAD'], stdout=PIPE)
        d = 'r%s' % p.communicate()[0].strip('\n')

    p = Popen(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=PIPE)
    b = p.communicate()[0].strip('\n')
    return '%s-%s' % (d, b)

def pwd_hg_version():
    p = Popen(['hg', 'tip', '--template', '{rev}'], stdout=PIPE)
    d = 'r%s' % p.communicate()[0]
    p = Popen(['hg', 'branch'], stdout=PIPE)
    b = p.communicate()[0].strip('\n')
    return '%s-%s' % (d, b)

def pwd_bzr_version():
    p = Popen(['bzr', 'revno'], stdout=PIPE)
    d = '%s' % p.communicate()[0].strip()
    return d

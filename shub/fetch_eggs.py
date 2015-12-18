from __future__ import absolute_import

from six.moves.urllib.parse import urljoin

import click
import requests

from click import ClickException

from shub.click_utils import log
from shub.config import get_target
from shub.exceptions import AuthException


@click.command(help="Download a project's eggs from the Scrapy Cloud")
@click.argument("target", required=False, default='default')
def cli(target):
    project, endpoint, apikey = get_target(target)
    destfile = 'eggs-%s.zip' % project
    fetch_eggs(project, endpoint, apikey, destfile)


def fetch_eggs(project, endpoint, apikey, destfile):
    auth = (apikey, '')
    url = urljoin(endpoint, "../eggs/bundle.zip?project=%s" % project)
    rsp = requests.get(url=url, auth=auth, stream=True, timeout=300)

    _assert_response_is_valid(rsp)

    log("Downloading eggs to %s" % destfile)

    with open(destfile, 'wb') as f:
        for chunk in rsp.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()


def _assert_response_is_valid(rsp):
    if rsp.status_code == 403:
        raise AuthException()
    elif rsp.status_code != 200:
        msg = 'Eggs could not be fetched. Status: %d' % rsp.status_code
        raise ClickException(msg)

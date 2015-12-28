import json

import click

from scrapinghub import Connection, APIError
from six.moves.urllib.parse import urljoin

from shub.exceptions import RemoteErrorException
from shub.config import get_target


@click.command(help='Schedule a spider to run on Scrapy Cloud')
@click.argument('spider', type=click.STRING)
@click.option('-a', '--argument',
              help='spider argument (-a name=value)', multiple=True)
@click.option('-s', '--set',
              help='job-specific setting (-s name=value)', multiple=True)
def cli(spider, argument, set):
    try:
        target, spider = spider.rsplit('/', 1)
    except ValueError:
        target = 'default'
    project, endpoint, apikey = get_target(target)
    job_key = schedule_spider(project, endpoint, apikey, spider, argument, set)
    watch_url = urljoin(
        endpoint,
        '../../p/{}/job/{}/{}'.format(*job_key.split('/')),
    )
    click.echo(
        'Spider {} scheduled, watch it running here:\n{}'
        ''.format(spider, watch_url)
    )


def schedule_spider(project, endpoint, apikey, spider, arguments=(),
                    settings=()):
    conn = Connection(apikey, url=urljoin(endpoint, '..'))
    try:
        return conn[project].schedule(
            spider,
            job_settings=json.dumps(dict(x.split('=') for x in settings)),
            **dict(x.split('=') for x in arguments)
        )
    except APIError as e:
        raise RemoteErrorException(e.message)

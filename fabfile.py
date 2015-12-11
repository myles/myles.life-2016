#!/usr/bin/env python

import datetime

from fabric.utils import error
from fabric.api import env, task, run, get, roles

env.user = 'myles_myles-life'
env.hosts = ['ssh.phx.nearlyfreespeech.net']
env.use_ssh_config = True
env.output_prefix = []
env.roledefs = {
    'wp': ['ssh.phx.nearlyfreespeech.net']
}

def wp_cli(args):
    run('wp {0}'.format(args))


@task
@roles('wp')
def plugin(arg=None):
    """
    Manage the plugins.
    """
    if arg == 'update':
        wp_cli('plugin update --all')
    elif arg == 'status':
        wp_cli('plugin status')
    elif arg == 'list':
        wp_cli('plugin list')
    else:
        error('No argument found.')


@task
@roles('wp')
def theme(arg=None):
    if arg == 'update':
        wp_cli('theme update --all')
    elif arg == 'status':
        wp_cli('theme status')
    elif arg == 'list':
        wp_cli('theme list')
    else:
        error('No argument found.')


@task
@roles('wp')
def db(arg=None):
    if arg == 'optimize':
        wp_cli('db optimize')
    elif arg == 'repair':
        wp_cli('db repair')
    elif arg == 'backup':
        # Figure out the file name of the backup.
        now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = 'backup-{0}.sql'.format(now)

        # Use the WP-CLI command to export the database.
        wp_cli('db export /home/private/{0}'.format(filename))

        # Copy the export locally.
        get('/home/private/{0}'.format(filename),
            './backups/{0}'.format(filename))

        # Remove the backup from the server.
        run('rm /home/private/{0}'.format(filename))
    else:
        error('No argument found.')


@task
@roles('wp')
def core(arg=None):
    if arg == 'update':
        wp_cli('core update')
    elif arg == 'version':
        wp_cli('core version --extra')
    else:
        error('No argument found.')


@task
@roles('wp')
def update_all():
    plugin('update')
    theme('update')
    core('update')

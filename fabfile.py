#!/usr/bin/env python
"""
Fabric file to working with Myles' Life WordPress setup.
"""

import os
import datetime

from fabric.operations import prompt
from fabric.utils import error, abort
from fabric.api import env, task, run, get, roles

env.user = 'myles'
env.hosts = ['bear']
env.use_ssh_config = True

env.wordpress_path = '/srv/www/myles.life/www/html/'

env.output_prefix = []

env.roledefs = {
    'wp': ['bear']
}


def wp_cli(args):
    """Run the wpcli command on the server."""
    run('wp --path={0} {1}'.format(env.wordpress_path, args))


@task
@roles('wp')
def setup():
    """Setup the WordPress envoirment."""
    is_installed = wp_cli('core is-installed')

    if is_installed:
        wp_cli('core download')

        install_params = {}

        install_params['url'] = prompt('URL: ')
        install_params['title'] = prompt('Title: ')
        install_params['admin_user'] = prompt('Admin User: ')
        install_params['admin_password'] = prompt('Admin Password: ')
        install_params['admin_email'] = prompt('Admin Email: ')

        config_params = {}

        config_params['dbname'] = prompt('Database Name: ')
        config_params['dbuser'] = prompt('Database User: ')
        config_params['dbpass'] = prompt('Database Password: ')
        config_params['dbhost'] = prompt('Database Hostname: ')

        wp_cli('core install {0}'.format(' '.join(['--%s="%s"' % (k, v) for (k, v) in install_params.items()])))

        wp_cli('core config {0}'.format(' '.join(['--%s="%s"' % (k, v) for (k, v) in config_params.items()])))

        wp_cli('core update-db')
    else:
        abort('WordPress is already installed.')


@task
@roles('wp')
def plugin(arg=None):
    """Manage the plugins."""
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
    """Manage the themes."""
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
    """Manage the database."""
    if arg == 'optimize':
        wp_cli('db optimize')
    elif arg == 'repair':
        wp_cli('db repair')
    elif arg == 'backup':
        # Figure out the file name of the backup.
        now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = 'backup-{0}.sql'.format(now)

        # Use the WP-CLI command to export the database.
        wp_cli('db export /tmp/{0}'.format(filename))

        # Copy the export locally.
        get('/tmp/{0}'.format(filename),
            './backups/{0}'.format(filename))

        # Remove the backup from the server.
        run('rm /tmp/{0}'.format(filename))
    else:
        error('No argument found.')


@task
@roles('wp')
def core(arg=None):
    """Manage the WordPress install."""
    if arg == 'update':
        wp_cli('core update')
    elif arg == 'version':
        wp_cli('core version --extra')
    else:
        error('No argument found.')


@task
@roles('wp')
def update_all():
    """Update everything."""
    plugin('update')
    theme('update')
    core('update')


@task
@roles('wp')
def backup():
    """Backup the WordPress site."""
    # Backup the WordPress database.
    db('backup')

    # Copy teh wp-config.php file from the server.
    get(os.path.join(env.wordpress_path, 'wp-config.php'),
        './backups/wp-config.php')

    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    theme_list = wp_cli('theme list --format=csv')
    plugin_list = wp_cli('plugin list --format=csv')

    # Backup the installed themes
    #with open('./backups/themes.csv', 'w') as f:
    #    f.write(theme_list)

    # Backup the installed plugins
    #with open('./backups/plugins.csv', 'w') as f:
    #    f.write(plugin_list)

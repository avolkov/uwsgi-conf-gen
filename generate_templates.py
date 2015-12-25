#!/usr/bin/env python3

import argparse
import configparser
from os import path
from genshi.template import TextTemplate

DEFAULT_CONF_FILE = 'vars.ini'

nginx_conn_str = \
    "    server unix://${socket_dir}/${file_name}${count}.sock;"

supervisor_app_str = """

[program:app-uwsgi0${count}]
autorestart = true
process_name=%(program_name)s
command = ${venv}/bin/uwsgi --ini projname_${count}.ini
numprocs=1
numprocs_start=1
stdout_logfile=%(here)s/logs/%(program_name)s_status.log
stderr_logfile=%(here)s/logs/%(program_name)s_err.log
"""


def generate_configs(confparse, count):
    """Read out files and generate configs"""
    files = confparse['files']
    template_vars = confparse['template']
    templates = dict([(x, open(x, 'r').read()) for x in files.values()])
    nginx_conn = []
    supervisor_apps = []
    for k in range(count):
        out_wsgi_ini_fname = "%s%d.ini" % (template_vars['file_name'], k)
        out_wsgi = TextTemplate(templates[files['wsgi_template']])
        # Write out each of uwsgi config
        with open(out_wsgi_ini_fname, 'w') as out_fd:
            out_fd.write(out_wsgi.generate(count=k, **template_vars).__str__())

        out_nginx = TextTemplate(nginx_conn_str)
        nginx_conn.append(
            out_nginx.generate(count=k, **template_vars).__str__())
        out_super = TextTemplate(supervisor_app_str)
        supervisor_apps.append(
            out_super.generate(count=k, **template_vars).__str__())

    # Write out nginx config
    with open('site.conf', 'w') as out_fd:
        nginx_conn = "\n".join(nginx_conn)
        tmpl = TextTemplate(templates[files['nginx_template']])
        stream = tmpl.generate(server_block=nginx_conn, **template_vars)
        out_fd.write(stream.__str__())

    # Write out supervisord config
    with open('supervisord.conf', 'w') as out_fd:
        out_fd.write(open(files['supervisor_template'], 'r').read())
        out_fd.write("\n".join(supervisor_apps))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='NGINX/uwsgi config generator')
    parser.add_argument(
        '-i', '--instances', type=int, required=True,
        help='Enter the number of instances to generate from template file'
    )
    parser.add_argument(
        '-c', '--config', type=str,
        help="Source template variables. Default -- %s " % DEFAULT_CONF_FILE
    )

    args = parser.parse_args()
    conf_file = getattr(args, 'config', DEFAULT_CONF_FILE)
    if not conf_file:
        conf_file = DEFAULT_CONF_FILE
    assert path.exists(conf_file), "Configuration file '%s' does not exist" % \
        conf_file
    assert path.isfile(conf_file), "Configuration file '%s' is not a file" % \
        conf_file
    cp = configparser.ConfigParser()
    cp.read(conf_file)
    generate_configs(cp, getattr(args, 'instances', 1))

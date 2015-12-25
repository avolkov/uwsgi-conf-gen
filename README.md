uWSGI/nginx/supervisor config file generator
======

This is a quick and dirty solution to a problem I couldn't figure out how to solve with buildout receipts -- take one (uWSGI) configuration template and generate many configuration files.

The purpose of this project is to generate configuration files for production setup of django projects, with multiple non-master uWSGI instances controlled by Supervisor and nginx doing load balancing those instances, with nginx and uWsgi communicating over Unix sockets.

# Usage:

    $ python3 generate_templates.py

The script takes one mandatory parameter (-i) -- a number of uWSGI instances to create, nginx to load balance over, and supervisor to control; one optional parameter (-c) -- a configuration file with variables (default `vars.ini).

Supplied configuration files, all of the file names are specified in `vars.ini`:

projname_ini.tmpl -- a template for uWSGI, usually django project name.
site_conf.tmpl -- a template for Nginx
supervisor_conf.tmpl -- a template for supervisor
vars.ini -- sample variable definitions

# Requirements

Requirements for the script --  Python 3, Genshi. See `requirements.txt`



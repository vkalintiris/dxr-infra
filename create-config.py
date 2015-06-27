#!/usr/bin/env python2.7
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import re
import sys
import urlparse
import yaml

from jinja2 import Environment, FileSystemLoader
# from pprint import pprint

HERE = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(HERE, 'config.yml')


def convert_url(prefix, url):
    url_re = re.compile('/\*$')
    if url_re.search(url):
        url = url[:-1]
    path = urlparse.urlsplit(url).path.lstrip('/')
    return os.path.join(prefix, path)


def envget(dict, key):
    try:
        return os.environ['DXR_' + key.upper()]
    except KeyError:
        return dict[key]


if __name__ == '__main__':
    if 'VIRTUAL_ENV' not in os.environ:
        activate = os.path.join(HERE, 'venv', 'bin', 'activate_this.py')
        execfile(activate, dict(__file__=activate))
        sys.executable = os.path.join(HERE, 'venv', 'bin', 'python2.7')
        os.environ['VIRTUAL_ENV'] = os.path.join(HERE, 'venv')

    template_env = Environment(
        loader=FileSystemLoader(os.path.join(HERE, 'templates')),
        keep_trailing_newline=False,
        lstrip_blocks=False,
        trim_blocks=False,
    )
    templates = {
        'dxr_config.j2': os.path.join(HERE, 'dxr.config'),
        'jobs.yml.j2': os.path.join(HERE, 'jobs.yml'),
    }

    try:
        f = open(config_file, 'r')
        cfg = yaml.safe_load(f)
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
    finally:
        f.close()

    # override defaults with ENV
    dxr_defaults = cfg['dxr_defaults']
    for i in dxr_defaults:
        dxr_defaults[i] = envget(dxr_defaults, i)
    # pprint(dxr_defaults)

    trees = []
    for t in cfg['trees']:
        if 'source_folder' not in t:
            t['source_folder'] = convert_url('src', t['url'])
        if 'object_folder' not in t:
            t['object_folder'] = convert_url('obj', t['url'])
        # merge dicts, with tree dict taking precedence
        trees.append(dict(cfg['tree_defaults'], **t))
    # pprint(trees)

    for t in templates:
        print template_env.get_template(t).render(trees=trees,
                                                  dxr=dxr_defaults)
#        with open(templates[t], 'a') as f:
#            contents = template_env.get_template(t).render(config)
#            f.write(contents)
#            f.close()
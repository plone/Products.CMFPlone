# -*- coding: utf-8 -*-
# DEPRECATED
# This is more of a script runner for the _generate_gruntfile.py
# script. Just a wrapper so that script can be simply called
# from the bin directory
from Products.CMFPlone._scripts.compile_resources import generate_gruntfile
import argparse
import os
import sys

parser = argparse.ArgumentParser(
    description='Generate Gruntfile.js from a Plone site configuration')
parser.add_argument('--site-id', dest='site_id',
                    default='Plone', help='ID for the plone site id')
parser.add_argument('--instance', dest='instance',
                    help='path to instance executable. If not provided, '
                         'will look in bin this was executed from for '
                         'instance or client1')
parser.add_argument('--compile-dir', dest='compile_dir', default='',
                    help='Output directory for the compiled bundle files.')


def main(argv=sys.argv):
    print ('-' * 80)
    print(
        'DEPRECATED: {0}\n'
        'Use "bin/plone-compile-resources -IC [other params]" instead.\n'
        'For more information use "bin/plone-compile-resources --help"'.format(
            argv[0]
        )
    )
    print ('-' * 80)
    args, _ = parser.parse_known_args()
    # XXX is this a good way to do it?
    base_path = os.path.sep.join(
        os.path.abspath(sys.argv[0]).split(os.path.sep)[:-2])

    generate_gruntfile(
        base_path,
        args.instance,
        args.site_id,
        args.compile_dir
    )
    print('DONE DEPRECATED {0} (see above)'.format(argv[0]))

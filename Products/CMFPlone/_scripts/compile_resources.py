# -*- coding: utf-8 -*-
import argparse
import os
import sys
import subprocess

this_dir = os.path.dirname(os.path.realpath(__file__))

package_json_contents = """{
  "name": "gruntrunner",
  "version": "1.1.2",
  "private": true,
  "devDependencies": {
    "grunt": "~0.4.5",
    "grunt-cli": "~1.2.0",
    "grunt-contrib-less": "~1.3.0",
    "grunt-contrib-requirejs": "~1.0.0",
    "grunt-contrib-uglify": "~1.0.1",
    "grunt-contrib-watch": "~1.0.0",
    "grunt-sed": "collective/grunt-sed#e625902539f5c29f1246228270a0330c1097b1e4", 
    "less-plugin-inline-urls": "^1.2.0"
  }
}"""

if os.name == 'nt':
    NPM_CMD = 'npm.cmd'
else:
    NPM_CMD = 'npm'


def generate_package_json(base_path):
    # generate package.json file here if not exists...
    package_json = os.path.join(base_path, 'package.json')
    if not os.path.exists(package_json):
        with open(package_json, 'w') as fi:
            fi.write(package_json_contents)


def generate_gruntfile(base_path, instance, site_id, compile_dir):
    if not instance:
        # look for it, get bin directory, search for plone instance
        bin_path = os.path.join(base_path, 'bin')
        files = os.listdir(bin_path)
        if 'instance' in files:
            instance = os.path.join(bin_path, 'instance')
        elif 'client1' in files:
            instance = os.path.join(bin_path, 'client1')
    if not instance:
        print("Could not find plone instance to run command against.")
        sys.exit()
    script_path = os.path.join(this_dir, '_generate_gruntfile.py')
    cmd = [instance, 'run', script_path]
    os.environ['SITE_ID'] = site_id
    os.environ['COMPILE_DIR'] = compile_dir
    print('Running command: %s' % ' '.join(cmd))
    subprocess.check_call(cmd, env=os.environ)
    print('Gruntfile generated.')


def main(argv=sys.argv):
    parser = argparse.ArgumentParser(
        description='Generate and setup Grunt infrastructure, '
                    'then compile JS/LESS bundles for Plone.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i',
        '--instance',
        dest='instance',
        help='path to instance executable. If not provided, '
             'will look in bin this was executed from for '
             'instance or client1'
    )
    parser.add_argument(
        '-s',
        '--site-id',
        dest='site_id',
        default='Plone',
        help='ID of the Plone site to fetch the configuration from. '
             'Used only while Gruntfile generation.'
    )
    parser.add_argument(
        '-b',
        '--bundle',
        dest='bundle',
        default='all',
        help='Name of bundle to compile. Used while compile step.'
    )
    parser.add_argument(
        '--compile-dir',
        dest='compile_dir',
        default='',
        help='Output directory for the compiled bundle files. '
             'Used only while Gruntfile generation. '
             'If not given the directory is looked up from Plone registry. '
    )
    parser.add_argument(
        '-d',
        '--base-dir',
        dest='base_dir',
        default='.',
        help='Base directory for this script '
             '(by default current working directory).'
    )
    parser.add_argument(
        '-G',
        '--skip-generate-gruntfile',
        dest='skip_gruntfile',
        action='store_true',
        help='Skip generation of Gruntfile.js'
    )
    parser.add_argument(
        '-I',
        '--skip-npm-install',
        dest='skip_npminstall',
        action='store_true',
        help='Skip npm install step',
    )
    parser.add_argument(
        '-C',
        '--skip-compile',
        dest='skip_compile',
        action='store_true',
        help='Skip compile step (running grunt)',
    )

    args = parser.parse_args()

    base_path = args.base_dir
    if base_path == '.':
        base_path = os.getcwd()

    # generates only if not already there
    generate_package_json(base_path)
    if not args.skip_npminstall:
        cmd = [NPM_CMD, 'install']
        print('Setup npm env')
        print('Running command: %s' % ' '.join(cmd))
        subprocess.check_call(cmd)

    # Generate Gruntfile
    grunt = os.path.join(
        base_path,
        'node_modules',
        'grunt-cli',
        'bin',
        'grunt'
    )
    if not args.skip_gruntfile:
        generate_gruntfile(
            base_path,
            args.instance,
            args.site_id,
            args.compile_dir
        )
    gruntfile = os.path.join(base_path, 'Gruntfile.js')
    if not os.path.exists(gruntfile):
        print(
            "Error, no Gruntfile.js generated at {0} where expected".format(
                gruntfile
            )
        )

    if not args.skip_compile:
        print('Compile {0}'.format(args.bundle))
        cmd = [
            grunt,
            '--gruntfile={0}'.format(gruntfile),
            'compile-{0}'.format(args.bundle)
        ]
        print('Running command: %s' % ' '.join(cmd))
        subprocess.check_call(cmd)

    print('Done.')

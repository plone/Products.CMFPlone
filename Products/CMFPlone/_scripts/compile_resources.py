import argparse
import os
import sys
from Products.CMFPlone._scripts import generate_gruntfile
import subprocess

parser = argparse.ArgumentParser(
    description='Compile plone bundle JS/LESS')
parser.add_argument('--site-id', dest='site_id',
                    default='Plone', help='ID for the plone site id')
parser.add_argument('--grunt', dest='grunt',
                    help='path to grunt executable. If not provided, '
                         'will look in path')
parser.add_argument('--instance', dest='instance',
                    help='path to instance executable. If not provided, '
                         'will look in bin this was executed from for '
                         'instance or client1')
parser.add_argument('--bundle', dest='bundle', default='all',
                    help='Name of bundle to compile. Defaults to all of them.')

this_dir = os.path.dirname(os.path.realpath(__file__))


package_json_contents = """{
  "name": "gruntrunner",
  "version": "1.0.0",
  "private": true,
  "devDependencies": {
    "grunt": "~0.4.4",
    "grunt-contrib-less": "^1.0.0",
    "less-plugin-inline-urls": "^1.1.0",
    "grunt-contrib-requirejs": "~0.4.3",
    "grunt-contrib-uglify": "",
    "grunt-contrib-watch": "~0.5.3",
    "grunt-sed": "",
    "grunt-debug-task": "~0.1.5"
  }
}"""


def main(argv=sys.argv):
    args = parser.parse_args()

    grunt = args.grunt

    if not grunt:
        if 'PATH' in os.environ:
            path = os.environ['PATH']
            path = path.split(os.pathsep)
        else:
            path = ['/bin', '/usr/bin', '/usr/local/bin']

        for directory in path:
            fullname = os.path.join(directory, 'grunt')
            if os.path.exists(fullname):
                grunt = fullname
                break

    if not grunt:
        print('Error: no grunt executable found. Exiting')
        sys.exit(0)

    generate_gruntfile.main(args)

    # XXX is this a good way to do it?
    base_path = os.path.sep.join(
        os.path.abspath(sys.argv[0]).split(os.path.sep)[:-2])
    gruntfile = os.path.join(base_path, 'Gruntfile.js')

    if not os.path.exists(gruntfile):
        print("Error, no Gruntfile.js generated at %s where expected" % gruntfile)

    # generate package.json file here if not exists...
    package_json = os.path.join(base_path, 'package.json')
    if not os.path.exists(package_json):
        fi = open(package_json, 'w')
        fi.write(package_json_contents)
        fi.close()

    cmd = ['npm', 'install']
    print('Setup npm env')
    print('Running command: %s' % ' '.join(cmd))
    subprocess.check_call(cmd)

    cmd = [grunt, '--gruntfile=%s' % gruntfile, 'compile-%s' % args.bundle]
    print('Running command: %s' % ' '.join(cmd))
    subprocess.check_call(cmd)

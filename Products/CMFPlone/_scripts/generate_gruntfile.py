#
# This is more of a script runner for the _generate_gruntfile.py
# script. Just a wrapper so that script can be simply called
# from the bin directory
import os
import argparse
import sys
import subprocess

parser = argparse.ArgumentParser(
    description='Generate Gruntfile.js from Plone site')
parser.add_argument('--site-id', dest='site_id',
                    default='Plone', help='ID for the plone site id')
parser.add_argument('--instance', dest='instance',
                    help='path to instance executable. If not provided, '
                         'will look in bin this was executed from for '
                         'instance or client1')

this_dir = os.path.dirname(os.path.realpath(__file__))


def main(argv=sys.argv):
    args, _ = parser.parse_known_args()
    instance = args.instance
    if not instance:
        # look for it, get bin directory, search for plone instance
        bin_path = os.path.sep.join(
            os.path.abspath(sys.argv[0]).split(os.path.sep)[:-1])
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
    os.environ['SITE_ID'] = args.site_id

    print('Running command: %s' % ' '.join(cmd))
    subprocess.check_call(cmd, env=os.environ)

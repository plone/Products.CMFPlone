# -*- coding: utf-8 -*-
from collections import Counter
from Zope2.Startup.run import make_wsgi_app
from ZODB.interfaces import IStorageCurrentRecordIteration
from ZODB.serialize import PersistentUnpickler

import argparse
import io
import logging
import pdb
import pickletools
import sys
import traceback
import Zope2

logger = logging.getLogger('zodbverify')


def zopectl_entry(self, arg):
    parser = argparse.ArgumentParser(
        prog=sys.argv[0] + ' verifydb',
        description='Verifies that all records in the database can be loaded.',
    )
    parser.add_argument(
        '-D', '--debug', action='store_true', dest='debug',
        help='pause to debug broken pickles')
    options = parser.parse_args(arg.split(' ') if arg else [])

    logging.basicConfig(level=logging.INFO)
    make_wsgi_app({}, self.options.configfile)
    app = Zope2.app()
    verify_zodb(app, debug=options.debug)


def verify_zodb(obj, debug=False):
    storage = obj._p_jar._db._storage
    if not IStorageCurrentRecordIteration.providedBy(storage):
        raise TypeError(
            'ZODB storage {} does not implement record_iternext'.format(
                storage))

    logger.info('Scanning ZODB...')

    next_ = None
    count = 0
    errors = 0
    issues = []
    while True:
        count += 1
        oid, tid, data, next_ = storage.record_iternext(next_)
        logger.debug('Verifying {}'.format(oid))
        success, msg = verify_record(oid, data, debug)
        if not success:
            errors += 1
            issues.append(msg)
        if next_ is None:
            break

    issues = dict(Counter(sorted(issues)))
    msg = ''
    for value, amount in issues.items():
        msg += '{}: {}\n'.format(value, amount)

    logger.info(
        'Done! Scanned {} records. \n'
        'Found {} records that could not be loaded. \n'
        'Exceptions and how often they happened: \n'
        '{}'.format(count, errors, msg)
    )


def verify_record(oid, data, debug=False):
    input_file = io.BytesIO(data)
    unpickler = PersistentUnpickler(None, persistent_load, input_file)
    class_info = 'unknown'
    pos = None
    try:
        class_info = unpickler.load()
        pos = input_file.tell()
        unpickler.load()
    except Exception as e:
        input_file.seek(0)
        pickle = input_file.read()
        logger.info('\nCould not process {} record {}:'.format(
            class_info,
            repr(oid),
        ))
        logger.info(repr(pickle))
        logger.info(traceback.format_exc())
        if debug and pos is not None:
            try:
                pickletools.dis(pickle[pos:])
            except Exception:
                # ignore exceptions while disassembling the pickle since the
                # real issue is that it references a unavailable module
                pass
            finally:
                pdb.set_trace()
        elif debug and pos is None:
            pdb.set_trace()
        # The same issues should have the same msg
        msg = '{}: {}'.format(e.__class__.__name__, str(e))
        return False, msg
    return True, None


def persistent_load(ref):
    pass

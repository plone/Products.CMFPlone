# -*- coding: utf-8 -*-
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
    while True:
        count += 1
        oid, tid, data, next_ = storage.record_iternext(next_)
        logger.debug('Verifying {}'.format(oid))
        success = verify_record(oid, data, debug)
        if not success:
            errors += 1
        if next_ is None:
            break

    logger.info(
        'Done! Scanned {} records. '
        'Found {} records that could not be loaded.'.format(
            count, errors)
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
    except Exception:
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
                logger.info(traceback.format_exc())
            finally:
                pdb.set_trace()
        elif debug and pos is None:
            pdb.set_trace()
        return False
    return True


def persistent_load(ref):
    pass

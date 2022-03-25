from collections import Counter
from collections import defaultdict
from five.intid.intid import addIntIdSubscriber
from plone.app.linkintegrity.handlers import modifiedContent
from plone.app.linkintegrity.utils import referencedRelationship
from plone.app.relationfield.event import update_behavior_relations
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemataForType
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone import PloneMessageFactory as _
from z3c.relationfield import event
from z3c.relationfield import RelationValue
from z3c.relationfield.event import updateRelations
from z3c.relationfield.schema import Relation
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zc.relation.interfaces import ICatalog
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.intid.interfaces import IIntIds
from zope.intid.interfaces import ObjectMissingError

import logging
import pkg_resources

try:
    # "iterate" is not a dependency of CMFPlone, but a consumer of it
    pkg_resources.get_distribution("plone.app.iterate")
except pkg_resources.DistributionNotFound:
    HAS_ITERATE = False
else:
    HAS_ITERATE = True
    from plone.app.iterate.dexterity import ITERATE_RELATION_NAME
    from plone.app.iterate.dexterity.relation import StagingRelationValue


logger = logging.getLogger(__name__)

RELATIONS_KEY = 'ALL_REFERENCES'


def rebuild_relations(context=None, flush_and_rebuild_intids=False):
    store_relations()
    purge_relations()
    if flush_and_rebuild_intids:
        flush_intids()
        rebuild_intids()
    else:
        cleanup_intids()
    restore_relations()


def get_relations_stats():
    info = defaultdict(int)
    broken = defaultdict(int)
    relation_catalog = getUtility(ICatalog)
    for token in relation_catalog.findRelationTokens():
        try:
            rel = relation_catalog.resolveRelationToken(token)
        except ObjectMissingError:
            broken['Object is missing'] += 1
            logger.info('Token {} has no object.'.format(token))
            continue

        if rel.isBroken():
            broken[rel.from_attribute] += 1
        else:
            info[rel.from_attribute] += 1
    return info, broken


def get_all_relations():
    """Get all data from zc.relation catalog.
    Logs some useful statistics.
    """
    results = []
    info = defaultdict(int)

    relation_catalog = getUtility(ICatalog)
    for token in relation_catalog.findRelationTokens():
        try:
            rel = relation_catalog.resolveRelationToken(token)
        except ObjectMissingError:
            logger.info('Token {} has no object.'.format(token))
            continue

        if rel.from_object and rel.to_object:
            try:
                results.append({
                    'from_uuid': rel.from_object.UID(),
                    'to_uuid': rel.to_object.UID(),
                    'from_attribute': rel.from_attribute,
                })
                info[rel.from_attribute] += 1
            except AttributeError as ex:
                logger.info(f'Something went wrong while storing {rel}: \n {ex}')
        else:
            logger.info(f'Dropping relation {rel.from_attribute} from {rel.from_object} to {rel.to_object}')
    msg = ''
    for key, value in info.items():
        msg += f'{key}: {value}\n'
    logger.info(f'\nFound the following relations:\n{msg}')
    return results


def store_relations(context=None):
    """Store all relations in a annotation on the portal.
    """
    all_relations = get_all_relations()
    portal = getSite()
    IAnnotations(portal)[RELATIONS_KEY] = all_relations
    logger.info(f'Stored {len(all_relations)} relations on the portal')


def purge_relations(context=None):
    """Removes all entries form zc.relation catalog.
    RelationValues that were set as attribute on content are still there!
    These are removed/overwritten when restoring the relations.
    """
    rel_catalog = getUtility(ICatalog)
    rel_catalog.clear()
    logger.info('Purged zc.relation catalog')


def restore_relations(context=None, all_relations=None):
    """Restore relations from a annotation on the portal.
    """

    portal = getSite()
    if all_relations is None:
        all_relations = IAnnotations(portal)[RELATIONS_KEY]
    logger.info(f'Loaded {len(all_relations)} relations to restore')
    update_linkintegrity = set()
    modified_items = set()
    modified_relation_lists = defaultdict(list)

    # remove duplicates but keep original order
    unique_relations = []
    seen = set()
    seen_add = seen.add
    for rel in all_relations:
        hashable = tuple(rel.items())
        if hashable not in seen:
            unique_relations.append(rel)
            seen_add(hashable)
        else:
            logger.info(f'Dropping duplicate: {hashable}')

    if len(unique_relations) < len(all_relations):
        logger.info(f'Dropping {len(all_relations) - len(unique_relations)} duplicates')
        all_relations = unique_relations

    intids = getUtility(IIntIds)
    for index, item in enumerate(all_relations, start=1):
        if not index % 500:
            logger.info(f'Restored {index} of {len(all_relations)} relations...')

        try:
            source_obj = uuidToObject(item['from_uuid'])
        except KeyError:
            # brain exists but no object
            source_obj = None
        try:
            target_obj = uuidToObject(item['to_uuid'])
        except KeyError:
            # brain exists but no object
            target_obj = None

        if not source_obj:
            logger.info(f'{item["from_uuid"]} is missing')
            continue

        if not target_obj:
            logger.info(f'{item["to_uuid"]} is missing')
            continue

        if not IDexterityContent.providedBy(source_obj):
            logger.info(f'{source_obj} is no dexterity content')
            continue

        if not IDexterityContent.providedBy(target_obj):
            logger.info(f'{target_obj} is no dexterity content')
            continue

        from_attribute = item['from_attribute']
        try:
            to_id = intids.getId(target_obj)
        except KeyError as e:
            logger.warning(f'No intid for {target_obj}')
            continue

        if from_attribute == referencedRelationship:
            # Ignore linkintegrity for now. We'll rebuilt it at the end!
            update_linkintegrity.add(item['from_uuid'])
            continue

        if HAS_ITERATE and from_attribute == ITERATE_RELATION_NAME:
            # Iterate relations are not set as values of fields
            relation = StagingRelationValue(to_id)
            event._setRelation(source_obj, ITERATE_RELATION_NAME, relation)
            continue

        field_and_schema = get_field_and_schema_for_fieldname(from_attribute, source_obj.portal_type)
        if field_and_schema is None:
            # the from_attribute is no field
            logger.info(f'No field. Setting relation: {item}')
            event._setRelation(source_obj, from_attribute, RelationValue(to_id))
            continue

        field, schema = field_and_schema
        relation = RelationValue(to_id)

        if isinstance(field, RelationList):
            logger.info(f'Add relation to relationslist {from_attribute} from {source_obj.absolute_url()} to {target_obj.absolute_url()}')
            if item['from_uuid'] in modified_relation_lists.get(from_attribute, []):
                # Do not purge relations
                existing_relations = getattr(source_obj, from_attribute, [])
            else:
                # First touch. Make sure we purge!
                existing_relations = []
            existing_relations.append(relation)
            setattr(source_obj, from_attribute, existing_relations)
            modified_items.add(item['from_uuid'])
            modified_relation_lists[from_attribute].append(item['from_uuid'])
            continue

        elif isinstance(field, (Relation, RelationChoice)):
            logger.info(f'Add relation {from_attribute} from {source_obj.absolute_url()} to {target_obj.absolute_url()}')
            setattr(source_obj, from_attribute, relation)
            modified_items.add(item['from_uuid'])
            continue

        else:
            # we should never end up here!
            logger.warn(f'Unexpected relation {from_attribute} from {source_obj.absolute_url()} to {target_obj.absolute_url()}')

    update_linkintegrity = set(update_linkintegrity)
    logger.info(f'Updating linkintegrity for {len(update_linkintegrity)} items')
    for uuid in sorted(update_linkintegrity):
        modifiedContent(uuidToObject(uuid), None)
    logger.info(f'Updating relations for {len(modified_items)} items')
    for uuid in sorted(modified_items):
        obj = uuidToObject(uuid)
        # updateRelations from z3c.relationfield does not properly update relations in behaviors
        # that are registered with a marker-interface.
        # update_behavior_relations (from plone.app.relationfield) does that but does not update
        # those in the main schema. Duh!
        updateRelations(obj, None)
        update_behavior_relations(obj, None)

    # purge annotation from portal if they exist
    if RELATIONS_KEY in IAnnotations(portal):
        del IAnnotations(portal)[RELATIONS_KEY]
    logger.info('Done!')


def get_intid(obj):
    """Intid from intid-catalog"""
    intids = queryUtility(IIntIds)
    if intids is None:
        return
    # check that the object has an intid, otherwise there's nothing to be done
    try:
        return intids.getId(obj)
    except KeyError:  # noqa
        # The object has not been added to the ZODB yet
        return


def get_field_and_schema_for_fieldname(field_id, portal_type):
    """Get field and its schema from a portal_type.
    """
    # Turn form.widgets.IDublinCore.title into title
    field_id = field_id.split('.')[-1]
    for schema in iterSchemataForType(portal_type):
        field = schema.get(field_id, None)
        if field is not None:
            return (field, schema)


def cleanup_intids(context=None):
    intids = getUtility(IIntIds)
    all_refs = [f'{i.object.__class__.__module__}.{i.object.__class__.__name__}'
                for i in intids.refs.values()]
    logger.info(Counter(all_refs))

    count = 0
    refs = [i for i in intids.refs.values() if isinstance(i.object, RelationValue)]
    for ref in refs:
        intids.unregister(ref)
        count += 1
    logger.info(f'Removed all {count} RelationValues from IntId-tool')

    count = 0
    for ref in intids.refs.values():
        if 'broken' in repr(ref.object):
            intids.unregister(ref)
    logger.info(f'Removed {count} broken refs from IntId-tool')
    all_refs = ['{i.object.__class__.__module__}.{i.object.__class__.__name__}'
                for i in intids.refs.values()]
    logger.info(Counter(all_refs))


def flush_intids():
    """ Flush all intids
    """
    intids = getUtility(IIntIds)
    intids.ids = intids.family.OI.BTree()
    intids.refs = intids.family.IO.BTree()


def rebuild_intids():
    """ Create new intids
    """
    def add_to_intids(obj, path):
        if IContentish.providedBy(obj):
            logger.info(f'Added {obj} at {path} to intid')
            addIntIdSubscriber(obj, None)
    portal = getSite()
    portal.ZopeFindAndApply(portal,
                            search_sub=True,
                            apply_func=add_to_intids)

# -*- coding: UTF-8 -*-
from AccessControl.SecurityManagement import getSecurityManager
from collections import Counter
from collections import defaultdict
from five.intid.intid import addIntIdSubscriber
from plone import api
from plone.app.iterate.dexterity import ITERATE_RELATION_NAME
from plone.app.iterate.dexterity.relation import StagingRelationValue
from plone.app.linkintegrity.handlers import modifiedContent
from plone.app.linkintegrity.utils import referencedRelationship
from plone.app.relationfield.event import update_behavior_relations
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import iterSchemataForType
from Products.CMFCore.interfaces import IContentish
from Products.Five.browser import BrowserView
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
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import modified

import json
import logging

logger = logging.getLogger(__name__)

RELATIONS_KEY = 'ALL_REFERENCES'


class RelationsRebuildControlpanel(BrowserView):

    def __call__(self, rebuild=False, flush_and_rebuild_intids=False):
        self.done = False
        if rebuild:
            rebuild_relations(flush_and_rebuild_intids=flush_and_rebuild_intids)
            self.done = True
            api.portal.show_message(u'Finished! See log for details.', self.request)

        self.relations_stats = get_relations_stats()
        return self.index()


class RelationsInspectControlpanel(BrowserView):

    def __call__(self, relation=None, inspect_backrelation=False):
        self.relation = relation or self.request.get('relation')
        self.inspect_backrelation = inspect_backrelation or self.request.get('inspect_backrelation')

        self.relations = []
        self.relations_stats = get_relations_stats()
        view_action = api.portal.get_registry_record('plone.types_use_view_action_in_listings')

        if not self.relation:
            api.portal.show_message(u'Please select a relation', self.request)
            return self.index()

        intids = queryUtility(IIntIds)
        relation_catalog = getUtility(ICatalog)
        query = {'from_attribute': self.relation}
        info = defaultdict(list)

        # relations: column_1 = source, column_2 = target(s)
        # backrelation: column_1 = target, column_2 source(s)
        for rel in relation_catalog.findRelations(query):
            if self.inspect_backrelation:
                info[rel.to_id].append(rel.from_id)
            else:
                info[rel.from_id].append(rel.to_id)

        for column_1_intid in info:
            obj = intids.getObject(column_1_intid)
            use_view_action = obj.portal_type in view_action
            url = obj.absolute_url() + '/view' if use_view_action else obj.absolute_url()
            item = {}
            item['column_1'] = {
                'title': obj.title,
                'url': url,
                'portal_type': obj.portal_type,
            }
            item['column_2'] = []
            for column_2_intid in info[column_1_intid]:
                obj = intids.getObject(column_2_intid)
                use_view_action = obj.portal_type in view_action
                url = obj.absolute_url() + '/view' if use_view_action else obj.absolute_url()
                item['column_2'].append({
                    'title': obj.title,
                    'url': url,
                    'portal_type': obj.portal_type,
                    })
            self.relations.append(item)

        return self.index()


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
    relation_catalog = getUtility(ICatalog)
    for rel in relation_catalog.findRelations():
        if rel.isBroken():
            info[rel.from_attribute + ' (broken)'] += 1
        else:
            info[rel.from_attribute] += 1
    return info


def get_all_relations():
    """Get all data from zc.relation catalog.
    Logs some useful statistics.
    """
    results = []
    info = defaultdict(int)

    relation_catalog = getUtility(ICatalog)
    for rel in relation_catalog.findRelations():
        if rel.from_object and rel.to_object:
            try:
                results.append({
                    'from_uuid': rel.from_object.UID(),
                    'to_uuid': rel.to_object.UID(),
                    'from_attribute': rel.from_attribute,
                })
                info[rel.from_attribute] += 1
            except AttributeError as ex:
                logger.info(u'Something went wrong while storing {0}: \n {1}'.format(rel, ex))
        else:
            logger.info(u'Dropping relation {} from {} to {}'.format(rel.from_attribute, rel.from_object, rel.to_object))
    msg = ''
    for k, v in info.items():
        msg += u'{}: {}\n'.format(k, v)
    logger.info(u'\nFound the following relations:\n{}'.format(msg))
    return results


def store_relations(context=None):
    """Store all relations in a annotation on the portal.
    """
    all_relations = get_all_relations()
    portal = api.portal.get()
    IAnnotations(portal)[RELATIONS_KEY] = all_relations
    logger.info('Stored {0} relations on the portal'.format(
        len(all_relations))
    )


def export_relations(context=None):
    """Store all relations in a annotation on the portal.
    """
    all_relations = get_all_relations()
    with open('all_relations.json', 'w') as f:
        json.dump(all_relations, f)
        logger.info('Stored {0} relations as all_relations.json'.format(
            len(all_relations))
        )


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

    portal = api.portal.get()
    if all_relations is None:
        all_relations = IAnnotations(portal)[RELATIONS_KEY]
    logger.info('Loaded {0} relations to restore'.format(
        len(all_relations))
    )
    update_linkintegrity = set()
    modified_items = set()
    modified_relation_lists = defaultdict(list)

    # remove duplicates but keep original order
    unique_relations = []
    seen = set()
    seen_add = seen.add
    for i in all_relations:
        hashable = tuple(i.items())
        if hashable not in seen:
            unique_relations.append(i)
            seen_add(hashable)
        else:
            logger.info(u'Dropping duplicate: {}'.format(hashable))

    if len(unique_relations) < len(all_relations):
        logger.info('Dropping {0} duplicates'.format(
            len(all_relations) - len(unique_relations)))
        all_relations = unique_relations

    intids = getUtility(IIntIds)
    for index, item in enumerate(all_relations, start=1):
        if not index % 500:
            logger.info(u'Restored {} of {} relations...'.format(index, len(all_relations)))
        source_obj = uuidToObject(item['from_uuid'])
        target_obj = uuidToObject(item['to_uuid'])

        if not source_obj:
            logger.info(u'{} is missing'.format(item['from_uuid']))
            continue

        if not target_obj:
            logger.info(u'{} is missing'.format(item['to_uuid']))
            continue

        if not IDexterityContent.providedBy(source_obj):
            logger.info(u'{} is no dexterity content'.format(source_obj.portal_type))
            continue

        if not IDexterityContent.providedBy(target_obj):
            logger.info(u'{} is no dexterity content'.format(target_obj.portal_type))
            continue

        from_attribute = item['from_attribute']
        to_id = intids.getId(target_obj)

        if from_attribute == referencedRelationship:
            # Ignore linkintegrity for now. We'll rebuilt it at the end!
            update_linkintegrity.add(item['from_uuid'])
            continue

        if from_attribute == ITERATE_RELATION_NAME:
            # Iterate relations are not set as values of fields
            relation = StagingRelationValue(to_id)
            event._setRelation(source_obj, ITERATE_RELATION_NAME, relation)
            continue

        fti = getUtility(IDexterityFTI, name=source_obj.portal_type)
        field_and_schema = get_field_and_schema_for_fieldname(from_attribute, fti)
        if field_and_schema is None:
            # the from_attribute is no field
            # we could either create a fresh relation or log the case
            logger.info(u'No field. Setting relation: {}'.format(item))
            event._setRelation(source_obj, from_attribute, RelationValue(to_id))
            continue

        field, schema = field_and_schema
        relation = RelationValue(to_id)

        if isinstance(field, RelationList):
            logger.info('Add relation to relationslist {} from {} to {}'.format(
                from_attribute, source_obj.absolute_url(), target_obj.absolute_url()))
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
            logger.info('Add relation {} from {} to {}'.format(
                from_attribute, source_obj.absolute_url(), target_obj.absolute_url()))
            setattr(source_obj, from_attribute, relation)
            modified_items.add(item['from_uuid'])
            continue

        else:
            # we should never end up here!
            logger.info('Warning: Unexpected relation {} from {} to {}'.format(
                from_attribute, source_obj.absolute_url(), target_obj.absolute_url()))

    update_linkintegrity = set(update_linkintegrity)
    logger.info('Updating linkintegrity for {} items'.format(len(update_linkintegrity)))
    for uuid in sorted(update_linkintegrity):
        modifiedContent(uuidToObject(uuid), None)
    logger.info('Updating relations for {} items'.format(len(modified_items)))
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


def link_objects(source, target, relationship):
    """Create a relation from source to target using zc.relation

    For RelationChoice or RelationList it will add the relation as attribute.
    Other relations they will only be added to the relation-catalog.
    """
    if not IDexterityContent.providedBy(source):
        logger.info(u'{} is no dexterity content'.format(source.portal_type))
        return

    if not IDexterityContent.providedBy(target):
        logger.info(u'{} is no dexterity content'.format(target.portal_type))
        return

    relation_catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    to_id = intids.getId(target)
    from_id = intids.getId(source)
    from_attribute = relationship

    # Check if there is exactly this relation.
    # If so remove it and create a fresh one.
    query = {
        'from_attribute': from_attribute,
        'from_id': from_id,
        'to_id': to_id,
    }
    for rel in relation_catalog.findRelations(query):
        relation_catalog.unindex(rel)

    if from_attribute == referencedRelationship:
        # Don't mess with linkintegrity-relations!
        # Refresh them by triggering this subscriber.
        modifiedContent(source, None)
        return

    if from_attribute == ITERATE_RELATION_NAME:
        # Iterate relations use a subclass of RelationValue
        relation = StagingRelationValue(to_id)
        event._setRelation(source, ITERATE_RELATION_NAME, relation)
        return

    fti = queryUtility(IDexterityFTI, name=source.portal_type)
    if not fti:
        logger.info(u'{} is no dexterity content'.format(source.portal_type))
        return
    field_and_schema = get_field_and_schema_for_fieldname(from_attribute, fti)

    if field_and_schema is None:
        # The relationship is not the name of a field. Only create a relation.
        logger.info(u'No field. Setting relation {} from {} to {}'.format(
            source.absolute_url(), target.absolute_url(), relationship))
        event._setRelation(source, from_attribute, RelationValue(to_id))
        return

    field, schema = field_and_schema

    if isinstance(field, RelationList):
        logger.info('Add relation to relationlist {} from {} to {}'.format(
            from_attribute, source.absolute_url(), target.absolute_url()))
        existing_relations = getattr(source, from_attribute, [])
        existing_relations.append(RelationValue(to_id))
        setattr(source, from_attribute, existing_relations)
        modified(source)
        return

    elif isinstance(field, (Relation, RelationChoice)):
        logger.info('Add relation {} from {} to {}'.format(
            from_attribute, source.absolute_url(), target.absolute_url()))
        setattr(source, from_attribute, RelationValue(to_id))
        modified(source)
        return

    # We should never end up here!
    logger.info('Warning: Unexpected relation {} from {} to {}'.format(
        from_attribute, source.absolute_url(), target.absolute_url()))


# Main API method

def get_relations(obj, attribute=None, backrels=False, restricted=True, as_dict=False):
    """Get specific relations or backrelations for a content object
    """
    if not IDexterityContent.providedBy(obj):
        logger.info(u'{} is no dexterity content'.format(obj))
        return

    results = []
    if as_dict:
        results = defaultdict(list)
    int_id = get_intid(obj)
    if not int_id:
        return results

    relation_catalog = getUtility(ICatalog)
    if not relation_catalog:
        return results

    query = {}
    if backrels:
        query['to_id'] = int_id
    else:
        query['from_id'] = int_id

    if restricted:
        checkPermission = getSecurityManager().checkPermission

    if attribute and isinstance(attribute, (list, tuple)):
        # The relation-catalog does not support queries for multiple from_attributes
        # We make multiple queries to support this use-case.
        relations = []
        for from_attribute in attribute:
            query['from_attribute'] = from_attribute
            relations.extend(relation_catalog.findRelations(query))
    elif attribute:
        # query with one attribute
        query['from_attribute'] = attribute
        relations = relation_catalog.findRelations(query)
    else:
        # query without constraint on a attribute
        relations = relation_catalog.findRelations(query)

    for relation in relations:
        if relation.isBroken():
            continue

        if backrels:
            obj = relation.from_object
        else:
            obj = relation.to_object

        if as_dict:
            if restricted:
                if checkPermission('View', obj):
                    results[relation.from_attribute].append(obj)
                else:
                    results[relation.from_attribute].append(None)
            else:
                results[relation.from_attribute].append(obj)
        else:
            if restricted:
                if checkPermission('View', obj):
                    results.append(obj)
            else:
                results.append(obj)
    return results


# Convenience API

def relations(obj, attribute=None, as_dict=False):
    """Get related objects"""
    return get_relations(obj, attribute=attribute, restricted=True, as_dict=as_dict)


def unrestricted_relations(obj, attribute=None, as_dict=False):
    """Get related objects without permission check"""
    return get_relations(obj, attribute=attribute, restricted=False, as_dict=as_dict)


def backrelations(obj, attribute=None, as_dict=False):
    """Get objects with a relation to this object."""
    return get_relations(obj, attribute=attribute, backrels=True, restricted=True, as_dict=as_dict)


def unrestricted_backrelations(obj, attribute=None, as_dict=False):
    """Get objects with a relation to this object without permission check"""
    return get_relations(obj, attribute=attribute, backrels=True, restricted=False, as_dict=as_dict)


# Convenience api to deal with relationchoice

def relation(obj, attribute, restricted=True):
    """Get related object.
    Only valid if the attribute is the name of a relationChoice field on the object.
    """
    if not attribute:
        raise RuntimeError(u'Missing parameter "attribute"')

    check_for_relationchoice(obj, attribute)
    items = get_relations(obj, attribute=attribute, restricted=restricted)
    if items:
        return items[0]


def unrestricted_relation(obj, attribute):
    """Get related object without permission checks.
    Only valid if the attribute is the name of a relationChoice field on the object.
    """
    return relation(obj, attribute=attribute, restricted=False)


def backrelation(obj, attribute, restricted=True):
    """Get relating object.
    This makes sense when only one item has a relation of this type to obj.
    One example is parent -> child where only one parent can exist.
    """
    if not attribute:
        raise RuntimeError(u'Missing parameter "attribute"')

    items = get_relations(obj, attribute=attribute, backrels=True, restricted=restricted)
    if len(items) > 1:
        raise RuntimeError(u'Multiple incoming relations of type {}.'.format(attribute))

    if items:
        source_obj = items[0]
        check_for_relationchoice(source_obj, attribute)
        return source_obj


def unrestricted_backrelation(obj, attribute):
    """Get relating object without permission checks.
    This makes sense when only one item has a relation of this type to obj.
    One example is parent -> child where only one parent can exist.
    """
    return backrelation(obj, attribute, restricted=False)


def check_for_relationchoice(obj, attribute):
    """Raise a exception if the attribute is no RelationChoice field for the object.
    """
    fti = getUtility(IDexterityFTI, name=obj.portal_type)
    field_and_schema = get_field_and_schema_for_fieldname(attribute, fti)
    if field_and_schema is None:
        # No field found
        raise RuntimeError(u'{} is no field on {}.'.format(
            attribute, obj.portal_type))
    field, schema = field_and_schema
    if not isinstance(field, (Relation, RelationChoice)):
        # No RelationChoice field found
        raise RuntimeError(u'{} is no RelationChoice field for {}.'.format(
            attribute, obj.portal_type))


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


def get_field_and_schema_for_fieldname(field_id, fti):
    """Get field and its schema from a fti.
    """
    # Turn form.widgets.IDublinCore.title into title
    field_id = field_id.split('.')[-1]
    for schema in iterSchemataForType(fti):
        field = schema.get(field_id, None)
        if field is not None:
            return (field, schema)


def cleanup_intids(context=None):
    intids = getUtility(IIntIds)
    all_refs = ['{}.{}'.format(i.object.__class__.__module__, i.object.__class__.__name__)
                for i in intids.refs.values()]
    logger.info(Counter(all_refs))

    count = 0
    refs = [i for i in intids.refs.values() if isinstance(i.object, RelationValue)]
    for ref in refs:
        intids.unregister(ref)
        count += 1
    logger.info('Removed all {} RelationValues from IntId-tool'.format(count))

    count = 0
    for ref in intids.refs.values():
        if 'broken' in repr(ref.object):
            intids.unregister(ref)
    logger.info('Removed {} broken refs from IntId-tool'.format(count))
    all_refs = ['{}.{}'.format(i.object.__class__.__module__, i.object.__class__.__name__)
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
            logger.info('Added {0} at {1} to intid'.format(obj, path))
            addIntIdSubscriber(obj, None)
    portal = api.portal.get()
    portal.ZopeFindAndApply(portal,
                            search_sub=True,
                            apply_func=add_to_intids)

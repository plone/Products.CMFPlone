from collections import Counter
from collections import defaultdict
from collections import OrderedDict
from five.intid.intid import addIntIdSubscriber
from plone.app.linkintegrity.handlers import modifiedContent
from plone.app.linkintegrity.utils import referencedRelationship
from plone.app.relationfield.event import update_behavior_relations
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemataForType
from Products.CMFCore.interfaces import IContentish
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

RELATIONS_KEY = "ALL_REFERENCES"


def rebuild_relations(context=None, flush_and_rebuild_intids=False):
    store_relations()
    purge_relations()
    if flush_and_rebuild_intids:
        flush_intids()
        rebuild_intids()
    else:
        cleanup_intids()
    restore_relations()
    log_relations()


def get_relations_stats():
    info = defaultdict(int)
    broken = defaultdict(int)
    relation_catalog = getUtility(ICatalog)
    for token in relation_catalog.findRelationTokens():
        try:
            rel = relation_catalog.resolveRelationToken(token)
        except ObjectMissingError:
            broken["Object is missing"] += 1
            logger.warning(f"Token {token} has no object.")
            continue

        if rel.isBroken():
            broken[rel.from_attribute] += 1
        else:
            info[rel.from_attribute] += 1
    return info, broken


def get_all_relations():
    """Get relations from zc.relation catalog.

    Log statistics.
    Return list of dictionaries:
        from_uuid: source UID if available else None
        to_uuid: target UID if available else None
        from_attribute: relation name
    """
    results = []
    info = defaultdict(int)

    relation_catalog = getUtility(ICatalog)
    for token in relation_catalog.findRelationTokens():
        try:
            rel = relation_catalog.resolveRelationToken(token)
        except ObjectMissingError:
            logger.warning(f"No relation for relation token '{token}'.")
            continue

        rel_uid_info = OrderedDict()
        rel_uid_info["from_attribute"] = rel.from_attribute
        try:
            rel_uid_info["from_uuid"] = (
                rel.from_object.UID() if rel.from_object else None
            )
        except AttributeError as e:
            rel_uid_info["from_uuid"] = None
            logger.warning(f"Broken relation: {rel_uid_info} '{str(e)}'")
        try:
            rel_uid_info["to_uuid"] = rel.to_object.UID() if rel.to_object else None
        except AttributeError as e:
            rel_uid_info["to_uuid"] = None
            logger.warning(f"Broken relation: {rel_uid_info} '{str(e)}'")
        info[rel.from_attribute] += 1
        results.append(rel_uid_info)

    # Log stats
    msg = ""
    for key, value in info.items():
        msg += f"{key}: {value}\n"
    logger.info(f"\nFound the following relations:\n{msg}")
    return results


def store_relations(context=None):
    """Store all relations in a annotation on the portal."""
    all_relations = get_all_relations()
    portal = getSite()
    IAnnotations(portal)[RELATIONS_KEY] = all_relations


def purge_relations(context=None):
    """Removes all entries form zc.relation catalog.

    RelationValues that were set as attribute on content are still there!
    These are removed/overwritten when restoring the relations.
    """
    relation_catalog = getUtility(ICatalog)
    relation_catalog.clear()
    logger.info("zc.relation catalog purged.")


def restore_relations(context=None, all_relations=None):
    """Restore relations from an annotation on the portal."""

    portal = getSite()
    if all_relations is None:
        all_relations = IAnnotations(portal)[RELATIONS_KEY]
    logger.info(f"Loaded {len(all_relations)} relations to restore.")
    update_linkintegrity = set()
    modified_items = set()
    modified_relation_lists = defaultdict(list)

    # Remove duplicates but keep original order.
    unique_relations = []
    seen = set()
    for rel in all_relations:
        hashable = tuple(rel.items())
        if hashable not in seen:
            unique_relations.append(rel)
            seen.add(hashable)
        else:
            logger.info(f"Dropping duplicate: {hashable}")

    if len(unique_relations) < len(all_relations):
        logger.info(f"Dropping {len(all_relations) - len(unique_relations)} duplicates")

    # Update relations.
    intids = getUtility(IIntIds)
    new_index = 0
    for index, item in enumerate(unique_relations, start=1):
        # Get source object for UID. Skip relation if no object found.
        if item["from_uuid"] is None:
            logger.warning(f"No source object. {tuple(item.items())}.")
            continue
        else:
            try:
                source_obj = uuidToObject(item["from_uuid"])
            except KeyError:
                # brain exists but no object
                source_obj = None

        # Get target object of UID. Do not skip relation, but update source_obj below.
        if item["to_uuid"] is None:
            target_obj = None
        else:
            try:
                target_obj = uuidToObject(item["to_uuid"])
            except KeyError:
                # brain exists but no object
                target_obj = None
        if target_obj is None:
            logger.warning(f"No target object. {tuple(item.items())}")
            # The source_obj will be updated to remove the broken relation below.

        # source_obj and target_obj are dexterity content types.
        if not IDexterityContent.providedBy(source_obj):
            logger.warning(f"Source {source_obj} is no dexterity content.")
            continue
        if not IDexterityContent.providedBy(target_obj):
            logger.warning(f"Target {target_obj} is no dexterity content.")

        # Get intId for target_obj.
        try:
            to_id = intids.getId(target_obj)
        except KeyError:
            logger.warning(f"No intId for {target_obj}")
            to_id = None

        # Postpone linkintegrity check.
        from_attribute = item["from_attribute"]
        if from_attribute == referencedRelationship:
            update_linkintegrity.add(item["from_uuid"])
            continue

        # Working copy relations
        if HAS_ITERATE and from_attribute == ITERATE_RELATION_NAME:
            # Iterate relations are not set as values of fields
            if to_id:
                relation = StagingRelationValue(to_id)
                event._setRelation(source_obj, ITERATE_RELATION_NAME, relation)
            continue

        # Relations not based on schema field
        field_and_schema = get_field_and_schema_for_fieldname(
            from_attribute, source_obj.portal_type
        )
        if field_and_schema is None:
            # the from_attribute is no field
            logger.info(f"No field. Setting relation: {tuple(item.items())}")
            event._setRelation(source_obj, from_attribute, RelationValue(to_id))
            continue

        field, schema = field_and_schema
        relationvalue = RelationValue(to_id) if to_id else None

        # schema field relations: RelationList, RelationChoice, Relation
        #
        # RelationList
        if isinstance(field, RelationList):
            if not target_obj:
                logger.warning(
                    f"Broken relation not restored: {from_attribute} from {source_obj.absolute_url()}"
                )

            if item["from_uuid"] in modified_relation_lists.get(from_attribute, []):
                # Do not purge relations
                existing_relations = getattr(source_obj, from_attribute, [])
            else:
                # First touch. Make sure we purge!
                existing_relations = []
            if relationvalue:
                existing_relations.append(relationvalue)
            setattr(source_obj, from_attribute, existing_relations)
            modified_items.add(item["from_uuid"])
            modified_relation_lists[from_attribute].append(item["from_uuid"])

        # Relation, RelationChoice
        elif isinstance(field, (Relation, RelationChoice)):
            if not target_obj:
                logger.info(
                    f"Broken relation not restored: {from_attribute} from {source_obj.absolute_url()}"
                )
            setattr(source_obj, from_attribute, relationvalue)
            modified_items.add(item["from_uuid"])

        else:
            # we should never end up here!
            logger.warn(
                f"Unexpected relation {from_attribute} from {source_obj.absolute_url()} to {target_obj.absolute_url()}"
            )

        new_index += 1
        if not new_index % 500:
            logger.info(f"Restored {new_index} relations.")

    # Link integrity
    update_linkintegrity = set(update_linkintegrity)
    logger.info(f"Updating linkintegrity for {len(update_linkintegrity)} items.")
    for uuid in sorted(update_linkintegrity):
        modifiedContent(uuidToObject(uuid), None)

    # Reindex relations in relations catalog.
    logger.info(f"Updating relations for {len(modified_items)} items.")
    for uuid in sorted(modified_items):
        obj = uuidToObject(uuid)
        # updateRelations from z3c.relationfield does not properly update relations in behaviors
        # that are registered with a marker-interface.
        # update_behavior_relations (from plone.app.relationfield) does that but does not update
        # those in the main schema. Duh!
        updateRelations(obj, None)
        update_behavior_relations(obj, None)

    # Purge annotation from portal.
    if RELATIONS_KEY in IAnnotations(portal):
        del IAnnotations(portal)[RELATIONS_KEY]

    logger.info("All valid relations restored.")


def log_relations():
    info, broken = get_relations_stats()
    msg = ""
    for key, value in info.items():
        msg += f"{key}: {value}\n"
    logger.info(f"\nRestored relations: \n{msg}")

    if len(broken.items()) > 0:
        msg = ""
        for key, value in broken.items():
            msg += f"{key}: {value}\n"
        logger.info(f"\nStill broken relations: \n{msg}")


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
    """Get field and its schema from a portal_type."""
    # Turn form.widgets.IDublinCore.title into title
    field_id = field_id.split(".")[-1]
    for schema in iterSchemataForType(portal_type):
        field = schema.get(field_id, None)
        if field is not None:
            return (field, schema)


def cleanup_intids(context=None):
    logger.info("Clean up intIds.")
    intids = getUtility(IIntIds)
    all_refs = [
        f"{i.object.__class__.__module__}.{i.object.__class__.__name__}"
        for i in intids.refs.values()
    ]
    logger.info(Counter(all_refs))

    # Unregister RelationValues
    count = 0
    refs = [i for i in intids.refs.values() if isinstance(i.object, RelationValue)]
    for ref in refs:
        intids.unregister(ref)
        count += 1
    logger.info(f"Removed all {count} RelationValues from IntId-tool")

    # Unregister broken references
    count = 0
    for ref in intids.refs.values():
        if "broken" in repr(ref.object):
            intids.unregister(ref)
    logger.info(f"Removed {count} broken references from IntId-tool")

    all_refs = [
        f"{i.object.__class__.__module__}.{i.object.__class__.__name__}"
        for i in intids.refs.values()
    ]
    logger.info(Counter(all_refs))


def flush_intids():
    """Flush all intIds"""
    intids = getUtility(IIntIds)
    intids.ids = intids.family.OI.BTree()
    intids.refs = intids.family.IO.BTree()


def rebuild_intids():
    """Create new intIds"""

    def add_to_intids(obj, path):
        if IContentish.providedBy(obj):
            # logger.info(f"Added intId for {obj} at {path} to intId utility.")
            addIntIdSubscriber(obj, None)

    portal = getSite()
    portal.ZopeFindAndApply(portal, search_sub=True, apply_func=add_to_intids)

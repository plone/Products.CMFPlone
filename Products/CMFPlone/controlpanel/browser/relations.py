from collections import defaultdict
from plone.base import PloneMessageFactory as _
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.relationhelper import get_relations_stats
from Products.CMFPlone.relationhelper import rebuild_relations
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.component import queryUtility
from zope.intid.interfaces import IIntIds
from zope.intid.interfaces import IntIdMissingError

import logging


logger = logging.getLogger(__name__)


class RelationsRebuildControlpanel(BrowserView):
    def __call__(self, rebuild=False, flush_and_rebuild_intids=False):
        self.done = False
        if rebuild:
            rebuild_relations(flush_and_rebuild_intids=flush_and_rebuild_intids)
            self.done = True
            IStatusMessage(self.request).addStatusMessage(
                _("Finished! See log for details."), "info"
            )

        self.relations_stats, self.broken = get_relations_stats()
        return self.index()


class RelationsInspectControlpanel(BrowserView):
    def __call__(self, relation=None, inspect_backrelation=False):
        self.relation = relation or self.request.get("relation")
        self.inspect_backrelation = inspect_backrelation or self.request.get(
            "inspect_backrelation"
        )

        self.relations = []
        self.relations_stats, self.broken = get_relations_stats()
        registry = getUtility(IRegistry)
        view_action = registry["plone.types_use_view_action_in_listings"]

        if not self.relation:
            IStatusMessage(self.request).addStatusMessage(
                _("Please select a relation"), "info"
            )
            return self.index()

        intids = queryUtility(IIntIds)
        relation_catalog = getUtility(ICatalog)
        query = {"from_attribute": self.relation}
        info = defaultdict(list)

        # relations: column_1 = source, column_2 = target(s)
        # backrelation: column_1 = target, column_2 source(s)
        for rel in relation_catalog.findRelations(query):
            if rel.isBroken():
                continue
            try:
                hasattr(rel, "from_id")
                hasattr(rel, "to_id")
            except IntIdMissingError:
                continue
            if self.inspect_backrelation:
                info[rel.to_id].append(rel.from_id)
            else:
                info[rel.from_id].append(rel.to_id)

        for column_1_intid in info:
            obj = intids.getObject(column_1_intid)
            use_view_action = obj.portal_type in view_action
            url = (
                obj.absolute_url() + "/view" if use_view_action else obj.absolute_url()
            )
            item = {}
            item["column_1"] = {
                "title": obj.title_or_id(),
                "url": url,
                "portal_type": obj.portal_type,
            }
            item["column_2"] = []
            for column_2_intid in info[column_1_intid]:
                obj = intids.getObject(column_2_intid)
                use_view_action = obj.portal_type in view_action
                url = (
                    obj.absolute_url() + "/view"
                    if use_view_action
                    else obj.absolute_url()
                )
                item["column_2"].append(
                    {
                        "title": obj.title_or_id(),
                        "url": url,
                        "portal_type": obj.portal_type,
                    }
                )
            self.relations.append(item)
        self.relations.sort(key=lambda x: x["column_1"]["title"])
        return self.index()

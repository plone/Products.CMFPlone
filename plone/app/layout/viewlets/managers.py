
class OrderedViewletManager(object):
    def sort(self, viewlets):
        """Sort the viewlets.

        ``viewlets`` is a list of tuples of the form (name, viewlet).
        """

        # first get the known ones
        name_map = dict(viewlets)
        result = []
        for name in self.order_by_name:
            if name in name_map:
                result.append((name, name_map[name]))
                del name_map[name]

        # then sort the remaining ones
        remaining = sorted(name_map.items(), lambda x, y: cmp(x[1], y[1]))

        # return both together
        return result + remaining


class PortalTopManager(OrderedViewletManager):
    order_by_name = ('plone.header',
                     'plone.personal_bar',
                     'plone.app.i18n.locales.languageselector',
                     'plone.path_bar',
                    )


class PortalHeaderManager(OrderedViewletManager):
    order_by_name = ('plone.skip_links',
                     'plone.site_actions',
                     'plone.searchbox',
                     'plone.logo',
                     'plone.global_sections',
                    )

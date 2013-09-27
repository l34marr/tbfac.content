from zc.relation.interfaces import ICatalog
from zope.component import getUtility

from Products.Five.browser import BrowserView

from plone.supermodel.model import Schema
try:
    from plone.directives.form.schema import Schema as oldSchema
except:
    # do not brack instance after we remove old Schema class
    oldSchema = None


class FixCatalogView(BrowserView):
    """ Remove old plone.directives.form Schema class from
        relation catalog z3c.relationfield indexes.
    """

    def __call__(self):
        if oldSchema:
            catalog = getUtility(ICatalog)
            to_map = catalog._name_TO_mapping['to_interfaces_flattened']
            from_map = catalog._name_TO_mapping['from_interfaces_flattened']

            if oldSchema in to_map:
                to_map[Schema] = to_map[oldSchema]
                # remove old interface
                del to_map[oldSchema]

            if oldSchema in from_map:
                from_map[Schema] = from_map[oldSchema]
                #remove old interface
                del from_map[oldSchema]

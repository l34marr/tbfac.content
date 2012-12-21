from time import time

from zope.interface import implements
from zope.component import getUtility
from Products.Five import BrowserView

from plone.memoize import ram
from plone.registry.interfaces import IRegistry

from collective.geo.contentlocations.interfaces import IGeoManager

from .interfaces import IInfoVenuesMapView


DESC_TEMPLATE = """<![CDATA[<div
class='infovenue-description'
dir="ltr">%s</div>]]>
"""


class InfoVenuesMapKMLView(BrowserView):

    implements(IInfoVenuesMapView)

    def __init__(self, context, request):
        super(InfoVenuesMapKMLView, self).__init__(context, request)
        self.request.set('disable_border', True)

    @property
    def title(self):
        return self.context.Title()

    @property
    def description(self):
        return "<![CDATA[%s]]>" % self.context.Description()

    @property
    def user_coords_tool(self):
        return getUtility(IUsersCoordinates)

    def get_venues(self):
        """This function retrieves all related Venue objects for given Info
        and for each Venue gets the coordinates.

        Return a list of venues which have coordinates set.

        Each element of this list is a dictionary that contains three keys:
        location, title, description
        """
        venues = []
        for ref in self.context.venue:
            ob = ref.to_object
            geo = IGeoManager(ob, None)
            if geo and geo.isGeoreferenceable():
                geometry, (longitude, latitude) = geo.getCoordinates()
                if geometry == 'Point' and longitude and latitude:
                    venue = {
                        'title': ob.Title(),
                        'description': DESC_TEMPLATE % ob.Description(),
                        'location': "%r,%r,0.000000" % (longitude, latitude),
                    }

            venues.append(venue)

        return venues

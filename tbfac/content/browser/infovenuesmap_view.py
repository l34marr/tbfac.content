from zope.interface import implements

from Products.Five import BrowserView

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

    def get_venues(self):
        """This function retrieves all related Venue objects for given Info
        and for each Venue gets the coordinates.

        Return a list of venues which have coordinates set.

        Each element of this list is a dictionary that contains three keys:
        location, title, description
        """
        venues = []
        refs = self.context.venue
        if not refs:
            return venues

        for ref in refs:
            ob = ref.to_object
            geo = IGeoManager(ob, None)
            if geo and geo.isGeoreferenceable():
                geometry, coordinates = geo.getCoordinates()
                if not coordinates or len(coordinates) != 2:
                    continue
                else:
                    longitude, latitude = coordinates
                if geometry == 'Point' and longitude and latitude:
                    venue = {
                        'title': ob.Title(),
                        'description': DESC_TEMPLATE % ob.Description(),
                        'location': "%r,%r,0.000000" % (longitude, latitude),
                    }
                    venues.append(venue)

        return venues

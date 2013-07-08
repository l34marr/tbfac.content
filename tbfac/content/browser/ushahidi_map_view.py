from plone.uuid.interfaces import IUUID
from plone.memoize.instance import memoize

from collective.geo.contentlocations.interfaces import IGeoManager
from collective.geo.ushahidi.browser import map_view as base


EXCLUDE_TYPES = ('tbfac.Venue',)

class UshahidiMapView(base.UshahidiMapView):
    """We customize it to:
    
    * hide some content types
    * to display Info with Related Venues
    """

    def friendly_types(self):
        """Exclude some extra types. Mostly related"""
        types = super(UshahidiMapView, self).friendly_types()
        return tuple([t for t in types if t not in EXCLUDE_TYPES])

    @memoize
    def _get_markers(self, brain):
        """Return dict of marker details.

        Handle Info objects in special way.
        """
        markers = []
        if brain.portal_type == 'tbfac.Info':
            # get related Venues
            obj = brain.getObject()
            if obj is None:
                return []

            refs = obj.venue
            if not refs:
                return []

            for ref in refs:
                venue = ref.to_object
                geo = IGeoManager(venue, None)
                if geo and geo.isGeoreferenceable():
                    geometry, coordinates = geo.getCoordinates()
                    if not coordinates or len(coordinates) != 2:
                        continue
                    else:
                        longitude, latitude = coordinates
                    if geometry == 'Point' and longitude and latitude:
                        markers.append({
                            'uid': IUUID(venue),
                            'search_uid': brain.UID,
                            'url': brain.getURL(),
                            'title': brain.Title,
                            'tags': brain.Subject or [],
                            'start': brain.start or '',
                            'end': brain.end or '',
                            'geometry': {
                                'style': None,
                                'type': 'Point',
                                'coordinates': (longitude, latitude)},
                            'latitude': latitude,
                            'longitude': longitude,
                        })
        else:
            markers = super(UshahidiMapView, self)._get_markers(brain)

        return markers

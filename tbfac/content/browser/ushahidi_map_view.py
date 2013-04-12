import json
import calendar
from datetime import datetime

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.utils import DT2dt
from Products.AdvancedQuery import Eq, Ge, Le, In

from plone.uuid.interfaces import IUUID
from plone.memoize.instance import memoize

from collective.geo.contentlocations.interfaces import IGeoManager
from collective.geo.ushahidi.browser.map_settings_js import DEFAULT_MARKER_COLOR
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
    def getObjectsInfo(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        portal_types = getToolByName(context, 'portal_types')

        categories = set() # to store unique object keywords
        ctypes = [] # to store portal type and it's title
        ctypes_added = [] # to avoid duplicates in content types list
        ctypes_meta = {} # to cache portal type Titles

        query = Eq('path', '/'.join(context.getPhysicalPath())) & \
            In('portal_type', self.friendly_types()) & \
            Eq('object_provides',
                'collective.geo.geographer.interfaces.IGeoreferenceable')

        brains = catalog.evalAdvancedQuery(query, (('start', 'asc'),))
        for brain in brains:
            # skip if no coordinates set
            markers = self._get_markers(brain)
            if not markers:
                continue

            # populate categories
            if markers[0]['tags']:
                categories |= set(markers[0]['tags'])

            # populate types
            ptype = brain.portal_type
            if ptype not in ctypes_added:
                if ptype in ctypes_meta:
                    title = ctypes_meta[ptype]
                else:
                    title = portal_types.getTypeInfo(ptype).title
                    ctypes_meta[ptype] = title
                ctypes.append({'id': ptype, 'title': title})
                ctypes_added.append(ptype)

        # sort our data
        categories = list(categories)
        categories.sort()

        ctypes = list(ctypes)
        ctypes.sort(lambda x,y:cmp(x['title'], y['title']))

        # prepare dates, for this we just generate range of years and months
        # between first and last item fetched list of objects
        dates = []
        if len(brains) > 0:
            # skip object w/o set start date
            start_brain = None
            for brain in brains:
                # skip if no coordinates set
                markers = self._get_markers(brain)
                if not markers:
                    continue

                if brain.start and brain.start.year() > 1000:
                    start_brain = brain
                    break

            if start_brain:
                # now try to find last date, based on end field
                end_brain = None
                for brain in catalog.evalAdvancedQuery(query,
                    (('end', 'desc'),)):
                    # skip if no coordinates set
                    markers = self._get_markers(brain)
                    if not markers:
                        continue

                    if brain.end and brain.end.year() < 2499:
                        end_brain = brain
                        break

                if not end_brain:
                    end = brains[-1].start
                else:
                    end = end_brain.end

                start = start_brain.start
                first_year, last_year = start.year(), end.year()
                first_month, last_month = start.month(), end.month()

                if first_year and last_year:
                    for year in range(first_year, last_year+1):
                        months = []

                        # count from first month only for first year
                        month_from = 1
                        if year == first_year:
                            month_from = first_month

                        # count till last month only for last year
                        month_to = 12
                        if year == last_year:
                            month_to = last_month

                        for month in range(month_from, month_to+1):
                            dt = datetime(year, month, 1)
                            months.append({
                                'datetime': dt,
                                'label': '%s %s' % (dt.strftime('%b'), year),
                                'timestamp': calendar.timegm(dt.timetuple()),
                            })

                        dates.append((year, months))

            # sort by year
            if dates:
                dates.sort(lambda x,y: cmp(x[0], y[0]))

        return {
            'categories': tuple(categories),
            'types': tuple(ctypes),
            'dates': tuple(dates),
        }

    def getJSONCluster(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')

        # prepare catalog query
        query = Eq('path', '/'.join(context.getPhysicalPath())) & \
            In('portal_type', self.friendly_types()) & \
            Eq('object_provides',
                'collective.geo.geographer.interfaces.IGeoreferenceable')

        # apply categories
        category = self.request.get('c') and [self.request.get('c')] or []
        color = DEFAULT_MARKER_COLOR
        if category:
            query &= In('Subject', category)
            color = self.getCategoryColor(category[0],
                default=DEFAULT_MARKER_COLOR)

        # apply content types
        if self.request.get('m'):
            query &= Eq('portal_type', self.request['m'])

        # apply 'from' date
        start = self.request.get('s')
        if start and start != '0':
            query &= Ge('end', int(start))

        # apply 'to' date
        end = self.request.get('e')
        if end and end != '0':
            query &= Le('start', int(end))

        # get zoom and calculate distance based on zoom
        zoom = self.request.get('z') and int(self.request.get('z')) or 7
        distance = float(10000000 >> zoom) / 100000.0

        # query all markers for the map
        markers = []
        added = []
        for brain in catalog.evalAdvancedQuery(query, (
            ('start', 'asc'), ('end', 'desc'))):
            for m in self._get_markers(brain):
                if m['uid'] not in added:
                    markers.append(m)
                    added.append(m['uid'])

        # cluster markers based on zoom level
        clusters = []
        singles = []
        while len(markers) > 0:
            marker = markers.pop()
            cluster = []

            for target in markers:
                pixels = abs(marker['longitude'] - target['longitude']) + \
                    abs(marker['latitude'] - target['latitude'])

                # if two markers are closer than defined distance, remove
                # compareMarker from array and add to cluster.
                if pixels < distance:
                    markers.pop(markers.index(target))
                    cluster.append(target)

            # if a marker was added to cluster, also add the marker we were
            # comparing to
            if len(cluster) > 0:
                cluster.append(marker)
                clusters.append(cluster)
            else:
                singles.append(marker)

        # create json from clusters
        features = []
        for cluster in clusters:
            # calculate cluster center
            bounds = self.calculate_center(cluster)

            # json string for popup window
            marker = cluster[0]

            start = marker['start']
            if start:
                start = calendar.timegm(DT2dt(start).timetuple())

            features.append({
                'type': 'Feature',
                'properties': {
                    'id': marker['uid'],
                    'name': marker['title'],
                    'link': marker['url'],
                    'category': marker['tags'],
                    'color': color,
                    'icon': '',
                    'thumb': '',
                    'timestamp': start,
                    'count': len(cluster),
                    'class': 'stdClass'
                },
                'geometry': {
                     'type': 'Point',
                     'coordinates': [bounds['center']['longitude'],
                         bounds['center']['latitude']]
                }
            })

        # pass single points to standard markers json
        for marker in singles:
            start = marker['start']
            if start:
                start = calendar.timegm(DT2dt(start).timetuple())

            features.append({
                'type': 'Feature',
                'properties': {
                    'id': marker['uid'],
                    'name': marker['title'],
                    'link': marker['url'],
                    'category': marker['tags'],
                    'color': color,
                    'icon': '',
                    'thumb': '',
                    'timestamp': start,
                    'count': 1,
                    'class': 'stdClass'
                },
                'geometry': marker['geometry'],
            })

        return json.dumps({"type":"FeatureCollection", "features": features})

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
                            'url': venue.absolute_url(),
                            'title': venue.Title(),
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
        elif brain.zgeo_geometry:
            markers.append({
                'uid': brain.UID,
                'url': brain.getURL(),
                'title': brain.Title,
                'tags': brain.Subject or [],
                'start': brain.start or '',
                'end': brain.end or '',
                'geometry': brain.zgeo_geometry,
                'latitude': brain.zgeo_geometry['coordinates'][1],
                'longitude': brain.zgeo_geometry['coordinates'][0],
            })

        return markers

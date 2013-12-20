from zc.relation.interfaces import ICatalog
from zope.component import getUtility

from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName
import urllib2
import json
from ..config import ADDTHIS_API_ADD, ADDTHIS_USERNAME, ADDTHIS_PASSWORD
from ..config import ONETIME_FILE

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

            # fix existing relations
            for k, v in catalog._reltoken_name_TO_objtokenset.items():
                if k[1] in ('to_interfaces_flattened',
                            'from_interfaces_flattened'):
                    if oldSchema in v:
                        v.remove(oldSchema)
                        v.add(Schema)


class AddThisAdd(BrowserView):
    def __call__(self):
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        # Add the username and password.
        password_mgr.add_password(None, ADDTHIS_API_ADD, ADDTHIS_USERNAME, ADDTHIS_PASSWORD)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        # create "opener" (OpenerDirector instance)
        opener = urllib2.build_opener(handler)
        # use the opener to fetch a URL
        resultJson = opener.open(api_url)
        # read result to to string format
        resultStr = resultJson.read()
        # load string to list format
        resultList = json.loads(resultStr)

        for record in resultList:
            try:
                path = str(record['url'].split('?')[0].split('/view')[0].replace('http://talks.taishinart.org.tw', '/taishin'))
                catalog = getToolByName(self, 'portal_catalog')
                brains = catalog(path=path)
                item = brains[0].getObject()
                prev_counts = getattr(item, 'v_counts', 0)
                item.v_counts = prev_counts
                item.v_counts += int(record['clicks'])
            except: pass


class OneTime(BrowserView):
    def __call__(self):
        catalog = getToolByName(self, 'portal_catalog')
        with open(ONETIME_FILE, 'r') as onetime:
            for line in onetime.read().split('\n'):
                if line == '':
                    break
                url, shares, clicks = str(line.split('\t')[0]), int(line.split('\t')[1]), int(line.split('\t')[2])
                path = url.replace('http://talks.taishinart.org.tw', '/taishin').split('?')[0]
                if path.split('/')[2] not in ['event', 'juries']:
                    continue
                brain = catalog(path=path)
                item = brain[0].getObject()
                prev_counts = getattr(item, 'v_counts', 0)
                item.v_counts = prev_counts
                item.v_counts += shares
                item.v_counts += clicks


from Products.CMFCore.utils import getToolByName

def addCalendarTypes(portal):
    portal_calendar = getToolByName(portal, 'portal_calendar')
    # 'Event' was already here, we're just adding the
    # 'tbfac.Info' content-type.
    portal_calendar.calendar_types = ('Event', 'tbfac.Info')

def importVarious(context):
    """Miscellanous steps import handle
    """
    if context.readDataFile('tbfac.content_various.txt') is None:
        return
    portal = context.getSite()

    addCalendarTypes(portal)
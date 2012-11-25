from five import grok
from zope import schema
from plone.directives import form

class IActivityFolder(form.Schema):
    """A container for ActivityInfo
    """

# Note that we use the standard folder_listing view for this type, so there
# is no specific view here

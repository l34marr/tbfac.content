from five import grok
from zope import schema
from plone.directives import form

class IActivity(form.Schema):
    """A container for Activity
    """

# Note that we use the standard folder_listing view for this type, so there
# is no specific view here

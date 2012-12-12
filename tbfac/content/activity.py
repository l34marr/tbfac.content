from five import grok
from zope import schema
from plone.directives import form, dexterity

class IActivity(form.Schema):
    """A container for Activity
    """

class Activity(dexterity.Container):
    grok.implements(IActivity)

    # Add your class methods and properties here

# Note that we use the standard folder_listing view for this type, so there
# is no specific view here

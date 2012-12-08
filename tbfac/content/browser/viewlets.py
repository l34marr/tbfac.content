from Acquisition import aq_inner
from AccessControl import getSecurityManager

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets.common import ViewletBase

from ..behaviors.recommendations import IRecommendations


class RecommendationsViewlet(ViewletBase):
    template = ViewPageTemplateFile('templates/recommendations.pt')

    def update(self):
        context = aq_inner(self.context)
        self.adapted = adapted = IRecommendations(context)
        self.recommended = adapted.isRecommended()
        self.recommendations = adapted.numberOfRecommends()
        user = getSecurityManager().getUser()
        self.userid = user.getId()
        self.advisor = user.has_permission('TBFAC: Add recommendation', context)
        self.recommended_by_me = False
        if self.advisor and adapted.isRecommendedBy(self.userid):
            self.recommended_by_me = True

    def render(self):
        return self.template()

class RecommendationsView(BrowserView):

    def toggleRecommendation(self):
        """Recommend or unrecommend object"""
        context = aq_inner(self.context)
        viewlet = self._getViewlet()
        if viewlet.recommended_by_me:
            viewlet.adapted.unrecommend(viewlet.userid)
        else:
            viewlet.adapted.recommend(viewlet.userid)
        
        if self.request.form.get('ajax') == '1':
            # one more time update viewlet to get updated data after last action
            viewlet.update()
            return viewlet.render()
        else:
            return self.request.response.redirect(context.absolute_url())

    def renderViewlet(self):
        return self._getViewlet().render()

    def _getViewlet(self):
        context = aq_inner(self.context)
        viewlet = RecommendationsViewlet(context, self.request, None, None)
        viewlet = viewlet.__of__(context)
        viewlet.update()
        return viewlet

# gamification/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Badge

class BadgeListView(LoginRequiredMixin, ListView):
    """
    يعرض قائمة بجميع الشارات المتاحة في المنصة، مع توضيح أي منها
    قد حصل عليه المستخدم الحالي.
    """
    model = Badge
    template_name = 'gamification/badge_list.html'
    context_object_name = 'badges'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # جلب IDs الشارات التي يملكها المستخدم الحالي
        context['earned_badge_ids'] = set(
            self.request.user.badges.values_list('badge_id', flat=True)
        )
        return context
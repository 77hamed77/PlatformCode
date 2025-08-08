# gamification/urls.py

from django.urls import path
from .views import BadgeListView

app_name = 'gamification'

urlpatterns = [
    # رابط لعرض قائمة بجميع الشارات المتاحة في المنصة
    path('badges/', BadgeListView.as_view(), name='badge_list'),
]
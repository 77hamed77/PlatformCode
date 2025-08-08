# chat/urls.py

from django.urls import path
from .views import ChatRoomListView, ChatRoomDetailView
from chat import views

app_name = 'chat'

urlpatterns = [
    # رابط لعرض قائمة بجميع غرف الشات
    path('', ChatRoomListView.as_view(), name='room_list'),
    
    # رابط للدخول إلى غرفة شات معينة
    path('<slug:slug>/', ChatRoomDetailView.as_view(), name='room_detail'),
    
    path('message/<int:pk>/delete/', views.DeleteChatMessageView.as_view(), name='delete_message'),
]
# chat/views.py

# 1. Standard Library Imports
# (None in this case)

# 2. Django Core Imports
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.views import View # <-- CRITICAL FIX: Imported the base View class
from django.views.generic import ListView, DetailView

# 3. Local Application Imports
from .models import ChatRoom, ChatMessage

# =================================================================
# Main Chat Views
# =================================================================

class ChatRoomListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = 'chat/room_list.html'
    context_object_name = 'chat_rooms'

class ChatRoomDetailView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = 'chat/room_detail.html'
    context_object_name = 'room'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # جلب آخر 50 رسالة لعرضها كسجل، مع تحسين الأداء
        context['messages'] = self.object.messages.filter(is_deleted=False).select_related('author').order_by('timestamp')[:50]
        return context

# =================================================================
# Moderation Views
# =================================================================

class DeleteChatMessageView(LoginRequiredMixin, View):
    """
    Handles the deletion of a chat message via a POST request.
    This is intended to be used with HTMX for a seamless experience.
    """
    def post(self, request, *args, **kwargs):
        # `select_related` here is a minor optimization to pre-fetch the author
        message = get_object_or_404(ChatMessage.objects.select_related('author'), pk=kwargs['pk'])
        
        # Check if the user has permission to delete the message
        if request.user.is_moderator or request.user == message.author:
            message.is_deleted = True
            message.content = "تم حذف هذه الرسالة."
            message.save(update_fields=['is_deleted', 'content'])
            
            # Return the updated message partial to be swapped by HTMX
            return render(request, 'chat/partials/chat_message.html', {'msg': message})
            
        return HttpResponseForbidden("ليس لديك الصلاحية لحذف هذه الرسالة.")
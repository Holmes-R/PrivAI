from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.ChatHistoryListView.as_view(), name="chat-history"),
]

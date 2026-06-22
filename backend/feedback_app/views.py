from rest_framework import generics, permissions
from .models import ChatHistory
from .serializers import ChatHistorySerializer


class ChatHistoryListView(generics.ListAPIView):
    serializer_class = ChatHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        document_id = self.request.query_params.get("document_id")
        qs = ChatHistory.objects.filter(user=self.request.user)
        if document_id:
            qs = qs.filter(document_id=document_id)
        return qs

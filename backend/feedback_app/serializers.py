from rest_framework import serializers
from .models import ChatHistory


class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = ["id", "document", "question", "answer", "sources", "created_at"]
        read_only_fields = ["id", "created_at"]

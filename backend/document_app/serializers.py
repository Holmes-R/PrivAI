from rest_framework import serializers
from .models import Document
from .vector_store import get_user_collection


class DocumentSerializer(serializers.ModelSerializer):
    chunk_count = serializers.SerializerMethodField()

    file_type = serializers.ChoiceField(
        choices=[
            ("pdf", "PDF"),
            ("txt", "Text"),
            ("docx", "Word"),
        ]
    )

    class Meta:
        model = Document
        fields = [
            "id", "title", "file_type", "file",
            "remote_id", "remote_url", "created_at", "updated_at",
            "chunk_count",
        ]
        read_only_fields = [
            "id", "remote_id", "remote_url", "created_at", "updated_at", "chunk_count",
        ]

    def get_chunk_count(self, obj):
        try:
            collection = get_user_collection(obj.user_id)
            ids = collection.get(where={"document_id": obj.id}).get("ids", [])
            return len(ids)
        except Exception:
            return 0

    def validate(self, attrs):
        file_type = attrs.get("file_type")
        file_obj = attrs.get("file")
        if file_type and not file_obj:
            raise serializers.ValidationError(
                "A file is required for local upload (pdf/txt/docx)."
            )
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

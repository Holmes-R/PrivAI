# document_app/serializers.py  (NEW/COMPLETE)
from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    # For CREATE (upload): limit file_type to local files only
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
            "id",
            "title",
            "file_type",
            "file",
            "remote_id",
            "remote_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "remote_id",
            "remote_url",
            "created_at",
            "updated_at",
        ]

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
        # file_type only local, so no remote_id/url set here
        return super().create(validated_data)
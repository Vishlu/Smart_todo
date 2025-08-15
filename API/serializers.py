from rest_framework import serializers
from AI_todo.models import Task, Category, ContextEntry

class CategorySerializer(serializers.ModelSerializer):
    class Meta: model = Category; fields = ["id","name","usage_count"]

class ContextEntrySerializer(serializers.ModelSerializer):
    class Meta: model = ContextEntry; fields = ["id","content","source_type","created_at","processed_insights"]

class TaskSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category',
        write_only=True, required=False, allow_null=True
    )
    class Meta:
        model = Task
        fields = ["id","title","description","category","category_id",
                  "priority_score","deadline","status","created_at","updated_at"]

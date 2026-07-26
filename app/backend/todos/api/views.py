from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema

from todos.models import Todo
from todos.api.serializers import TodoSerializer
from todos.permissions import IsOwner
from todos.services.todo_service import get_user_todos


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = "pk"

    def get_queryset(self):
        return get_user_todos(self.request.user, self.request.query_params)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

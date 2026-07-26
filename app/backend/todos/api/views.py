from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status

from todos.models import Todo
from todos.api.serializers import TodoSerializer
from todos.permissions import IsOwner
from todos.services.todo_service import get_user_todos, create_todo


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return get_user_todos(self.request.user, self.request.query_params)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

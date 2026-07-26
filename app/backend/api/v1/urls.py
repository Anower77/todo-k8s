from django.urls import path, include

urlpatterns = [
    path("auth/", include("accounts.api.urls")),
    path("", include("todos.api.urls")),
]

from todos.models import Todo


def get_user_todos(user, filters=None):
    qs = Todo.objects.filter(owner=user)
    if filters:
        status = filters.get("status")
        priority = filters.get("priority")
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
    return qs


def create_todo(user, data):
    return Todo.objects.create(owner=user, **data)

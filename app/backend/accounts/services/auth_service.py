from accounts.models import User


def register_user(email, username, password):
    user = User.objects.create_user(username=username, email=email, password=password)
    return user

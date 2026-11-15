from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from recipes.models import Subscription

from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_active",
        "date_joined",
        "avatar",
        "password",
    )
    search_fields = (
        "email",
        "username",
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author", "created_at")
    search_fields = ("user__username", "author__username")

from django.contrib import admin
from django.contrib.admin.models import LogEntry

from .models import UPUser, AppClient, ApiLog


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UPUser)
class UPUserAdmin(ReadOnlyAdmin):
    list_display = ["username", "note", "parent_path", "is_enable"]

    search_fields = ["username", "note", "parent_path"]


@admin.register(LogEntry)
class LogEntryAdmin(ReadOnlyAdmin):
    list_display = ["action_time", "user", "content_type", "object_id", "object_repr", "action_flag", "change_message"]


@admin.register(AppClient)
class AppClientAdmin(admin.ModelAdmin):
    list_display = ["user", "appid"]


@admin.register(ApiLog)
class ApiLogAdmin(ReadOnlyAdmin):
    list_display = [
        "date_time", "method", "host", "path", "status_code",
        "operator", "remote_addr", "keyword", "result", "user"
    ]

    list_filter = ["status_code", "date_time", "user"]

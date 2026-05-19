from django.contrib import admin

from .models import ShortURL
from .models import SMSLog


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = [
        "phone_number",
        "category",
        "status",
        "message_length",
        "related_user",
        "created_at",
    ]
    list_filter = ["category", "status", "created_at"]
    search_fields = ["phone_number", "message"]
    readonly_fields = [
        "phone_number",
        "message",
        "message_length",
        "original_length",
        "category",
        "provider_response",
        "status",
        "failure_reason",
        "related_user",
        "related_organization",
        "created_at",
    ]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False  # SMSLog is append-only via the service

    def has_change_permission(self, request, obj=None):
        return False  # SMSLog is read-only

    def has_delete_permission(self, request, obj=None):
        return False  # SMSLog is append-only


@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ["code", "category", "is_expired", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["code", "original_url"]
    readonly_fields = ["code", "created_at"]

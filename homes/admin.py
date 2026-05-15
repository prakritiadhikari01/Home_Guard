from django.contrib import admin

from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.models.home_member_model import HomeMember


# -------------------------
# Home Admin (CLEAN UI)
# -------------------------
@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "address",
        "created_at",
    )

    search_fields = (
        "name",
        "address",
        "owner__email",
    )

    list_filter = (
        "created_at",
    )

    ordering = ("-created_at",)

    readonly_fields = ("id", "created_at")


# -------------------------
# HomeMember Admin (MORE POWERFUL UI)
# -------------------------
@admin.register(HomeMember)
class HomeMemberAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "home",
        "role",
        "can_view_dashboard",
        "can_control_devices",
        "can_manage_members",
        "can_unlock_door",
        "receive_alerts",
        "joined_at",
    )

    search_fields = (
        "user__email",
        "home__name",
    )

    list_filter = (
        "role",
        "can_view_dashboard",
        "can_control_devices",
        "can_manage_members",
        "can_unlock_door",
        "receive_alerts",
    )

    ordering = ("-joined_at",)

    readonly_fields = ("id", "joined_at")
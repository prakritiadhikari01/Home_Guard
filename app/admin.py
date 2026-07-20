from django.contrib import admin

from app.infrastructure.db.models.face_profile_model import FaceProfile
from app.infrastructure.db.models.enrollment_session_model import EnrollmentSession
from app.infrastructure.db.models.user_settings_model import UserSettings
from app.infrastructure.db.models.home_settings_model import HomeSettings
import json

print("APP ADMIN LOADED")


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "push_notifications",
        "email_notifications",
        "dark_mode",
        "timezone",
    )

    search_fields = (
        "user__email",
        "user__full_name",
    )


@admin.register(HomeSettings)
class HomeSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "home",
    )


# ==========================================================
# ENROLLMENT SESSION
# ==========================================================

@admin.register(EnrollmentSession)
class EnrollmentSessionAdmin(admin.ModelAdmin):

    list_display = (
        "id_short",
        "user_email",
        "invitation_home_name",
        "status_badge",
        "started_at",
        "completed_at",
        "ai_engine",
    )

    list_filter = (
        "status",
        "started_at",
        "completed_at",
    )

    search_fields = (
        "user__email",
        "invitation__home__name",
    )

    readonly_fields = (
        "id",
        "user",
        "invitation",
        "status",
        "ai_engine",
        "started_at",
        "completed_at",
        "failure_reason",
    )

    ordering = (
        "-started_at",
    )

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = "Session"

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User"

    def invitation_home_name(self, obj):
        # invitation is optional now — settings-triggered enrollment has none
        return obj.invitation.home.name if obj.invitation else "-"
    invitation_home_name.short_description = "Home (via invite)"

    def status_badge(self, obj):

        icons = {
            "pending": "🟡 Pending",
            "completed": "🟢 Completed",
            "failed": "🔴 Failed",
            "cancelled": "⚫ Cancelled",
        }

        return icons.get(obj.status, obj.status)

    status_badge.short_description = "Status"


# ==========================================================
# FACE PROFILE
# ==========================================================

@admin.register(FaceProfile)
class FaceProfileAdmin(admin.ModelAdmin):

    list_display = (
        "id_short",
        "member_name",
        "member_email",
        "verified",
        "pose_summary",
        "created_at",
    )

    list_filter = (
        "is_verified",
        "created_at",
    )

    search_fields = (
        "label_name",
        "user__email",
        "user__full_name",
    )

    readonly_fields = (
        "id",
        "user",
        "label_name",
        "is_verified",
        "created_at",
        "updated_at",
        "formatted_embeddings",
    )

    exclude = (
        "embeddings",
    )

    ordering = (
        "-created_at",
    )

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = "Profile"

    def member_name(self, obj):
        return obj.label_name
    member_name.short_description = "Person"

    def member_email(self, obj):
        return obj.user.email
    member_email.short_description = "Email"

    def verified(self, obj):
        return "✅ Yes" if obj.is_verified else "❌ No"
    verified.short_description = "Verified"

    def pose_summary(self, obj):
        if not obj.embeddings:
            return "-"

        total = 0
        parts = []

        for pose in ["CENTER", "LEFT", "RIGHT", "UP", "DOWN"]:
            embeddings = obj.embeddings.get(pose, [])

            count = len(embeddings) if isinstance(embeddings, list) else 0

            total += count
            parts.append(f"{pose}: {count}")

        return f"{total} total ({', '.join(parts)})"

    pose_summary.short_description = "Embeddings"

    def formatted_embeddings(self, obj):
        return json.dumps(
            obj.embeddings,
            indent=4,
        )

    formatted_embeddings.short_description = "Embedding JSON"
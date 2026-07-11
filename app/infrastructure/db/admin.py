from django.contrib import admin

from app.infrastructure.db.models.face_profile_model import FaceProfile
from app.infrastructure.db.models.enrollment_session_model import EnrollmentSession
from app.infrastructure.db.models.user_settings_model import UserSettings
from app.infrastructure.db.models.home_settings_model import HomeSettings
import json

from django.contrib import admin

from app.infrastructure.db.models.enrollment_session_model import (
    EnrollmentSession,
)

from app.infrastructure.db.models.face_profile_model import (
    FaceProfile,
)

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

# app/infrastructure/db/admin.py




# ==========================================================
# ENROLLMENT SESSION
# ==========================================================

@admin.register(EnrollmentSession)
class EnrollmentSessionAdmin(admin.ModelAdmin):

    list_display = (
        "id_short",
        "member_email",
        "home_name",
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
        "invitation__email",
        "invitation__home__name",
    )

    readonly_fields = (
        "id",
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

    def member_email(self, obj):
        return obj.invitation.email
    member_email.short_description = "Invited User"

    def home_name(self, obj):
        return obj.invitation.home.name
    home_name.short_description = "Home"

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
        "home_member__user__email",
        "home_member__user__full_name",
    )

    readonly_fields = (
        "id",
        "home_member",
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
        return obj.home_member.user.email
    member_email.short_description = "Email"

    def verified(self, obj):
        return "✅ Yes" if obj.is_verified else "❌ No"
    verified.short_description = "Verified"

    def pose_summary(self, obj):

        if not obj.embeddings:
            return "-"

        summary = []

        for pose, value in obj.embeddings.items():

            count = len(value.get("embeddings", []))

            summary.append(f"{pose}: {count}")

        return " | ".join(summary)

    pose_summary.short_description = "Embeddings"

    def formatted_embeddings(self, obj):

        return json.dumps(
            obj.embeddings,
            indent=4,
        )

    formatted_embeddings.short_description = "Embedding JSON"
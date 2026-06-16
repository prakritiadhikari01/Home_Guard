# app/infrastructure/db/admins/detection_event_admin.py

from django.contrib import admin
from django.utils.html import format_html

from app.infrastructure.db.models.detection_event_model import (
    DetectionEvent
)


@admin.register(DetectionEvent)
class DetectionEventAdmin(admin.ModelAdmin):

    list_display = (
        "event_time",
        "person_badge",
        "person_name",
        "camera",
        "device_name",
        "confidence",
        "snapshot_preview",
        "event_type",
    )

    list_filter = (
        "person_type",
        "event_type",
        "camera_location",
        "timestamp",
    )

    search_fields = (
        "person_label",
        "camera_location",
        "event_summary",
        "device__name",
    )

    readonly_fields = (
        "id",
        "home",
        "device",
        "matched_member",
        "matched_face",
        "event_type",
        "person_type",
        "person_label",
        "confidence_score",
        "camera_location",
        "image_url",
        "snapshot_url",
        "event_summary",
        "metadata",
        "timestamp",
        "created_at",
        "large_snapshot",
    )

    ordering = (
        "-timestamp",
    )

    date_hierarchy = "timestamp"

    list_per_page = 25

    fieldsets = (

        (
            "Detection Information",
            {
                "fields": (
                    "id",
                    "event_type",
                    "person_type",
                    "person_label",
                    "confidence_score",
                )
            },
        ),

        (
            "Device Information",
            {
                "fields": (
                    "home",
                    "device",
                    "camera_location",
                )
            },
        ),

        (
            "Recognition Match",
            {
                "fields": (
                    "matched_member",
                    "matched_face",
                )
            },
        ),

        (
            "Evidence",
            {
                "fields": (
                    "large_snapshot",
                    "image_url",
                    "snapshot_url",
                )
            },
        ),

        (
            "Details",
            {
                "fields": (
                    "event_summary",
                    "metadata",
                )
            },
        ),

        (
            "Timestamps",
            {
                "fields": (
                    "timestamp",
                    "created_at",
                )
            },
        ),
    )

    def event_time(self, obj):
        return obj.timestamp.strftime(
            "%d %b %Y %H:%M:%S"
        )

    event_time.short_description = "Detected At"

    def device_name(self, obj):
        return obj.device.name

    device_name.short_description = "Device"

    def camera(self, obj):
        return obj.camera_location

    camera.short_description = "Location"

    def confidence(self, obj):
        return f"{obj.confidence_score:.2%}"

    confidence.short_description = "Confidence"

    def person_name(self, obj):

        if obj.person_label:
            return obj.person_label

        return "Unknown"

    person_name.short_description = "Person"

    def person_badge(self, obj):

        colors = {
            "KNOWN": "#28a745",
            "UNKNOWN": "#dc3545",
            "INTRUDER": "#ff0000",
            "VEHICLE": "#007bff",
        }

        color = colors.get(
            obj.person_type,
            "#6c757d"
        )

        return format_html(
            '''
            <span style="
                background:{};
                color:white;
                padding:4px 8px;
                border-radius:12px;
                font-weight:bold;
            ">
                {}
            </span>
            ''',
            color,
            obj.person_type
        )

    person_badge.short_description = "Type"

    def snapshot_preview(self, obj):

        if obj.snapshot_url:

            return format_html(
                """
                <img
                    src="{}"
                    width="80"
                    style="
                        border-radius:8px;
                        border:1px solid #ddd;
                    "
                />
                """,
                obj.snapshot_url
            )

        return "-"

    snapshot_preview.short_description = "Snapshot"

    def large_snapshot(self, obj):

        if obj.snapshot_url:

            return format_html(
                """
                <img
                    src="{}"
                    width="450"
                    style="
                        border-radius:10px;
                        border:1px solid #ccc;
                    "
                />
                """,
                obj.snapshot_url
            )

        return "No Image Available"

    large_snapshot.short_description = "Captured Evidence"
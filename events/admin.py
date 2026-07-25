# app/admin.py — add/replace the DetectionEvent registration

from django.contrib import admin
from django.utils.html import format_html

from app.infrastructure.db.models.detection_event_model import DetectionEvent


@admin.register(DetectionEvent)
class DetectionEventAdmin(admin.ModelAdmin):
    # --- List view: the columns you see on /admin/app/detectionevent/ ---
    list_display = [
        "timestamp", "status", "event_type", "person_type", "person_label",
        "camera_location", "confidence_score", "is_enriched",
        "thumbnail_preview", "has_clip", "summary_preview",
    ]
    list_filter = ["status", "event_type", "person_type", "is_enriched", "camera_location"]
    search_fields = ["person_label", "camera_location", "event_summary", "track_id"]
    ordering = ["-timestamp"]

    # --- Detail view: what you see when you click into one event ---
    readonly_fields = [
        "id", "created_at", "clip_preview", "thumbnail_full_preview", "event_summary",
    ]
    fields = [
        "id", "home", "device", "track_id",
        "status", "pipeline_stage",
        "event_type", "person_type", "person_label", "matched_member", "matched_face",
        "confidence_score", "camera_location",
        "thumbnail_full_preview", "clip_preview",
        "event_summary",
        "clip_url", "thumbnail_url", "image_url", "snapshot_url",
        "started_at", "last_seen_at", "ended_at", "duration_seconds", "timestamp",
        "metadata", "is_enriched", "created_at",
    ]

    # ---- List view helpers ----
    def thumbnail_preview(self, obj):
        if not obj.thumbnail_url:
            return "—"
        return format_html(
            '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:4px;" />',
            obj.thumbnail_url,
        )
    thumbnail_preview.short_description = "Thumb"

    def has_clip(self, obj):
        return bool(obj.clip_url)
    has_clip.boolean = True
    has_clip.short_description = "Clip?"

    def summary_preview(self, obj):
        if not obj.event_summary:
            return "—"
        text = obj.event_summary
        return text if len(text) <= 60 else text[:57] + "..."
    summary_preview.short_description = "AI Summary"

    # ---- Detail view helpers ----
    def thumbnail_full_preview(self, obj):
        if not obj.thumbnail_url:
            return "No thumbnail attached"
        return format_html(
            '<a href="{0}" target="_blank">'
            '<img src="{0}" style="max-height:220px;border-radius:8px;" />'
            '</a><div style="margin-top:4px;"><a href="{0}" target="_blank">{0}</a></div>',
            obj.thumbnail_url,
        )
    thumbnail_full_preview.short_description = "Thumbnail"

    def clip_preview(self, obj):
        if not obj.clip_url:
            return "No clip attached"
        return format_html(
            '<video controls style="max-width:420px;border-radius:8px;">'
            '<source src="{0}" type="video/mp4"></video>'
            '<div style="margin-top:4px;"><a href="{0}" target="_blank">{0}</a></div>',
            obj.clip_url,
        )
    clip_preview.short_description = "Clip"
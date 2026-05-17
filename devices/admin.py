from django.contrib import admin

from app.infrastructure.db.models.device_model import (
    Device,
)

from app.infrastructure.db.models.smart_lock_model import (
    SmartLock,
)

from app.infrastructure.db.models.access_log_model import (
    AccessLog,
)


admin.site.register(Device)
admin.site.register(SmartLock)
admin.site.register(AccessLog)
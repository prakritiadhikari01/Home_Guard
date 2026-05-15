from django.contrib import admin

from app.infrastructure.db.models.home_model import Home
from app.infrastructure.db.models.home_member_model import HomeMember


admin.site.register(Home)
admin.site.register(HomeMember)
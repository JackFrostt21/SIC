from django.contrib import admin
from .models import DirectoryServices, Applications, BuildingEriell, FloorEriell, BlockEriell, TelegramUser

admin.site.register(TelegramUser)
admin.site.register(DirectoryServices)
admin.site.register(Applications)
admin.site.register(BuildingEriell)
admin.site.register(FloorEriell)
admin.site.register(BlockEriell)
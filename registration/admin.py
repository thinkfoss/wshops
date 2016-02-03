from django.contrib import admin
from registration.models import *

class UserAdmin(admin.ModelAdmin):
    search_fields = ('email', 'username' )
    list_display = ('email', 'date_joined')
admin.site.register(User, UserAdmin)


class EventAdmin(admin.ModelAdmin):
    pass
admin.site.register(Event, EventAdmin)


class EventModulesAdmin(admin.ModelAdmin):
    pass
admin.site.register(EventModules, EventModulesAdmin)


class EventModuleReviewAdmin(admin.ModelAdmin):
    pass
admin.site.register(EventModuleReview, EventModuleReviewAdmin)
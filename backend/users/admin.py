from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    search_fields = ('username', 'email')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)

from django.contrib import admin

from .models import SubscribeUser, User


class UserAdmin(admin.ModelAdmin):

    list_display = ('id', 'first_name', 'last_name', 'username', 'email')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
    empty_value_display = '-empty-'


class SubscribeUserAdmin(admin.ModelAdmin):

    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(SubscribeUser, SubscribeUserAdmin)

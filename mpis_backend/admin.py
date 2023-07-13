from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserCreationForm
from django.contrib import admin
from .models import *


@admin.register(Jimbo)
class JimboAdmin(admin.ModelAdmin):
    list_display = ('jina_la_jimbo', 'mkoa')
    search_fields = ['jina_la_jimbo']
    ordering = ['jina_la_jimbo']


@admin.register(Sekta)
class SektaAdmin(admin.ModelAdmin):
    pass


@admin.register(RC)
class RCAdmin(admin.ModelAdmin):
    pass


@admin.register(Maoni)
class MaoniAdmin(admin.ModelAdmin):
    list_display = ['maoni', 'status']
    pass


class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm

    list_display = ('username',)
    list_filter = ('is_admin',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_admin',)})
    )
    search_fields = ('username',)
    ordering = ('username',)

    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)

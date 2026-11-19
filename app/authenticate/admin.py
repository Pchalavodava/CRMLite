from django.contrib import admin

from .models import User, Company, Storage


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'inn')
    search_fields = ('title',)


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'company')
    list_filter = ('company',)
    search_fields = ('address', 'company__title')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        # 'first_name',
        # 'last_name',
        'username',
        'company',
        'is_company_owner',
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
    )

    list_display_links = ('id', 'email')

    ordering = ('id',)

    fields = (
        'email',
        # 'first_name',
        # 'last_name',
        'username',
        'company',
        'is_company_owner',
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
    )

    readonly_fields = ('date_joined',)
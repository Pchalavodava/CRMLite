# from django.contrib import admin
#
# from .models import User
#
#
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('id', 'email', 'is_active', 'is_superuser')
#     list_display_links = ('id', 'email')
#

from django.contrib import admin

from .models import User, Company, Storage


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'inn')
    search_fields = ('title',)


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'company_id', 'company__title')
    list_filter = ('company_id',)
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

    # Поля, по которым можно перейти к редактированию
    list_display_links = ('id', 'email')
    #
    # # Поля для поиска
    # search_fields = ('email', 'first_name', 'last_name')
    #
    # # Фильтры справа
    # list_filter = ('is_active', 'is_staff', 'is_superuser')

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
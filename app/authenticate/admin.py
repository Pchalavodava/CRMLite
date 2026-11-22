from django.contrib import admin

from .models import User, Company, Storage, Supplier, Supply, Product, SupplyProduct, Sale, ProductSale


# ______________________Company___________________________
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'inn')
    search_fields = ('title',)


# ______________________Storage___________________________
@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'company')
    list_filter = ('company',)
    search_fields = ('address', 'company__title')


# ______________________Supplier___________________________
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'title', 'inn')
    list_filter = ('company',)
    search_fields = ('title', 'inn', 'company__title')


# _______________________SupplyProduct__________________________

class SupplyProductInline(admin.TabularInline):
    model = SupplyProduct
    extra = 1
    autocomplete_fields = ('product',)


# __________________________Supply_____________________________
@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier_id', 'delivery_date')
    list_filter = ('delivery_date',)
    search_fields = ('supplier_id', )
    readonly_fields = ('delivery_date',)
    inlines = (SupplyProductInline,)


# ______________________Product___________________________
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'purchase_price', 'sale_price', 'quantity', 'storage_id')
    list_filter = ('title',)
    search_fields = ('title', 'storage_id')
    readonly_fields = ('quantity',)


# _________________________ProductSale_______________________
class ProductSaleInLine(admin.TabularInline):
    model = ProductSale
    extra = 1
    autocomplete_fields = ('product',)


# _______________________Sale______________________________
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer_name', 'company', 'sale_date')
    list_filter = ('sale_date',)
    inlines = (ProductSaleInLine,)


# __________________________User___________________________

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
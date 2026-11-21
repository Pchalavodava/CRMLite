from django.urls import path
from .views import CreateUserView, DeleteUserView, GetUserView, LoginView, LogoutView, RefreshView, CreateCompanyView, \
    DeleteCompanyView, GetCompanyView, UpdateCompanyView, GetStorageView, CreateStorageView, UpdateStorageView, \
    DeleteStorageView, CreateSupplierView, GetSuppliersView, UpdateSupplierView, DeleteSupplierView, GetProductListView, \
    GetProductView, UpdateProductView, DeleteProductView, CreateProductView, CreateSupplyView, SupplyListView, \
    AttachUserToCompanyView

urlpatterns = [
    path("create/", CreateUserView.as_view(), name="create-user"),
    path("delete/<int:id>/", DeleteUserView.as_view(), name="delete-user"),
    path("get/<int:id>/", GetUserView.as_view(), name="get-user"),

    path("company/create/", CreateCompanyView.as_view(), name="company-create"),
    path("company/<int:id>/delete/", DeleteCompanyView.as_view(), name="delete-company"),
    path("company/<int:id>/", GetCompanyView.as_view(), name="get-company"),
    path("company/<int:id>/update/", UpdateCompanyView.as_view(), name="update-company"),
    path("company/users/<int:user_id>/attach/", AttachUserToCompanyView.as_view(), name="attach-user-to-company"),

    path("storages/", GetStorageView.as_view(), name="storages"),
    path("storages/create/", CreateStorageView.as_view(), name="storage-create"),
    path("storages/<int:id>/update/", UpdateStorageView.as_view(), name="storage-update"),
    path("storages/<int:id>/delete/", DeleteStorageView.as_view(), name="storage-delete"),

    # ______________________Supplier___________________________
    path("suppliers/", GetSuppliersView.as_view(), name="suppliers"),
    path("suppliers/create/", CreateSupplierView.as_view(), name="supplier-create"),
    path("suppliers/<int:id>/update/", UpdateSupplierView.as_view(), name="supplier-update"),
    path("suppliers/<int:id>/delete/", DeleteSupplierView.as_view(), name="supplier-delete"),

    # ___________________________Products_______________________________
    path("products/", GetProductListView.as_view(), name="products"),
    path("products/create/", CreateProductView.as_view(), name="create-product"),
    path("products/<int:id>/", GetProductView.as_view(), name="get-product"),
    path("products/<int:id>/update/", UpdateProductView.as_view(), name="update-product"),
    path("products/<int:id>/delete/", DeleteProductView.as_view(), name="delete-product"),

    # ___________________________Supply_______________________________
    path("supplies/", SupplyListView.as_view(), name="supplies-list"),
    path("supplies/create/", CreateSupplyView.as_view(), name="create-supply"),

    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('refresh/', RefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='token_blacklist'),
]

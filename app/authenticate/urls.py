from django.urls import path
from .views import CreateUserView, DeleteUserView, GetUserView, LoginView, LogoutView, RefreshView, CreateCompanyView, \
    DeleteCompanyView, GetCompanyView, UpdateCompanyView, GetStorageView, CreateStorageView, UpdateStorageView, \
    DeleteStorageView

urlpatterns = [
    path("create/", CreateUserView.as_view(), name="create-user"),
    path("delete/<int:id>/", DeleteUserView.as_view(), name="delete-user"),
    path("get/<int:id>/", GetUserView.as_view(), name="get-user"),

    path("company/create/", CreateCompanyView.as_view(), name="company-create"),
    path("company/<int:id>/delete/", DeleteCompanyView.as_view(), name="delete-company"),
    path("company/<int:id>/", GetCompanyView.as_view(), name="get-company"),
    path("company/<int:id>/update/", UpdateCompanyView.as_view(), name="update-company"),

    path("storages/", GetStorageView.as_view(), name="storages"),
    path("storages/create/", CreateStorageView.as_view(), name="storage-create"),
    path("storages/<int:id>/update/", UpdateStorageView.as_view(), name="storage-update"),
    path("storages/<int:id>/delete/", DeleteStorageView.as_view(), name="storage-delete"),

    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('refresh/', RefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='token_blacklist'),
]

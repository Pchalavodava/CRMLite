from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

BASE_API_V1_PREFIX = 'api/v1'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'{BASE_API_V1_PREFIX}/users/', include('authenticate.urls')),
    path(f'{BASE_API_V1_PREFIX}/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(f'{BASE_API_V1_PREFIX}/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path(f'{BASE_API_V1_PREFIX}/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # path(f'{BASE_API_V1_PREFIX}/auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    # path(f'{BASE_API_V1_PREFIX}/auth/refresh/', RefreshView.as_view(), name='token_refresh'),
    # path(f'{BASE_API_V1_PREFIX}/auth/logout/', LogoutView.as_view(), name='token_blacklist'),
]

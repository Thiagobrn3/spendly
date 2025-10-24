from django.contrib import admin
from django.urls import path, include
from tracker.views import SignUpView # Importamos nuestra vista de registro

urlpatterns = [
    path('admin/', admin.site.urls),

    # URLs de nuestra app 'tracker' (la homepage)
    path('', include('tracker.urls')),

    # URLs de Autenticación de Django
    # path('accounts/login/', ...) -> Vista de Login (usa login.html)
    # path('accounts/logout/', ...) -> Vista de Logout
    # ...y otras (cambio de contraseña, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Nuestra URL de Registro personalizada
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
]
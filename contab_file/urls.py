# contab_file/urls.py (ou o nome do seu projeto)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URL raiz - redireciona para login
    path('', RedirectView.as_view(url='/usuarios/login/'), name='index'),
    
    # Apps
    path('usuarios/', include('usuarios.urls')),  # Mude de 'lista_pedidos' para 'usuarios'
    path('', include('documentos.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
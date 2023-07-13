from django.urls import path, include
from mpis_backend.views import SektaListView, maoni, reply, send_message, upload_data_from_file, upload_data_sekta
from django.conf import settings
from django.conf.urls.static import static

app_name = 'mpis_backend'
urlpatterns = [
    path('sekta/', SektaListView.as_view(), name='sekta-list'),
    path('maoni/', maoni, name='maoni'),
    path('add-data/', upload_data_from_file, name='add-data'),
    path('add-sekta/', upload_data_sekta, name='add-sekta'),
    path('reply/<pk>/', reply, name='reply'),
    path('send-message/<pk>/', send_message, name='send-msg'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)

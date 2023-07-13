from mpis_backend.serializers import MajimboSerializer
from mpis_backend.models import Jimbo
from rest_framework import status
from rest_framework import generics


class ListOrCreateJimbo(generics.ListCreateAPIView):
    serializer_class = MajimboSerializer
    queryset = Jimbo.objects.all()

    def get_queryset(self):
        return self.queryset.filter(mkoa=self.kwargs.get('mkoa'))

from rest_framework import serializers
from mpis_backend.models import Jimbo


class MajimboSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jimbo
        fields = ['jina_la_jimbo', ]


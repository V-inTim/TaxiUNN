from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Client
        fields = ['email', 'password']

    def create(self, validated_data):
        user = Client.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

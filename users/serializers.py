from rest_framework import serializers

from users.models import AnonUser


class AnonUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def create(self, validated_data):
        return AnonUser.objects.get_or_create(id=validated_data['id'])

    def update(self, instance, validated_data):
        pass

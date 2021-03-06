from django.contrib.auth import login
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import AnonUser, CustomToken
from users.serializers import AnonUserSerializer
from django.utils import timezone


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = AnonUserSerializer

    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = serializer.save()
        token = CustomToken.objects.create(user=user, created=timezone.now())
        return Response({'token': token.key})

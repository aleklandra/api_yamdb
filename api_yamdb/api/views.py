from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from .permissions import (IsAdmin)
from .serializers import (ConfirmationCodeSerializer, UserCreationSerializer, 
                          UserSerializer, ConfirmationCodeSerializer, 
                          MeSerializer)

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    serializer = UserCreationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.data['email']
    username = serializer.data['username']

    user, created = User.objects.get_or_create(email=email, username=username)

    confirmation_code = default_token_generator.make_token(user)

    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    serializer = ConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.data.get('username')
    confirmation_code = serializer.data.get('confirmation_code')

    user = get_object_or_404(User, username=username)

    if default_token_generator.check_token(user, confirmation_code):
        token = AccessToken.for_user(user)
        return Response(
            {'token': str(token)}, status=status.HTTP_200_OK
        )

    return Response({'confirmation_code': 'Неверный код подтверждения'},
                    status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)

    @action(
        detail=False,
        methods=('get', 'patch'),
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action == 'me':
            return MeSerializer
        return super().get_serializer_class()

from django.contrib.auth.models import User
from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers import UserSerializer, LoginSerializer, UserInfoSerializer, UserDetailedSerializer
from ..permissions import IsOwnerOrReadOnly


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)

            return Response({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return UserInfoSerializer
        elif self.action == 'retrieve':
            return UserDetailedSerializer
        return UserSerializer

    def perform_update(self, serializer):
        if self.request.user == self.get_object():
            serializer.save()
        else:
            raise permissions.PermissionDenied(
                "You do not have permission to edit this profile.")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop(
            'partial',
            False
        )

        if request.data.keys() != ['password', 'email', 'username']:
            partial = True

        if 'password' in request.data and not request.data['password']:
            request.data.pop('password')
            partial = True

        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

from knox.models import AuthToken
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


class MobileRegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        _, token = AuthToken.objects.create(user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token,
        }, status=status.HTTP_201_CREATED)


class MobileLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        _, token = AuthToken.objects.create(user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token,
        })


class MobileLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Knox: 現在のトークンだけ削除（他の端末に影響しない）
        request._auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MobileMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        user = request.user
        request._auth.delete()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

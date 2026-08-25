from django.contrib.auth import authenticate
from rest_framework import serializers

from config.content_moderation import find_objectionable_phrase
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'display_name', 'bio', 'avatar_url', 'role', 'date_joined']
        read_only_fields = ['id', 'username', 'role', 'date_joined']

    def _validate_public_text(self, value):
        if find_objectionable_phrase(value):
            raise serializers.ValidationError(
                '他の利用者を傷つける可能性のある表現が含まれています。表現を変えてください。'
            )
        return value

    def validate_display_name(self, value):
        return self._validate_public_text(value)

    def validate_bio(self, value):
        return self._validate_public_text(value)


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('このユーザー名は既に使用されています。')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('このメールアドレスは既に使用されています。')
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'パスワードが一致しません。'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError('ユーザー名またはパスワードが正しくありません。')
        if not user.is_active:
            raise serializers.ValidationError('このアカウントは無効です。')
        data['user'] = user
        return data

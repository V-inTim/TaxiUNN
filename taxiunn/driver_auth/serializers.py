from typing import Optional

from rest_framework import serializers

from .models import Driver


class BaseDriverSerializer(serializers.ModelSerializer):
    """Базовый сериалайзер для водителя."""

    email = serializers.EmailField(write_only=True)

    def validate_email(self, value: str) -> Optional[str]:
        """Валидация email (что пользователь с таким email ещё не создан)."""
        if Driver.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exist!",
            )
        return value


class DriverRegisterSerializer(BaseDriverSerializer):
    """Сериалайзер для регистрации водителя."""

    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(write_only=True)

    class Meta:
        model = Driver
        fields = ['email', 'password', 'full_name']

    def create(self, validated_data: dict) -> Driver:
        """Создание объекта класса Driver."""
        user = Driver.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
        )
        return user


class DriverVerifyRegisterSerializer(serializers.ModelSerializer):
    """Сериалайзер для верификации регистрации водителя."""

    verification_code = serializers.CharField(write_only=True)

    class Meta:
        model = Driver
        fields = ['email', 'verification_code']


class DriverLoginSerializer(serializers.ModelSerializer):
    """Сериалайзер входа в учётную запись."""

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Driver
        fields = ['email', 'password']

    def validate_email(self, value: str) -> Optional[str]:
        """Валидация email (что пользователь с таким email существует)."""
        if not Driver.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email does not exist!",
            )
        return value


class PasswordRecoverySerializer(serializers.ModelSerializer):
    """Сериалайзер восстановления пароля для водителя."""

    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Driver
        fields = ['email']

    def validate_email(self, value: str) -> Optional[str]:
        """Валидация email (что пользователь с таким email существует)."""
        if not Driver.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email does not exist!",
            )
        return value


class DriverPasswordRecoveryVerifySerializer(PasswordRecoverySerializer):
    """Сериалайзер верификации восстановления пароля для водителя."""

    verification_code = serializers.CharField(write_only=True)

    class Meta(PasswordRecoverySerializer.Meta):
        fields = PasswordRecoverySerializer.Meta.fields + ['verification_code']


class DriverPasswordRecoveryChangeSerializer(PasswordRecoverySerializer):
    """Сериалайзер изменения пароля водителя."""

    password = serializers.CharField(write_only=True)

    class Meta(PasswordRecoverySerializer.Meta):
        fields = PasswordRecoverySerializer.Meta.fields + ['password']

    def save(self) -> Driver:
        """Метод сохранения нового пароля."""
        user = Driver.objects.get(
            email=self.validated_data.get('email'),
        )

        user.set_password(
            self.validated_data['password'],
        )

        user.save()
        return user

"""DRF serializers for the accounts app."""

from django.contrib.auth import password_validation, update_session_auth_hash
from rest_framework import serializers

from .models import User, UserProfile


# ── Profile (nested) ────────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id",
            "display_name",
            "bio",
            "avatar_url",
            "timezone",
            "locale",
            "onboarding_completed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ── User read ───────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    """Read-only representation of a user (safe for listing/detail)."""

    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_email_verified",
            "phone_number",
            "date_of_birth",
            "date_joined",
            "last_login",
            "is_active",
            "profile",
        ]
        read_only_fields = fields


# ── User create (registration) ──────────────────────────────────────

class UserCreateSerializer(serializers.ModelSerializer):
    """Handles user registration with password confirmation."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "password",
            "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        password_validation.validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        return UserSerializer(instance, context=self.context).data


# ── User update (profile edits) ─────────────────────────────────────

class UserUpdateSerializer(serializers.ModelSerializer):
    """Partial-update serializer for the current user's own account."""

    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "phone_number",
            "date_of_birth",
            "profile",
        ]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data and hasattr(instance, "profile"):
            for attr, value in profile_data.items():
                setattr(instance.profile, attr, value)
            instance.profile.save()

        return instance

    def to_representation(self, instance):
        return UserSerializer(instance, context=self.context).data


# ── Password change (authenticated) ────────────────────────────────

class PasswordChangeSerializer(serializers.Serializer):
    """Change password for an authenticated user (requires current password)."""

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match."}
            )
        password_validation.validate_password(attrs["new_password"])
        return attrs

    def save(self, **kwargs):
        request = self.context["request"]
        user = request.user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        # Keep current session valid; invalidate all other sessions.
        update_session_auth_hash(request, user)
        return user


# ── Password reset (unauthenticated, request step) ──────────────────

class PasswordResetSerializer(serializers.Serializer):
    """Request a password-reset email. Always succeeds to prevent enumeration."""

    email = serializers.EmailField()

    def validate_email(self, value):
        # Normalise to lowercase; actual sending is handled in the view.
        return value.lower()

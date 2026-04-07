"""DRF views for the accounts app."""

from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User
from .serializers import (
    PasswordChangeSerializer,
    PasswordResetSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """CRUD operations for users.

    - Admin users can list / retrieve / delete any user.
    - Regular authenticated users can only create (register).
    - Detail actions (retrieve/update/delete) for your own account should
      go through MeView instead.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from guardian.conf import settings as guardian_settings

        return (
            User.objects.filter(is_active=True)
            .exclude(email=guardian_settings.ANONYMOUS_USER_NAME)
            .select_related("profile")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ("update", "partial_update"):
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        if self.action in ("list", "retrieve", "update", "partial_update", "destroy"):
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=["post"],
        url_path="password-reset",
        permission_classes=[permissions.AllowAny],
        serializer_class=PasswordResetSerializer,
    )
    def password_reset(self, request):
        """Request a password-reset email (always returns 200)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # In production: dispatch an async email task here.
        return Response(
            {"detail": "If that email exists, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )


class MeView(generics.RetrieveUpdateAPIView):
    """GET / PATCH the currently authenticated user's own account."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return User.objects.select_related("profile").get(pk=self.request.user.pk)

    @action(detail=False, methods=["post"])
    def change_password(self, request):
        """Change the current user's password."""
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )


class PasswordChangeView(generics.GenericAPIView):
    """Standalone endpoint for authenticated password changes."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )

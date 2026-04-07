"""Django Ninja router for the accounts app."""

from typing import Optional
from uuid import UUID

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.errors import HttpError

from .models import User, UserProfile

router = Router(tags=["Accounts"])


# ── Schemas ──────────────────────────────────────────────────────────

class UserProfileOut(Schema):
    id: UUID
    display_name: str
    bio: str
    avatar_url: str
    timezone: str
    locale: str
    onboarding_completed: bool


class UserOut(Schema):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_email_verified: bool
    phone_number: str
    date_of_birth: Optional[str] = None
    profile: Optional[UserProfileOut] = None


class UserCreateIn(Schema):
    email: str
    username: str
    password: str
    password_confirm: str
    first_name: str = ""
    last_name: str = ""
    phone_number: str = ""
    date_of_birth: Optional[str] = None


class UserUpdateIn(Schema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
    onboarding_completed: Optional[bool] = None


class PasswordChangeIn(Schema):
    current_password: str
    new_password: str
    new_password_confirm: str


class PasswordResetIn(Schema):
    email: str


class MessageOut(Schema):
    detail: str


# ── Endpoints ────────────────────────────────────────────────────────

@router.post("/users/", response={201: UserOut}, auth=None)
def register(request, payload: UserCreateIn):
    """Register a new user account."""
    if payload.password != payload.password_confirm:
        raise HttpError(422, "Passwords do not match.")
    try:
        password_validation.validate_password(payload.password)
    except DjangoValidationError as exc:
        raise HttpError(422, " ".join(exc.messages))

    data = payload.dict(exclude={"password", "password_confirm"})
    user = User(**data)
    user.set_password(payload.password)
    user.save()
    return 201, user


@router.get("/users/", response=list[UserOut])
def list_users(request):
    """List all users (admin only)."""
    if not request.user.is_staff:
        raise HttpError(403, "Admin access required.")
    return User.objects.select_related("profile").all()


@router.get("/users/{user_id}/", response=UserOut)
def get_user(request, user_id: int):
    """Retrieve a specific user by ID (admin only)."""
    if not request.user.is_staff:
        raise HttpError(403, "Admin access required.")
    user = get_object_or_404(User.objects.select_related("profile"), pk=user_id)
    return user


@router.get("/me/", response=UserOut)
def me(request):
    """Get the current authenticated user."""
    return User.objects.select_related("profile").get(pk=request.user.pk)


@router.patch("/me/", response=UserOut)
def update_me(request, payload: UserUpdateIn):
    """Update the current authenticated user's account and profile."""
    user = User.objects.select_related("profile").get(pk=request.user.pk)

    user_fields = {"first_name", "last_name", "username", "phone_number", "date_of_birth"}
    profile_fields = {"display_name", "bio", "avatar_url", "timezone", "locale", "onboarding_completed"}

    data = payload.dict(exclude_unset=True)

    user_updates = {k: v for k, v in data.items() if k in user_fields}
    if user_updates:
        for attr, value in user_updates.items():
            setattr(user, attr, value)
        user.save(update_fields=list(user_updates.keys()))

    profile_updates = {k: v for k, v in data.items() if k in profile_fields}
    if profile_updates and hasattr(user, "profile"):
        for attr, value in profile_updates.items():
            setattr(user.profile, attr, value)
        user.profile.save(update_fields=list(profile_updates.keys()))

    user.refresh_from_db()
    return user


@router.post("/me/password/", response=MessageOut)
def change_password(request, payload: PasswordChangeIn):
    """Change the current user's password."""
    user = request.user
    if not user.check_password(payload.current_password):
        raise HttpError(400, "Current password is incorrect.")
    if payload.new_password != payload.new_password_confirm:
        raise HttpError(422, "New passwords do not match.")
    try:
        password_validation.validate_password(payload.new_password)
    except DjangoValidationError as exc:
        raise HttpError(422, " ".join(exc.messages))

    user.set_password(payload.new_password)
    user.save(update_fields=["password"])
    return {"detail": "Password updated successfully."}


@router.post("/password-reset/", response=MessageOut, auth=None)
def password_reset(request, payload: PasswordResetIn):
    """Request a password-reset email (always returns 200 to prevent enumeration)."""
    # In production: dispatch an async email task here.
    return {"detail": "If that email exists, a reset link has been sent."}

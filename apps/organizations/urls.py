"""URL configuration for the organizations app.

Provides nested routes:
  /organizations/                               - list / create orgs
  /organizations/<slug>/                        - retrieve / update / delete org
  /organizations/<slug>/members/                - list members
  /organizations/<slug>/members/<pk>/           - update / remove member
  /organizations/<slug>/invites/                - list / create invites
  /organizations/<slug>/invites/<pk>/           - retrieve / delete invite
  /organizations/<slug>/invites/<pk>/revoke/    - revoke invite
  /organizations/<slug>/invites/accept/<token>/ - accept invite
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InviteViewSet, MembershipViewSet, OrganizationViewSet

app_name = "organizations"

router = DefaultRouter()
router.register(r"", OrganizationViewSet, basename="organization")

# Nested routers for members and invites under an organization
member_router = DefaultRouter()
member_router.register(r"", MembershipViewSet, basename="membership")

invite_router = DefaultRouter()
invite_router.register(r"", InviteViewSet, basename="invite")

urlpatterns = [
    path(
        "<slug:organization_slug>/members/",
        include(member_router.urls),
    ),
    path(
        "<slug:organization_slug>/invites/",
        include(invite_router.urls),
    ),
    path("", include(router.urls)),
]

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    オブジェクトの所有者のみ編集可能。
    obj.user または obj.created_by で判定。
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, 'user', None) or getattr(obj, 'created_by', None)
        return owner == request.user


class IsShopUser(permissions.BasePermission):
    """
    店舗ユーザーのみアクセス可能。
    Phase2 の店舗ダッシュボード等で使用。
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ('shop', 'admin')
        )

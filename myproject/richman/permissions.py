from rest_framework import permissions


class CheckUserEdit(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.id


class CheckEdit(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner


class CheckProductEdit(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.group.owner


class CheckProductSizeEdit(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.product.group.owner


from rest_framework import permissions

# 관리자만 정보글을 생성할수 있게
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):

        # GET은 모두가 접근 가능
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # POST는 관리자만 접근 가능
        return request.user and request.user.is_staff
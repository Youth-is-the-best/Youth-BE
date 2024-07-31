from rest_framework import permissions
from .models import Bingo

class IsValidLoc(permissions.BasePermission):
    def has_permission(self, request, view):
        location_on_bingo_board = request.parser_context['kwargs'].get('location')
        
        try:
            location_on_bingo_board = int(location_on_bingo_board)
            
            bingo = Bingo.objects.get(user=request.user, is_active=True)
            
            bingo_size = bingo.size  # 경우에 따라 9 또는 16
            
            if location_on_bingo_board in range(bingo_size):
                return True
            else:
                raise ValueError
        except Exception as e:
            return False
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def current_user(request):
    user = request.user
    if user.is_anonymous:
        return Response({
                'username': '-',
                'fullname': '-',
                'email': '-',
                'is_anonymous': True
            })
    return Response({
        'username': user.username,
        'fullname': user.get_full_name(),
        'email': user.email,
        'is_anonymous': False
    })
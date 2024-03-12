from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import CustomUserSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    API endpoint for user registration (signup).

    Request:
    - Method: POST
    - Requires 'username' and 'password' fields in the request data.

    Response:
    - Returns a token and user_id if the user is registered successfully.
    - If 'username' or 'password' is missing or invalid, returns a 400 status with an error message.
    """
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        login(request, user)

        return Response({'token': token.key, 'user_id': user.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.authtoken.models import Token

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """
    API endpoint for user login.

    Request:
    - Method: POST
    - Requires 'username' and 'password' fields in the request data.

    Response:
    - Returns a token and user_id if the login is successful.
    - If 'username' or 'password' is incorrect, returns a 401 status with an error message.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Both username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        login(request, user)

        return Response({'token': token.key, 'user_id': user.id}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """
    API endpoint for user logout.

    Request:
    - Method: POST
    - Requires authentication.

    Response:
    - Deletes the authentication token and logs the user out.
    - Returns a success message if logout is successful.
    """
    request.auth.delete()
    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

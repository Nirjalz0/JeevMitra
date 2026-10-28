from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.views import APIView

class LoginView(ObtainAuthToken):
    permission_classes=[permissions.AllowAny]

    def post(self,request,  *args, **kwargs):
        serializer=self.serializer_class(data=request.data,context={'request':request})

        if not serializer.is_valid(): return Response( { 'message': 'Invalid username or password.', 'errors': serializer.errors })
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        token, _ =Token.objects.get_or_create(user=user)
        return Response({
            'token':token.key,
            'id': user.id,
            'username':user.username,
            'role': user.role,
            'is_verified': user.is_verified,
            
        })
class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response({'detail':'Logged out.'})


# Create your views here.

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import permissions,generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from .models import User
from .permissions import IsAdminRole
from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset=User.objects.all()
    serializer_class=RegisterSerializer
    permission_classes=[permissions.AllowAny]

class LoginView(ObtainAuthToken):
    permission_classes=[permissions.AllowAny]

    def post(self,request,  *args, **kwargs):
        serializer=self.serializer_class(data=request.data,context={'request':request})

        if not serializer.is_valid(): return Response( { 'message': 'Invalid username or password.', 'errors': serializer.errors },
                                                      status=status.HTTP_400_BAD_REQUEST
                                                      )

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
    
class MeView(generics.RetrieveAPIView):
    serializer_class=UserSerializer

    def get_object(self):
        return self.request.user

class pendingUsersView(generics.ListAPIView):
    serializer_class=UserSerializer
    permission_classes=[IsAdminRole]

    def get_queryset(self):
        return User.objects.filter(
            role__in=[User.Role.RESCUER,User.Role.SHELTER],
            is_verified=False,

        )
class VerifyUserView(APIView):
    permission_classes=[IsAdminRole]

    def post(self,request,pk):
        user =get_object_or_404(
            User, pk=pk, role__in=[User.Role.RESCUER, User.Role.SHELTER]  )
        user.is_verified=True
        user.save()
        return Response(UserSerializer(user).data)
# Create your views here.

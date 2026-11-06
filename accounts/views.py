from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import  permissions,generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from .models import User
from .permissions import IsAdminRole
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
    check_password_rules,

)



class RegisterView(generics.CreateAPIView):
    queryset=User.objects.all()
    serializer_class=RegisterSerializer
    permission_classes=[permissions.AllowAny]

class LoginView(TokenObtainPairView):
    serializer_class=LoginSerializer
      
   
            
        
class LogoutView(APIView):
    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response({'detail': 'Refresh token is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            return Response({'detail': 'Invalid or expired token.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Logged out.'})
    
class MeView(generics.RetrieveAPIView):
    serializer_class=UserSerializer

    def get_object(self):
        return self.request.user

class PendingUsersView(generics.ListAPIView):
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
    
class ChangePasswordView(APIView):
    """Logged in user changes their own password."""

    def post(self,request):
        serializer= ChangePasswordSerializer(
            data=request.data, context={'request':request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response ({'detail':'password changed.'})

class PasswordResetRequestView(APIView):
    """Step 1 of 'forgot password': email a reset link."""
    permission_classes=[permissions.AllowAny]

    def post(self, request):
        serializer=PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email=serializer.validated_data['email']

        user=User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = f'{settings.FRONTEND_URL}/reset-password/{uid}/{token}'
            send_mail(
                subject='Reset your Jeev Mitra password',
                message=f'Use this link to reset your password:\n\n{link}\n\n'
                        'If you did not ask for this, you can ignore this email.',
                from_email=None,
                recipient_list=[user.email],
            )
        # Same answer whether or not the email exists, so nobody can probe for accounts.
        return Response({'detail': 'If that email is registered, a reset link has been sent.'})


class PasswordResetConfirmView(APIView):
    """Step 2 of 'forgot password': set the new password using the link's uid and token."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(data['uid'])))
        except (ValueError, TypeError, OverflowError, User.DoesNotExist):
            user = None

        if user is None or not default_token_generator.check_token(user, data['token']):
            return Response(
                {'detail': 'Invalid or expired reset link.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        check_password_rules(data['new_password'], user)
        user.set_password(data['new_password'])
        user.save()
        return Response({'detail': 'Password has been reset.'})


# Create your views here.

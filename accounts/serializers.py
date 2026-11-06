from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password=serializers.CharField(write_only=True, min_length=10)

    class Meta:
        model=User
        fields=['id','username','email','password','role','phone']

    def validate_role(self,value):
        if value== User.Role.ADMIN:
            raise serializers.ValidationError('you cannot register as admin.')
        return value
    
    def validate_email(self,value):
        if not value:
            raise serializers.ValidationError('Email is required.')
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value
    
    def create(self,validated_data):
        password= validated_data.pop('password')
        user=User(**validated_data)
        user.set_password(password)

        # public users are verified right away; rescuers and shelters wait for admin approval

        user.is_verified = user.role == User.Role.PUBLIC
        user.save()
        return user



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','email','role','phone','is_verified']
        read_only_fields=fields
class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token=super().get_token(user)
        token['role']=user.role
        return token
    
    def validate(self, attrs):
        data=super().validate(attrs)
        data['id']=self.user.id
        data['username']=self.user.username
        data['role']=self.user.role
        data['is_verified']=self.user.is_verified
        return data 

def check_password_rules(password, user=None):
    try:
        validate_password(password, user)
    except DjangoValidationError as exc:
        raise serializers.ValidationError(list(exc.messages))
    return password

class ChangePasswordSerializer(serializers.Serializer):
    old_password=serializers.CharField(write_only=True)
    new_password=serializers.CharField(write_only=True,min_length=8)

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value

    def validate_new_password(self, value):
        return check_password_rules(value, self.context['request'].user)
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email =serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid=serializers.CharField()
    token=serializers.CharField()
    new_password=serializers.CharField(write_only=True,min_length=8)
    
    
    
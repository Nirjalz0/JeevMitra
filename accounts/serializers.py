from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True, min_length=10)

    class Meta:
        model=User
        fields=['id','username','email','password','role','phone']

    def validate_role(self,value):
        if value== User.Role.ADMIN:
            raise serializers.ValidateError('you cannot register as admin.')
        return value
    
    def validate_email(self,value):
        if not value:
            raise serializers.ValidationError('Email is required.')
        if User.objects.filter(email_iexact=value).exists():
            raise serializers.validationError('A user with this email already exists.')
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
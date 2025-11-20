from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(
        write_only=True, style={'input_type': 'password'})
    
    models = User
    fields = ['first_name', 'last_name', 'email',
              "password", "confirm_password"]
    
    read_only = ("user_id",)
    extra_kwargs = {
        "email" : {"required": True},
        "first_name" : {"required": True},
        "last_name" : {"required": True}
        }
    
    def validate(self, attrs):
        pw = attrs.get('password')
        pw_confirm = attrs.get('password')
        
        if pw != pw_confirm:
            raise serializers.ValidationError({"confirm_password": "Password do not match."})
        
        try:
            validate_password(pw, user=User(**{k: v for k, v in attrs.items() if k not in ("password", "confirm_password")}))
            
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})
        
        return attrs
 
   
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Most include email and password')       


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        pw = attrs.get('password')
        pw_confirm = attrs.get('password')
        
        if not pw or not pw_confirm:
            raise serializers.ValidationError({"detail": "Both password fields are required."})
        
        if pw != pw_confirm:
            raise serializers.ValidationError({"confirm_password": "password do not match."})
        
        try:
            validate_password(pw)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"new_password": list(exc.messages)})
        
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # Ensure new passwords match
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({
                "confirm_new_password": "Passwords do not match."
            })

        # Validate password strength
        try:
            validate_password(attrs['new_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                "new_password": list(e.messages)
            })

        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)

    def validate(self, attrs):
        self.token = attrs.get('refresh')
        if not self.token:
            raise serializers.ValidationError({'refresh': 'Refresh token is required.'})
        return attrs

    def save(self, **kwargs):
        """
        Blacklist the refresh token. Raises serializers.ValidationError if invalid.
        """
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError as e:
            raise serializers.ValidationError({'refresh': 'Invalid or expired token.'})
        

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "notifications_enabled",
        ]
        read_only_fields = ["id", "email"]
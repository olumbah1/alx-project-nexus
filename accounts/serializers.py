from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_password': 'password'})
    confirm_password = serializers.CharField(
        write_only=True, style={'input_password': 'password'})
    
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
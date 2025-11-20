from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from .serializers import (
    SignUpSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, 
    LogoutSerializer, ProfileSerializer, ChangePasswordSerializer
)
from .utils import send_password_reset_email
from rest_framework.views import APIView


User = get_user_model()


token_generator = PasswordResetTokenGenerator()


class SignupAPIView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # add custom claims if needed
        token['email'] = user.email
        token['user_id'] = str(user.user_id)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Optionally add user serialized info to response
        data.update({
            'user': {
                'user_id': str(self.user.user_id),
                'email': self.user.email,
                'business_name': self.user.business_name,
                'username': self.user.username,
            }
        })
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class LogoutAPIView(generics.GenericAPIView):
    """
    Logout by blacklisting provided refresh token.
    Request body: {"refresh": "<refresh_token>"}
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            # Blacklist this specific refresh token
            token.blacklist()
            return Response({'detail': 'Logout successful.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordAPIView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Always return generic response to avoid user enumeration
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Return generic message even if user not found
            return Response({'detail': 'If an account with that email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)

        # send email (uses settings for email backend)
        send_password_reset_email(user)
        return Response({'detail': 'If an account with that email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)


class ResetPasswordAPIView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            uid_decoded = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid_decoded)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Invalid uid/token.'}, status=status.HTTP_400_BAD_REQUEST)

        if not token_generator.check_token(user, token):
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        # set new password
        user.set_password(new_password)
        user.save()

        # OPTIONAL: blacklist all outstanding refresh tokens for this user (force logout of other sessions)
        try:
            for outstanding in OutstandingToken.objects.filter(user=user):
                # Blacklist each outstanding refresh token
                BlacklistedToken.objects.get_or_create(token=outstanding)
        except Exception:
            # If token blacklist app not enabled or no tokens, ignore
            pass

        return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]  # optionally require auth

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # attempts to blacklist
        return Response({'detail': 'Logout successful.'}, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"error": "Old password incorrect"}, status=400)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"message": "Password updated successfully"})

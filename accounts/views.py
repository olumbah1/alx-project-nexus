from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from .serializers import (
    SignUpSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, 
    LogoutSerializer, ProfileSerializer, ChangePasswordSerializer, MyTokenObtainPairSerializer
)
from .utils import send_password_reset_email
from rest_framework.views import APIView
from .utils import send_verification_email 

User = get_user_model()


token_generator = PasswordResetTokenGenerator()


class SignupAPIView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save()
        from .utils import send_verification_email
        send_verification_email(user)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class LogoutAPIView(generics.GenericAPIView):
    """
    Logout by blacklisting provided refresh token.
    Request body: {"refresh": "<refresh_token>"}
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer
    
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


class ResendVerificationAPIView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer  # re-use simple email serializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({'detail': 'If an account exists, a verification sent.'}, status=200)
        if user.is_verified:
            return Response({'detail': 'Email already verified.'}, status=200)
        send_verification_email(user)
        return Response({'detail': 'If an account exists, a verification sent.'}, status=200)


class ResetPasswordAPIView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        # Decode UID safely for UUID fields
        try:
            uid_bytes = urlsafe_base64_decode(uid)
            uid_str = uid_bytes.decode()
            user = User.objects.get(id=uid_str)   # UUID lookup MUST be string UUID
        except Exception:
            return Response({'detail': 'Invalid uid/token.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate token
        if not token_generator.check_token(user, token):
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        # Reset password
        user.set_password(new_password)
        user.save()

        # OPTIONAL: Blacklist old refresh tokens
        try:
            for outstanding in OutstandingToken.objects.filter(user=user):
                BlacklistedToken.objects.get_or_create(token=outstanding)
        except:
            pass

        return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)


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


class VerifyEmailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uid, token):
        try:
            user = User.objects.get(id=uid)  # directly use UUID
        except User.DoesNotExist:
            return Response({'detail': 'Invalid link.'}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({'detail': 'Invalid or expired token.'}, status=400)

        user.is_verified = True
        user.save()
        return Response({'detail': 'Email verified successfully.'})
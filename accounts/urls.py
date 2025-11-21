from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (SignupAPIView, MyTokenObtainPairView, LogoutAPIView,
                    ResetPasswordAPIView, ChangePasswordView, ProfileView, 
                    ForgotPasswordAPIView, VerifyEmailAPIView, ResendVerificationAPIView)


urlpatterns = [
    path('auth/signup/', SignupAPIView.as_view(), name='auth-signup'),
    path('auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutAPIView.as_view(), name='auth-logout'),
    path('auth/forgot-password/', ForgotPasswordAPIView.as_view(), name='auth-forgot-password'),
    path('resend-verification/', ResendVerificationAPIView.as_view(), name='resend-verification'),

    path('auth/reset-password/', ResetPasswordAPIView.as_view(), name='auth-reset-password'),
    path('auth/verify/<uuid:uid>/<str:token>/', VerifyEmailAPIView.as_view(), name='verify-email'),

    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/change-password/", ChangePasswordView.as_view(), name="change-password"),

]


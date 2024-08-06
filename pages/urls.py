from django.urls import path, re_path
from django.conf.urls import handler404

from . import views

urlpatterns = [
    path('', views.view_home, name='home'),
    path('test/', views.view_test, name='test'),
    path('test/color-scheme/', views.view_test_color_scheme, name='Test.ColorScheme'),
    path('auth/login/', views.view_user_login, name='Auth.Login'),
    path('profile/', views.view_user_profile, name='UserProfile'),
    path('api/class/resources/', views.view_class_resources, name='API.ClassResources'),
    path('api/dashboard/data/', views.api_dashboard_data, name='API.DashboardData'),
    path('api/user/parents/', views.api_user_parents, name='API.DashboardData'),
    path('api/user/information/', views.api_user_information, name='API.UserInformation'),
    re_path('api/user/photo/', views.api_user_photo, name='API.UserPhoto')
]

# handler404 = views.error_404
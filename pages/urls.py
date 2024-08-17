from django.urls import path, re_path
from django.conf.urls import handler404

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('test/color-scheme/', views.test_color_scheme, name='Test.ColorScheme'),
    path('auth/login/', views.user_login, name='Auth.Login'),
    path('auth/logout/', views.user_logout, name='Auth.Logout'),
    path('profile/', views.user_profile, name='UserProfile'),
    path('overview/', views.app_overview, name='Overview'),
    path('calendar/', views.app_calendar, name='Calendar'),
    path('api/class/resources/', views.class_resources, name='API.ClassResources'),
    path('api/dashboard/data/', views.api_dashboard_data, name='API.DashboardData'),
    path('api/user/parents/', views.api_user_parents, name='API.DashboardData'),
    path('api/user/information/', views.api_user_information, name='API.UserInformation'),
    path('api/class/color/', views.api_update_class_color, name='API.ClassColor'),
    path('api/user/photo/', views.api_user_photo, name='API.UserPhoto')
]

# handler404 = views.error_404
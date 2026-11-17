from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('upload/', views.upload, name='upload'),
    path('export/<int:pk>/', views.export_report, name='export_report'),
    path('delete/<int:pk>/', views.delete_dataset, name='delete_dataset'),
    path('api/datasets/', views.api_datasets, name='api_datasets'),
    path('api/datasets/<int:pk>/metrics/', views.api_metrics, name='api_metrics'),
    path('api/datasets/<int:pk>/ask/', views.api_ask, name='api_ask'),
    path('api/datasets/<int:pk>/insights/', views.api_insights, name='api_insights'),
    path('api/datasets/<int:pk>/ai-ask/', views.api_ai_ask, name='api_ai_ask'),
    path('api/datasets/<int:pk>/ai-summary/', views.api_ai_summary, name='api_ai_summary'),
]

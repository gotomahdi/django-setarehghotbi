from django.urls import path
from .views import(
				SignUpView ,
				Activate ,
				LoginView ,
				LogoutView ,
				ResetPasswordView ,
				ResetPasswordActivate
			)

app_name='account'

urlpatterns=[
	path('signup/',SignUpView,name='sign_up'),
	path('activate/<slug:uidb64>/<slug:token>/', Activate, name='activate'),

	path('PasswrodActivate/<slug:uidb64>/<slug:token>/', ResetPasswordActivate, name='reset_password_activate'),
	path('ResstPassword/',ResetPasswordView,name='reset_password'),

	path('login/', LoginView, name='login'),
	path('logout/', LogoutView, name='logout'),
] 

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
	description=models.TextField(verbose_name='user description',blank=True,max_length=500)
	is_auther=models.BooleanField(verbose_name='Is  user  author?',default=False)
	profile=models.ImageField(upload_to='media/account',verbose_name='user profile',null=True,default='static/account/images/user-profile.png')
	email=models.EmailField(blank=True,null=True, max_length=150, verbose_name='last name',error_messages={'unique':'email already exists'},unique=True)
	is_team=models.BooleanField(default=False,verbose_name='Is this user a team member?')
	telegram=models.URLField(max_length=200,blank=True,null=True,default=None,verbose_name='auther telegram')
	twitter=models.URLField(max_length=200,blank=True,null=True,default=None,verbose_name='auther twitter')
	github=models.URLField(max_length=200,blank=True,null=True,default=None,verbose_name='auther github')
	instagram=models.URLField(max_length=200,blank=True,null=True,default=None,verbose_name='auther instagram')
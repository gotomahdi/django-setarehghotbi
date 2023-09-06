from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth import get_user
from django.core import mail
from .models import User
import re 

# Create your tests here.


class AccountTest(TestCase):

	def setUp(self):
		self.user=User.objects.create_user(
				username='testusername',
				password='testpassword',
				email='testemail@gmail.com',
				is_active=True
			)
	
	def test_signup_view(self):

		data={
			'password1':'testpassword',
			'password2':'testpassword',
			'username':'testusername2',
			'email':'testemail2@gmail.com',

		}


		resp=self.client.post(reverse('account:sign_up'),data=data)
		message=list(get_messages(resp.wsgi_request))
		self.assertEqual(resp.status_code,200)
		self.assertEqual(len(message),1)
		self.assertEqual(str(message[0]),'پیامی حاوی لینک اهراز حویت به ایمیل شما ارسال شد.')
		self.assertTemplateUsed(resp,'account/registration/sign_up.html')
		self.assertEqual(User.objects.count(),2)


		data.pop('email')
		resp=self.client.post(reverse('account:sign_up'),data=data)
		self.assertEqual(resp.status_code,200)
		self.assertTemplateUsed(resp,'account/registration/sign_up.html')



		resp=self.client.get(reverse('account:sign_up'))
		self.assertEqual(resp.status_code,200)
		self.assertTemplateUsed(resp,'account/registration/sign_up.html')



	# Test token activation view
	def test_acitve_token_view(self):

		data={
			'password1':'testpassword',
			'password2':'testpassword',
			'username':'testusername1',
			'email':'testemail2@gmail.com',

		}


		resp=self.client.post(reverse('account:sign_up'),data=data)
		self.assertEqual(len(mail.outbox),1)

		toekn_acitvaiton_url=re.findall(r"http:\/\/\w+\/account\/activate\/\w+\/\w+-\w+\/",mail.outbox[0].body)[0]
		resp=self.client.get(toekn_acitvaiton_url)
		self.assertEqual(User.objects.get(username='testusername1').is_active,True)
		self.assertEqual(resp.status_code,200)



		resp=self.client.get(toekn_acitvaiton_url)
		self.assertEqual(resp.status_code,200)
		self.assertTemplateUsed(resp,'account/registration/activation_invalid.html')




	def test_login_view(self):

		data={'username':'testusername','password':'testpassword'}

		resp=self.client.post(reverse('account:login'),data=data)
		self.assertTrue(get_user(self.client).is_authenticated)
		self.assertRedirects(resp,reverse('blog:home'))


		data['username']='chert'
		resp=self.client.post(reverse('account:login'),data=data)
		message=list(get_messages(resp.wsgi_request))
		self.assertEqual(len(message),1)
		self.assertTemplateUsed(resp,'account/registration/login.html')
		self.assertEqual(resp.status_code,200)


		data.pop('username')
		resp=self.client.post(reverse('account:login'),data=data)
		self.assertTemplateUsed(resp,'account/registration/login.html')
		self.assertEqual(resp.status_code,200)

		resp=self.client.get(reverse('account:login'))
		self.assertTemplateUsed(resp,'account/registration/login.html')
		self.assertEqual(resp.status_code,200)






	def test_logout_view(self):

		resp=self.client.get(reverse('account:logout'))
		self.assertFalse(get_user(self.client).is_authenticated)
		self.assertRedirects(resp,reverse('blog:home'))



	def test_rest_password_view(self):

		resp=self.client.post(reverse('account:reset_password'),data={'email':self.user.email})
		message=list(get_messages(resp.wsgi_request))
		self.assertEqual(len(mail.outbox),1)
		self.assertEqual(len(message),1)
		self.assertEqual(str(message[0]),'پیامی حاوی لینک تغییر گذرواژه به ایمیل شما ارسال شد.')
		self.assertTemplateUsed(resp,'account/registration/rest_password_email.html')


		resp=self.client.post(reverse('account:reset_password'),data={'email':'cher@gmail.com'})
		message=list(get_messages(resp.wsgi_request))
		self.assertEqual(len(message),1)
		self.assertEqual(str(message[0]),'فردی با ایمیل وارد شده در سایت موجود نمی باشد')
		self.assertTemplateUsed(resp,'account/registration/rest_password_email.html')


		resp=self.client.get(reverse('account:reset_password'))
		self.assertTemplateUsed(resp,'account/registration/rest_password_email.html')




		def test_reset_password_acitvate_view(self):
			# Make a token and test ResetPasswordActivate view when everythin is OK. 			
			resp=self.client.post(reverse('account:reset_password'),data={'email':self.user.email})
			self.assertEqual(len(mail.outbox),1)

			toekn_acitvaiton_url=re.findall(r"http:\/\/\w+\/account\/activate\/\w+\/\w+-\w+\/",mail.outbox[0].body)[0]
			resp=self.client.post(toekn_acitvaiton_url,data={'password1':'password','password2':'password'})
			self.assertNotFalse(self.user.password,User.objects.get(username='testusername').password)
			self.assertRedirects(resp,reverse('blog:login'))

			# Make a token for test ResetPasswordActivate view when passswords is not correct
			resp=self.client.post(reverse('account:reset_password'),data={'email':self.user.email})
			self.assertEqual(len(mail.outbox),1)

			toekn_acitvaiton_url=re.findall(r"http:\/\/\w+\/account\/activate\/\w+\/\w+-\w+\/",mail.outbox[0].body)[0]
			resp=self.client.post(toekn_acitvaiton_url,data={'password1':'password','password2':'password_chert'})
			message=list(get_messages(resp.wsgi_request))
			self.assertEqual(len(message),1)
			self.assertEqual(str(message[0]),'گذرواژه ها یکسان نیستند')
			self.assertTemplateUsed(resp,'account/registration/rest_password_confirm.html')


			# Test ResetPasswordActivate view when the token is corrupt
			resp=self.client.post(toekn_acitvaiton_url,data={'password1':'password','password2':'password_chert'})
			self.assertEqual(resp.status_code,200)
			self.assertTemplateUsed(resp,'account/registration/activation_invalid.html')
			

			resp=self.client.post(toekn_acitvaiton_url,data={'password1':'password_chert'})
			self.assertEqual(resp.status_code,200)
			self.assertTemplateUsed(resp,'account/registration/rest_password_confirm.html')
			

			resp=self.client.get(toekn_acitvaiton_url)
			self.assertEqual(resp.status_code,200)
			self.assertTemplateUsed(resp,'account/registration/rest_password_confirm.html')
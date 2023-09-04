from django.test import TestCase
from django.urls import reverse
from .models import (
			TicketModel ,
			SubscribtionEmail ,
			Comment ,
			BlogModel ,
			CategoryModels
)
from account.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.


class BlogTest(TestCase):


	def setUp(self):
		self.user=User.objects.create(username='test',)
		self.user.set_password('testpassword')
		self.user.save()

		image=SimpleUploadedFile(
			name='test_image.jpg',
			content=open('/home/Anitx/Project/django-setarehghotbi/setarehghotbi/media/media/images.jpeg','rb').read(),
			content_type='image/jpeg'
		)

		self.test_category = CategoryModels.objects.create(
			title = 'Test category',
			description = 'This is just a test category',
			image = image,
			slug = 'test_category',


			)

		self.test_article=BlogModel.objects.create(
			title = 'Test',
			description = 'This is test article',
			image = image ,
			slug = 'test',
			auther = self.user ,
			category = self.test_category,

			)

		self.test_comment=Comment.objects.create(
			post=self.test_article,
			commenter=self.user,
			content='test comment',

			)

	def test_home_page(self):

		resp = self.client.get(reverse('blog:home'))
		# Take blog content from context
		blog=resp.context['blog']

		self.assertEqual(resp.status_code,200)
		self.assertTemplateUsed(resp,'blog/home.html')

		if blog.has_other_pages():
			check_pagination=self.client.get('{}?p={}'.format(reverse('blog:home'),blog.next_page_number()))
			self.assertEqual(check_pagination.status_code,200)
			# Check pagination with str p
			check_pagination=self.client.get('{}?p={}'.format(reverse('blog:home'),'chert'))
			self.assertEqual(check_pagination.status_code,200)
			# Check pagination big number on p
			check_pagination=self.client.get('{}?p={}'.format(reverse('blog:home'),blog.end_index() + 1))
			self.assertEqual(check_pagination.status_code,200)





	def test_send_ticket_view(self):

		self.client.login(username='test',password='testpassword')
		data={
			'title':'say my name',
			'message':'there is some bug on your website'
		}

		# Check the view when the form sente is right and everything is OK.
		ticket_request=self.client.post(reverse('blog:ticket'),data=data)
		self.assertEqual(ticket_request.content.decode('utf-8'),'ممنون از گزارش شما')
		self.assertEqual(TicketModel.objects.count(),1)

		# Check the view when form is not right and i have a invalid form.
		data.pop('title')
		ticket_request=self.client.post(reverse('blog:ticket'),data=data)
		self.assertEqual(ticket_request.content.decode('utf-8'),'فرم پر شده معتبر نمی باشد')


		# Check the view when user is not authenticated.
		self.client.logout()
		ticket_request=self.client.post(reverse('blog:ticket'),data=data)
		self.assertEqual(ticket_request.content.decode('utf-8'),'pleas authentication')


		# Check the view when request is GET.
		ticket_request=self.client.get(reverse('blog:ticket'))
		self.assertEqual(ticket_request.status_code,200)



	def test_subscribe_view(self):

		# Check subscribe view when email format is right
		subscribe_request=self.client.post(reverse('blog:subscribe'),data={'email':'testemail@gmail.com'})
		self.assertEqual(subscribe_request.content.decode('utf-8'),'Thankyou for subscribe')
		self.assertEqual(SubscribtionEmail.objects.count(),1)


		# Check subscribe view when email format is not right
		subscribe_request=self.client.post(reverse('blog:subscribe'),data={'email':'chert'})
		self.assertEqual(subscribe_request.content.decode('utf-8'),'Your email format is not right')


		# Check subscribe view when request is GET		
		subscribe_request=self.client.get(reverse('blog:subscribe'))
		self.assertRedirects(subscribe_request,reverse('blog:home'))



	# Check SinglePostView and single_post template
	def test_single_post_view(self):


		response=self.client.get(reverse('blog:single_post',kwargs={'slug':self.test_article.slug,}))

		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'blog/single_post.html')




	def test_create_comment_view(self):

		self.client.login(username='test',password='testpassword')
		data={
			'content':'Its just a test comment',
			'article_slug':self.test_article.slug
		}


		# Test CreateComment view when the data is valid and comment dont't have a parent
		create_request=self.client.post(reverse('blog:create-comment'),data=data)
		self.assertRedirects(create_request,reverse('blog:single_post',kwargs={'slug':self.test_article.slug}))
		self.assertEqual(Comment.objects.count(),2)# I create a test comment on setUp

		# Test CreateComment view when data is valid and comment have a parent
		data['comment_id']=1
		create_request=self.client.post(reverse('blog:create-comment'),data=data)
		self.assertRedirects(create_request,reverse('blog:single_post',kwargs={'slug':self.test_article.slug}))
		self.assertEqual(Comment.objects.count(),3)



		# Test CreateComment view When form is not valid and data is ######
		data.pop('content')		
		create_request=self.client.post(reverse('blog:create-comment'),data=data)
		self.assertEqual(create_request.content.decode('utf-8'),'Form is not valid')


		# Test CreateComment when user is not authenticated
		self.client.logout()
		create_request=self.client.post(reverse('blog:create-comment'),data=data)
		self.assertEqual(create_request.content.decode('utf-8'),'Pleas authentication')


		# Test CreateComment when requset is GET
		create_request=self.client.get(reverse('blog:create-comment'))
		self.assertRedirects(create_request,reverse('blog:home'))




	def test_like_comment_view(self):
		
		self.client.login(username='test',password='testpassword')

		data={
			'comment_id':self.test_comment.id,
			'slug':self.test_article.slug
		}
		# Check the view when the form sent is right and everything is okTest
		# LikeComment view when user dont like comment before and user likes a comment
		like_request=self.client.post(reverse('blog:like_comment'),data=data)
		self.assertRedirects(like_request,reverse('blog:single_post',kwargs={'slug':self.test_article.slug}))
		self.assertEqual(Comment.objects.get(id=1).like_count,1)


		# Test LikeComment view when user liked the comment before and user wants to dislike the comment
		like_request=self.client.post(reverse('blog:like_comment'),data=data)
		self.assertRedirects(like_request,reverse('blog:single_post',kwargs={'slug':self.test_article.slug}))
		self.assertEqual(Comment.objects.get(id=1).like_count,0)


		like_request=self.client.get(reverse('blog:like_comment'))
		self.assertEqual(like_request.content.decode('utf-8'),'Pleas send post request')

		self.client.logout()
		like_request=self.client.get(reverse('blog:like_comment'))
		self.assertEqual(like_request.content.decode('utf-8'),'pleas authentication')




	def test_authger_articles_view(self):

		resp = self.client.get(reverse('blog:auther_articles',kwargs={'slug':self.user.username}))
		# Take articles content from context
		articles=resp.context['articles']

		self.assertEqual(resp.status_code,200)
		self.assertTemplateUsed(resp,'blog/auther_articles.html')

		if articles.has_other_pages():
			check_pagination=self.client.get('{}?p={}'.format(reverse('blog:auther_articles',kwargs={'slug':self.user.username}),articles.next_page_number()))
			self.assertEqual(check_pagination.status_code,200)
			# Check pagination with str p
			check_pagination=self.client.get('{}?p={}'.format(reverse('blog:auther_articles',kwargs={'slug':self.user.username}),'chert'))
			self.assertEqual(check_pagination.status_code,200)
			# Check pagination big number on p
			check_pagination_with=self.client.get('{}?p={}'.format(reverse('blog:auther_articles',kwargs={'slug':self.user.username}),articles.end_index() + 1))
			self.assertEqual(check_pagination.status_code,200)



	def test_category_view(self):
		resp = self.client.get(reverse('blog:category',kwargs={'slug':self.test_category.slug}))
		# Take articles content from context
		articles=resp.context['articles']

		self.assertEqual(resp.status_code,200)
		self.assertTemplateUsed(resp,'blog/categorys.html')

		if articles.has_other_pages():
			check_pagination=self.client.get('{}?p={}'.format(reverse('blog:category',kwargs={'slug':self.test_category.slug}),articles.next_page_number()))
			self.assertEqual(check_pagination.status_code,200)
			# Check pagination with str p
			check_pagination=self.client.get('{}?p={}'.format(reverse('blog:category',kwargs={'slug':self.test_category.slug}),'chert'))
			self.assertEqual(check_pagination.status_code,200)
			# Check pagination big number on p
			check_pagination_with=self.client.get('{}?p={}'.format(reverse('blog:category',kwargs={'slug':self.test_category.slug}),articles.end_index() + 1))
			self.assertEqual(check_pagination.status_code,200)




	def test_blog_search_view(self):
		resp = self.client.get("{}?search=a".format(reverse('blog:blog_search')))
		# Take articles content from context
		blog=resp.context['blog']

		self.assertEqual(resp.status_code,200)
		self.assertTemplateUsed(resp,'blog/home.html')

		if blog.has_other_pages():
			check_pagination=self.client.get('{}?search=a&p={}'.format(reverse('blog:blog_search'),blog.next_page_number()))
			self.assertEqual(check_pagination.status_code,200)
			# Check pagination with str p
			check_pagination=self.client.get('{}?search=a&p={}'.format(reverse('blog:blog_search'),'chert'))
			self.assertEqual(check_pagination.status_code,200)
			# Check pagination big number on p
			check_pagination_with=self.client.get('{}?search=a&p={}'.format(reverse('blog:blog_search'),blog.end_index() + 1))
			self.assertEqual(check_pagination.status_code,200)




	def test_category_search_view(self):
		resp = self.client.get("{}?search=a".format(reverse('blog:category_search',kwargs={'slug':self.test_category.slug})))
		# Take articles content from context
		articles=resp.context['articles']

		self.assertEqual(resp.status_code,200)
		self.assertTemplateUsed(resp,'blog/home.html')

		if articles.has_other_pages():
			check_pagination=self.client.get('{}?search=a&p={}'.format(reverse('blog:category_search',kwargs={'slug':self.test_category.slug}),articles.next_page_number()))
			self.assertEqual(check_pagination.status_code,200)
			# Check pagination with str p
			check_pagination=self.client.get('{}?search=a&p={}'.format(reverse('blog:category_search',kwargs={'slug':self.test_category.slug}),'chert'))
			self.assertEqual(check_pagination.status_code,200)
			# Check pagination big number on p
			check_pagination_with=self.client.get('{}?search=a&p={}'.format(reverse('blog:category_search',kwargs={'slug':self.test_category.slug}),articles.end_index() + 1))
			self.assertEqual(check_pagination.status_code,200)





	def test_auther_article_search_view(self):
		resp = self.client.get("{}?search=a".format(reverse('blog:search_auther_articles',kwargs={'slug':self.user.username})))
		# Take articles content from context
		articles=resp.context['articles']

		self.assertEqual(resp.status_code,200)
		self.assertTemplateUsed(resp,'blog/search_auther_articles.html')

		if articles.has_other_pages():
			check_pagination=self.client.get('{}?search=a&p={}'.format(reverse('blog:search_auther_articles',kwargs={'slug':self.user.username}),articles.next_page_number()))
			self.assertEqual(check_pagination.status_code,200)
			# Check pagination with str p
			check_pagination=self.client.get('{}?search=a&p={}'.format(reverse('blog:search_auther_articles',kwargs={'slug':self.user.username}),'chert'))
			self.assertEqual(check_pagination.status_code,200)
			# Check pagination big number on p
			check_pagination_with=self.client.get('{}?search=a&p={}'.format(reverse('blog:search_auther_articles',kwargs={'slug':self.user.username}),articles.end_index() + 1))
			self.assertEqual(check_pagination.status_code,200)





	def test_about_us_view(self):

		resp=self.client.get(reverse('blog:about_us'))
		self.assertEqual(resp.status_code,200)
		self.assertTemplateUsed(resp,'blog/about_us.html')
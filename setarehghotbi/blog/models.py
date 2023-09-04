from django.db import models
from account.models import User
from django.utils import timezone
from django.db.models import Q

# Create your models here.


#This model is for my blog categories related to BlogModels
class CategoryModels(models.Model):
	title=models.CharField(max_length=30,verbose_name='category name/title')
	description=models.TextField(max_length=200,verbose_name='category description',blank=True)
	image=models.ImageField(upload_to='media/blog/categorys',verbose_name='category image',default=None)
	slug=models.SlugField(max_length=150,verbose_name='slug category')
	parent=models.ForeignKey('CategoryModels',verbose_name='category parend',on_delete=models.CASCADE,related_name='children',default=None,blank=True,null=True)
	have_children=models.BooleanField(verbose_name='category is parent of another category',default=False)


	def __str__(self):
		return self.title 





#this model for article content in my blog 
class BlogModel(models.Model):
	BLOG_CHOICES=(('public','public'),('draft','draft'))
	title=models.CharField(verbose_name='blog title',max_length=100)
	description=models.TextField(verbose_name='blog description')
	date=models.DateTimeField(verbose_name='blog date',default=timezone.now)
	image=models.ImageField(verbose_name='blog image',upload_to='media/blog/articles',null=True,default=None)
	is_image_header=models.BooleanField(verbose_name='is header image?',default=True)
	slug=models.SlugField(verbose_name='blog slug',max_length=50)
	status=models.CharField(verbose_name='blog status',choices=BLOG_CHOICES,max_length=50,default='draft')
	auther=models.ForeignKey(User,verbose_name='blog auther',on_delete=models.CASCADE,related_name='auther_articles')
	category=models.ForeignKey(CategoryModels,verbose_name='blog category',on_delete=models.CASCADE,default=None,related_name='article')


	def __str__(self):
		return self.title





#This model is for reports that will be sent by users
class TicketModel(models.Model):
	name=models.CharField(verbose_name='name user',max_length=30)
	email=models.EmailField(verbose_name='email user',max_length=250)
	title=models.CharField(verbose_name='title ticket',max_length=100)
	message=models.TextField(verbose_name='messge ticket',max_length=500)
	accepted=models.BooleanField(default=False)
	admin_response=models.CharField(verbose_name='admin answer',max_length=500,blank=True)
	user=models.ForeignKey(User,verbose_name='sender user',on_delete=models.CASCADE,null=True)
	


	def __str__(self):
		return self.title







#This model is for storing emails that users send to us on the site,
#and after publishing each article,
#we send a message to inform users to these emails.
class SubscribtionEmail(models.Model):
	email=models.EmailField(verbose_name='email',max_length=256)

	def __str__(self):
		return self.email





class Comment(models.Model):
	post=models.ForeignKey(BlogModel,verbose_name='comment post',on_delete=models.CASCADE,related_name='comments')
	commenter=models.ForeignKey(User,verbose_name='commenter',on_delete=models.CASCADE)
	content=models.CharField(verbose_name='comment content',max_length=300)
	status=models.BooleanField(verbose_name='comment status',default=False)
	date_created=models.DateTimeField(verbose_name='comment date created',default=timezone.now)
	parent=models.ForeignKey('Comment',verbose_name='reply comments',on_delete=models.CASCADE,related_name='replys',default=None,null=True,blank=True)
	have_reply=models.BooleanField(verbose_name='This comment have reply/replies',default=False)
	likes=models.ManyToManyField(User,related_name='likes',verbose_name='likes comment',default=None,blank=True)
	like_count=models.IntegerField(verbose_name='The number of likes',default=0)
	parent_count=models.IntegerField(verbose_name='The number of replies',default=0)

	def comment_likes_count(self):
		return self.likes.count()


	def comment_parent_count(self):
		return Comment.objects.filter(Q(status=True)&Q(parent=self)).count()


	def __str__(self):
		return 'comment by {} : {}'.format(self.commenter.username,self.content[:30])
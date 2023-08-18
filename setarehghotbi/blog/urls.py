#blog urls

from django.urls import path
from .views import( 
					home ,
					SendTicket ,
					SubscribeView ,
					SinglePostView ,
					CategoryView ,
					BlogSearchView ,
					CategorySearchView ,
					AutherArticlesView ,
					SearchAutherArticles ,
					AboutUS,
					LikeComment,
)


app_name='blog'

urlpatterns=[
	path('',home,name='home'),
	path('send-ticket/',SendTicket,name='ticket'),
	path('subscribe/',SubscribeView,name='subscribe'), 
	path('aboutUS',AboutUS,name='about_us'),     

	path('article/<slug:slug>',SinglePostView,name='single_post'),   
	path('blog/search/',BlogSearchView,name='blog_search'),
	path('like_comment/',LikeComment,name='like_comment'),

	path('category/<slug:slug>',CategoryView,name='category'),     
	path('category/search/<slug:slug>',CategorySearchView,name='category_search'),
	     
	path('auther/<slug:slug>',AutherArticlesView,name='auther_articles'),     
	path('auther/search/<slug:slug>',SearchAutherArticles,name='search_auther_articles'),     
]

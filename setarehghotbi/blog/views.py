from django.shortcuts import render , redirect , get_object_or_404
from .models import( 
                    BlogModel , 
                    TicketModel , 
                    SubscribtionEmail ,
                    CategoryModels,
                    Comment,
                    )
from .forms import TicketForm , CommentForm
from django.http import HttpResponse , HttpResponseRedirect
from account.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator ,EmptyPage, PageNotAnInteger
from django.urls import reverse
import re

# Create your views here.

# the main page view of the blog
def home(request):
    blog_model=BlogModel.objects.filter(status='public')

    paginator=Paginator(blog_model,6)

    page_number=request.GET.get('p')

    try:
        page_object=paginator.get_page(page_number)
    except PageNotAnInteger:
        page_object=paginator.get_page(1)
    except EmptyPage:
        page_object=paginator.get_page(paginator.num_pages)


    form=TicketForm()

    context={
        'blog':page_object,
        'form':form,
        'url':reverse('blog:home'),
        }

    return render(request,'blog/home.html',context)





#This view is for reports that will be sent by users
def SendTicket(request):
    if request.user.is_authenticated:
        if request.method == 'POST':

            form=TicketForm(request.POST)
            form.name=request.user.username 
            form.email=request.user.email
            if form.is_valid():
                form.save(commit=False)
                user=User.objects.get(id=request.user.id)
                form.user=user
                form.save()
                
                return HttpResponse('ممنون از گزارش شما')
            else:
                return HttpResponse('فرم پر شده معتبر نمی باشد')
        else:
            return redirect('blog:home')
    else :

        return HttpResponse('pleas authentication')         





#This view is for storing emails that users send to us on the site,
#and after publishing each article,
#we send a message to inform users to these emails.
def SubscribeView(request):
    if request.method=='POST':

        email_regex=r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
        email=request.POST.get('email')

        if re.fullmatch(email_regex,email):
            SubscribtionEmail(email=email).save()
            return HttpResponse('Thankyou for subscribe')
        else:
            return HttpResponse('Your email format is not right')

    else:
        return redirect('blog:home')







# This view  for showing article content page
def SinglePostView(request,slug):

    all_comments=Comment.objects.select_related('commenter','parent').filter(status=True,post__slug=slug)
    article=BlogModel.objects.select_related('auther').get(slug=slug)
    if request.user.is_authenticated:
        user_likes=request.user.likes.all() 
    else :
        user_likes=None

    # This part is for create a new comment by user and save the comment 
    # The another bart of the comment system is like comment that created on anotehr view
    if request.method == 'POST':
        if request.user.is_authenticated:
            comment_form=CommentForm(request.POST or None)
            if comment_form.is_valid():
                content=comment_form.cleaned_data['content']

                if request.POST.get('comment_id'):
                    comment_parent=get_object_or_404(Comment,id=request.POST.get('comment_id'))
                    comment=Comment.objects.create(
                        post=article,
                        commenter=request.user,
                        content=content,
                        parent=comment_parent,
                        )
                    comment_parent.have_reply=True
                    comment_parent.parent_count+=1
                    comment_parent.save()

                else:
                    comment=Comment.objects.create(
                        post=article,
                        commenter=request.user,
                        content=content
                        )

                comment.save()
            else: 
                return HttpResponse('form is not valid')
        else:
            return HttpResponse('pleas authentication')
    else:
        comment_form=CommentForm()


    context={
        'article':article,
        'comment_form':comment_form,
        'all_comments':all_comments,
        'user_likes':user_likes,
    }

    return render(request,'blog/single_post.html',context)




def LikeComment(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            comment_id=request.POST.get('comment_id')
            comment=Comment.objects.prefetch_related('likes').get(id=comment_id)
            if comment.likes.filter(id=request.user.id).exists():
                comment.likes.remove(request.user)
                comment.like_count-=1
                comment.save()
            else:
                comment.likes.add(request.user)
                comment.like_count+=1
                comment.save()


            article_slug=request.POST.get('slug')
            return HttpResponseRedirect(reverse('blog:single_post',kwargs={'slug':article_slug}))
        else:
            return HttpResponse('pleas send post request')
    else:
        return HttpResponse('pleas authentication')





# This view is for displaying all the articles of an author
def AutherArticlesView(request,slug):

    auther=get_object_or_404(User,username=slug)
    articles=auther.auther_articles.filter(status='public')
    articles_count=articles.count()

    paginator=Paginator(articles,6)

    page_number=request.GET.get('p')

    try:
        page_object=paginator.get_page(page_number)
    except PageNotAnInteger:
        page_object=paginator.get_page(1)
    except EmptyPage:
        page_object=paginator.get_page(paginator.num_pages)


    context={
    'articles':page_object,
    'auther':auther,
    'articles_count':articles_count,
    'url':reverse('blog:auther_articles',kwargs={'slug':slug})
    }
    return render(request,'blog/auther_articles.html',context)





# This view is for showing articles related to a category
def CategoryView(request,slug):


    category = get_object_or_404(CategoryModels,slug=slug)
    articles = category.article.filter(status='public')

    paginator=Paginator(articles,6)

    page_number=request.GET.get('p')

    try:
        page_object=paginator.get_page(page_number)
    except PageNotAnInteger:
        page_object=paginator.get_page(1)
    except EmptyPage:
        page_object=paginator.get_page(paginator.num_pages)


    context={
    'articles':page_object,
    'category':category,
    'url':reverse('blog:category',kwargs={'slug':slug}),
    }

    return render(request,'blog/categorys.html',context)






# This view is for searching users on the main page
def BlogSearchView(request):

    search_word=request.GET.get('search')

    if search_word:
        blog_model=BlogModel.objects.filter(
                Q(title__icontains=search_word) |
                Q(description__icontains=search_word),
                status='public'
            )

        paginator=Paginator(blog_model,6)

        page_number=request.GET.get('p')


        try:
            page_object=paginator.get_page(page_number)
        except PageNotAnInteger:
            page_object=paginator.get_page(1)
        except EmptyPage:
            page_object=paginator.get_page(paginator.num_pages)


        context={
            'blog':page_object,
            'search_word':search_word,
            'url':reverse('blog:blog_search')
            }
        return render(request,'blog/home.html',context)
    else:
        return HttpResponse('pleas search a word')





# This view is for searching users on the category page
def CategorySearchView(request,slug):

    search_word=request.GET.get('search')

    if search_word:
        category=CategoryModels.objects.get(slug=slug)
        articles = category.article.filter(
                Q(title__icontains=search_word) |
                Q(description__icontains=search_word),
                status='public'
            )

        paginator=Paginator(articles,6)

        page_number=request.GET.get('p')

        try:
            page_object=paginator.get_page(page_number)
        except PageNotAnInteger:
            page_object=paginator.get_page(1)
        except EmptyPage:
            page_object=paginator.get_page(paginator.num_pages)

        context={
        'articles':page_object,
        'category':category,
        'search_word':search_word,
        'url':reverse('blog:category_search',kwargs={'slug':slug}),
        }

        return render(request,'blog/categorys.html',context)

    else:
        return HttpResponse('pleas search a word')




# This view for searching users on the auther article page
def SearchAutherArticles(request,slug):

    search_word=request.GET.get('search')
    
    if search_word:    
        auther=User.objects.get(username=slug)
        articles=auther.auther_articles.filter(
                Q(title__icontains=search_word)|
                Q(description__icontains=search_word),
                status='public',)


        paginator=Paginator(articles,6)

        page_number=request.GET.get('p')

        try:
            page_object=paginator.get_page(page_number)
        except PageNotAnInteger:
            page_object=paginator.get_page(1)
        except EmptyPage:
            page_object=paginator.get_page(paginator.num_pages)

        context={
                'articles':page_object,
                'auther':auther,
                'search_word':search_word,
                'articles_count':auther.auther_articles.filter(status='public').count(),
                'url':reverse('blog:search_auther_articles',kwargs={'slug':slug})
                }

        return render(request,'blog/search_auther_articles.html',context)
    else:
        return HttpResponse('pleas search a word')






# This view is for displaying information about the team
def AboutUS(request):

    team=User.objects.filter(is_superuser=True,is_team=True)

    return render(request,'blog/about_us.html',{'team':team})
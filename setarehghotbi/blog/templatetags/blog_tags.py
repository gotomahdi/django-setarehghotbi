from django import template
from ..models import CategoryModels



# register django teplate tags
register = template.Library()


# my teplate tags

@register.inclusion_tag('blog/template_tags/navbar.html')
def navbar(request):
	all_categories = CategoryModels.objects.select_related('parent')
	return {'all_categories':all_categories,'request':request}



@register.inclusion_tag('blog/template_tags/pagination.html')
def pagination(page_object,url,search=False):
	return {'page_object':page_object,'search':search,'url':url}



@register.inclusion_tag('blog/comment_loop.html')
def comment_loop(all_comment,comment,article,request,comment_form):

	comment_reply=filter(lambda item: item.parent and item.parent.id==comment.id,all_comment) 


	return {
		'all_comment':all_comment,
		'comment_reply':comment_reply,
		'article':article,
		'request':request,
		'comment_form':comment_form
	}



@register.inclusion_tag('blog/template_tags/navbar_loop.html')
def navbar_loop(all_categories,category):

	category_childrens=filter(lambda item: item.parent and item.parent.id==category.id , all_categories)


	return {
		'all_categories':all_categories,
		'category':category,
		'category_childrens':category_childrens,
	}
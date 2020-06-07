from django.shortcuts import render
from django.http import HttpResponse
from blog.models import Blogpost

# Create your views here.
def index(request):
    blogpost = Blogpost.objects.all()
    params = {'blogpost':blogpost}
    return render(request,"blog/index.html",params)

def blogpost(request,myid):
    blogpost = Blogpost.objects.filter(post_id = myid)
    print(blogpost)
    params = {'blogpost':blogpost}
    return render(request,"blog/blogpost.html",params)
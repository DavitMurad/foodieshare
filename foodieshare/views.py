from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from foodieshare.models import *
from foodieshare.forms import PostForm, UserRegisterForm, UserProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse



def main_feed(request):
    posts = Post.objects.all().order_by('-created_at')
    likes = Like.objects.all()
    context_dict = {"posts": posts, "likes": likes}
    return render(request, 'foodieshare/main_feed.html', context=context_dict)


@login_required
def my_profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(auth_user=request.user)
    post_form = PostForm()
    profile_form = UserProfileForm(instance=user_profile)

    if request.method == 'POST':
        form_type = request.POST.get('form_type', '')

        if form_type == 'post_form':
            post_form = PostForm(request.POST, request.FILES)
            if post_form.is_valid():
                new_post = post_form.save(commit=False)
                new_post.user = user_profile
                new_post.save()
                messages.success(request, "Your post has been created!")
                return redirect('foodieshare:main_feed')

        elif form_type == 'profile_form':
            profile_form = UserProfileForm(
                request.POST, request.FILES, instance=user_profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Your profile has been updated!")
                return redirect('foodieshare:my_profile')

    context = {
        'user_profile': user_profile,
        'post_form': post_form,
        'profile_form': profile_form,
    }
    return render(request, 'foodieshare/my_profile.html', context)

@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    return render(request, 'foodieshare/user_profile.html', {'profile_user': profile_user})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('foodieshare:login')
    else:
        form = UserRegisterForm()
    return render(request, 'foodieshare/register.html', {'form': form})


def login(request):
    return render(request, 'foodieshare/login.html')

@login_required
def add_comment_to_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    if request.method == "POST":
        content = request.POST.get('content')
        comment = Comment.objects.create(
            post=post, user=request.user.userprofile, content=content)
        comment.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def toggle_like(request):
    if request.method == 'POST' and request.is_ajax():
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)
        like, created = Like.objects.get_or_create(post=post, user=request.user.userprofile)

        if not created:
            like.delete()  # If like exists, remove it
            action = 'unliked'
        else:
            action = 'liked'

        return JsonResponse({'status': 'success', 'action': action})
    #return JsonResponse({'status': 'failed'})
    return HttpResponseBadRequest()
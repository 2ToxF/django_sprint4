from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .constants import BLOG_TEMP_DIR, PAGINATE_NUM
from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()


# Non-view function
def get_posts():
    return Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        pub_date__lte=timezone.now(), is_published=True,
        category__is_published=True
    )


# Non-view function
def get_number_comments(post):
    return post.comments.count()


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        post = get_object_or_404(get_posts(), pk=post_id)
    comments = Comment.objects.filter(post=post)
    context = {'post': post, 'form': CommentForm(), 'comments': comments}
    return render(request, BLOG_TEMP_DIR + 'detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )

    post_list = category.posts.filter(
        pub_date__lte=timezone.now(),
        is_published=True
    )

    paginator = Paginator(post_list, PAGINATE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for post in page_obj:
        post.comment_count = get_number_comments(post)

    context = {'page_obj': page_obj, 'category': category}
    return render(request, BLOG_TEMP_DIR + 'category.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    context = {'profile': profile}

    if request.user == profile:
        posts = Post.objects.filter(author=profile)
    else:
        posts = Post.objects.select_related(
            'category', 'location'
        ).filter(
            author_id=profile.id, is_published=True,
            category__is_published=True, pub_date__lte=timezone.now()
        )

    paginator = Paginator(posts, PAGINATE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for post in page_obj:
        post.comment_count = get_number_comments(post)

    context['page_obj'] = page_obj
    return render(request, BLOG_TEMP_DIR + 'profile.html', context)


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('username', 'first_name', 'last_name', 'email')
    template_name = BLOG_TEMP_DIR + 'user.html'

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.request.user.id)


class IndexListView(ListView):
    template_name = BLOG_TEMP_DIR + 'index.html'
    paginate_by = PAGINATE_NUM
    queryset = get_posts()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for post in context['object_list']:
            post.comment_count = get_number_comments(post)

        return context


class PostsBaseMixin(LoginRequiredMixin):
    model = Post
    form_class = PostForm
    template_name = BLOG_TEMP_DIR + 'create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostsCreateView(PostsBaseMixin, CreateView):
    pass


class PostsEditMixin(PostsBaseMixin):
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostsUpdateView(PostsEditMixin, UpdateView):
    pass


class PostsDeleteView(PostsEditMixin, DeleteView):
    def get_success_url(self):
        return reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form = PostForm(instance=instance)
        context['form'] = form
        return context


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


class CommentsEditMixin(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    template_name = BLOG_TEMP_DIR + 'comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if instance.author != request.user:
            return redirect('blog:index')
        return super().dispatch(request, *args, **kwargs)


class CommentsUpdateView(CommentsEditMixin, UpdateView):
    pass


class CommentsDeleteView(CommentsEditMixin, DeleteView):
    pass

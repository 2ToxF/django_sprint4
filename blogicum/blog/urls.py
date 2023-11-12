from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path(
        'category/<slug:category_slug>/', views.category_posts,
        name='category_posts'
    ),

    path('posts/create/', views.PostsCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path(
        'posts/<int:post_id>/edit/', views.PostsUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/', views.PostsDeleteView.as_view(),
        name='delete_post'
    ),

    path(
        'posts/<int:post_id>/comment/', views.add_comment,
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentsUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentsDeleteView.as_view(),
        name='delete_comment'
    ),

    path(
        'profile/edit_profile/', views.ProfileEditView.as_view(),
        name='edit_profile'
    ),
    path(
        'profile/<str:username>/', views.profile, name='profile'
    ),
]

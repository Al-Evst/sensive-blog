from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from blog.models import Comment, Post, Tag


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts.count(),
    }


def serialize_post(post):
    tags = list(post.tags.all())
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': getattr(post, 'comments_count', 0),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in tags],
        'first_tag_title': tags[0].title if tags else '',
    }


def index(request):
    popular_posts = (
        Post.objects
        .popular()
        .prefetch_related('tags')
        .select_related('author')[:5]
        .fetch_with_comments_count()
    )

    fresh_posts = (
        Post.objects
        .order_by('-published_at')[:5]
        .prefetch_related('tags')
        .select_related('author')
        .fetch_with_comments_count()
    )

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [serialize_post(post) for post in popular_posts],
        'page_posts': [serialize_post(post) for post in fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }

    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = (
        Post.objects
        .filter(slug=slug)
        .select_related('author')
        .prefetch_related('tags', 'likes', 'comments__author')
        .annotate(
            comments_count=Count('comments', distinct=True),
            likes_count=Count('likes', distinct=True)
        )
        .get()
    )

    serialized_comments = [{
        'text': comment.text,
        'published_at': comment.published_at,
        'author': comment.author.username,
    } for comment in post.comments.all()]

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
    }

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = (
        Post.objects
        .popular()
        .prefetch_related('tags')
        .select_related('author')[:5]
        .fetch_with_comments_count()
    )

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }

    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag, title=tag_title)

    related_posts = (
        tag.posts
        .all()
        .select_related('author')
        .prefetch_related('tags')
        .annotate(comments_count=Count('comments', distinct=True))[:20]
    )

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = (
        Post.objects
        .popular()
        .prefetch_related('tags')
        .select_related('author')[:5]
        .fetch_with_comments_count()
    )

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }

    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})
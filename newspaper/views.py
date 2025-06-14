from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, CreateView, View
from newspaper.forms import CommentForm, ContactForm
from newspaper.models import Advertisement, Category, Contact, OurTeam, Post, Tag
from django.contrib.messages.views import SuccessMessageMixin
from django.utils import timezone
from datetime import timedelta


# Create your views here.
class SideBarMixin:
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["popular_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-published_at")[:5]

        context["advertisement"] = (
            Advertisement.objects.all().order_by("-created_at").first()
        )
        return context


class HomeView(SideBarMixin, ListView):
    model = Post
    template_name = "newsportal/home.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(
        published_at__isnull=False, status="active"
    ).order_by("-published_at")[:4]

    # for providing extra data to template we need to use get_context_data()
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["featured_post"] = (
            Post.objects.filter(published_at__isnull=False, status="active")
            .order_by("-published_at", "-views_count")
            .first()
        )

        one_week_ago = timezone.now() - timedelta(days=7)
        context["weekly_top_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active", published_at__gte=one_week_ago
        ).order_by("-published_at", "-views_count")[:5]

        context["breaking_news"] = Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-published_at")[:3]

        return context


class PostListView(SideBarMixin, ListView):
    model = Post
    template_name = "newsportal/list/list.html"
    context_object_name = "posts"
    paginate_by = 2

    def get_queryset(self):
        return Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-published_at")


class PostDetailView(SideBarMixin, DetailView):
    model = Post
    template_name = "newsportal/detail/detail.html"
    context_object_name = "post"

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(published_at__isnull=False, status="active")
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Increment the views count for the current post
        current_post = self.object
        current_post.views_count += 1
        current_post.save()
        # Get the related posts based on the same category
        context["related_posts"] = (
            Post.objects.filter(
                category=self.object.category,
                published_at__isnull=False,
                status="active",
            )
            .exclude(id=self.object.id)
            .order_by("-published_at", "-views_count")[:2]
        )

        return context


class PostByCategoryView(SideBarMixin, ListView):
    model = Post
    template_name = "newsportal/list/list.html"
    context_object_name = "posts"
    paginate_by = 1

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(
            published_at__isnull=False,
            status="active",
            category__id=self.kwargs["category_id"],
        ).order_by("-published_at")
        return query


class TagListView(ListView):
    model = Tag
    template_name = "newsportal/tags.html"
    context_object_name = "tags"


class CategoryListView(ListView):
    model = Category
    template_name = "newsportal/categories.html"
    context_object_name = "categories"


class AboutView(TemplateView):
    template_name = "newsportal/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["our_teams"] = OurTeam.objects.all()
        return context


class ContactCreateView(SuccessMessageMixin, CreateView):
    model = Contact
    template_name = "newsportal/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact")
    success_message = "Your message has been sent successfully!"


class CommentView(View):

    def post(self, request, *args, **kwargs):
        post_id = request.POST["post"]

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.save()
            return redirect("post-detail", post_id)
        else:
            post = Post.objects.get(pk=post_id)

            popular_posts = Post.objects.filter(
                published_at__isnull=False, status="active"
            ).order_by("-published_at")[:5]
            advertisement = Advertisement.objects.all().order_by("-created_at").first()
            return render(
                request,
                "newsportal/detail/detail.html",
                {
                    "post": post,
                    "form": form,
                    "popular_posts": popular_posts,
                    "advertisement": advertisement,
                },
            )

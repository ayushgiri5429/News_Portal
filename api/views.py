from django.contrib.auth.models import User, Group
from rest_framework import permissions, viewsets, exceptions
from api.serializers import (
    ContactSerializer,
    NewsletterSerializer,
    PostSerializer,
    UserSerializer,
    GroupSerializer,
    TagSerializer,
    CategorySerializer,
)
from newspaper.models import Contact, Newsletter, Post, Tag, Category

from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView



class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tags to be viewed or edited.
    """

    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        
        return super().get_permissions()
    

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows categories to be viewed or edited.
    """

    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        
        return super().get_permissions()
    

class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows posts to be viewed or edited.
    """

    queryset = Post.objects.all().order_by("-published_at")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action in ["list", "retrieve"]:
            queryset = queryset.filter(status="active", published_at__isnull=False)

            # Search functionality
            from django.db.models import Q
            search_term = self.request.query_params.get("search")
            if search_term:
                queryset = queryset.filter(
                    Q(title__icontains=search_term) | Q(content__icontains=search_term)
                )

        return queryset

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve to increment views_count every time a post is retrieved.
        """
        instance = self.get_object()

        # Only increment views if the post is active and published
        if instance.status == "active" and instance.published_at:
            instance.views_count = instance.views_count + 1 if instance.views_count else 1
            instance.save(update_fields=["views_count"])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class NewsletterViewSet(viewsets.ModelViewSet):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "destroy"]:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def update(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)
    

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "destroy"]:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def update(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)
    


class  PostListByCategoryView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            status="active",
            published_at__isnull=False,
            category=self.kwargs["category_id"],
        )
        return queryset
    

class  PostListByTagView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            status="active",
            published_at__isnull=False,
            category=self.kwargs["tag_id"],
        )
        return queryset
    

class  DraftListView(ListAPIView):
    queryset = Post.objects.filter(published_at__isnull=True)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]


class  DraftDetailView(RetrieveAPIView):
    queryset = Post.objects.filter(published_at__isnull=True)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
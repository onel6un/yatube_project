from rest_framework import filters, pagination, viewsets

from posts.models import *

from .permission import *
from .serializers import *


class PostAPI(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (AuthorOrOnlyRead,)
    pagination_class = pagination.LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()


class GroupAPI(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentAPI(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrOnlyRead,)
    
    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        queryset = Comment.objects.filter(pk=post_id)
        return queryset
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post_comment = Post.objects.get(pk=post_id)
        serializer.save(
            author=self.request.user,
            post=post_comment
        )


class FollowAPI(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('following__username', )

    def get_queryset(self):
        queryset = Follow.objects.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

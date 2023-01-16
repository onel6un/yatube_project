from rest_framework import serializers
from rest_framework.relations import SlugRelatedField


from posts.models import *

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('post',)


class PostSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)
    comment = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'text', 'group', 'author', 'image', 'comment', 'pub_date')
        model = Post
        read_only_fields = ('comment',)

    def get_comment(self, obj):
        comments = Comment.objects.filter(post=obj.id)
        serializer = CommentSerializer(comments, many=True)
        return serializer.data


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Group


class FollowSerializer(serializers.ModelSerializer):
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        required=True
    )
    user = SlugRelatedField(slug_field='username', read_only=True)
    class Meta:
        fields = '__all__'
        model = Follow
        read_only_fields = ('user',)

    def validate_following(self, value):
        if value == self.context.get("request").user:
            raise serializers.ValidationError('Вы не можете подписаться сами на себя!')
        return value

    def validate(self, data):
        user = self.context.get("request").user
        following = data['following']
        follows_user = Follow.objects.filter(user=user)
        if follows_user.filter(following=following).contains:
            raise serializers.ValidationError('Вы уже подписанны на этого пользователя!')
        return data
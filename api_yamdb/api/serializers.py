from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import (Comment, Review, Categories, Genre, Title,
                            GenreTitle)

User = get_user_model()


class UserCreationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        max_length=254
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        required=True,
        max_length=150
    )

    def validate(self, data):
        user = User.objects.filter(email=data['email'],
                                   username=data['username'])
        if user.exists():
            return data
        else:
            email = User.objects.filter(email=data['email'])
            username = User.objects.filter(username=data['username'])
            if not email.exists() and not username.exists():
                return data
            else:
                raise serializers.ValidationError('email и username должны'
                                                  'быть уникальными')

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать me в качестве username')
        return value


class ConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'role', 'email',
                  'first_name', 'last_name', 'bio')
        read_only_fields = ('role',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'role',
                  'first_name', 'last_name', 'bio')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True)
    score = serializers.IntegerField(max_value=10, min_value=1)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data

        user = self.context['request'].user
        title_id = (
            self.context['request'].parser_context['kwargs']['title_id']
        )
        if Review.objects.filter(author=user, title__id=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на данное произведение'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class CategoriesSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(queryset=Categories.objects.all())])

    class Meta:
        model = Categories
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(queryset=Genre.objects.all())])

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class GenreConvertSerializer(serializers.ListField):

    def to_representation(self, value):
        print(value)
        genres = []
        if value is None:
            return None
        else:
            for val in value.all():
                genre = {'name': vars(val)['name'],
                         'slug': vars(val)['slug']}
                genres.append(genre)
            return genres

    def to_internal_value(self, data):
        print(data)
        genres = []
        for g in data:
            try:
                genre = Genre.objects.get(slug=g)
                genres.append(genre)
            except Genre.DoesNotExist:
                raise serializers.ValidationError(f'{g} - такого жанра '
                                                  f'не существует')
        print(genres)
        return genres


class CategoryConvertSerializer(serializers.Field):
    def to_representation(self, value):
        if vars(value) is None:
            return None
        else:
            category = {'name': vars(value)['name'],
                        'slug': vars(value)['slug']}
            return category

    def to_internal_value(self, data):
        try:
            category = Categories.objects.get(slug=data)
        except Categories.DoesNotExist:
            raise serializers.ValidationError(f'{data} - такой категории '
                                              f'не существует')
        return category


class TitleListSerializer(serializers.ModelSerializer):
    category = CategoriesSerializer(many=False, )
    genre = GenreSerializer(many=True, )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre',
                  'category', 'rating', 'id')
        read_only_field = ('id', )

    def get_rating(self, obj):
        raiting_count = (Title.objects
                         .filter(id=obj.pk)
                         .annotate(score_avg=Avg('reviews__score')))
        if list(raiting_count) == []:
            return None
        else:
            return list(raiting_count)[0].score_avg


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreConvertSerializer()
    name = serializers.CharField(required=True, max_length=256)
    year = serializers.IntegerField(required=True)
    category = CategoryConvertSerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre',
                  'category', 'rating', 'id')
        read_only_field = ('id', )

    def get_rating(self, obj):
        raiting_count = (Title.objects
                         .filter(id=obj.pk)
                         .annotate(score_avg=Avg('reviews__score')))
        if list(raiting_count) == []:
            return None
        else:
            return list(raiting_count)[0].score_avg

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        category = validated_data.pop('category')
        title = Title.objects.create(**validated_data, category=category)
        for genre in genres:
            GenreTitle.objects.create(genre=genre, title=title)
        return title

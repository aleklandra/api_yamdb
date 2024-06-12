import django_filters
from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name='year', lookup_expr='iexact',
                                       label='year')
    name = django_filters.CharFilter(field_name='name', lookup_expr='iexact',
                                     label='name')
    genre = django_filters.CharFilter(field_name='genre__slug',
                                      lookup_expr='iexact',
                                      label='genre')
    category = django_filters.CharFilter(field_name='category__slug',
                                         lookup_expr='iexact',
                                         label='category')

    class Meta:
        model = Title
        fields = ['year', 'name', 'genre', 'category']

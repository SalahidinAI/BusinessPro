from django_filters import FilterSet, DateFilter
from .models import SalesHistory

class SalesHistoryFilter(FilterSet):
    sold_date__gte = DateFilter(field_name='sold_date', lookup_expr='gte', label='Sold after or on')
    sold_date__lte = DateFilter(field_name='sold_date', lookup_expr='lte', label='Sold before or on')

    class Meta:
        model = SalesHistory
        fields = ['sold_date__gte', 'sold_date__lte']


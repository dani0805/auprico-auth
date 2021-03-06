import json

from auprico_core.schema import CountableConnectionBase
from graphql_relay import from_global_id
from graphene import Node
from .models import *
import graphene
import django_filters
from django.core.paginator import Paginator
from graphene_django import DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

'''
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class StateMutation(SerializerMutation):

    class Meta:
        serializer_class = UserSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'
'''


class CustomDjangoFilterConnectionField(DjangoFilterConnectionField):
    @classmethod
    def connection_resolver(cls, resolver, connection, default_manager, max_limit,
                            enforce_first_or_last, filterset_class, filtering_args,
                            root, info, **args):
        context = info.context
        filter_kwargs = args
        qs = default_manager.get_queryset()
        # filterset_class = args["filterset_class"]
        qs = filterset_class(data=filter_kwargs, queryset=qs, context=context).qs
        if args.get("first"):
            paginator = Paginator(qs, args.get("first"))
            page = str(int(args.get("after", "0")) + 1)
            qs = paginator.page(page)
        return DjangoConnectionField.connection_resolver(resolver, connection, qs, max_limit, enforce_first_or_last,
                                                         root, info, **args)


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        interfaces = (Node,)
        filter_fields = []
        connection_class = CountableConnectionBase


def user_custom_filter_action(query, field_name, value):
    qs = query.filter(is_active=True)
    if value:
        filters = json.loads(value)
        ids = filters.get('ids')
        term = filters.get('term')
        role = filters.get('role')
        _, team_id = from_global_id(filters.get('team_id')) if filters.get('team_id') else (None, None)
        #size = filters.get('size', 20)
        order_by = filters.get('order_by')
        #page = filters.get('page', 0)
        if ids:
            qs = qs.filter(id__in=ids)
        if role and not team_id:
            qs = qs.filter(affiliations__role__name=role)
        if team_id and not role:
            qs = qs.filter(affiliations__team_id=team_id)
        if team_id and role:
            affiliations = Affiliation.objects.filter(team_id=team_id, role__name=role)
            qs = qs.filter(affiliations__in=affiliations)
        if term:
            searchTerms = term.split(' ')
            for t in searchTerms:
                qs = qs.filter(first_name__icontains=t) | \
                     qs.filter(last_name__icontains=t) | \
                     qs.filter(username__icontains=t) | \
                     qs.filter(emails__val__icontains=t)

        if order_by:
            qs = qs.order_by(order_by).distinct()
        return qs
    return qs


class UserFilter(django_filters.FilterSet):
    # Do case-insensitive lookups on 'name'
    json_filter = django_filters.CharFilter(method=user_custom_filter_action)
    context = None

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context')
        super(UserFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ['json_filter']

    @property
    def qs(self):
        filtered_qs = super(UserFilter, self).qs
        relay_id = self.data.get("mdv_id")
        return filtered_qs


class UserQuery(graphene.ObjectType):
    all_users = DjangoFilterConnectionField(UserNode)
    filter_user = CustomDjangoFilterConnectionField(UserNode, filterset_class=UserFilter)
    user = Node.Field(UserNode)

    def resolve_all_users(self, info):
        return User.objects.all()


class UserEmailNode(DjangoObjectType):
    class Meta:
        model = UserEmail
        interfaces = (Node,)
        filter_fields = []
        connection_class = CountableConnectionBase


class UserAddressNode(DjangoObjectType):
    class Meta:
        model = UserAddress
        interfaces = (Node,)
        filter_fields = []
        connection_class = CountableConnectionBase


class UserPhoneNode(DjangoObjectType):
    class Meta:
        model = UserPhone
        interfaces = (Node,)
        filter_fields = []
        connection_class = CountableConnectionBase


class TeamNode(DjangoObjectType):
    class Meta:
        model = Team
        interfaces = (Node,)
        filter_fields = []
        connection_class = CountableConnectionBase


def team_custom_filter_action(query, field_name, value):
    qs = query.all()
    if value:
        filters = json.loads(value)
        ids = filters.get('ids')
        term = filters.get('term')
        #size = filters.get('size', 20)
        order_by = filters.get('order_by')
        #page = filters.get('page', 0)
        if ids:
            qs = qs.filter(id__in=ids)
        if term:
            searchTerms = term.split(' ')
            for t in searchTerms:
                qs = qs.filter(name__icontains=t) | \
                     qs.filter(code__icontains=t)
        if order_by:
            qs = qs.order_by(order_by).distinct()
        return qs
    return qs


class TeamFilter(django_filters.FilterSet):
    # Do case-insensitive lookups on 'name'
    json_filter = django_filters.CharFilter(method=team_custom_filter_action)
    context = None

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context')
        super(TeamFilter, self).__init__(*args, **kwargs)

    class Meta:
        model = Team
        fields = ['json_filter']

    @property
    def qs(self):
        filtered_qs = super(TeamFilter, self).qs
        relay_id = self.data.get("mdv_id")
        return filtered_qs


class TeamQuery(graphene.ObjectType):
    all_teams = DjangoFilterConnectionField(TeamNode)
    filter_team = CustomDjangoFilterConnectionField(TeamNode, filterset_class=TeamFilter)
    team = Node.Field(TeamNode)

    def resolve_all_teams(self, info):
        return Team.objects.all()

from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.rest_framework.mutation import SerializerMutation
from rest_framework import serializers
from graphene import Node
from graphene_django import DjangoObjectType
from .models import *
import graphene
from graphene_django.debug import DjangoDebug

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


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = []
        interfaces = (Node,)


class UserQuery(graphene.ObjectType):
    all_users = DjangoFilterConnectionField(UserNode)
    user = Node.Field(UserNode)

    def resolve_all_users(self, info):
        return User.objects.all()

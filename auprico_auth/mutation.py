import graphene

from auprico_auth.model_service.user import create_user
from auprico_auth.schema import UserNode


class CreateUser(graphene.ClientIDMutation):
    class Input:
        username = graphene.String()
        password = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()

    user = graphene.Field(UserNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        data = input

        user = create_user(info.context, data)

        return CreateUser(user=user)


class Mutation(graphene.AbstractType):
    create_user = CreateUser.Field()

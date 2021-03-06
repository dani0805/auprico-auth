import graphene
from django.db.transaction import atomic
from graphql_relay import from_global_id

from auprico_auth.model_service.team import create_team, update_team
from auprico_auth.model_service.user import create_user, update_user, update_user_password
from auprico_auth.schema import UserNode, TeamNode


class CreateUser(graphene.ClientIDMutation):
    class Input:
        username = graphene.String()
        password = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()

    user = graphene.Field(UserNode)

    @classmethod
    @atomic
    def mutate_and_get_payload(cls, root, info, **input):
        data = input

        user = create_user(info.context, data)

        return CreateUser(user=user)


class UpdateUser(graphene.ClientIDMutation):
    class Input:
        id = graphene.String()
        gender = graphene.String()
        title = graphene.String()
        language_id = graphene.String()
        institution = graphene.String()
        department = graphene.String()
        job_description = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()
        # json dumps [{}]
        emails = graphene.String()
        phones = graphene.String()
        addresses = graphene.String()

    user = graphene.Field(UserNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        data = kwargs
        # load real id
        node, data['id'] = from_global_id(data['id'])

        # data['emails'] = json.loads(data.get('emails', '[]'))
        # data['phones'] = json.loads(data.get('phones', '[]'))
        # data['addresses'] = json.loads(data.get('addresses', '[]'))

        if data.get('language_id'):
            _, data['language_id'] = from_global_id(data['language_id'])

        if node == "UserNode":
            # mis.models.User (DETAIL)
            user = update_user(info.context, data)
            return UpdateUser(user=user)


class UpdateUserPassword(graphene.ClientIDMutation):
    class Input:
        id = graphene.String()
        password = graphene.String()

    user = graphene.Field(UserNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        data = kwargs
        # load real id
        node, data['id'] = from_global_id(data['id'])

        if node == "UserNode":
            # mis.models.User (DETAIL)
            user = update_user_password(info.context, data)
            return UpdateUserPassword(user=user)


class CreateTeam(graphene.ClientIDMutation):
    class Input:
        name = graphene.String()
        code = graphene.String()

    team = graphene.Field(TeamNode)

    @classmethod
    @atomic
    def mutate_and_get_payload(cls, root, info, **input):
        data = input

        team = create_team(info.context, data)

        return CreateTeam(team=team)


class UpdateTeam(graphene.ClientIDMutation):
    class Input:
        id = graphene.String()
        name = graphene.String()
        code = graphene.String()

    team = graphene.Field(TeamNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        data = kwargs
        # load real id
        node, data['id'] = from_global_id(data['id'])

        if node == "TeamNode":
            team = update_team(info.context, data)
            return UpdateTeam(team=team)


class Mutation(graphene.AbstractType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    create_team = CreateTeam.Field()
    update_team = UpdateTeam.Field()
    update_user_password = UpdateUserPassword.Field()

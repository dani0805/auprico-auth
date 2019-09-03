from auprico_auth.models import Team


def create_team(context, params):
    """
    Create a new team in the system (models.Team)
    :param params: metadata/dictionary-like that characterize the team
    :return:
    """
    form_team = dict()

    form_team['name'] = params.get('name')
    form_team['code'] = params.get('code')

    team = Team.objects.create(**form_team)

    return team


def update_team(context, params):
    """
    Update team informations (models.Team)
    :param params: metadata/dictionary-like that characterize the team
    :return:
    """

    team = Team.objects.filter(id=params.get('id')).first()
    if not team:
        raise ValueError("team not found")

    team.name = params.get('name')
    team.code = params.get('code')

    return team

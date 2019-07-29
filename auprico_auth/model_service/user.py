from auprico_core.models import Language
from auprico_workflow.utils import camelcase_to_underscore

from auprico_auth.models import User, UserEmail


def create_username(params):
    if params.get('username'):
        return params.get('username')
    username = ""
    try:
        username += params.get('first_name')[0]
        username += params.get('last_name')
    except:
        raise ValueError('first/last name not found')

    return username


def create_person(params):
    """
    Create a dictionary with the person fields filled with params
    :param params: dictionary with the information for person field
    :return: {} (the filled dictionary)
    """
    form = dict()
    form['gender'] = params.get('gender', None)
    form['title'] = params.get('title', None)

    return form


def create_email(context, params):
    """
    Create a person email
    :param context: dict-like object
    :param params: email information
    :return: mis.models.Email
    """
    updated = {}
    for key in params:
        updated[camelcase_to_underscore(key)] = params[key]
    params = updated
    if not params.get('val') or params.get('is_deleted'):
        return None
    form_email = dict()
    if not params.get('label'):
        form_email['label'] = "Office"
    form_email['label'] = params.get('label')
    form_email['is_main'] = params.get('is_main', False)
    form_email['value'] = params.get('val')
    # form_email['edited_by'] = context.user
    form_email['user'] = params.get('person')
    return UserEmail.objects.create(**form_email)


def create_user(context, params):
    """
    Create a new user in the system (mis.models.User)
    :param params: metadata/dictionary-like that characterize the user
    :return:
    """
    form_user = dict()
    # form_user['edited_by'] = context.user
    if params.get('username'):
        form_user['username'] = params.get('username')
    else:
        form_user['username'] = create_username(params)  # 'email_user{}'.format(MISUser.objects.latest('id').id + 1
    form_user['first_name'] = params.get('first_name')
    form_user['last_name'] = params.get('last_name')
    form_person = create_person(params)
    form_user.update(form_person)
    user = User.objects.create(**form_user)
    user.set_password(params.get('password'))

    email = {'label': 'Work', 'val': params.get('email'), 'person': user, 'is_main': True}
    create_email(context, email)

    user.save()
    return user


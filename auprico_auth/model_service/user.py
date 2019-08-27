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

def update_person(context, obj, params):
    """
    Update the person fields in obj
    :param obj: model to update (user / inquirer)
    :param params: fields to update
    :return:
    """

    obj.gender = params.get('gender')
    obj.first_name = params.get('first_name')
    obj.last_name = params.get('last_name')
    obj.title = params.get('title')
    if params.get('language'):
        obj.language = params.get('language')
    else:
        obj.language = Language.objects.filter(id=params.get('language_id')).first()
    obj.institution = params.get('institution')
    obj.department = params.get('department')
    obj.job_description = params.get('job_description')
    # count isMain (non-deleted) object, we must always have 1 main contact
    # count_main_contact = _count_main_contact(params)

    # for email in params.get('emails', []):
    #     if not email.get('val'):
    #         continue
    #     if count_main_contact == 0:
    #         email['isMain'] = True
    #         count_main_contact = 1
    #     if email.get('id'):
    #         update_email(context, email)
    #     else:
    #         email['person'] = obj
    #         create_email(context, email)
    # for phone in params.get('phones', []):
    #     if not phone.get('val'):
    #         continue
    #     if count_main_contact == 0:
    #         phone['isMain'] = True
    #         count_main_contact = 1
    #     if phone.get('id'):
    #         update_phone(context, phone)
    #     else:
    #         phone['person'] = obj
    #         create_phone(context, phone)
    # for address in params.get('addresses', []):
    #     if count_main_contact == 0:
    #         address['isMain'] = True
    #         count_main_contact = 1
    #     if address.get('id'):
    #         update_address(context, address)
    #     else:
    #         address['person'] = obj
    #         create_address(context, address)

    if not (obj.emails.exists() or obj.phones.exists() or obj.addresses.exists()):
        raise ValueError("At least one contact must be specified")


def update_user(context, params):
    """
    Update user informations (mis.models.User)
    :param params: metadata/dictionary-like that characterize the user
    :return:
    """

    user = User.objects.filter(id=params.get('id')).first()
    if not user:
        raise ValueError("user not found")
    user.language = Language.objects.filter(id=params.get('language_id', None)).first()
    user.deputy = User.objects.filter(id=params.get('deputy_id', None)).first()
    # user.edited_by = context.user

    user.save()

    update_person(context, user, params)

    user.save()
    return user

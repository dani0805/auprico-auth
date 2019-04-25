import ast

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now as django_now
from auprico_core.models import Person, Email, Address, Language, Country

# Create your models here.
from django.db.models import PROTECT
from django.utils.translation import ugettext_lazy


# django-admin.py makemigrations auprico_auth --settings=test_settings

class Version(models.Model):
    version_number = models.IntegerField()
    edited_ts = models.DateTimeField()
    edited_by = models.ForeignKey("User", on_delete=PROTECT, null=True, blank=True)


class VersionChange(models.Model):
    version = models.ForeignKey(Version, on_delete=PROTECT)
    fieldname = models.CharField(max_length=400)
    old_value = models.CharField(max_length=4000)
    new_value = models.CharField(max_length=4000)


class VersionChangeClob(models.Model):
    version = models.ForeignKey(Version, on_delete=PROTECT)
    fieldname = models.CharField(max_length=400)
    old_value = models.TextField(max_length=60000)
    new_value = models.TextField(max_length=60000)


class VersionedModel(models.Model):
    versioned_fields = None
    created_ts = models.DateTimeField(default=django_now)
    created_by = models.ForeignKey("User", on_delete=PROTECT, null=True, blank=True,  related_name="%(app_label)s_%(class)s_created")
    edited_ts = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey("User", on_delete=PROTECT, null=True, blank=True, related_name="%(app_label)s_%(class)s_edited")
    versions = models.ManyToManyField(Version, related_name="%(app_label)s_%(class)s")

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(VersionedModel, self).__init__(*args, **kwargs)
        # default to all fields being versioned except the created and edited
        if self.versioned_fields is None:
            self.versioned_fields = [f.name for f in type(self)._meta.get_fields() if f.name not in ['created_ts', 'created_by', 'edited_ts', 'edited_by', 'version']]
        self.changed_by_user: User = None
        if self.pk:
            for field in self.versioned_fields:
                setattr(self, '__original_%s' % field, getattr(self, field))

    def has_changed(self):
        if self.pk is None:
            return True
        for field in self.versioned_fields:
            orig = '__original_%s' % field
            if (hasattr(self, orig) and getattr(self, orig) != getattr(self, field)) or (not hasattr(self, orig) and hasattr(self, field)):
                return True
        return False

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.has_changed():
            if self.changed_by_user is not None:
                self.edited_by = self.changed_by_user
                self.edited_ts = django_now()
                if self.pk is None:
                    self.created_by = self.changed_by_user
                last_version = self.versions.order_by("-version_number").first()
                version_number = 1
                if last_version is not None:
                    version_number = last_version.version_number + 1
                new_version = Version.objects.create(version_number=version_number, edited_by=self.changed_by_user, edited_ts=django_now())
                for field in self.versioned_fields:
                    orig = '__original_%s' % field
                    old_value = getattr(self, orig, None)
                    new_value = getattr(self, field, None)
                    if old_value != new_value:
                        VersionChange.objects.create(version=new_version, fieldname=field, old_value=str(old_value)[:4000], new_value=str(new_value)[:4000])
        super(VersionedModel, self).save()


class Team(VersionedModel):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    default_language = models.ForeignKey(Language, on_delete=PROTECT, null=True, blank=True)
    segregated_data = models.BooleanField(default=False)
    restricted_team = models.BooleanField(default=False)
    private_team = models.BooleanField(default=False)
    timezone_code = models.CharField(max_length=20, null=True)
    parent_team = models.ForeignKey("Team", on_delete=PROTECT, null=True, blank=True, related_name='sub_teams')
    countries = models.ManyToManyField(Country, blank=True, related_name='teams')
    override_cluster_root = models.ForeignKey("Team", on_delete=PROTECT, null=True, blank=True, default=None, related_name='cluster_root_for_teams')

    class GraphCache:
        def __init__(self, team, direct_graph=None, inverse_graph=None):
            self.team = team
            self._direct_graph = direct_graph
            self._inverse_graph = inverse_graph
            self._segregated_cluster_descendants = None
            self._segregated_cluster = None
            self._segregated_cluster_root = None
            self._cluster_root = None
            self._segregated_cluster_ancestors = None
            self._cluster_ancestors = None
            self._cluster_descendants = None
            self._cluster = None

        @property
        def direct_graph(self):
            if self._direct_graph is None:
                self._direct_graph, self._inverse_graph = Team.team_graph()
            return self._direct_graph

        @property
        def inverse_graph(self):
            if self._inverse_graph is None:
                self._direct_graph, self._inverse_graph = Team.team_graph()
            return self._inverse_graph

        @property
        def segregated_cluster_descendants(self):
            if self._segregated_cluster_descendants is None:
                ids = self.team.segregated_cluster_descendants_ids(self.direct_graph, self.inverse_graph)
                self._segregated_cluster_descendants = Team.objects.filter(id__in=ids)
            return self._segregated_cluster_descendants

        @property
        def segregated_cluster(self):
            if self._segregated_cluster is None:
                ids = self.team.segregated_cluster_ids(self.direct_graph, self.inverse_graph)
                self._segregated_cluster = Team.objects.filter(id__in=ids)
            return self._segregated_cluster

        @property
        def segregated_cluster_root(self):
            if self._segregated_cluster_root is None:
                id = self.team.segregated_cluster_root_id(self.direct_graph, self.inverse_graph)
                self._segregated_cluster_root = Team.objects.get(id=id)
            return self._segregated_cluster_root

        @property
        def cluster_root(self):
            if self._cluster_root is None:
                id = self.team.cluster_root_id(self.direct_graph, self.inverse_graph)
                self._cluster_root = Team.objects.get(id=id)
            return self._cluster_root

        @property
        def segregated_cluster_ancestors(self):
            if self._segregated_cluster_ancestors is None:
                ids = self.team.segregated_cluster_ancestors_ids(self.direct_graph, self.inverse_graph)
                self._segregated_cluster_ancestors = Team.objects.filter(id__in=ids)
            return self._segregated_cluster_ancestors

        @property
        def cluster_ancestors(self):
            if self._cluster_ancestors is None:
                ids = self.team.cluster_ancestors_ids(self.direct_graph, self.inverse_graph)
                self._cluster_ancestors = Team.objects.filter(id__in=ids)
            return self._cluster_ancestors

        @property
        def cluster_descendants(self):
            if self._cluster_descendants is None:
                ids = self.team.cluster_descendants_ids(self.direct_graph, self.inverse_graph)
                self._cluster_descendants = Team.objects.filter(id__in=ids)
            return self._cluster_descendants

        @property
        def cluster(self):
            if self._cluster is None:
                ids = self.team.cluster_ids(self.direct_graph, self.inverse_graph)
                self._cluster = Team.objects.filter(id__in=ids)
            return self._cluster

    @classmethod
    def team_graph(cls):
        all_teams = Team.objects.all().values_list(
            "id", "parent_team__id", "private_team", "restricted_team", "segregated_data", "override_cluster_root__id")
        inverse_graph = {
            t[0]: {
            "parent_team__id": t[1],
            "private_team": t[2],
            "restricted_team": t[3],
            "segregated_data": t[4],
            "override_cluster_root__id": t[5]}
            for t in all_teams
        }
        direct_graph = {
            t[0]: [
                c[0] for c in all_teams
                if c[1] == t[0]
            ] for t in all_teams
        }
        return direct_graph, inverse_graph

    @classmethod
    def _segregated_cluster_descendants_ids(cls, team_id, direct_graph, inverse_graph):
        first_lev_cluster = [
            x for x in direct_graph[team_id]
            if not inverse_graph[x]["segregated_data"]
               and not inverse_graph[x]["private_team"]
        ]
        return [team_id,]  + [
            z
            for y in first_lev_cluster
            for z in Team._segregated_cluster_descendants_ids(y, direct_graph, inverse_graph)
        ]

    def segregated_cluster_descendants_ids(self, direct_graph, inverse_graph):
        return Team._segregated_cluster_descendants_ids(self.id, direct_graph, inverse_graph)

    def segregated_cluster_ids(self, direct_graph, inverse_graph):
        root = self.segregated_cluster_root_id(direct_graph, inverse_graph)
        return Team._segregated_cluster_descendants_ids(root, direct_graph, inverse_graph)

    def segregated_cluster_root_id(self, direct_graph, inverse_graph):
        root = self.id
        while inverse_graph[root]["parent_team__id"] \
                and not inverse_graph[root]["segregated_data"] \
                and not inverse_graph[root]["restricted_team"] \
                and root != self.override_cluster_root_id:
            root = inverse_graph[root]["parent_team__id"]
        return root

    def cluster_root_id(self, direct_graph, inverse_graph):
        root = self.id
        while inverse_graph[root]["parent_team__id"] \
                and root != self.override_cluster_root_id:
            root = inverse_graph[root]["parent_team__id"]
        return root

    def segregated_cluster_ancestors_ids(self, direct_graph, inverse_graph):
        team = self.id
        teams = [team,]
        while inverse_graph[team]["parent_team__id"] \
                and not inverse_graph[team]["segregated_data"] \
                and not inverse_graph[team]["restricted_team"] \
                and team != self.override_cluster_root_id:
            team = inverse_graph[team]["parent_team__id"]
            teams = teams + [team,]
        return teams

    def cluster_ancestors_ids(self, direct_graph, inverse_graph):
        team = self.id
        teams = [team, ]
        while inverse_graph[team]["parent_team__id"] \
                and team != self.override_cluster_root_id:
            team = inverse_graph[team]["parent_team__id"]
            teams = teams + [team, ]
        return teams

    @classmethod
    def _cluster_descendants_ids(cls, team_id, direct_graph, inverse_graph):
        return [team_id,] + [
            z
            for y in direct_graph[team_id]
            for z in Team._cluster_descendants_ids(y, direct_graph, inverse_graph)
        ]

    def cluster_descendants_ids(self, direct_graph, inverse_graph):
        return Team._cluster_descendants_ids(self.id, direct_graph, inverse_graph)

    def cluster_ids(self, direct_graph, inverse_graph):
        root = self.cluster_root_id(direct_graph, inverse_graph)
        return Team._cluster_descendants_ids(root, direct_graph, inverse_graph)

    def nearest_neighbour(self,direct_graph, inverse_graph, candidates):
        candidates_id = [x.id for x in candidates]
        for id in self.segregated_cluster_descendants_ids(direct_graph, inverse_graph):
            if id in candidates_id:
                return [x for x in candidates if x.id == id][0]
        for id in self.segregated_cluster_ancestors_ids(direct_graph, inverse_graph):
            if id in candidates_id:
                return [x for x in candidates if x.id == id][0]
        for id in self.segregated_cluster_ids(direct_graph, inverse_graph):
            if id in candidates_id:
                return [x for x in candidates if x.id == id][0]
        for id in self.cluster_descendants_ids(direct_graph, inverse_graph):
            if id in candidates_id:
                return [x for x in candidates if x.id == id][0]
        for id in self.cluster_ancestors_ids(direct_graph, inverse_graph):
            if id in candidates_id:
                return [x for x in candidates if x.id == id][0]
        for id in self.cluster_ids(direct_graph, inverse_graph):
            if id in candidates_id:
                return [x for x in candidates if x.id == id][0]
        return None


class Role(VersionedModel):
    name = models.CharField(max_length=20, verbose_name=ugettext_lazy("Name"))
    description = models.CharField(max_length=200, verbose_name=ugettext_lazy("Description"))


class Affiliation(VersionedModel):
    team = models.ForeignKey(Team, on_delete=PROTECT, related_name='affiliations_for_team')
    user = models.ForeignKey("User", on_delete=PROTECT, related_name='affiliations')
    role = models.ForeignKey(Role, on_delete=PROTECT)


class ObjectPermission(VersionedModel):
    object_type = models.CharField(max_length=200, verbose_name=ugettext_lazy("Object Type"))
    role = models.ForeignKey(Role, models.CASCADE, verbose_name=ugettext_lazy("Role"), related_name='object_permissions')
    create_own_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Create for own team"))
    delete_own_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Delete for own team"))
    edit_own_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Edit for own team"))
    view_own_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("View for own team"))
    list_own_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("List for own team"))
    create_descendant_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Create for any descendant team"))
    delete_descendant_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Delete for any descendant team"))
    edit_descendant_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Edit for any descendant team"))
    view_descendant_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("View for any descendant team"))
    list_descendant_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("List for any descendant team"))
    create_segregated_descendant_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Create for non segregated descendant team"))
    delete_segregated_descendant_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Delete for non segregated descendant team"))
    edit_segregated_descendant_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Edit for non segregated descendant team"))
    view_segregated_descendant_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("View for non segregated descendant team"))
    list_segregated_descendant_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("List for non segregated descendant team"))
    create_cluster_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Create for any cluster team"))
    delete_cluster_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Delete for any cluster team"))
    edit_cluster_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Edit for any cluster team"))
    view_cluster_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("View for any cluster team"))
    list_cluster_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("List for any cluster team"))
    create_segregated_cluster_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Create for non segregated cluster team"))
    delete_segregated_cluster_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Delete for non segregated cluster team"))
    edit_segregated_cluster_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Edit for non segregated cluster team"))
    view_segregated_cluster_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("View for non segregated cluster team"))
    list_segregated_cluster_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("List for non segregated cluster team"))
    create_any_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Create for any team"))
    delete_any_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Delete for any team"))
    edit_any_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("Edit for any team"))
    view_any_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("View for any team"))
    list_any_team = models.BooleanField(default=False, verbose_name=ugettext_lazy("List for any team"))
    # dictionary includes extra filters to be applied structure should be like
    # {"list_cluster_team": {"status_label__icontains":"New"}}
    filters = models.CharField(max_length=4000, default=None, null=True, blank=True, verbose_name=ugettext_lazy("Filters"))

class ObjectPermissionProxy:

    def __init__(self, *args, **kwargs):
        self.object_type = kwargs.get("object_type", "")
        self.team = None
        self.create_own_team = False
        self.delete_own_team = False
        self.edit_own_team = False
        self.view_own_team = False
        self.list_own_team = False
        self.create_descendant_team = False
        self.delete_descendant_team = False
        self.edit_descendant_team = False
        self.view_descendant_team = False
        self.list_descendant_team = False
        self.create_segregated_descendant_team = False
        self.delete_segregated_descendant_team = False
        self.edit_segregated_descendant_team = False
        self.view_segregated_descendant_team = False
        self.list_segregated_descendant_team = False
        self.create_cluster_team = False
        self.delete_cluster_team = False
        self.edit_cluster_team = False
        self.view_cluster_team = False
        self.list_cluster_team = False
        self.create_segregated_cluster_team = False
        self.delete_segregated_cluster_team = False
        self.edit_segregated_cluster_team = False
        self.view_segregated_cluster_team = False
        self.list_segregated_cluster_team = False
        self.create_any_team = False
        self.delete_any_team = False
        self.edit_any_team = False
        self.view_any_team = False
        self.list_any_team = False
        self.filters = {}

    def or_object_permission(self, objectPermission):
        assert self.object_type == objectPermission.object_type
        self.create_own_team = self.create_own_team or objectPermission.create_own_team
        self.delete_own_team = self.delete_own_team or objectPermission.delete_own_team
        self.edit_own_team = self.edit_own_team or objectPermission.edit_own_team
        self.view_own_team = self.view_own_team or objectPermission.view_own_team
        self.list_own_team = self.list_own_team or objectPermission.list_own_team
        self.create_descendant_team = self.create_descendant_team or objectPermission.create_descendant_team
        self.delete_descendant_team = self.delete_descendant_team or objectPermission.delete_descendant_team
        self.edit_descendant_team = self.edit_descendant_team or objectPermission.edit_descendant_team
        self.view_descendant_team = self.view_descendant_team or objectPermission.view_descendant_team
        self.list_descendant_team = self.list_descendant_team or objectPermission.list_descendant_team
        self.create_segregated_descendant_team = self.create_segregated_descendant_team or \
                                                 objectPermission.create_segregated_descendant_team
        self.delete_segregated_descendant_team = self.delete_segregated_descendant_team or \
                                                 objectPermission.delete_segregated_descendant_team
        self.edit_segregated_descendant_team = self.edit_segregated_descendant_team or \
                                               objectPermission.edit_segregated_descendant_team
        self.view_segregated_descendant_team = self.view_segregated_descendant_team or \
                                               objectPermission.view_segregated_descendant_team
        self.list_segregated_descendant_team = self.list_segregated_descendant_team or \
                                               objectPermission.list_segregated_descendant_team
        self.create_cluster_team = self.create_cluster_team or objectPermission.create_cluster_team
        self.delete_cluster_team = self.delete_cluster_team or objectPermission.delete_cluster_team
        self.edit_cluster_team = self.edit_cluster_team or objectPermission.edit_cluster_team
        self.view_cluster_team = self.view_cluster_team or objectPermission.view_cluster_team
        self.list_cluster_team = self.list_cluster_team or objectPermission.list_cluster_team
        self.create_segregated_cluster_team = self.create_segregated_cluster_team or \
                                              objectPermission.create_segregated_cluster_team
        self.delete_segregated_cluster_team = self.delete_segregated_cluster_team or \
                                              objectPermission.delete_segregated_cluster_team
        self.edit_segregated_cluster_team = self.edit_segregated_cluster_team or \
                                            objectPermission.edit_segregated_cluster_team
        self.view_segregated_cluster_team = self.view_segregated_cluster_team or \
                                            objectPermission.view_segregated_cluster_team
        self.list_segregated_cluster_team = self.list_segregated_cluster_team or \
                                            objectPermission.list_segregated_cluster_team
        self.create_any_team = self.create_any_team or objectPermission.create_any_team
        self.delete_any_team = self.delete_any_team or objectPermission.delete_any_team
        self.edit_any_team = self.edit_any_team or objectPermission.edit_any_team
        self.view_any_team = self.view_any_team or objectPermission.view_any_team
        self.list_any_team = self.list_any_team or objectPermission.list_any_team
        if objectPermission.filters is not None and len(objectPermission.filters) > 6:
            filter_dict = ast.literal_eval(objectPermission.filters)
            for key in filter_dict:
                if key in self.filters:
                    self.filters[key].append(filter_dict[key])
                else:
                    self.filters[key] = [filter_dict[key], ]


class User(AbstractUser, Person, VersionedModel):
    first_name = models.CharField('first name', max_length=300, blank=True)
    last_name = models.CharField('last name', max_length=300, blank=True)

    def object_permissions(self, object_type):
        all_object_permissions = ObjectPermission.objects.all()
        object_permissions = dict()
        for affiliation in self.affiliations.all().select_related("team", "role"):
            if affiliation.team not in object_permissions:
                object_permissions.update({affiliation.team: ObjectPermissionProxy(object_type=object_type)})
            proxy = object_permissions.get(affiliation.team)
            for objPermission in all_object_permissions.filter(role__id=affiliation.role.id, object_type=object_type):
                proxy.or_object_permission(objPermission)
            object_permissions.update({affiliation.team: proxy})
        return object_permissions


class UserEmail(Email, VersionedModel):
    user = models.ForeignKey(User, on_delete=PROTECT, related_name="emails")


class UserAddress(Address, VersionedModel):
    user = models.ForeignKey(User, on_delete=PROTECT, related_name="addresses")

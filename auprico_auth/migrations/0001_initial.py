# Generated by Django 2.2 on 2019-04-25 07:27

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('auprico_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('gender', models.CharField(blank=True, max_length=10, null=True)),
                ('title', models.CharField(blank=True, max_length=40, null=True)),
                ('created_ts', models.DateTimeField(default=django.utils.timezone.now)),
                ('edited_ts', models.DateTimeField(blank=True, null=True)),
                ('first_name', models.CharField(blank=True, max_length=300, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=300, verbose_name='last name')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auprico_auth_user_created', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auprico_auth_user_edited', to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_number', models.IntegerField()),
                ('edited_ts', models.DateTimeField()),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VersionChangeClob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fieldname', models.CharField(max_length=400)),
                ('old_value', models.TextField(max_length=60000)),
                ('new_value', models.TextField(max_length=60000)),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auprico_auth.Version')),
            ],
        ),
        migrations.CreateModel(
            name='VersionChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fieldname', models.CharField(max_length=400)),
                ('old_value', models.CharField(max_length=4000)),
                ('new_value', models.CharField(max_length=4000)),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auprico_auth.Version')),
            ],
        ),
        migrations.CreateModel(
            name='UserEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=30)),
                ('is_main', models.BooleanField(default=False)),
                ('created_ts', models.DateTimeField(default=django.utils.timezone.now)),
                ('edited_ts', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('value', models.EmailField(max_length=300)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auprico_auth_useremail_created', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auprico_auth_useremail_edited', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='emails', to=settings.AUTH_USER_MODEL)),
                ('versions', models.ManyToManyField(related_name='auprico_auth_useremail', to='auprico_auth.Version')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_1', models.CharField(blank=True, max_length=1000, null=True)),
                ('address_2', models.CharField(blank=True, max_length=1000, null=True)),
                ('city', models.CharField(blank=True, max_length=200, null=True)),
                ('state', models.CharField(blank=True, max_length=200, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=10, null=True)),
                ('created_ts', models.DateTimeField(default=django.utils.timezone.now)),
                ('edited_ts', models.DateTimeField(blank=True, null=True)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='auprico_core.Country')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auprico_auth_useraddress_created', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auprico_auth_useraddress_edited', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='addresses', to=settings.AUTH_USER_MODEL)),
                ('versions', models.ManyToManyField(related_name='auprico_auth_useraddress', to='auprico_auth.Version')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_ts', models.DateTimeField(default=django.utils.timezone.now)),
                ('edited_ts', models.DateTimeField(blank=True, null=True)),
                ('code', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=200)),
                ('segregated_data', models.BooleanField(default=False)),
                ('restricted_team', models.BooleanField(default=False)),
                ('private_team', models.BooleanField(default=False)),
                ('timezone_code', models.CharField(max_length=20, null=True)),
                ('countries', models.ManyToManyField(blank=True, related_name='teams', to='auprico_core.Country')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auprico_auth_team_created', to=settings.AUTH_USER_MODEL)),
                ('default_language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='auprico_core.Language')),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auprico_auth_team_edited', to=settings.AUTH_USER_MODEL)),
                ('override_cluster_root', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cluster_root_for_teams', to='auprico_auth.Team')),
                ('parent_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sub_teams', to='auprico_auth.Team')),
                ('versions', models.ManyToManyField(related_name='auprico_auth_team', to='auprico_auth.Version')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_ts', models.DateTimeField(default=django.utils.timezone.now)),
                ('edited_ts', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=20, verbose_name='Name')),
                ('description', models.CharField(max_length=200, verbose_name='Description')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auprico_auth_role_created', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auprico_auth_role_edited', to=settings.AUTH_USER_MODEL)),
                ('versions', models.ManyToManyField(related_name='auprico_auth_role', to='auprico_auth.Version')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ObjectPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_ts', models.DateTimeField(default=django.utils.timezone.now)),
                ('edited_ts', models.DateTimeField(blank=True, null=True)),
                ('object_type', models.CharField(max_length=200, verbose_name='Object Type')),
                ('create_own_team', models.BooleanField(default=False, verbose_name='Create for own team')),
                ('delete_own_team', models.BooleanField(default=False, verbose_name='Delete for own team')),
                ('edit_own_team', models.BooleanField(default=False, verbose_name='Edit for own team')),
                ('view_own_team', models.BooleanField(default=False, verbose_name='View for own team')),
                ('list_own_team', models.BooleanField(default=False, verbose_name='List for own team')),
                ('create_descendant_team', models.BooleanField(default=False, verbose_name='Create for any descendant team')),
                ('delete_descendant_team', models.BooleanField(default=False, verbose_name='Delete for any descendant team')),
                ('edit_descendant_team', models.BooleanField(default=False, verbose_name='Edit for any descendant team')),
                ('view_descendant_team', models.BooleanField(default=False, verbose_name='View for any descendant team')),
                ('list_descendant_team', models.BooleanField(default=False, verbose_name='List for any descendant team')),
                ('create_segregated_descendant_team', models.BooleanField(default=False, verbose_name='Create for non segregated descendant team')),
                ('delete_segregated_descendant_team', models.BooleanField(default=False, verbose_name='Delete for non segregated descendant team')),
                ('edit_segregated_descendant_team', models.BooleanField(default=False, verbose_name='Edit for non segregated descendant team')),
                ('view_segregated_descendant_team', models.BooleanField(default=False, verbose_name='View for non segregated descendant team')),
                ('list_segregated_descendant_team', models.BooleanField(default=False, verbose_name='List for non segregated descendant team')),
                ('create_cluster_team', models.BooleanField(default=False, verbose_name='Create for any cluster team')),
                ('delete_cluster_team', models.BooleanField(default=False, verbose_name='Delete for any cluster team')),
                ('edit_cluster_team', models.BooleanField(default=False, verbose_name='Edit for any cluster team')),
                ('view_cluster_team', models.BooleanField(default=False, verbose_name='View for any cluster team')),
                ('list_cluster_team', models.BooleanField(default=False, verbose_name='List for any cluster team')),
                ('create_segregated_cluster_team', models.BooleanField(default=False, verbose_name='Create for non segregated cluster team')),
                ('delete_segregated_cluster_team', models.BooleanField(default=False, verbose_name='Delete for non segregated cluster team')),
                ('edit_segregated_cluster_team', models.BooleanField(default=False, verbose_name='Edit for non segregated cluster team')),
                ('view_segregated_cluster_team', models.BooleanField(default=False, verbose_name='View for non segregated cluster team')),
                ('list_segregated_cluster_team', models.BooleanField(default=False, verbose_name='List for non segregated cluster team')),
                ('create_any_team', models.BooleanField(default=False, verbose_name='Create for any team')),
                ('delete_any_team', models.BooleanField(default=False, verbose_name='Delete for any team')),
                ('edit_any_team', models.BooleanField(default=False, verbose_name='Edit for any team')),
                ('view_any_team', models.BooleanField(default=False, verbose_name='View for any team')),
                ('list_any_team', models.BooleanField(default=False, verbose_name='List for any team')),
                ('filters', models.CharField(blank=True, default=None, max_length=4000, null=True, verbose_name='Filters')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auprico_auth_objectpermission_created', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auprico_auth_objectpermission_edited', to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='object_permissions', to='auprico_auth.Role', verbose_name='Role')),
                ('versions', models.ManyToManyField(related_name='auprico_auth_objectpermission', to='auprico_auth.Version')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Affiliation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_ts', models.DateTimeField(default=django.utils.timezone.now)),
                ('edited_ts', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auprico_auth_affiliation_created', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auprico_auth_affiliation_edited', to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auprico_auth.Role')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='affiliations_for_team', to='auprico_auth.Team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='affiliations', to=settings.AUTH_USER_MODEL)),
                ('versions', models.ManyToManyField(related_name='auprico_auth_affiliation', to='auprico_auth.Version')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='user',
            name='versions',
            field=models.ManyToManyField(related_name='auprico_auth_user', to='auprico_auth.Version'),
        ),
    ]
from django.test import TestCase


# Create your tests here.
from auprico_auth.models import Role, Version, User, VersionChange


class ETLTest(TestCase):
    source_file_name = "/tmp/source.sqlite3"
    dest_file_name = "/tmp/dest.sqlite3"

    def setUp(self):
        self.user = User.objects.create(username="admin")

    def test_versions(self):
        role = Role.objects.create(name="Admin")
        role = Role.objects.get(name="Admin")
        self.assertEqual(Version.objects.count(), 0, "number of versions does not match")
        role.changed_by_user = self.user
        role.description = "Administration Role"
        role.save()
        self.assertEqual(role.created_by, self.user)
        self.assertEqual(role.edited_by, self.user)
        self.assertEqual(Version.objects.count(), 1, "number of versions does not match")
        version_change = VersionChange.objects.all().first()
        self.assertEqual(version_change.new_value, "Administration Role")
        self.assertEqual(version_change.old_value, "")




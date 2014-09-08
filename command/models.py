from django.db import models
from django.contrib.auth.models import User
from boxshell.settings import USER_FILE_ROOT

#USER_FILE_ROOT = os.path.join(os.path.dirname(__file__),'../../file_root/')
# Create your models h

# account model
class Account(models.Model):
    home_dir = models.CharField(max_length = 100)
    avatar = models.CharField(max_length = 100, blank=True)
    gender = models.CharField(max_length = 10, blank=True)
    location = models.CharField(max_length = 100, blank=True)
    country = models.CharField(max_length = 100, blank=True)
    city = models.CharField(max_length = 50, blank=True)
    website1 = models.URLField( blank=True)
    website2 = models.URLField( blank=True)
    company = models.CharField(max_length = 50, blank=True)
    occupation = models.CharField(max_length = 100, blank=True)
    introduction = models.TextField(blank=True)
    user = models.OneToOneField(User)

    def __unicode__(self):
        return "%s" % self.user.username

    def __getitem__(self,name):
        return getattr(self,name)

    def __setitem__(self,name,value):
        setattr(self,name,value)


class Project(models.Model):
    name = models.CharField(max_length = 100)
    created_datetime = models.DateTimeField(auto_now = True)
    modified_datetime = models.DateTimeField(blank = True)
    description = models.TextField(blank = True)
    user = models.ForeignKey(User)
    publicity = models.CharField(max_length = 50)

    def __unicode__(self):
        return "%s" % self.name

    def __getitem__(self,name):
        return getattr(self,name)

    def __setitem__(self,name,value):
        setattr(self,name,value)

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

    def __str__(self):
        return "%s" % self.user.username



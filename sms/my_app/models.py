from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Notes(models.Model):
    class Meta:
        verbose_name = 'notes'
        verbose_name_plural = 'notes'
    user = models.ForeignKey(User,on_delete = models.CASCADE)
    title = models.CharField(max_length = 100)
    description = models.TextField()

    def __str__(self):
        return self.title

class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Add additional attributes
    portfolio = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_pics',blank=True)


    def __str__(self):
        return self.user.username
    
class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    date = models.DateTimeField()
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return self.title    
    
class Homework(models.Model):
    user = models.ForeignKey(User,on_delete = models.CASCADE)
    subject = models.CharField(max_length=100)
    title = models.CharField(max_length = 100)
    description = models.TextField()
    due = models.DateTimeField()
    is_finished = models.BooleanField(default = False)

    def __str__(self):
        return self.title

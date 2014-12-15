from django.db import models

# Create your models here.
class ToDo(models.Model):
    item = models.TextField(default='')
    added_by = models.IntegerField()
    date_todo = models.DateField(auto_now=False)
    archive = models.IntegerField()
    
    def __unicode__(self):
        return self.item
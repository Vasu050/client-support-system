from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
# Create your models here.
User=get_user_model()
class Complaints(models.Model):
    id = models.AutoField(primary_key=True)  
    product = models.CharField(max_length=200, null=False,blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    client = models.ForeignKey(User, on_delete=models.CASCADE,null=False,related_name='client')
    assigned_worker=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='assigned_worker')
    choices=[
        ('Raised','Raised'),
        ('Assigned','Assigned'),
        ('Resolved','Resolved')
            ]

    status=models.CharField(max_length=200, null=False,blank=False,choices=choices,default='Raised')


    def __str__(self):
        return f"{self.id}"
    


    # worker.assigned_complaints.all() =  Complaint.objects.filter(assigned_worker=worker)
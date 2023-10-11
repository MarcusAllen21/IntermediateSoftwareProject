import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# database to track quiz data  
class Quiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    Num1 = models.CharField(max_length=100, default=None)
    Num2 = models.CharField(max_length=100, default=None)
    Num3 = models.CharField(max_length=100, default=None)
    Num4 = models.CharField(max_length=100, default=None)
    correct_answer = models.IntegerField(choices=[(1, 'Num 1'), (2, 'Num 2'), (3, 'Num 3'), (4, 'Num 4')], default=None)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
    
class Grade(models.Model):
    id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.quiz.title
    
# database for discussions and the replies for each
class Discussion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    parent_post = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.subject
    
    def delete(self):
        self.file.delete()
        super().delete()
    
class Reply(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.post.subject
    
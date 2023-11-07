from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, default="Math")
    # Other fields related to the quiz

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    # Other fields related to the option

    def __str__(self):
        return self.text

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE) 
    grade = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) 
    submission_attempts = models.PositiveIntegerField(default=0)  # Submission attempts

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"


class Discussion(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    file = models.FileField(upload_to='discussion_files/', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_post = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    # Other fields related to the discussion


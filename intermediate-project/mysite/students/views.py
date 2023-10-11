from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.urls import reverse
from teachers.models import Discussion, Reply, Quiz, Grade
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.db.models import OuterRef, Subquery

# Create your views here.
def index(request):

    student = request.user

    discussions = Discussion.objects.all()
    grades = Grade.objects.all()

    # Create a subquery to get graded quizzes for the current student
    graded_quizzes = Grade.objects.filter(student=student)

    # Query quizzes that don't have a corresponding grade for the current student
    ungraded_quizzes = Quiz.objects.annotate(
        has_grade=Subquery(graded_quizzes.values('quiz'))
    ).filter(has_grade=None)

    composite = 0
    for grade in grades:
        composite += grade.grade

    if composite != 0:
        composite = composite / int(len(grades))
    else:
        composite = 0

    context = {
        'discussions': discussions,
        'quizzes': ungraded_quizzes,
        'student_grades': grades,
        'final_grade': composite,
    }
    return render(request, "students/index.html", context)

def submit_quiz(request,id):

    quiz = Quiz.objects.get(pk = id)
    

    if request.method == 'POST':
        # Process form data to create a new quiz
        selected_answer = request.POST.get(f'{id}')  
        correct = 0

        selected_answer = int(selected_answer)

        if selected_answer == int(quiz.correct_answer) :
            correct += 1
        total = correct * 100

        Grade.objects.create(
            grade = total,
            quiz = quiz,
            student = request.user
        )
    return redirect('students:index')
    

def create_discussion(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        file = request.FILES.get('file')  # Get the uploaded file
        author = request.user

        parent_post_id = request.POST.get('parent_post')
        parent_post = None

        if parent_post_id:
            try:
                parent_post = Discussion.objects.get(pk=parent_post_id)
            except Discussion.DoesNotExist:
                pass  # Handle the case where the parent post does not exist

        discussion = Discussion.objects.create(
            subject=subject,
            message=message,
            file=file,
            author=author,
            parent_post=parent_post,
        )
        messages.success(request, 'Discussion created successfully.')
        return redirect('students:index')  # Redirect to the discussions page

    return redirect('students:index')

    
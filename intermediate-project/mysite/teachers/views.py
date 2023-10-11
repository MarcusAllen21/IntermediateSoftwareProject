from django.shortcuts import render
from django.shortcuts import render, redirect
from django.urls import reverse
from teachers.models import Quiz, Grade, Discussion
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Avg
from django.db.models import OuterRef, Subquery

# Create your views here.
def index(request):

    teacher = request.user

    discussions = Discussion.objects.all()
    grades = Grade.objects.all()

    # Create a subquery to get graded quizzes for the current student
    graded_quizzes = Grade.objects.filter(quiz=OuterRef('pk'))

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
    return render(request, "teachers/index.html", context)

def teacher_dashboard(request):
    # Retrieve quizzes created by the teacher
    quizzes = Quiz.objects.filter(author=request.user)

    # Retrieve average quiz scores for each quiz
    quiz_scores = {}
    for quiz in quizzes:
        quiz_scores[quiz.id] = Grade.objects.filter(quiz=quiz).aggregate(Avg('grade'))['grade__avg']

    context = {
        'quizzes': quizzes,
        'quiz_scores': quiz_scores,
    }
    return render(request, "teachers/index.html", context)

def view_quiz_results(request, quiz_id):
    # Retrieve the quiz
    quiz = Quiz.objects.get(pk=quiz_id)

    # Retrieve all the grades for this quiz
    grades = Grade.objects.filter(quiz=quiz)

    context = {
        'quiz': quiz,
        'grades': grades,
    }
    return render(request, "teachers/index.html", context)

def create_quiz(request):
    if request.method == 'POST':
        # Process form data to create a new quiz
        title = request.POST.get('title')
        answ1 = request.POST.get('answ1')
        answ2 = request.POST.get('answ2')
        answ3 = request.POST.get('answ3')
        answ4 = request.POST.get('answ4')
        correct = request.POST.get('CA')
        Quiz.objects.create(
            title=title,
            Num1=answ1,
            Num2=answ2,
            Num3=answ3,
            Num4=answ4,
            correct_answer=correct,
            author=request.user
        )
        messages.success(request, 'Quiz created successfully.')
        return redirect('teachers:index')

    return render(request, "teachers/index.html")

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

def logout_page(request):
    logout(request)
    return redirect(reverse('login'))

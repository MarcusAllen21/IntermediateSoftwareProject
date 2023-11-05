from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from teachers.models import Quiz, Grade, Discussion, Question, Option
from teachers.forms import QuestionForm, OptionForm, QuizForm, AnswerForm
from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.db.models import Avg

def index(request):
    context = {}
    return render(request, "students/index.html", context)

def create_discussion(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        file = request.FILES.get('file')
        author = request.user

        parent_post_id = request.POST.get('parent_post')
        parent_post = None

        if parent_post_id:
            try:
                parent_post = Discussion.objects.get(pk=parent_post_id)
            except Discussion.DoesNotExist:
                pass

        discussion = Discussion.objects.create(
            subject=subject,
            message=message,
            file=file,
            author=author,
            parent_post=parent_post,
        )
        messages.success(request, 'Discussion created successfully.')
        return redirect('students:index')

    return render(request, "students/create_discussion.html")

def discussions(request):
    discussions = Discussion.objects.all()
    context = {
        'discussions': discussions,
    }
    return render(request, "students/created_discussions.html", context)

def quizzes(request, quiz_id):
    try:
        quiz = get_object_or_404(Quiz, pk=quiz_id)
    except Quiz.DoesNotExist:
        messages.error(request, 'No quizzes are available.')
        return redirect('students:index')

    student = request.user
    form = None  # Initialize the 'form' variable

    if request.method == 'POST':
        # Check if the student has already exceeded max attempts for the entire quiz
        if student_has_exceeded_attempts(student, quiz):
            messages.error(request, 'You have exceeded the maximum number of attempts for this quiz.')
            return redirect('students:quizzes', quiz_id=quiz_id)

        question_id = request.POST.get('question_id')
        question = get_object_or_404(Question, pk=question_id)

        # Check if the student has already exceeded max attempts for the current question
        if student_has_exceeded_attempts_for_question(student, question):
            messages.error(request, 'You have exceeded the maximum number of attempts for this question.')
            return redirect('students:quizzes', quiz_id=quiz_id)

        form = AnswerForm(request.POST, question=question)  # Pass the 'question' to the form

        if form.is_valid():
            selected_option = form.cleaned_data['selected_option']

            # Check if the selected option is correct
            is_correct = question.is_correct(selected_option)

            # Create or get a Grade object for the student's attempt on the current question
            grade, created = Grade.objects.get_or_create(student=student, quiz=quiz, question=question)

            # Update the grade object
            grade.attempts += 1
            grade.score = grade.score if created else grade.score + is_correct  # Update score only if not a new attempt
            grade.save()

            # Check if the student has completed the quiz
            if student_has_completed_quiz(student, quiz):
                return redirect('students:quiz_results', quiz_id=quiz_id)

    questions = quiz.question_set.all()
    context = {
        'quiz': quiz,
        'questions': questions,
        'form': form,
    }
    return render(request, 'students/quizzes.html', context)




def grades(request):
    student = request.user
    student_grades = Grade.objects.filter(student=student)
    subjects = student_grades.values_list('quiz__subject', flat=True).distinct()

    grades_by_subject = []
    for subject in subjects:
        quizzes = Quiz.objects.filter(subject=subject)
        subject_grades = student_grades.filter(quiz__subject=subject)
        total_score = subject_grades.aggregate(Avg('grade'))['grade__avg']
        grades_by_subject.append({
            'subject': subject,
            'quizzes': quizzes,
            'average_score': total_score,
        })

    context = {
        'student_grades': student_grades,
        'grades_by_subject': grades_by_subject,
    }
    return render(request, "students/grades.html", context)

# Define these functions in your views.py or a separate utility module

def student_has_exceeded_attempts(student, quiz):
    # Check if the student has exceeded the maximum number of attempts for the entire quiz
    max_attempts = 3  # Adjust this as needed
    return Grade.objects.filter(student=student, quiz=quiz).count() >= max_attempts

def student_has_exceeded_attempts_for_question(student, question):
    # Check if the student has exceeded the maximum number of attempts for the current question
    max_attempts = 2  # Adjust this as needed
    return Grade.objects.filter(student=student, question=question).count() >= max_attempts

def student_has_completed_quiz(student, quiz):
    # Check if the student has completed the quiz (e.g., answered all questions)
    total_questions = quiz.question_set.count()
    return Grade.objects.filter(student=student, quiz=quiz).count() >= total_questions

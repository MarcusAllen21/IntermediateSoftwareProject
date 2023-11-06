from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from teachers.models import Quiz, Grade, Discussion, Question, Option
from teachers.forms import QuestionForm, OptionForm, QuizForm, AnswerForm
from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.db.models import Avg
from decimal import Decimal

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


def quizzes(request):
    # Retrieve all quizzes
    all_quizzes = Quiz.objects.all()

    # Create an empty dictionary to organize quizzes by subject
    quizzes_by_subject = {}

    # Iterate through all quizzes and group them by subject
    for quiz in all_quizzes:
        subject = quiz.subject
        if subject not in quizzes_by_subject:
            quizzes_by_subject[subject] = []
        quizzes_by_subject[subject].append(quiz)

    context = {
        'quizzes_by_subject': quizzes_by_subject
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
    print(total_questions)
    Grade.objects.filter(student=student, quiz=quiz).count()
    return Grade.objects.filter(student=student, quiz=quiz).count() >= total_questions


def get_question_somehow(quiz_id, question_id):
    # Retrieve the quiz
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Retrieve the question for the given quiz and question_id
    question = get_object_or_404(Question, quiz=quiz, id=question_id)

    return question

def student_grades(request):
    # Retrieve all grades for the current user (student)
    student_grades = Grade.objects.filter(student=request.user)

    context = {
        'student_grades': student_grades,
    }

    return render(request, 'students/grades.html', context)

import json

def take_quiz(request, quiz_id):
    # Retrieve the quiz
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Check if the student has exceeded the maximum number of attempts for the entire quiz
    if student_has_exceeded_attempts(request.user, quiz):
        messages.error(request, 'You have exceeded the maximum number of quiz attempts.')
        return redirect('students:quizzes')

    # Retrieve the questions for the quiz and create forms for each question
    question_forms = []
    for question in quiz.question_set.all():
        options = Option.objects.filter(question=question)
        question_form = {
            'question': question,
            'options': options,
        }
        question_forms.append(question_form)

    if request.method == 'POST':
        # Process the submitted quiz answers and update question-wise correctness
        total_score = 0
        submission_attempts = 0  # Initialize submission attempts
        question_responses = {}  # Initialize question-wise correctness

        for question in quiz.question_set.all():
            option_id = request.POST.get(f'question_{question.id}')
            if option_id:
                option = Option.objects.get(pk=option_id)
                is_correct = option.is_correct
                total_score += 1 if is_correct else 0
                submission_attempts += 1  # Increment submission attempts
                question_responses[str(question.id)] = is_correct  # Update question-wise correctness

        # Update the Grade entry with the question-wise correctness
        grade, created = Grade.objects.get_or_create(student=request.user, quiz=quiz, defaults={'submission_attempts': submission_attempts})
        if not created:
            grade.grade = None  # Reset the grade
            grade.submission_attempts = submission_attempts
        grade.question_responses = json.dumps(question_responses)  # Store question-wise correctness as JSON
        grade.save()

        # Check if the student has completed the quiz
        if student_has_completed_quiz(request.user, quiz):
            messages.success(request, 'Quiz submitted successfully. You have completed the quiz.')

            # Calculate the average score by subject
            subject = quiz.subject
            subject_grades = Grade.objects.filter(student=request.user, quiz__subject=subject)
            total_attempts = subject_grades.count()
            average_score = Decimal(total_score) / Decimal(total_attempts) * 100 if total_attempts > 0 else 0
            # Update the Grade entry for the subject with the calculated average score
            grade.grade = average_score
            grade.save()
        else:
            messages.success(request, 'Quiz submitted successfully. Continue to the next question.')

        return redirect('students:quizzes')

    context = {
        'quiz': quiz,
        'question_forms': question_forms,
    }

    return render(request, 'students/take_quiz.html', context)



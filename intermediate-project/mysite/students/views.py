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


def take_quiz(request, quiz_id):
    # Retrieve the quiz object
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Check if there are questions associated with this quiz
    questions = Question.objects.filter(quiz=quiz)

    if not questions:
        # Handle the case where there are no questions for the quiz
        return render(request, 'students/quizzes.html')

    # Check if the student has exceeded the maximum number of attempts
    if student_has_exceeded_attempts(request.user, quiz):
        return render(request, 'students/quizzes.html')

    if request.method == 'POST':
        # Check if the student has completed the quiz
        if student_has_completed_quiz(request.user, quiz):
            # Redirect back to the list of quizzes
            return redirect('students:quizzes')

        # Create an empty list to store the student's answers
        student_answers = []
        print(questions)
        # Process each question and answer
        for question in questions:
            print("test")
            options = Option.objects.filter(question=question)
            question_form = AnswerForm(request.POST, prefix=f'question_{question.id}')
            question_form.fields['selected_option'].queryset = options
            if question_form.is_valid():
                # Process the submitted answer
                option_id = question_form.cleaned_data.get('selected_option')
                option = get_object_or_404(Option, id=option_id)

                # Save the student's answer
                student_answers.append({
                    'question': question,
                    'selected_option': option,
                })

        # Calculate the grade for the quiz and store the results
        total_score = 0
        for answer in student_answers:
            if answer['selected_option'] and answer['selected_option'].is_correct:
                total_score += 1  # Adjust scoring logic as needed

        grade = Grade.objects.create(
            student=request.user,
            quiz=quiz,
            grade=total_score,  # Adjust grading logic as needed
        )
        print("test")
        # Increment the number of attempts
        increment_attempts(request.user, quiz)

        # Check if the student has exceeded the maximum number of attempts after this attempt
        if student_has_exceeded_attempts(request.user, quiz):
            return render(request, 'students/quiz_unavailable.html')

        # Redirect back to the list of quizzes
        return redirect('students:quizzes')

    else:
        # Display the quiz questions to the student
        question_forms = []

        for question in questions:
            options = Option.objects.filter(question=question)
            question_form = AnswerForm(prefix=f'question_{question.id}')
            question_form.fields['selected_option'].queryset = options
            question_forms.append({
                'question': question,
                'options': options,
                'form': question_form,
            })

        context = {
            'quiz': quiz,
            'question_forms': question_forms,
        }
        return render(request, 'students/take_quiz.html', context)

def increment_attempts(request, user, quiz):
    # Use F expressions to increment "submission attempts" in the database
    Grade.objects.update_or_create(student=user, quiz=quiz, defaults={'submission_attempts': F('submission_attempts') + 1})

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

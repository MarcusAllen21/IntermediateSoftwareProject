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
from django.views.decorators.csrf import csrf_protect

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
    # Retrieve the current user
    user = request.user

    # Retrieve all quizzes
    quizzes_all = Quiz.objects.all()

    # Organize quizzes by subject
    quizzes_by_subject = {}

    # Filter Grade objects for the specified user
    user_grades = Grade.objects.filter(student=user)

    # Create a set to keep track of attempted quiz IDs and their submission attempts
    attempted_quizzes = {}

    # Create a list to store quizzes that have been attempted by the user
    taken_quizzes = []

    for grade in user_grades:
        attempted_quizzes[grade.quiz.id] = grade.submission_attempts
        # Add quizzes with grades to the list of taken_quizzes
        taken_quizzes.append(grade.quiz)

    for quiz in quizzes_all:
        subject = quiz.subject
        if subject not in quizzes_by_subject:
            quizzes_by_subject[subject] = []

        # Check if the quiz has been attempted by the user
        if quiz.id in attempted_quizzes:
            submission_attempts = attempted_quizzes[quiz.id]

            # Check if submission attempts have reached 3
            if submission_attempts < 3:
                # If submission attempts are less than 3, add the quiz to quizzes_by_subject
                quizzes_by_subject[subject].append(quiz)
        else:
            # If the user hasn't attempted the quiz, add it to quizzes_by_subject
            quizzes_by_subject[subject].append(quiz)

    print(user_grades)

    context = {
        'quizzes_by_subject': quizzes_by_subject,
        'taken_quizzes': taken_quizzes,  # Add taken quizzes to the context
        'user_grades': user_grades,
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


def take_quiz(request, quiz_id):
    # Retrieve the quiz
    quiz = get_object_or_404(Quiz, id=quiz_id)
    num_questions = 0

    # Check if the student has exceeded the maximum number of attempts for the entire quiz
    if student_has_exceeded_attempts(request.user, quiz):
        messages.error(request, 'You have exceeded the maximum number of quiz attempts.')
        return redirect('students:quizzes')

    # Retrieve the questions for the quiz and create forms for each question
    question_forms = []
    for question in quiz.question_set.all():
        num_questions += 1
        options = Option.objects.filter(question=question)
        question_form = {
            'question': question,
            'options': options,
        }
        question_forms.append(question_form)

    if request.method == 'POST':
        # Process the submitted quiz answers and update question-wise correctness
        grade, created = Grade.objects.get_or_create(student=request.user, quiz=quiz)
        submission_attempts = grade.submission_attempts
        total_score = 0.00
        question_responses = {}  # Initialize question-wise correctness

        for question in quiz.question_set.all():
            option_id = request.POST.get(f'question_{question.id}')
            if option_id:
                option = Option.objects.get(pk=option_id)
                is_correct = option.is_correct
                total_score += 1 if is_correct else 0
                question_responses[str(question.id)] = is_correct  # Update question-wise correctness

        submission_attempts += 1  # Increment submission attempts

        # Update the Grade entry with the question-wise correctness
        grade, created = Grade.objects.get_or_create(student=request.user, quiz=quiz, defaults={'submission_attempts': submission_attempts, 'grade': total_score})
        if not created:
            average_score = Decimal(total_score) * 100
            grade.grade = average_score / num_questions
            grade.submission_attempts = submission_attempts
        grade.question_responses = json.dumps(question_responses)  # Store question-wise correctness as JSON
        print(grade)
        grade.save()

        # Check if the student has completed the quiz
        if student_has_completed_quiz(request.user, quiz):
            messages.success(request, 'Quiz submitted successfully. You have completed the quiz.')
            average_score = Decimal(total_score) * 100
            # Update the Grade entry for the subject with the calculated average score
            grade.grade = average_score / num_questions
            print(grade)
            grade.save()
        else:
            messages.success(request, 'Quiz submitted successfully. Continue to the next question.')

        return redirect('students:quizzes')

    context = {
        'quiz': quiz,
        'question_forms': question_forms,
    }

    return render(request, 'students/take_quiz.html', context)


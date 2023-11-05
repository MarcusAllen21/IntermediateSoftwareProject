from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Quiz, Grade, Discussion, Question, Option
from .forms import QuestionForm, OptionForm, QuizForm
from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.forms import formset_factory
from django.forms.formsets import formset_factory, BaseFormSet

def index(request):
    quizzes = Quiz.objects.all()
    grades = Grade.objects.all()

    composite = 0
    for grade in grades:
        composite += grade.grade

    if composite != 0:
        composite = composite / len(grades)
    else:
        composite = 0

    context = {
        'quizzes': quizzes,
        'student_grades': grades,
        'final_grade': composite,
    }
    return render(request, "teachers/index.html", context)

def view_quiz_results(request, quiz_id):
    quiz = Quiz.objects.get(pk=quiz_id)
    grades = Grade.objects.filter(quiz=quiz)
    context = {
        'quiz': quiz,
        'grades': grades,
    }
    return render(request, "teachers/view_quiz_results.html", context)

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
        return redirect('teachers:index')

    return render(request, "teachers/create_discussion.html")

def created_quizzes(request):
    quizzes = Quiz.objects.all()

    quiz_data = []
    for quiz in quizzes:
        questions = Question.objects.filter(quiz=quiz)
        grades = Grade.objects.filter(quiz=quiz)
        total_score = sum(grade.grade for grade in grades)
        average_score = total_score / len(grades) if len(grades) > 0 else 0

        quiz_data.append({
            'quiz': quiz,
            'questions': questions,
            'average_score': average_score,
        })

    context = {
        'quiz_data': quiz_data,
    }

    return render(request, "teachers/created_quizzes.html", context)

def created_discussions(request):
    discussions = Discussion.objects.filter(author=request.user)
    context = {
        'discussions': discussions,
    }
    return render(request, "teachers/created_discussions.html", context)

def create_quiz(request):
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        num_questions = int(request.POST.get('num_questions'))
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.author = request.user
            quiz.save()
            for i in range(num_questions):
                question_form = QuestionForm(request.POST, prefix=f'question_{i}')
                if question_form.is_valid():
                    question = question_form.save(commit=False)
                    question.quiz = quiz
                    question.save()
                    option_valid = True
                    for j in range(4):  # Assuming you have 4 options for each question
                        option_form = OptionForm(request.POST, id='option_{i}_{j}_text')
                        if not option_form.is_valid():
                            option_valid = False
                            print(f"Failed to create option {j} for question {i} with error: {option_form.errors}")
                            messages.error(request, f'Failed to create options for question {i}. Please check your input.')
                            break
                        option = option_form.save(commit=False)
                        option.question = question
                        option.save()
                    if not option_valid:
                        break
                    correct_option_index = request.POST.get(f'correct_option_{i}')
                    question.correct_option = question.options.all()[int(correct_option_index)]
                    question.save()
                else:
                    print(f"Failed to create question {i} with error: {question_form.errors}")
                    messages.error(request, f'Failed to create questions. Please check your input.')
                    break
            messages.success(request, 'Quiz and questions created successfully.')
            return JsonResponse({'success': True})
        else:
            print(f"Failed to create quiz with error: {quiz_form.errors}")
            messages.error(request, 'Failed to create the quiz. Please check your input.')
    else:
        quiz_form = QuizForm()
        context = {
            'quiz_form': quiz_form,
        }
        return render(request, "teachers/create_quiz.html", context)

    return render(request, "teachers/create_quiz.html")

def manage_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    questions = Question.objects.filter(quiz=quiz)
    context = {
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, "teachers/manage_questions.html", context)

def search_quizzes(request):
    query = request.GET.get('q')
    quizzes = Quiz.objects.filter(title__icontains=query)
    return render(request, 'teachers/search_quizzes.html', {'quizzes': quizzes, 'query': query})

def search_discussions(request):
    query = request.GET.get('q')
    discussions = Discussion.objects.filter(subject__icontains=query)
    return render(request, 'teachers/search_discussions.html', {'discussions': discussions, 'query': query})

def paginated_quizzes(request):
    quizzes = Quiz.objects.all()
    paginator = Paginator(quizzes, 10)
    page = request.GET.get('page')
    try:
        quizzes = paginator.page(page)
    except PageNotAnInteger:
        quizzes = paginator.page(1)
    except EmptyPage:
        quizzes = paginator.page(paginator.num_pages)
    return render(request, 'teachers/paginated_quizzes.html', {'quizzes': quizzes})

def view_quiz_chart(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    grades = Grade.objects.filter(quiz=quiz)

    student_names = [grade.student.username for grade in grades]
    student_grades = [grade.grade for grade in grades]

    chart_data = {
        'labels': student_names,
        'data': student_grades,
    }

    return render(request, "teachers/view_quiz_chart.html", {'quiz': quiz, 'chart_data': json.dumps(chart_data)})

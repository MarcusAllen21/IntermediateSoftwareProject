from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Quiz, Grade, Discussion, Question, Option
from .forms import QuestionForm, OptionForm, QuizForm,SubjectSelectionForm
import json
from django.views.decorators.csrf import csrf_protect
from decimal import Decimal

def index(request):
    quizzes = Quiz.objects.all()
    grades = Grade.objects.all()

    composite = Decimal('0.0')  # Initialize composite to a Decimal value

    # Assuming you have a list of Grade objects in grades_list
    for grade in grades:
        if grade.grade is not None:
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
        total_score = sum(grade.grade for grade in grades if grade.grade is not None)

        average_score = total_score / len(grades) if len(grades) > 0 else 0

        quiz_data.append({
            'quiz': quiz,
            'questions': questions,
            'total_score': total_score,
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

# views.py
def create_quiz(request):
    if request.method == 'POST':
        subject_form = SubjectSelectionForm(request.POST)
        quiz_form = QuizForm(request.POST)

        if subject_form.is_valid() and quiz_form.is_valid():
            # Create the quiz object with the selected subject
            quiz = quiz_form.save(commit=False)
            quiz.author = request.user
            quiz.subject = subject_form.cleaned_data['subject']  # Assign the selected subject

            quiz.save()

            question_ids = set()

            for param in request.POST:
                if param.startswith("questions_"):
                    question_id = param.split('_')[1]
                    if question_id not in question_ids:
                        question_ids.add(question_id)
                        question_text = request.POST.get(f'questions_{question_id}_text')

                        if question_text:
                            # Create the question for the quiz
                            question = Question(quiz=quiz, text=question_text)
                            question.save()

                            option_valid = True

                            for j in range(4):  # Assuming you have 4 options for each question
                                option_text = request.POST.get(f'options_{question_id}_{j}_text')
                                is_correct = request.POST.get(f'correct_options_{question_id}') == str(j)

                                if option_text:
                                    # Create the option for the question
                                    option = Option(question=question, text=option_text, is_correct=is_correct)
                                    option.save()
                                else:
                                    option_valid = False
                                    break

                            if not option_valid:
                                messages.error(request, f'Failed to create options for question {question_id}. Please check your input.')
                                quiz.delete()  # Rollback quiz creation if options are not valid
                                return redirect('teachers:create_quiz')  # Redirect to the form again with an error message

            messages.success(request, 'Quiz and questions created successfully.')
            return redirect('teachers:created_quizzes')  # Redirect to the page where you show created quizzes

    else:
        quiz_form = QuizForm()
        subject_form = SubjectSelectionForm()

    context = {
        'quiz_form': quiz_form,
        'subject_form': subject_form,
    }
    return render(request, "teachers/create_quiz.html", context)



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

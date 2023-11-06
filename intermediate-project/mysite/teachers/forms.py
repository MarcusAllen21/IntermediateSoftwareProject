# teachers/forms.py
from django import forms
from .models import Question, Option, Quiz

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['quiz', 'text'] 

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']  

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title']


class AnswerForm(forms.ModelForm):
    selected_option = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect,
        empty_label=None,
    )

    class Meta:
        model = Option
        fields = []

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)
        super(AnswerForm, self).__init__(*args, **kwargs)
        if question:
            self.fields['selected_option'].queryset = Option.objects.filter(question=question)

    def clean(self):
        cleaned_data = super().clean()
        selected_option = cleaned_data.get('selected_option')  # Use get() to avoid KeyError
        if selected_option:
            question = selected_option.question  # Retrieve the question associated with the selected option
            student = self.instance.quiz.author  # Assuming the author is the student

class SubjectSelectionForm(forms.Form):
    SUBJECT_CHOICES = [
        ('Math', 'Math'),
        ('Science', 'Science'),
        ('English', 'English'),
        ('History', 'History'),
    ]
    
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES)

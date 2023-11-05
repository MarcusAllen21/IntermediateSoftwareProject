# teachers/forms.py
from django import forms
from .models import Question, Option, Quiz

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['quiz', 'text', 'subject'] 

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
        model = Question
        fields = []

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)  # Retrieve the question from the keyword arguments
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.fields['selected_option'].queryset = question.options.all()

    def clean(self):
        cleaned_data = super().clean()
        selected_option = cleaned_data['selected_option']
        question = selected_option.question  # Retrieve the question associated with the selected option
        student = self.instance.quiz.author  # Assuming the author is the student

        if not question.has_max_attempts(student):
            raise forms.ValidationError("You have exceeded the maximum number of attempts for this question.")

        return cleaned_data



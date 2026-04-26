from django import forms
from django.db.models import Q

from core.models import Classroom, Subject, User


CONTROL_CLASSES = 'w-full rounded-2xl border border-default bg-white px-4 py-3 outline-none focus:border-brand'
CHECKBOX_CLASSES = 'h-4 w-4 rounded border-default text-brand focus:ring-brand'


# ClassroomForm
class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': CONTROL_CLASSES,
                'placeholder': 'Например: 3А',
            }),
        }


class ClassroomCreateForm(ClassroomForm):
    pass


class ClassroomUpdateForm(ClassroomForm):
    pass


# ClassroomSubjectAssignForm
class ClassroomSubjectAssignForm(forms.Form):
    classroom = forms.ModelChoiceField(
        queryset=Classroom.objects.none(),
        widget=forms.Select(attrs={'class': CONTROL_CLASSES}),
        label='Класс',
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': CONTROL_CLASSES}),
        label='Предмет',
    )

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['classroom'].queryset = Classroom.objects.filter(teacher=teacher)


# ClassroomStudentsAttachForm
class ClassroomStudentsAttachForm(forms.Form):
    classroom = forms.ModelChoiceField(
        queryset=Classroom.objects.none(),
        widget=forms.Select(attrs={
            'class': CONTROL_CLASSES,
        }),
    )

    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, teacher=None, search_query='', **kwargs):
        super().__init__(*args, **kwargs)

        if teacher:
            self.fields['classroom'].queryset = Classroom.objects.filter(
                teacher=teacher
            ).order_by('name')

        learners = User.objects.filter(role=User.Role.LEARNER).order_by(
            'first_name',
            'last_name',
            'email',
        )

        if search_query:
            learners = learners.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(username__icontains=search_query)
            )

        self.fields['students'].queryset = learners
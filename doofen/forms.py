from django import forms


class Student(forms.Form):
    grade = forms.CharField(label='届别',max_length=4,min_length=4)
    classnum = forms.CharField(label='班级',min_length=1,max_length=2)
    name = forms.CharField(label='姓名',max_length=8)
    passwd = forms.CharField(label='密码',widget=forms.PasswordInput,required=False,max_length=20)

    def clean(self):
        cleaned_data = super().clean()
        grade = cleaned_data.get('grade')
        classnum = cleaned_data.get('classnum')

        if grade and classnum:
            if not all([grade.isdigit(),classnum.isdigit()]):
                raise forms.ValidationError('班级与届别只含数字')
        return cleaned_data


class Register(forms.Form):
    passwd = forms.CharField(label='设置密码',widget=forms.PasswordInput,min_length=5,max_length=19)
    passwd_ = forms.CharField(label='确认密码',widget=forms.PasswordInput)
    email = forms.EmailField(error_messages={'invalid':'邮箱格式不正确'})

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('passwd')
        pwd_ = cleaned_data.get('passwd_')

        if pwd and pwd_:
            if pwd != pwd_:
                raise forms.ValidationError('两次输入密码不同')
        return cleaned_data


class ResetForm(forms.Form):
    grade = forms.CharField(label='届别',max_length=4,min_length=4)
    classnum = forms.CharField(label='班级',min_length=1,max_length=2)
    name = forms.CharField(label='姓名',max_length=8)
    email = forms.EmailField(label='邮箱',error_messages={'invalid':'邮箱格式错误'})

    def clean(self):
        cleaned_data = super().clean()
        grade = cleaned_data.get('grade')
        classnum = cleaned_data.get('classnum')

        if grade and classnum:
            if not all([grade.isdigit(),classnum.isdigit()]):
                raise forms.ValidationError('班级与届别只含数字')
        return cleaned_data



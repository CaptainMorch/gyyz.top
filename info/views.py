from django.shortcuts import render,get_object_or_404,redirect
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound

from .models import Item,University,DiscussGroup,AdmissionData
from .forms import UniversityForm,GroupForm

# Create your views here.
def home(request):
    return render(request,'info/home.html')

def item_home(request):
    paginator = Paginator(Item.objects.all(),10)
    page = request.GET.get('p',1)
    contact = paginator.get_page(page)
    return render(request,'items.html',{'contact':contact})

def university_home(request):
    paginator = Paginator(University.objects.all(),10)
    page = request.GET.get('p',1)
    contact = paginator.get_page(page)
    return render(request,'universities.html',{'contact':contact})

def university(request,university_id):
    return render(
            request,
            'university.html',
            {'university':get_object_or_404(University,pk=university_id)},
            )

def add_university(request):
    if request.method == 'POST':
        form = UniversityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('info:university_home')
        else:
            return render(request,'change_university.html',{'form':form})
    else:
        return render(request,'change_university.html',{'form':UniversityForm()})

def edit_university(request,university_id):
    _university = get_objects_or_404(University,pk=university_id)
    if request.method == 'POST':
        form = UniversityForm(request.POST,instance=_university)
        if form.is_valid():
            form.save()
            return redirect('info:university',university_id=university_id)
        else:
            return render(request,'change_university.html',{'form':form})
    else:
        form = UniversityForm(_university)
        return render(request,'change_university.html',{'form':form})

def group(request,university_id,group_id):
    _group = get_objects_or_404(
            DiscussGroup,
            university__pk=university_id,
            pk=group_id
            )
    return render(request,'group.html',{'group':_group})

def add_group(request,university_id):
    _university = get_object_or_404(University,pk=university_id)
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.university = _university
            group.save()
            return redirect('info:university',university_id=university_id)
        else:
            return render(request,'add_group.html',{'form':form})
    else:
        form = GroupForm()
        return render(request,'add_group.html',{'form':form})

def add_admission(request,university_id):
    _university = get_object_or_404(University,pk=university_id)
    if request.method == 'POST':
        form = AdmissionForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.university = _university
            data.save()
            return redirect('info:university',university_id=university_id)
        else:
            return render(request,'add_admission.html',{'form':form})
    else:
        form = AdmissionForm()
        return render(request,'add_admission.html',{'form':form})

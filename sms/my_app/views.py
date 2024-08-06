from django.shortcuts import render, redirect
from my_app.models import *
from my_app.forms import *
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from youtubesearchpython import VideosSearch
from django.contrib.auth.models import User
from django.shortcuts import render
import requests
import wikipedia


# Create your views here.
def home(request):
    return render(request,'my_app/home.html')


@login_required
def notes(request):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            user = request.user
            title = request.POST['title']
            description = request.POST['description']

            notes = Notes(user=user, title=title, description=description)
            notes.save()
            messages.success(request, f'Notes added by {user} successfully')
            form = NotesForm()
            
    else:
        form = NotesForm()
    notes = Notes.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(notes, 4)
    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        notes = paginator.page(1)
    except EmptyPage:
        notes = paginator.page(paginator.num_pages)
    dic = { 'notes':notes, 'form':form }
    return render(request,'my_app/notes.html',context=dic)

def delete_note(request, pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect('my_app:notes')


@login_required
def notes_detail(request):
    notes = Notes.objects.filter(user=request.user)
    return render(request, 'my_app/notes_detail.html', {'notes':notes})



def register(request):
    if request.method == "GET":
        return render(request, "my_app/register.html")
    else:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        re_password = request.POST.get('confirm_password')
        error_msg = None
        if password != re_password:
            error_msg = "Hey! Your Password Not Matched"
        elif User.objects.filter(username=username).first():
            error_msg = "This Username Has Been Already Registered"
        elif len(password) < 8:
            error_msg = "Password must Be 8 character"

        if not error_msg:
            user_object = User.objects.create(username=username, email=email)
            user_object.set_password(password)
            user_object.save()
            messages.success(request,f"Account created for {username} !!")
            return redirect('my_app:home')
        else:
            data = {
                "error": error_msg,
            }
            return render(request, 'my_app/register.html', data)
        

def forget_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        try:
            user_object = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            user_object = None
        error_msg = ""
        if user_object is None:
            error_msg = "User not found. Please try again."
            return render(request, 'forgetPassword.html', {'error': error_msg})
        else:
            reset_password_url = reverse('resetPassword') + f'?user_id={user_object.id}'
            return redirect(reset_password_url)
    else:
        return render(request, 'my_app/forgetPassword.html')
    
def reset_password(request):
    if request.method == 'POST':
        user_id = request.GET.get('user_id')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = None
        error_msg = ""
        if new_password != confirm_password:
            error_msg = 'New password and confirm password do not match.'
        else:
            user_obj = authenticate(request, username=user.username, password=old_password)
            if user_obj is not None:
                # set the new password and log the user in
                user_obj.set_password(new_password)
                user_obj.save()
                return redirect('my_app:login')
            else:
                error_msg = "Invalid old password."
        return render(request, 'resetPassword.html', {'error': error_msg})
    else:
        return render(request, 'my_app/resetPassword.html')


#def user_login(request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            

            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('my_app:home'))
                else:
                    return HttpResponse('Kindly Sign Up!!')
            
            else:
                print('Someone tried to login but failed!!')
                print(f'username:{username} and password : {password}')
                return HttpResponse('invalid login details')
            
        else:
            return render(request, 'my_app/login.html')

def user_login(request):
    if request.method == "GET":
        return render(request, 'my_app/login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user_object = User.objects.filter(username=username).first()
        error_msg = ""
        if user_object is None:
            error_msg = "User not found. Please try again"
        else:
            user = authenticate(username=username, password=password)
            if user is None:
                error_msg = "Wrong password."
            else:
                login(request, user)
                return redirect('my_app:home')
    return render(request, 'my_app/login.html', {'error': error_msg})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('my_app:user_login'))


@login_required
def profile(request):
    homeworks=Homework.objects.filter(is_finished=False,user=request.user)
    todos=Todo.objects.filter(is_finished=False,user=request.user)
    print(request.user.username)
    if len(homeworks)==0:
        homework_done=True
    else:
        homework_done=False
    if len(todos)==0:
        todos_done=True
    else:
        todos_done=False
    context={
        'homeworks':homeworks,
        'todos':todos,
        'homework_done':homework_done,
        'todos_done':todos_done,
        'user_detail':request.user
    }
    return render(request, "my_app/profile.html", context)




@login_required
def homework(request):
    if request.method == "POST":
        subject = request.POST.get('subject')
        title = request.POST.get('title')
        description = request.POST.get('description')
        due = request.POST.get('due')
        finished = request.POST['is_finished']
        # print(subject, title, description, due, finished)
        if finished == "yes":
            finished = True
        else:
            finished = False
        
        try:
            # create a user object
            homework_object = Homework.objects.create(user=request.user, subject=subject, title=title, description=description, date=due, is_finished=finished)
            homework_object.save()
            return redirect('my_app:homework')
        except Exception as e:
            print(e)
    homeworks = Homework.objects.filter(user=request.user)
    if len(homeworks)==0:
        homework_done= True
    else:
        homework_done=False
    return render(request, 'my_app/homework.html', {'homeworks':homeworks, 'homework_done':homework_done})

    


@login_required
def update_homework(request, pk=None):
    homework=Homework.objects.get(id=pk)
    if homework.is_finished==True:
        homework.is_finished=False
    else:
        homework.is_finished=True
    homework.save()
    return render(request, 'my_app/homework.html')


@login_required
def delete_homework(request, pk=None):
    Homework.objects.get(id=pk).delete()     
    return redirect('my_app:homework', request=request)

@login_required
def youtube(request):
    if request.method == 'POST':
        form = MyappForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text, limit = 10)
        result_list = []
        for i in video.result()['result']:

            result_dict ={ 'input':text,
                           'title':i['title'],
                            'duration':i['duration'], 
                            'thumbnail':i['thumbnails'][0]['url'], 
                            'channel':i['channel']['name'], 
                            'link':i['link'], 
                            'views':i['viewCount']['short'], 
                            'published':i['publishedTime'],
                          }
            description = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    description += j['text']
            result_dict['description'] = description
            result_list.append(result_dict)
            context={
                'form':form,
                'results':result_list
            }
        return render(request, 'my_app/youtube.html',context)    
    else:
        form = MyappForm()
    context = {'form':form}
    return render(request, 'my_app/youtube.html',context)


@login_required
def todo(request):
    if request.method == "POST":
        title = request.POST.get('title')
        due = request.POST.get('due')
        finished = request.POST['is_finished']
        # print(title, due, finished)
        if finished == "yes":
            finished = True
        else:
            finished = False
        try:
            # create a user object
            todo_object = Todo.objects.create(user=request.user, title=title, date=due, is_finished=finished)
            todo_object.save()
            return redirect('my_app:todo')
        except Exception as e:
            print(e)

    todos = Todo.objects.filter(user=request.user)
    if len(todos)==0:
        todo_done = True
    else:
        todo_done = False
    return render(request, 'my_app/todo.html', {"todos": todos, "todo_done": todo_done})

@login_required
def update_todo(request, pk=None):
    todo=Todo.objects.get(id=pk)
    if todo.is_finished==True:
        todo.is_finished=False
    else:
        todo.is_finished=True
    todo.save()
    return redirect('my_app:todo')

@login_required
def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect('my_app:todo')

@login_required
def books(request):
    if request.method=="POST":
        form=MyappForm(request.POST)
        text=request.POST['text']
        url="https://www.googleapis.com/books/v1/volumes?q="+text
        r=requests.get(url)
        answer=r.json()
        result_list=[]
        for i in range(10):
            result_dict={
                'title':answer['items'][i]['volumeInfo']['title'],
                 'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                 'description':answer['items'][i]['volumeInfo'].get('description'),
                 'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                 'categories':answer['items'][i]['volumeInfo'].get('categories'),
                 'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                 'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                 'preview':answer['items'][i]['volumeInfo'].get('previewLink')
            }
            result_list.append(result_dict)
            context={
                'form':form,
                'results':result_list
            }
        return render(request,'my_app/books.html',context)
    else:
        form=MyappForm()
    form=MyappForm()
    context={'form':form}
    return render(request,'my_app/books.html', context)

@login_required
def dictionary(request):
    if request.method=="POST":
        form=MyappForm(request.POST)
        text=request.POST['text']
        url="https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r=requests.get(url)
        answer=r.json()
        try:
           phonetics=answer[0]['phonetics'][0]['text']
           audio=answer[0]['phonetics'][0]['audio']
           definition=answer[0]['meanings'][0]['definitions'][0]['definition']
           example = answer[0]['meanings'][0]['definitions'][0]['example']
           synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
           context = {
                'form':form,
                'input':text,
                'phonetics':phonetics,
                'audio':audio,
                'definition':definition,
                'example':example,
                'synonyms':synonyms
            }
        except:
            context = {
                'form':form,
                'input':"",
            } 
         
        return render(request,"my_app/dictionary.html",context)
    
          
    else:
        form = MyappForm()
        context={'form':form}
    return render(request,"my_app/dictionary.html",context)

def wiki(request):
    if request.method == 'POST':
        text = request.POST['text']
        form = MyappForm(request.POST)
        search = wikipedia.page(text)
        context = {
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
        }
        return render(request,"my_app/wiki.html",context)
    else:
       
       form = MyappForm()
       context = {
            'form':form
       }

    return render(request,"my_app/wiki.html",context)

    
def conversion(request):
    if request.method == "POST":
        form =ConversionForm(request.POST)
        if request.POST['measurement'] =='length':
            measurement_form = ConversionLengthForm()
            context = {
                'form':form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >=0:
                    if first == 'yard' and second == 'foot':
                        answer = f'{input} yard = {int(input)*3} foot'
                    if first == 'foot' and second == 'yard':
                        answer = f'{input} foot = {int(input)/3} yard'
                context = {
                    'form':form,
                    'm_form':measurement_form,
                    'input': True,
                    'answer': answer
                } 
        if request.POST['measurement'] =='mass':
            measurement_form = ConversionMassForm()
            context = {
                'form':form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >=0:
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input} pound = {int(input)*0.453592} kilogram'
                    if first == 'kilogram' and second == 'pound':
                        answer = f'{input} kilogram = {int(input)*2.20462} pound'
                context = {
                    'form':form,
                    'm_form':measurement_form,
                    'input': True,
                    'answer': answer
                }         

               
    else:    
        form = ConversionForm()
        context = {
        'form':form,
        'input':False
        }
    return render(request,"my_app/conversion.html",context)


from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import AccountForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .models import Account
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.
def register(request):

    form = UserCreationForm()
    account_form = AccountForm()

    # get details
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        account_form = AccountForm(request.POST)


        # check validity of account
        try:
            user = form.save()
            account = account_form.save(commit = False)
            account.user = user

            # save object into table
            account.save()
        except Exception as e:
            print(e)

    # pass form into context
    context = {
        "form": form,
        "account_form": account_form,

    }

    return render(request, "users/registration.html", context)

def login_page(request):


    # get details
    if request.method == "POST":

        # get the input specifics
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        try:
            user = User.objects.get(username = username)
            account = Account.objects.get(user = user)

            auth = authenticate(request, username = username, password = password)

            if auth is not None:

                login(request, user)

                is_teacher = account.is_teacher
            
                if is_teacher:
                    return redirect("teachers:index")
                else:
                    return redirect("students:index")
            
        except Exception as e:
            messages.error(request, "The username does Not Exist")



    # pass form into context
    context = {}

    return render(request, "users/login.html", context)

def logout_page(request):
    logout(request)
    return redirect('users:login_page') 
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

            return redirect("users:login_page")

        except Exception as e:
            messages.error(request, "The username does Not Exist")

    # pass form into context
    context = {
        "form": form,
        "account_form": account_form,
    }
    
    return render(request, "users/registration.html", context)

# Login view with modifications
def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
            auth = authenticate(request, username=username, password=password)

            if auth is not None:
                login(request, user)
                try:
                    account = Account.objects.get(user=user)
                    is_teacher = account.is_teacher
                except Account.DoesNotExist:
                    # Handle the case where an Account doesn't exist
                    is_teacher = False  # Set a default value for is_teacher

                if is_teacher:
                    return redirect("teachers:index")
                else:
                    return redirect("students:index")
            else:
                messages.error(request, "Invalid credentials")

        except User.DoesNotExist:
            messages.error(request, "The username does not exist")

    context = {}
    return render(request, "users/login.html", context)


def logout_page(request):
    logout(request)
    return redirect('users:login_page') 
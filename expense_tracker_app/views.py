from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm
from .models import Expense
from .forms import ExpenseForm
from .forms import ExpenseFilterForm
from django.db.models import Sum
from django.db.models.functions import TruncMonth



# HOME
def home(request):
    return render(request, 'home.html')


# REGISTER
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)  
            return redirect('dashboard')  
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


# LOGIN
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})


# LOGOUT
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# FORGOT PASSWORD
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)

            return redirect('reset_password', email=user.email)

        except User.DoesNotExist:
            messages.error(request, "No account found with that email address.")

    return render(request, "forgot_password.html")


# RESET PASSWORD
def reset_password(request, email):
    if request.method == 'POST':
        new_password = request.POST.get('password')    
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('reset_password', email=email)

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            user = authenticate(username=user.username, password=new_password)
            if user:
                login(request, user)

            return redirect('dashboard')

        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, 'reset_password.html', {'email': email})


def logging_in(request):
    return render(request, 'logging_in.html')
#    ______________________________________________________________________________________________________________________________


def dashboard(request):
    return render(request, 'dashboard.html')


def filter_expense(request):
    return render(request, 'dashboard/filter_expense.html')

def expense_chart(request):
    return render(request, 'dashboard/expense_chart.html')



# EDIT EXPENSE
@login_required
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully.")
            return redirect('view_expense')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'dashboard/edit_expense.html', {'form': form})


# DELETE EXPENSE
@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, "Expense deleted successfully.")
        return redirect('view_expense')

    return render(request, 'dashboard/confirm_delete.html', {'expense': expense})


# ADD EXPENSE
@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('view_expense')
    else:
        form = ExpenseForm()

    return render(request, 'dashboard/add_expense.html', {'form': form})


# VIEW EXPENSE
@login_required
def view_expense(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    
    total_expense = sum(exp.amount for exp in expenses)
    
    return render(request, 'dashboard/view_expense.html', {
        'expenses': expenses,
        'total_expense': total_expense,
    })

# FILTER EXPENSE
@login_required
def filter_expense(request):
    form = ExpenseFilterForm(request.GET or None)
    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    if form.is_valid():
        category = form.cleaned_data.get('category')
        if category:
            expenses = expenses.filter(category=category)

    return render(request, 'dashboard/filter_expense.html', {
        'form': form,
        'expenses': expenses
    })


# MONTHLY EXPENSE
def monthly_expense(request):
    monthly_data = (
        Expense.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('-month')
    )

    return render(request, 'dashboard/monthly_expense.html', {
        'monthly_data': monthly_data
    })

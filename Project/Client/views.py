from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import auth
#from django.db.models import Count
from django.contrib import messages
from django.contrib.auth import authenticate,login,get_user_model
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import re
from google import genai
import google.generativeai as genai
from django.db import connection
# Create your views here.uu

User=get_user_model()

def register(request,role='client'):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        role = request.session.get('registration_role', 'client')
        manager = None
        if role == 'worker':
            manager = request.user
            '''User.objects.filter(role='manager') \
                .annotate(worker_count=Count('workers')) \
                .order_by('worker_count') \
                .first()'''
        
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            role=role,
            date_joined=timezone.now(),
            manager=manager
        )
        user.save()
        request.session.pop('registration_role', None)
        messages.success(request, "Account created successfully!")
        if request.user.is_authenticated and request.user.role == 'manager':
            return redirect('manager')
        return redirect('user_login')
    else:
        request.session['registration_role'] = role
        return render(request, 'register.html')
    
def user_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'client':
            return redirect('/complaints')
        elif request.user.role == 'manager':
            return redirect('/manager')
        elif request.user.role == 'worker':
            return redirect('/complaints/worker')
        else:
            return redirect('/admin')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            user_obj = None

        if user_obj is not None:
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                if user.role == 'client':
                    return redirect('/complaints')
                elif user.role == 'manager':
                    return redirect('/manager')
                elif user.role == 'worker':
                    return redirect('/complaints/worker')
                else:
                    return redirect('/admin')
            else:
                messages.info(request, 'Invalid Credentials')
                return redirect('/login')
        else:
            messages.info(request, 'User does not exist')
            return redirect('/')
    else:
        return render(request, 'login.html')

    
'''def profile(request):
    user=request.user
    if request.method=='POST':
        user.first_name=request.POST.get('first_name')
        user.last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        if User.objects.filter(email=email).exclude(email=user.email).exists():
            messages.error("email already exists")
            return redirect ('profile')
        else:
            user.email=email
            user.save()
            messages.success(request,"Profile Updated Successfully")
            return redirect('profile')
    else:
        return render(request,'profile.html',{'user':user})'''
    
def manager(request):
    if request.user.is_authenticated and request.user.role=='manager':
        workers = User.objects.filter(role='worker', manager=request.user)
        return render(request,'manager_dashboard.html',{'workers':workers})
    else:
        messages.info(request,"you are not authorised to access this")
        return redirect('/login')


def add_worker(request):
   if request.user.is_authenticated and request.user.role=='manager':
    return register(request,role="worker")
   else:
       messages.info('you are not authorised to access this')
       return redirect('/login')

def delete_worker(request,id):
    worker=get_object_or_404(User,id=id)
    if not request.user.is_authenticated or request.user.role != 'manager' or worker.manager != request.user : 
        messages.error(request, 'Authentication Required')
        return redirect('/login')
    try:
        worker.delete()
    except Exception as e:
            return f'There was a problem deleting that worker: {str(e)}'
    return redirect('manager') 
   
def update_user(request,id):
    user=get_object_or_404(User,id=id)
    if request.user != user:
        if request.user.role != 'manager' or user.role != 'worker' or user.manager != request.user:
            messages.error(request, "Unauthorized access.")
            return redirect('/login')
    if request.method=='POST':
        user.first_name=request.POST.get('first_name')
        user.last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error("email already exists")
            return redirect (f'/update_user/{id}')
        else:
            user.email=email
            user.save()
            messages.success(request,"Profile Updated Successfully")
            return redirect(f'/update_user/{id}')
    else:
        return render(request,'profile.html',{'user':user})


def delete(request):
    if not request.user.is_authenticated:  
        messages.error(request, 'Authentication Required')
        return redirect('/')
    
    user=request.user
    try:
        user = request.user
        user.delete()  
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('/') 
    except Exception as e:
        messages.error(request, f"Error deleting account: {str(e)}")
        return redirect('update_user') 
    

def logout(request):
    auth.logout(request)
    return redirect('/')


# ✅ Gemini config (replace with environment variable in production)
genai.configure(api_key="AIzaSyBLTZXr4KG6cbk9ajzdaE9Mp__IssyUyGo")

# ✅ Use supported free-tier model
model = genai.GenerativeModel("models/gemini-1.5-flash")  # You can also test "models/gemini-1.0"

# ✅ Helper: Call Gemini and return cleaned result
def gemini_generate(prompt: str) -> str:
    try:
        content = model.generate_content(prompt)
        print("response",content)
        return content.text.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

# ✅ Helper: Convert user message into SQL
def generate_sql_from_message(user_message: str, schema_hint: str = "") -> str:
    prompt = f"""
You are a SQL expert. Based on the following database schema and user message, write a SELECT SQL query.
Schema:
{schema_hint}

User Message:
"{user_message}"

Only return the SQL query. No explanation.
"""
    raw_sql = gemini_generate(prompt)
    print("raw",raw_sql)
    # Clean markdown formatting like ```sql ... ```
    cleaned_sql = re.sub(r"^```sql|```$", "", raw_sql.strip(), flags=re.IGNORECASE).strip()

    return cleaned_sql

# ✅ Helper: Convert query result into natural language
def generate_natural_response(user_message: str, query_result: list[dict]) -> str:
    prompt = f"""
User asked: "{user_message}"

The SQL result is:
{query_result}

Generate a human-readable response summarizing the result.
"""
    return gemini_generate(prompt)

# ✅ Execute safe SELECT query
def execute_select_query(sql_query: str) -> list[dict]:
    cleaned_sql = sql_query.strip().lower()
    if not cleaned_sql.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    return [dict(zip(columns, row)) for row in rows]

# ✅ Main Django view
@csrf_exempt
def chat_to_sql_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        body = json.loads(request.body)
        user_message = body.get("message", "").strip()

        if not user_message:
            return JsonResponse({"error": "Message is required"}, status=400)

        # : Replace with actual logged-in user
        user_id = request.user.id  # temp value for demo/testing
        print(user_id)
        # Provide schema and instructions to Gemini
        schema_hint = f"""
Table: client_customuser
- id INT
- username VARCHAR
- email VARCHAR
- role VARCHAR
- manager_id INT

Instructions:
dont query on username condition rather query on id condition for example SELECT * FROM client_customuser WHERE id = [user_id]
and take value of user_id variable not string.
Table: complaint_complaints
- id INT
- product VARCHAR
- status VARCHAR
- client_id INT
- assigned_worker_id INT

Instructions:
Use client_id = {user_id} or assigned_worker_id = {user_id} when needed.
Only SELECT queries.

"""

        print("🟢 Received message:", user_message)

        sql_query = generate_sql_from_message(user_message, schema_hint)
        print("🧠 Generated SQL:", sql_query)

        if "ERROR" in sql_query:
            return JsonResponse({"error": sql_query}, status=500)

        query_result = execute_select_query(sql_query)
        print("📦 Query result:", query_result)

        natural_response = generate_natural_response(user_message, query_result)
        print("💬 Natural language response:", natural_response)

        return JsonResponse({
            "response": natural_response,
            "sql_query": sql_query,
            "query_result": query_result
        })

    except Exception as e:
        print("❌ Chatbot error:", str(e))
        return JsonResponse({"error": "Internal server error", "details": str(e)}, status=500)

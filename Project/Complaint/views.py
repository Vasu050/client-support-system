from django.shortcuts import render,redirect,get_object_or_404
from .models import Complaints,User
from django.contrib import messages
from django.db.models import Count
from django.db import connection

#from mcp_server import get_user_info

# Create your views here.
def home(request):
    if not request.user.is_authenticated and request.user.role!='client':
        messages.info(request,"Authentication required")
        return redirect('/login')
    if request.method=='POST':
        product=request.POST.get('product')
        description=request.POST.get('description')
        client=request.user
        assigned_worker=assign_complaints()
        status='Assigned'
        complaint=Complaints(
            product=product,
            description=description,
            client=client,
            assigned_worker=assigned_worker,
            status=status
        )
        complaint.save()
        return redirect('/complaints/')
    else:
        #get_user_info(user_id=request.user.id)
        return render(request,'client_dashboard.html')

def tickets(request):
    if not request.user.is_authenticated or request.user.role!='client':
        messages.info(request,"Authentication required")
        return redirect('/login')
    tickets=Complaints.objects.filter(client=request.user).order_by('-date_created')
    if request.method=='GET':
        return render(request,'tickets.html',{'tickets':tickets})
    
def worker(request):
    if not request.user.is_authenticated or request.user.role!='worker':
        messages.info(request,"Authentication required")
        return redirect('/login')
    complaints=Complaints.objects.filter(assigned_worker=request.user,status='Assigned').order_by('-date_created')
    return render(request,'worker_dashboard.html',{'complaints':complaints})

def ticket_update(request,id):
    complaint=get_object_or_404(Complaints,id=id)
    if not request.user.is_authenticated or request.user.role!='worker' or complaint.assigned_worker!=request.user:
        messages.info(request,"Authentication required")
        return redirect('/login')
    if request.method=='POST':
        complaint.status=request.POST.get('status')
        complaint.save()
        return redirect('worker')
    else:
        return render(request,'ticket_update.html',{'complaint':complaint})
    

def assign_complaints():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.id
            FROM client_customuser as u
            LEFT JOIN complaint_complaints AS c ON c.assigned_worker_id = u.id
            WHERE u.role = 'worker'
            GROUP BY u.id
            ORDER BY COUNT(c.id)
            LIMIT 1;
        """)
        row = cursor.fetchone()
        worker_id=row[0]
        worker=User.objects.get(id=worker_id)
    return worker
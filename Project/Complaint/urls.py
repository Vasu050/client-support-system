from django.urls import path
from Complaint import views

urlpatterns=[
    path('',views.home,name='home'),
    path('tickets/',views.tickets,name='tickets'),
    path('tickets/update/<int:id>/',views.ticket_update,name='ticket_update'),
    path('worker/',views.worker,name="worker"),
    
]
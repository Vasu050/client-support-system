from django.urls import path
from Client import views

urlpatterns=[
    path('',views.register,name='register'),
    #path('register_worker/', lambda req: register(req, role='worker'), name='register_worker')
    path('login',views.user_login,name='user_login'),
    path('update_user/<int:id>/',views.update_user,name='update_user'),
    path('manager',views.manager,name='manager'),
    path('manager/add/',views.add_worker,name='add_worker'),
    path('manager/delete/<int:id>', views.delete_worker, name='delete_worker'),
    path('delete',views.delete,name="delete"),
    path('logout',views.logout,name="logout")
]
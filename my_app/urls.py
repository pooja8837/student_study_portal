from django.urls import path
from my_app import views

app_name = 'my_app'

urlpatterns = [

    path('', views.home, name='home'),
    path('notes/',views.notes,name='notes'),
    path('delete_note/<int:pk>',views.delete_note,name='delete_note'),
    path('notes_detail/', views.notes_detail, name="notes_detail"),
    path('register/',views.register, name='register'),
    path('login/',views.user_login, name='user_login'),
    #path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('forgetPassword/', views.forget_password, name="forgetPassword"),
    path('resetPassword/', views.reset_password, name="resetPassword"),
    path('logout/',views.user_logout, name='user_logout'),
    path('profile/',views.profile, name='profile'),
    path('homework/',views.homework, name='homework'),
    path('update_homework/<int:pk>',views.update_homework,name='update_homework'),
    path('delete_homework/<int:pk>',views.delete_homework,name='delete_homework'),
    path('youtube/',views.youtube,name = 'youtube'),
    path('todo/',views.todo,name = 'todo'),
    path('update_todo/<int:pk>',views.update_todo,name="update_todo"),
    path('delete_todo/<int:pk>',views.delete_todo,name="delete_todo"),
    path('books/', views.books, name="books"),
    path('dictionary/', views.dictionary, name="dictionary"),
    path('wiki/', views.wiki, name="wiki"), 
    path('conversion/', views.conversion, name="conversion"), 


    

]
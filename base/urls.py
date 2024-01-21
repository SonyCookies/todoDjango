from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name="home"),
  path('index/', views.index, name="index"),

  path('login/', views.loginPage, name="login"),
  path('logout/', views.logoutUser, name="logout"),
  path('register/', views.registerPage, name="register"),
  path('add-task/', views.addTask, name="add-task"),
  path('update-task/<str:pk>', views.updateTask, name="update-task"),
  path('delete-task/<str:pk>', views.deleteTask, name="delete-task"),
  path('done-task/<str:pk>', views.doneTask, name="done-task"),
  path('profile/', views.userProfile, name="profile"),
  path('update-user/', views.updateUser, name="update-user"),

  path('categories/', views.categoriesPage, name="categories"),
  path('activity/', views.activityPage, name="activity")
]
from django.urls import path

from zones.api import views

urlpatterns = [
    path('/edit', views.edit),
    path('/delete/<int:id>/<str:zone>', views.delete,name='delete'),
    path('/add',views.add,name='add'),
]

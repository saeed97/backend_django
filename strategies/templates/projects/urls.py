from django.urls import path
from .views import ProjectList, ProjectCreate, ProjectDetail, ProjectUpdate, ProjectDelete, ProjectLike, ProjectRequestToJoin

urlpatterns = [
    path('', ProjectList.as_view(), name='project-list'),
    path('new/', ProjectCreate.as_view(), name='project-create'),
    path('<int:pk>/', ProjectDetail.as_view(), name='project-detail'),
    path('<int:pk>/edit/', ProjectUpdate.as_view(), name='project-update'),
    path('<int:pk>/delete/', ProjectDelete.as_view(), name='project-delete'),
    path('<int:pk>/like', ProjectLike.as_view(), name='project-like'),
    path('<int:pk>/request-to-join', ProjectRequestToJoin.as_view(), name='project-request-to-join'),
]
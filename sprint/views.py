from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q, Count, Prefetch
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework import status
from project.models import Project, Sprint
from sprint.serializers import SprintCreateSerializer, SprintListSerializer, SprintUpdateSerializer
from ticket.models import Ticket

# Create your views here.

class SprintListAPIView(ListAPIView):
    
    serializer_class = SprintListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.kwargs['project_id']
        
        active_tickets = Ticket.objects.filter(
            is_active=True
        ).select_related(
            'status',
            'assigned_to',
            'created_by'
        ).prefetch_related(
            'labels'
        )
        
        return Sprint.objects.filter(project__members=self.request.user, project_id=project_id, is_active=True)\
            .annotate(ticket_count=Count('tickets', filter=Q(tickets__is_active=True), distinct=True))\
            .select_related('project').prefetch_related(
            Prefetch('tickets', queryset=active_tickets)
            )






class SprintCreateAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, project_id):
        serializer = SprintCreateSerializer(data=request.data)
        if serializer.is_valid():
            sprint = serializer.save(project_id=project_id)
            return Response(SprintListSerializer(sprint).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

class SprintUpdateStatusAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, sprint_id, project_id):
        
        project = get_object_or_404(Project, id=project_id, members=request.user)
        sprint = get_object_or_404(Sprint, id=sprint_id, project=project)
        
        new_status = request.data.get('status')
        
        if new_status not in dict(Sprint.CHOICES_STATUS):
            return Response({'error': 'Estado no válido'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_status == 'activo':
            Sprint.objects.filter(
                project=sprint.project,
                status='activo'
            ).exclude(id=sprint.id).update(status='planificado')
        
        sprint.status = new_status
        sprint.save()
        
        return Response(SprintListSerializer(sprint).data)





class SprintDeleteAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, sprint_id, project_id):

        project = get_object_or_404(Project, id=project_id, members=request.user)
        sprint = get_object_or_404(Sprint, id=sprint_id, project=project,  is_active=True)

        if sprint.tickets.exists():
            return Response({'error': 'No se puede eliminar un sprint con tickets asignados'}, status=status.HTTP_400_BAD_REQUEST)

        sprint.is_active = False
        sprint.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class SprintUpdateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, sprint_id, project_id):
        project = get_object_or_404(Project, id=project_id, members=request.user)
        sprint = get_object_or_404(Sprint, id=sprint_id, project=project)

        serializer = SprintUpdateSerializer(sprint, data=request.data, partial=True)
        if serializer.is_valid():
            sprint = serializer.save()
            return Response(SprintListSerializer(sprint).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

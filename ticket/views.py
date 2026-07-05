from rest_framework.views import APIView, PermissionDenied
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from django.db.models import Q, Count, Prefetch
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timesince import timesince
from datetime import timedelta
from rest_framework import status


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from project.models import Project, Sprint
from .models import Status, Ticket, TicketHistory
from utils.llm_client import ticket_with_llm
from .serializers import AssignTicketSerializer, BacklogTicketsSerializer, CreateTicketSerializer, TicketSerializer, TicketsByStatusListSerializer, UpdateTicketSerializer
import logging

logger = logging.getLogger(__name__)



def send_activity(project_id, user, message, created_at):
    actor = user.username

    data = {
        "message": message,
        "user": actor,
        "created_at": str(created_at),
        "time_ago": timesince(created_at, timezone.now()) + " atrás"
    }

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f'activities_{project_id}',
        {
            'type': 'send_activity',
            'data': data
        }
    )
    
    
class TicketPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    



class TicketListAPIView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    
    pagination_class = TicketPagination
    serializer_class = TicketSerializer
    
    def get_queryset(self):
        
        project_id = self.kwargs.get('project_id') 
        
        queryset = Ticket.objects.select_related(
            'project', 'status', 'assigned_to', 'created_by'
        ).prefetch_related('labels').filter(project__members=self.request.user, project__id=project_id
        ).order_by('-created_at')
        
        search_term = self.request.query_params.get('search_term')
        search_category = self.request.query_params.get('search_category')
        search_priority = self.request.query_params.get('search_priority')
        search_type = self.request.query_params.get('search_type')
        search_status = self.request.query_params.get('search_status')
        search_created_by = self.request.query_params.get('search_created_by')
        
        if search_term:
            queryset = queryset.filter(Q(title__icontains=search_term))
        if search_category:
            queryset = queryset.filter(Q(category__icontains=search_category))
        if search_priority:
            queryset = queryset.filter(Q(priority__icontains=search_priority))
        if search_type:
            queryset = queryset.filter(Q(type__icontains=search_type))
        if search_status:
            queryset = queryset.filter(Q(status__icontains=search_status))
        if search_created_by:
            queryset = queryset.filter(Q(created_by__icontains=search_created_by))
        
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        
        pagination = request.query_params.get('paginate', 'true').lower()
        queryset = self.get_queryset()
        
        if pagination == 'false':
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': serializer.data
            })
            
        return super().list(request, *args, **kwargs)
    
    
    
class BacklogTicketsAPIView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    
    pagination_class = TicketPagination
    serializer_class = BacklogTicketsSerializer
    
    def get_queryset(self):
        
        project_id = self.kwargs['project_id']
        queryset = Ticket.objects.filter(project__members=self.request.user, project_id=project_id, sprint__isnull=True, is_active=True)\
                   .select_related('project', 'status', 'assigned_to').prefetch_related('labels')\
                   .order_by('-created_at')
        
        search_term = self.request.query_params.get('search_term')
        
        if search_term:
            queryset = queryset.filter(Q(title__icontains=search_term) | Q(key__icontains=search_term))
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        
        pagination = request.query_params.get('paginate', 'true').lower()
        queryset = self.get_queryset()
        
        if pagination == 'false':
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': serializer.data
            })
            
        return super().list(request, *args, **kwargs)
    
    
    
    
class TicketGenerateView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get("title")
        description = request.data.get("description")

        if not title or not description:
            return Response(
                {"detail": "title y description son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ai_data = ticket_with_llm(title, description)
            return Response(ai_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": f"Error generando datos con IA: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            


class CreateTicketAPIView(CreateAPIView):
    
    serializer_class = CreateTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_project(self):
        return get_object_or_404(Project, id=self.kwargs['project_id'])

    def perform_create(self, serializer):
        project = self.get_project()

        if not project.members.filter(id=self.request.user.id).exists():
            raise PermissionDenied("No perteneces a este proyecto")

        ticket = serializer.save(
            project=project,
            created_by=self.request.user
        )

        send_activity(
            project_id=ticket.project.id,
            user=self.request.user,
            message=f"{self.request.user.username} creó el ticket #{ticket.key}",
            created_at=ticket.created_at
        )
     
     
     
     
     
class UpdateStatusTicketAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, project_id, ticket_id):
        
        ticket = Ticket.objects.filter(id=ticket_id, project__id=project_id).first()
        
        if not ticket:
            return Response({'detail': 'Ticket no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        status_id = request.data.get('status')
        
        if not status_id:
            return Response({'detail': 'El campo "status" es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_status = Status.objects.get(id=status_id)
        except Status.DoesNotExist:
            return Response({'detail': 'Status no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        old_status = ticket.status
        ticket.status = new_status
        ticket.save()
        
        TicketHistory.objects.create(
            ticket=ticket,
            changed_by=request.user, 
            old_status=old_status,
            new_status=new_status
        )
        
        send_activity(
            project_id=ticket.project.id,
            user=request.user,
            message=f"{request.user.username} cambió el estado de #{ticket.key} de '{old_status.name}' a '{new_status.name}'",
            created_at=timezone.now()
        )
        
        return Response(TicketSerializer(ticket).data, status=status.HTTP_200_OK)





class UpcomingDueTicketsView(APIView):

    def get(self, request, project_id):

        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)

        tickets = Ticket.objects.filter(
            project_id=project_id,
            due_date__isnull=False,
            is_active=True
        )

        results = []

        for ticket in tickets:
            due_date = timezone.localtime(ticket.due_date)
            due_day = due_date.date()

            if due_day == today:
                label = "Vence hoy"
            elif due_day == tomorrow:
                label = "Vence mañana"
            else:
                continue  # ignorar otros días

            # Formato hora (ej: 03:00 PM)
            hour = due_date.strftime("%I:%M %p")

            results.append({
                "key": ticket.key,
                "title": ticket.title,
                "message": f"{label}, {hour}"
            })

        # Ordenar por fecha más próxima
        results = sorted(results, key=lambda x: x['message'])

        return Response(results)
    
    
    

class TicketAssignToSprintAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, project_id, ticket_id):
        
        project = get_object_or_404(Project, id=project_id)
        ticket = get_object_or_404(Ticket, id=ticket_id, project=project)
        
        sprint_id = request.data.get('sprint_id')
        
        # Permitir quitar del sprint (backlog)
        if sprint_id in [None, '']:
            ticket.sprint = None
            ticket.save()
            return Response(TicketSerializer(ticket).data, status=status.HTTP_200_OK)
        
        try:
            sprint = project.sprints.get(id=sprint_id)
        except Sprint.DoesNotExist:
            return Response({'detail': 'Sprint no encontrado en este proyecto'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validación opcional (recomendada)
        if not sprint.is_active:
            return Response({'detail': 'El sprint no está activo'}, status=status.HTTP_400_BAD_REQUEST)
        
        ticket.sprint = sprint
        ticket.save()
        
        return Response(TicketSerializer(ticket).data, status=status.HTTP_200_OK)



class TicketByStatusListAPIView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    pagination_class = TicketPagination
    serializer_class = TicketsByStatusListSerializer
    
    def get_queryset(self):
        
        project_id = self.kwargs.get('project_id') 
        
        tickets_queryset = Ticket.objects.filter(
            is_active=True
        ).select_related(
            'project',
            'status',
            'assigned_to',
            'created_by'
        ).prefetch_related(
            'labels'
        )
        
        queryset = Status.objects.filter(
            project__members=self.request.user,
            project__id=project_id,
            is_active=True
        ).annotate(
            tickets_count=Count('tickets', filter=Q(tickets__is_active=True))
        ).prefetch_related(
            Prefetch('tickets', queryset=tickets_queryset)
        ).order_by('order')
        
        search_term = self.request.query_params.get('search_term')
        if search_term:
            queryset = queryset.filter(Q(tickets__title__icontains=search_term) | Q(tickets__key__icontains=search_term) | Q(tickets__key__icontains=search_term)).distinct()
        
        return queryset
    
    
    def list(self, request, *args, **kwargs):
        
        pagination = request.query_params.get('paginate', 'true').lower()
        queryset = self.get_queryset()
        
        if pagination == 'false':
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': serializer.data
            })
            
        return super().list(request, *args, **kwargs)
    
    
    
    

class TicketAssignedToUpdateAPIView(UpdateAPIView):
    
    serializer_class = AssignTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_project(self):
        return get_object_or_404(Project, id=self.kwargs['project_id'])

    def get_object(self):
        project = self.get_project()
        return get_object_or_404(
            Ticket,
            id=self.kwargs['ticket_id'],
            project=project
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = self.get_project()
        return context

    def perform_update(self, serializer):
        project = self.get_project()

        if not project.members.filter(id=self.request.user.id).exists():
            raise PermissionDenied("No perteneces a este proyecto")

        ticket = serializer.save()

        # (opcional) actividad
        if ticket.assigned_to:
            message = f"{self.request.user.username} asignó el ticket a {ticket.assigned_to.username}"
        else:
            message = f"{self.request.user.username} desasignó el ticket"

        send_activity(
            project_id=project.id,
            user=self.request.user,
            message=message,
            created_at=ticket.updated_at
        )




class TicketDeleteAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, project_id, ticket_id):

        project = get_object_or_404(Project, id=project_id)
        ticket = get_object_or_404(Ticket, id=ticket_id, project=project)

        if not project.members.filter(id=request.user.id).exists():
            raise PermissionDenied("No perteneces a este proyecto")

        ticket.is_active = False
        ticket.save()

        # send_activity(
        #     project_id=project.id,
        #     user=request.user,
        #     message=f"{request.user.username} eliminó el ticket #{ticket.key}",
        #     created_at=timezone.now()
        # )

        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateTicketAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, project_id, ticket_id):
        project = get_object_or_404(Project, id=project_id)

        if not project.members.filter(id=request.user.id).exists():
            raise PermissionDenied("No perteneces a este proyecto")

        ticket = get_object_or_404(Ticket, id=ticket_id, project=project)

        old_status = ticket.status
        serializer = UpdateTicketSerializer(ticket, data=request.data, partial=True, context={'project': project})

        if serializer.is_valid():
            ticket = serializer.save()

            if 'status' in request.data and old_status != ticket.status:
                TicketHistory.objects.create(
                    ticket=ticket,
                    changed_by=request.user,
                    old_status=old_status,
                    new_status=ticket.status
                )

            return Response(TicketSerializer(ticket).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
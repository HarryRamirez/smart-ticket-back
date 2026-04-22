from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework import status

from project.models import Project
from .models import Status, Ticket, TicketHistory
from utils.llm_client import ticket_with_llm
from .serializers import CreateTicketSerializer, TicketSerializer
import logging

logger = logging.getLogger(__name__)


class TicketPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    



class TicketListAPIView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    
    pagination_class = TicketPagination
    serializer_class = TicketSerializer
    
    def get_queryset(self):
        
        queryset = Ticket.objects.select_related(
            'project', 'status', 'assigned_to', 'created_by'
        ).prefetch_related('labels').filter(project__members=self.request.user).order_by('-created_at')
        
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
    
    
    
    
    
    
# Metodo que genera la respuesta con ia
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
            
            


# Metodo que crea el ticket
class CreateTicketAPIView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        
        project = get_object_or_404(Project, id=project_id)

        # validar que el usuario pertenece al proyecto
        if not project.members.filter(id=request.user.id).exists():
            return Response(
                {"error": "No perteneces a este proyecto"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CreateTicketSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            ticket = serializer.save(
                project=project,              
                created_by=request.user       
            )

            return Response(
                TicketSerializer(ticket).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            {'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
     
     
     
     
     
class UpdateStatusTicketAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk):
        
        ticket = Ticket.objects.filter(id=pk).first()
        
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

        for t in tickets:
            due_date = timezone.localtime(t.due_date)
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
                "key": t.key,
                "title": t.title,
                "message": f"{label}, {hour}"
            })

        # Ordenar por fecha más próxima
        results = sorted(results, key=lambda x: x['message'])

        return Response(results)

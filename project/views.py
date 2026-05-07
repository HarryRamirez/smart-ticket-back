from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.db.models import Q, Count, Max, Prefetch
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from django.utils.timesince import timesince
from django.utils import timezone
from rest_framework import status

from ticket.models import Attachment, Comment, Status, Ticket, TicketHistory
from .models import Project, ProjectMember
from .serializers import CreateProjectSerializer, DashboardCardsSerializer, ProjectListSerialzer, ProjectMemberCreateSerializer, ProjectMemberSerializer, StatusCreateSerializer, StatusProjectSerializer, UserSerializer
import logging

logger = logging.getLogger(__name__)    

class ProjectPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    
    


class ProjectListAPIView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectListSerialzer
    pagination_class = ProjectPagination

    def get_queryset(self):
        
        queryset = Project.objects.annotate(members_count=Count('members', distinct=True))\
                   .filter( members=self.request.user)\
                   .select_related('created_by').prefetch_related('members', 'sprints')
        
        search_term = self.request.query_params.get('search_term')
        
        if search_term:
            queryset =  queryset.filter(Q(name__icontains=search_term))
        
        return queryset.distinct().order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        pagination= request.query_params.get('paginate', 'true').lower()
        
        queryset = self.get_queryset()
        
        if pagination == 'false':
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': serializer.data   
            })
        
        return super().list(request, *args, **kwargs)


class StatusProjectAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            project = Project.objects.annotate(
                            tickets_count=Count('tickets', distinct=True),
                            sprints_count=Count('sprints', distinct=True))\
                      .prefetch_related(Prefetch('statuses', queryset=Status.objects.annotate(
                            total_tickets=Count('tickets', distinct=True))))\
                      .get(pk=pk, members=request.user)
                      
            serializer = StatusProjectSerializer(project)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'message': 'Proyecto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
   

class ActivityAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        
        user = request.user
        activities = []

        # Tickets creados
        tickets = Ticket.objects.filter(project_id=pk).select_related('created_by')[:10]

        for t in tickets:
            actor = "Tú" if t.created_by == user else t.created_by.username

            activities.append({
                "message": f"{actor} creó el ticket #{t.key}",
                "user": actor,
                "created_at": t.created_at
            })

        # Historial de estados
        history = TicketHistory.objects.filter(ticket__project_id=pk)\
                  .select_related('changed_by', 'ticket', 'old_status', 'new_status')[:10]

        for h in history:
            actor = "Tú" if h.changed_by == user else h.changed_by.username

            activities.append({
                "message": f"{actor} cambió el estado de #{h.ticket.key} de '{h.old_status}' a '{h.new_status}'",
                "user": actor,
                "created_at": h.created_at
            })

        # Comentarios
        comments = Comment.objects.filter(ticket__project_id=pk)\
                   .select_related('user', 'ticket')[:10]

        for c in comments:
            actor = "Tú" if c.user == user else c.user.username

            activities.append({
                "message": f"{actor} comentó en el ticket #{c.ticket.key}",
                "user": actor,
                "created_at": c.created_at
            })

        # Adjuntos
        attachments = Attachment.objects.filter(ticket__project_id=pk)\
                      .select_related('uploaded_by', 'ticket')[:10]

        for a in attachments:
            actor = "Tú" if a.uploaded_by == user else a.uploaded_by.username

            activities.append({
                "message": f"{actor} subió un archivo al ticket #{a.ticket.key}",
                "user": actor,
                "created_at": a.created_at
            })

        # Ordenar todo por fecha (clave)
        activities = sorted(activities, key=lambda x: x['created_at'], reverse=True)

        # Limitar resultados
        activities = activities[:10]

        # Formatear tiempo tipo "Hace 3 horas"
        for a in activities:
            a["time_ago"] = timesince(a["created_at"], timezone.now()) + " atrás"

        return Response(activities)      
    

class GetProjectAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            project = Project.objects.select_related('created_by')\
                             .prefetch_related('members', 'sprints')\
                             .get(pk=pk, members=request.user)
                             
            serializer = ProjectListSerialzer(project)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'message': 'Proyecto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        
        
class CreateProjectAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CreateProjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            project = serializer.save()

            return Response(ProjectListSerialzer(project).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UpdateProjectAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, members=request.user)
        except Project.DoesNotExist:
            return Response({'message': 'Proyecto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateProjectSerializer(project, data=request.data, partial=True)
        
        if serializer.is_valid():
            instance = serializer.save()
            return Response(ProjectListSerialzer(instance).data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteProjectAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):

        ids = request.data.get('ids', [])
        
        if not isinstance(ids, list):
            return Response({'message': 'ids debe ser una lista'}, status=status.HTTP_400_BAD_REQUEST)
        if not ids:
            return Response({'message': 'No se proporcionaron ids'}, status=status.HTTP_400_BAD_REQUEST)
        
        project = Project.objects.filter(id__in=ids, members=request.user)
        project.delete()
        
        return Response({'message': 'Proyectos eliminados correctamente'}, status=status.HTTP_200_OK)
    
    


class ProjectMembersListAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)

            # Validar que el usuario pertenece al proyecto
            if not ProjectMember.objects.filter(project=project, user=request.user).exists():
                return Response(
                    {'message': 'No tienes acceso a este proyecto'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Traer miembros desde el modelo intermedio
            members = ProjectMember.objects.filter(project=project)
            
            serializer = ProjectMemberSerializer(members, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Project.DoesNotExist:
            return Response(
                {'message': 'Proyecto no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
            


class ProjectMemberCreateAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        serializer = ProjectMemberCreateSerializer(data=request.data)

        if serializer.is_valid():
            try:
                project = Project.objects.get(pk=pk)
            except Project.DoesNotExist:
                return Response({'message': 'Proyecto no encontrado'}, status=404)

            # Validar acceso ANTES de crear
            if not ProjectMember.objects.filter(project=project, user=request.user).exists():
                return Response({'message': 'No tienes acceso'}, status=403)
            
            user = serializer.validated_data['user']

            if ProjectMember.objects.filter(project=project, user=user).exists():
                return Response(
                    {'message': 'Este usuario ya pertenece al proyecto'},
                    status=400
                )


            # Guardar correctamente
            member = serializer.save(project=project)

            return Response(
                ProjectMemberSerializer(member).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class ProjectMemberUpdateRoleAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk, member_id):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({'message': 'Proyecto no encontrado'}, status=404)

        # Validar acceso al proyecto
        try:
            current_member = ProjectMember.objects.get(project=project, user=request.user)
        except ProjectMember.DoesNotExist:
            return Response({'message': 'No tienes acceso'}, status=403)

        try:
            member = ProjectMember.objects.get(pk=member_id, project=project)
        except ProjectMember.DoesNotExist:
            return Response({'message': 'Miembro no encontrado'}, status=404)

        # Validar que venga el role
        new_role = request.data.get('role')
        if not new_role:
            return Response({'message': 'El campo role es requerido'}, status=400)

        # (Opcional pero recomendado) validar permisos
        if current_member.role != 'admin':
            return Response({'message': 'No tienes permisos para cambiar roles'}, status=403)

        # Actualizar
        member.role = new_role
        member.save()

        return Response(
            ProjectMemberSerializer(member).data,
            status=200
        )
        

class ProjectMemberDeleteAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk, member_id):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({'message': 'Proyecto no encontrado'}, status=404)

        # Validar acceso al proyecto
        if not ProjectMember.objects.filter(project=project, user=request.user).exists():
            return Response({'message': 'No tienes acceso'}, status=403)

        try:
            member = ProjectMember.objects.get(pk=member_id, project=project)
        except ProjectMember.DoesNotExist:
            return Response({'message': 'Miembro no encontrado'}, status=404)

        member.delete()

        return Response({'message': 'Miembro eliminado correctamente'}, status=200)



class MemberSearchProjectAPIView(ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        project_id = self.request.query_params.get('project_id')

        queryset = User.objects.all()

        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )

        # Excluir usuarios ya en el proyecto
        if project_id:
            queryset = queryset.exclude(
                id__in=ProjectMember.objects.filter(project_id=project_id)
                .values_list('user_id', flat=True)
            )

        return queryset
    



class DashboardCardsAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Query 1 → proyectos del usuario
        projects = ProjectMember.objects.filter(user=request.user)\
                    .values_list('project', flat=True)

        project_count = projects.count()

        # Query 2 → todos los conteos en una sola
        ticket_stats = Ticket.objects.filter(project__in=projects).aggregate(
            tickets_count=Count('id'),
            my_tickets_count=Count('id', filter=Q(assigned_to=request.user)),
            unassigned_tickets_count=Count('id', filter=Q(assigned_to__isnull=True))
        )

        data = {
            "project_count": project_count,
            "tickets_count": ticket_stats["tickets_count"],
            "my_tickets_count": ticket_stats["my_tickets_count"],
            "unassigned_tickets_count": ticket_stats["unassigned_tickets_count"],
        }

        serializer = DashboardCardsSerializer(data)

        return Response(serializer.data, status=status.HTTP_200_OK)
    



class StatusCreateAPIView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        
        project = get_object_or_404(Project, id=project_id)

        serializer = StatusCreateSerializer(data=request.data)
        
        if serializer.is_valid():

            # calcula el siguiente order
            last_order = Status.objects.filter(project=project)\
                        .aggregate(Max('order'))['order__max']
            
            next_order = (last_order or 0) + 1

            status_obj = serializer.save(
                project=project,
                created_by=request.user,
                order=next_order
            )

            return Response(
                StatusCreateSerializer(status_obj).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    

class ProjectDeleteAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, project_id):
        try:
            project = Project.objects.get(pk=project_id, members=request.user)
        except Project.DoesNotExist:
            return Response({'message': 'Proyecto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        project.delete()
        return Response({'message': 'Proyecto eliminado correctamente'}, status=status.HTTP_200_OK)
    
    
    
    
    
class StatusDeleteAPIView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, project_id, status_id):
        
        project = get_object_or_404(Project, id=project_id)
        status_obj = get_object_or_404(Status, id=status_id, project=project)

        if status_obj.tickets.exists():
            return Response(
                {'message': 'No se puede eliminar un estado con tickets asignados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        status_obj.is_active = False
        status_obj.save()

        return Response({'message': 'Estado eliminado correctamente'}, status=status.HTTP_200_OK)
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Project(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects'
    )
    key = models.CharField(max_length=10, unique=True, db_index=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMember',
        related_name='projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['name', '-created_at'])]

    def __str__(self):
        return self.name


class ProjectMember(models.Model):
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('developer', 'Developer'),
        ('qa', 'QA'),
        ('viewer', 'Viewer'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES) 

    class Meta:
        unique_together = ('user', 'project')
        indexes = [models.Index(fields=['project', 'role'])]

    def __str__(self):
        return f"{self.user} - {self.project} ({self.role})"
        
        
    

class Sprint(models.Model):
    
    CHOICES_STATUS = [
        ('planificado', 'Planificado'),
        ('activo', 'Activo'),
        ('completado', 'Completado'),
    ]
    
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='sprints')
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=CHOICES_STATUS, default='planificado')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']
        constraints = [
            models.UniqueConstraint(
                fields=['project'],
                condition=models.Q(status='activo'),
                name='unique_active_sprint_per_project'
            )
        ]
        indexes = [models.Index(fields=['project', 'is_active'])]

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("La fecha de inicio no puede ser mayor a la de fin")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        
        if self.status == 'activo':
            Sprint.objects.filter(
                project=self.project,
                status='activo'
            ).exclude(id=self.id).update(status='planificado')
        
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name} ({self.project.name})"






# class Activity(models.Model):

#     EVENT_TYPES = [
#         ('TICKET_CREATED', 'Ticket creado'),
#         ('TICKET_DELETED', 'Ticket eliminado'),
#         ('TICKET_MOVED', 'Ticket movido a sprint'),
#         ('TICKET_REMOVED_FROM_SPRINT', 'Ticket removido de sprint'),
#         ('SPRINT_CREATED', 'Sprint creado'),
#         ('SPRINT_DELETED', 'Sprint eliminado'),
#         ('STATUS_CHANGED', 'Estado cambiado'),
#         ('COMMENT_CREATED', 'Comentario creado'),
#         ('ATTACHMENT_UPLOADED', 'Archivo subido'),
#     ]

#     project = models.ForeignKey(Project, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)

#     event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
#     message = models.TextField()

#     # Opcional pero muy útil
#     ticket = models.ForeignKey(Ticket, null=True, blank=True, on_delete=models.CASCADE)
#     sprint = models.ForeignKey(Sprint, null=True, blank=True, on_delete=models.CASCADE)

#     created_at = models.DateTimeField(auto_now_add=True)

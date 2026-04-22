from django.db import models
from django.conf import settings
from project.models import Project, Sprint




class Label(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='labels')
    
    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['project', 'name'])]

    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active= models.BooleanField(default=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='statuses')
    
    class Meta:
        ordering = ['order']
        indexes = [models.Index(fields=['project', 'is_active'])]

    def __str__(self):
        return f'{self.name}'

class Ticket(models.Model):
    
    CATEGORY_CHOICES = [
        ('Backend', 'Backend'),
        ('Frontend', 'Frontend'),
        ('BaseDatos', 'Base de Datos'),
        ('Integraciones', 'Integraciones'),
        ('UIUX', 'UI/UX'),
        ('Documentacion', 'Documentación'),
        ('General', 'General'),
    ]

    PRIORITY_CHOICES = [
        ('crítica', 'Crítica'),
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
        ('muy_baja', 'Muy baja'),
    ]

    TYPE_CHOICES = [
        ('bug', 'Bug'),
        ('tarea', 'Tarea'),
        ('historia', 'Historia de usuario'),
        ('mejora', 'Mejora'),
        ('épica', 'Épica'),
    ]
    key = models.CharField(max_length=10, unique=True, db_index=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, blank=True, null=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=True, null=True)
    summary = models.CharField(max_length=500, blank=True, null=True)
    labels = models.ManyToManyField(Label, blank=True, related_name='tickets')
    suggested_solution = models.TextField(blank=True, null=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, related_name='tickets')
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    is_active = models.BooleanField(default=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    due_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['assigned_to', 'is_active']),
        ]

    def __str__(self):
        return f'{self.title} - {self.project.name}'


class TicketHistory(models.Model):

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    old_status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, related_name='+')
    new_status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['ticket', '-created_at'])]

    def __str__(self):
        return f'Historial Ticket #{self.ticket.id}'
    
    
class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['ticket', '-created_at'])]

    def __str__(self):
        return f'Comentario de {self.user.username} en Ticket #{self.ticket.id}'
    



class Attachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='tickets/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Adjunto de Ticket #{self.ticket.id}'


class AISuggestion(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True)
    response = models.JSONField()
    title_input = models.CharField(max_length=255)
    description_input = models.TextField()
    final_value = models.JSONField()# respuesta final después de limpieza y validación del usuario
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Sugerencia de IA para Ticket #{self.ticket.id}'



# Es decir:

# El usuario escribe su problema (título + descripción)

# La IA analiza y llena: categoría, tipo, prioridad, resumen, solución sugerida

# Tú mantienes los mismos modelos, pero los CHOICES deben ser estilo Jira, más profesionales, 
# más amplios, más de manejo de tareas / issues, no de infraestructura.

# Aquí te acomodo TODAS las opciones (choices) con un estilo Jira real, profesional, 
# moderno y con categorías amplias.
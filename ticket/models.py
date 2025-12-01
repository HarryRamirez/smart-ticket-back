from django.db import models
from django.conf import settings


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

    STATUS_CHOICES = [
        ('por_hacer', 'Por hacer'),
        ('en_progreso', 'En progreso'),
        ('en_revision', 'En revisión'),
        ('bloqueado', 'Bloqueado'),
        ('completado', 'Completado'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, blank=True, null=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=True, null=True)
    summary = models.CharField(max_length=500, blank=True, null=True)
    suggested_solution = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Por hacer')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TicketHistory(models.Model):

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    comment = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Historial Ticket #{self.ticket.id}'
    



# Es decir:

# El usuario escribe su problema (título + descripción)

# La IA analiza y llena: categoría, tipo, prioridad, resumen, solución sugerida

# Tú mantienes los mismos modelos, pero los CHOICES deben ser estilo Jira, más profesionales, 
# más amplios, más de manejo de tareas / issues, no de infraestructura.

# Aquí te acomodo TODAS las opciones (choices) con un estilo Jira real, profesional, 
# moderno y con categorías amplias.
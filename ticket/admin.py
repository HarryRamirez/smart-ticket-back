from django.contrib import admin
from .models import Ticket, Status, TicketHistory, Label, Attachment, AISuggestion

admin.site.register(Ticket)
admin.site.register(Status)
admin.site.register(TicketHistory)
admin.site.register(Label)
admin.site.register(Attachment)
admin.site.register(AISuggestion)
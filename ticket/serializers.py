from rest_framework import serializers
from utils.ollama_client import ticket_with_ollama
from .models import Ticket





class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"





class CreateTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "title",
            "description",
            "category",
            "priority",
            "type",
            "summary",
            "suggested_solution",
            "created_by"
        ]


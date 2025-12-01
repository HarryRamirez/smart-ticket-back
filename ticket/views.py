from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utils.ollama_client import ticket_with_ollama

from .serializers import CreateTicketSerializer, TicketSerializer


# Metodo que genera la respuesta con ia
class TicketGenerateView(APIView):

    def post(self, request):
        title = request.data.get("title")
        description = request.data.get("description")

        if not title or not description:
            return Response(
                {"detail": "title y description son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ai_data = ticket_with_ollama(title, description)
            print(ai_data)
            return Response(ai_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": f"Error generando datos con IA: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Metodo que crea el ticket
class CreateTicketAPIView(APIView):

    def post(self, request):
         serializer = CreateTicketSerializer(data=request.data)


         if serializer.is_valid():
             ticket = serializer.save()

             return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)
         
         return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from .services.client_service import ClientService


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ClientRegistrationView(APIView):
    def __init__(
            self,
            client_service: ClientService = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.client_service = client_service or ClientService()

    @swagger_auto_schema(
        operation_description="Register a new client with email, CPF, birth date, and password.",
        request_body=UserSerializer,
        responses={
            201: "Client successfully created.",
            400: "Validation error.",
            500: "Internal server error."
        }
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                self.client_service.create_user(
                    name=serializer.validated_data['name'],
                    email=serializer.validated_data['email'],
                    cpf=serializer.validated_data['cpf'],
                    birth_date=serializer.validated_data['birth_date'],
                    password=serializer.validated_data['password']
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"title": "Error", "message": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

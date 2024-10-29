from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name
        token['email'] = user.email
        token['role'] = user.role
        return token

    def validate(self, attrs):
        super().validate(attrs)

        token = self.get_token(self.user)

        response = {
            'access_token': str(token.access_token),
            'refresh_token': str(token),
        }

        return response

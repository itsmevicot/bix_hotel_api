from users.models import User


class UserRepository:
    @staticmethod
    def create_user(
            name: str,
            email: str,
            cpf: str,
            birth_date: str,
            password: str,
    ) -> User:
        user = User.objects.create_user(
            name=name,
            email=email,
            cpf=cpf,
            birth_date=birth_date,
            password=password,
        )
        return user

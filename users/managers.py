from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, name, email, cpf, birth_date, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        if not cpf:
            raise ValueError("The CPF field must be set.")
        email = self.normalize_email(email)
        user = self.model(name=name, email=email, cpf=cpf, birth_date=birth_date, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, cpf, birth_date, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, cpf, birth_date, password, **extra_fields)

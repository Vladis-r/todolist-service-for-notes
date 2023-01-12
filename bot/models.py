from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.crypto import get_random_string


class TgUser(models.Model):
    tg_chat_id = models.PositiveIntegerField()
    tg_user_id = models.PositiveIntegerField(unique=True)
    tg_username = models.CharField(max_length=32, validators=[MinLengthValidator(5)])
    user = models.ForeignKey("core.User", null=True, blank=True, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=10, unique=True)

    def generate_verification_code(self) -> str:
        self.verification_code = get_random_string(10)
        self.save()
        return self.verification_code

    class Meta:
        verbose_name = "Бот"

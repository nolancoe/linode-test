from django.db import models
from users.models import Profile

class Message(models.Model):
    sender = models.ForeignKey(Profile, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Profile, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField(max_length=2000)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} - {self.timestamp}"
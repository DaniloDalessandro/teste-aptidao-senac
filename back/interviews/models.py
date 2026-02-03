import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone


class Chat(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False)
    title = models.CharField(max_length=100, editable=False, verbose_name='Título')
    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE, related_name="chats", null=True, blank=True)
    completed = models.BooleanField(default=False)
    feedback = models.TextField(null=True, blank=True, verbose_name='Feedback do teste')
    recommended_job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommended_chats",
        verbose_name='Curso recomendado'
    )
    candidate_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nome do candidato')

    # Campos de auditoria
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chats_created',
        verbose_name='Criado por'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chats_updated',
        verbose_name='Atualizado por'
    )

    class Meta:
        verbose_name = 'Entrevista'
        verbose_name_plural = 'Entrevistas'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['job', 'completed']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()

            if self.job:
                # Entrevista para curso específico
                self.title = f"Chat {self.job.title} - {self.uuid}"
                super().save(*args, **kwargs)
                initial_prompt = settings.INITIAL_PROMPT_TEMPLATE
                initial_prompt = initial_prompt.replace("{job_title}", self.job.title)
                initial_prompt = initial_prompt.replace("{job_requirements}", self.job.requirements)
                initial_prompt = initial_prompt.replace("{job_responsibilities}", self.job.responsibilities)
                Message.objects.create(chat=self, role="system", content=initial_prompt)
            else:
                # Teste de aptidão geral
                self.title = f"Teste de Aptidão - {self.uuid}"
                super().save(*args, **kwargs)
                initial_prompt = self._get_default_aptitude_prompt()
                Message.objects.create(chat=self, role="system", content=initial_prompt)
                # Cria mensagem inicial de saudação do assistente
                greeting = self._get_initial_greeting()
                Message.objects.create(chat=self, role="assistant", content=greeting)
        else:
            super().save(*args, **kwargs)

    def _get_initial_greeting(self):
        """Gera saudação inicial personalizada."""
        name = self.candidate_name or "candidato"
        return f"""Olá, {name}! 👋

Sou a Ada, orientadora vocacional do SENAC. É um prazer conhecê-lo(a)!

Vou fazer uma breve entrevista para identificar seu perfil e indicar o curso de tecnologia mais adequado para você. São apenas algumas perguntas rápidas sobre seus interesses e experiências.

Vamos começar? Me conte um pouco sobre você: o que você gosta de fazer no dia a dia e quais atividades mais te interessam?"""

    def _get_default_aptitude_prompt(self):
        """Prompt padrão para teste de aptidão geral."""
        from jobs.models import Job
        jobs = Job.objects.all()
        courses_list = "\n".join([f"- {job.title} ({job.get_level_display()}): {job.description[:100]}..." for job in jobs])

        return f"""Você é um orientador vocacional especializado em tecnologia do SENAC.
Seu objetivo é descobrir o perfil do candidato através de uma conversa natural e indicar qual curso de tecnologia é mais adequado para ele.

CURSOS DISPONÍVEIS:
{courses_list}

INSTRUÇÕES:
1. Faça perguntas sobre experiências, interesses, habilidades e objetivos profissionais
2. Explore o que a pessoa gosta de fazer, como resolve problemas, se prefere trabalhar sozinha ou em equipe
3. Pergunte sobre familiaridade com tecnologia e computadores
4. Faça NO MÁXIMO 5 perguntas antes de dar o feedback
5. Seja amigável, use linguagem acessível
6. Ao final, indique o curso mais adequado e explique o porquê

Comece se apresentando brevemente e faça a primeira pergunta para conhecer o candidato."""


class Message(models.Model):
    ROLE_CHOICES = (
        ("system", "Sistema"),
        ("user", "Candidato"),
        ("assistant", "Ada")
    )

    chat = models.ForeignKey("interviews.Chat", on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=9, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role} - {self.chat.title}"

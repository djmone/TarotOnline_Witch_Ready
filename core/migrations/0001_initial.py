
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='GlobalSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('singleton', models.BooleanField(default=True, editable=False)),
                ('free_uses_default', models.IntegerField(default=2)),
                ('reversed_enabled', models.BooleanField(default=True)),
                ('reversed_prob', models.FloatField(default=0.5)),
                ('disclaimer_ru', models.TextField(blank=True, default='Только для развлечения.')),
                ('disclaimer_en', models.TextField(blank=True, default='For entertainment purposes only.')),
                ('ollama_base_url', models.CharField(default='http://localhost:11434', max_length=200)),
                ('llm_model', models.CharField(default='qwen2.5:14b', max_length=100)),
                ('llm_temperature', models.FloatField(default=0.6)),
                ('llm_max_tokens', models.IntegerField(default=1200)),
            ],
        ),
    ]

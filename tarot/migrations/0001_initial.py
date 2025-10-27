
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name='Deck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('back_image', models.ImageField(blank=True, null=True, upload_to='cards/images/')),
                ('theme_class', models.CharField(default='theme-witch', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SpreadPreset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('mode', models.CharField(choices=[('single', 'Single person'), ('couple', 'Two persons'), ('choice', 'Choice (3)'), ('yesno', 'Yes/No')], max_length=10)),
                ('cards_count', models.IntegerField()),
                ('price_credits', models.IntegerField(default=0)),
                ('allow_extra_questions', models.BooleanField(default=False)),
                ('positions_json', models.JSONField(default=list)),
            ],
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=40)),
                ('arcana', models.CharField(choices=[('major', 'Major'), ('minor', 'Minor')], max_length=10)),
                ('suit', models.CharField(blank=True, max_length=20)),
                ('rank', models.CharField(blank=True, max_length=10)),
                ('name_ru', models.CharField(max_length=100)),
                ('name_en', models.CharField(max_length=100)),
                ('img_upright', models.ImageField(blank=True, null=True, upload_to='cards/images/')),
                ('img_reversed', models.ImageField(blank=True, null=True, upload_to='cards/images/')),
                ('deck', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tarot.deck')),
            ],
            options={'unique_together': {('deck', 'code')}},
        ),
        migrations.CreateModel(
            name='SpreadSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('seed', models.CharField(max_length=64)),
                ('seed_hash', models.CharField(max_length=64)),
                ('reversed_enabled', models.BooleanField(default=True)),
                ('reversed_prob', models.FloatField(default=0.5)),
                ('reveal_mode', models.CharField(choices=[('step', 'Per-card'), ('all', 'All at once')], default='all', max_length=10)),
                ('p1_name', models.CharField(max_length=80)),
                ('p1_dob', models.DateField(blank=True, null=True)),
                ('p2_name', models.CharField(blank=True, max_length=80)),
                ('p2_dob', models.DateField(blank=True, null=True)),
                ('extra_questions', models.TextField(blank=True)),
                ('cards_json', models.JSONField(default=list)),
                ('committed', models.BooleanField(default=False)),
                ('deck', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tarot.deck')),
                ('preset', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tarot.spreadpreset')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SpreadReading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(max_length=100)),
                ('prompt_used', models.TextField()),
                ('temperature', models.FloatField(default=0.6)),
                ('tokens', models.IntegerField(default=0)),
                ('response_text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='reading', to='tarot.spreadsession')),
            ],
        ),
    ]

# Generated by Django 5.2.1 on 2025-05-23 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceDirection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Service Direction Name')),
                ('types', models.JSONField(default=list, verbose_name='Service Type IDs')),
                ('questions_answers', models.JSONField(default=list, verbose_name='Questions and Answers')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Service Direction',
                'verbose_name_plural': 'Service Directions',
            },
        ),
    ]

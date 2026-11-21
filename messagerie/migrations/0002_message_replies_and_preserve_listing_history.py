import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('messagerie', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='annonce',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='messages',
                to='annonces.annonce',
            ),
        ),
        migrations.AddField(
            model_name='message',
            name='reponse_a',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='reponses',
                to='messagerie.message',
            ),
        ),
    ]

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('annonces', '0002_validate_coordinates'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='imageannonce',
            options={
                'ordering': ['-is_principale', 'ordre', 'id'],
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
            },
        ),
    ]

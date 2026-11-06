import django.db.models.deletion
import wagtail.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_remove_reseausocial_logo_and_more'),
        migrations.swappable_dependency(settings.WAGTAIL_PAGE_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='footer',
            old_name='nom_entreprise',
            new_name='texte',
        ),
        migrations.AlterField(
            model_name='footer',
            name='texte',
            field=models.TextField(default='JARDIM JIM\nARCHITECTURAL DESIGN', verbose_name='Texte'),
        ),
        migrations.CreateModel(
            name='PageContenu',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.WAGTAIL_PAGE_MODEL)),
                ('contenu', wagtail.fields.RichTextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='Dataset', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('name', models.CharField(max_length=160)),
            ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ('record_count', models.PositiveIntegerField(default=0)),
            ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datasets', to=settings.AUTH_USER_MODEL)),
        ], options={'ordering': ['-uploaded_at']}),
        migrations.CreateModel(name='Sale', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('order_date', models.DateField()),
            ('customer', models.CharField(max_length=150)),
            ('product', models.CharField(max_length=150)),
            ('country', models.CharField(max_length=80)),
            ('quantity', models.PositiveIntegerField()),
            ('unit_price', models.DecimalField(decimal_places=2, max_digits=14)),
            ('revenue', models.DecimalField(decimal_places=2, max_digits=18)),
            ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='intelligence.dataset')),
        ]),
        migrations.AddIndex(model_name='sale', index=models.Index(fields=['dataset','order_date'],name='sale_dataset_date_idx')),
    ]

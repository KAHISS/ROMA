from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sale",
            name="card_fee_percentage",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=5,
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                verbose_name="Taxa da maquininha (%)",
            ),
        ),
    ]

from django.db import models

class Product(models.Model):
    barcode = models.CharField(max_length=100, unique=True, verbose_name="Código de Barras")
    description = models.CharField(max_length=255, verbose_name="Descrição")
    brand = models.CharField(max_length=100, blank=True, null=True, verbose_name="Marca")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    quantity = models.IntegerField(default=0, verbose_name="Quantidade")
    min_quantity = models.IntegerField(default=5, verbose_name="Quantidade Mínima")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    @property
    def status_label(self):
        if self.quantity <= 0:
            return "Esgotado"
        elif self.quantity <= self.min_quantity:
            return "Baixo"
        return "Em estoque"

    @property
    def status_css(self):
        if self.quantity <= 0:
            return "bg-black text-white dark:bg-white dark:text-black"
        elif self.quantity <= self.min_quantity:
            return "bg-gray-100 text-gray-900 dark:bg-neutral-800 dark:text-neutral-100"
        return "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

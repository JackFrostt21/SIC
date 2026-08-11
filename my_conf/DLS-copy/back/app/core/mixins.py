# TODO: добавить миксины для логирования

from django.db import models
class OrderableMixin(models.Model):
    """
    Миксин для упорядочиваемых моделей
    Добавляет поле order и методы для управления порядком элементов
    """
    order = models.PositiveSmallIntegerField("Order", default=0)

    class Meta:
        abstract = True
        ordering = ['order']

    @classmethod
    def reorder(cls, items_order: list):
        """
        Обновляет порядок элементов на основе переданного списка ID
        
        Args:
            items_order: Список ID элементов в новом порядке
        """
        for index, item_id in enumerate(items_order):
            cls.objects.filter(id=item_id).update(order=index)
            
    def move_up(self):
        """Перемещает элемент на одну позицию вверх"""
        prev_item = self.__class__.objects.filter(
            order__lt=self.order
        ).order_by('-order').first()
        
        if prev_item:
            self_order = self.order
            self.order = prev_item.order
            prev_item.order = self_order
            self.save(update_fields=['order'])
            prev_item.save(update_fields=['order'])
            
    def move_down(self):
        """Перемещает элемент на одну позицию вниз"""
        next_item = self.__class__.objects.filter(
            order__gt=self.order
        ).order_by('order').first()
        
        if next_item:
            self_order = self.order
            self.order = next_item.order
            next_item.order = self_order
            self.save(update_fields=['order'])
            next_item.save(update_fields=['order'])
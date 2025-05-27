# app/core/async_utils.py
from typing import TypeVar, Type, Generic, Any, Optional, List, Dict, Callable
from asgiref.sync import sync_to_async
from django.db import models, transaction
from django.db.models import QuerySet, Model

T = TypeVar('T', bound=models.Model)

class AsyncRepository(Generic[T]):
    """
    Базовый асинхронный репозиторий с базовыми операциями для работы с моделью Django.
    Обеспечивает единую точку доступа к ORM и оптимизирует использование sync_to_async.
    """
    model_class: Type[T]
    
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """Получить объект по ID"""
        return await sync_to_async(self._get_by_id)(id)
    
    def _get_by_id(self, id: int) -> Optional[T]:
        try:
            return self.model_class.objects.get(id=id)
        except self.model_class.DoesNotExist:
            return None
    
    async def get_by_filter(self, **kwargs) -> Optional[T]:
        """Получить объект по фильтру"""
        return await sync_to_async(self._get_by_filter)(**kwargs)
    
    def _get_by_filter(self, **kwargs) -> Optional[T]:
        try:
            return self.model_class.objects.get(**kwargs)
        except self.model_class.DoesNotExist:
            return None
    
    async def filter(self, **kwargs) -> List[T]:
        """Получить список объектов по фильтру"""
        return await sync_to_async(list)(self._filter(**kwargs))
    
    def _filter(self, **kwargs) -> QuerySet:
        return self.model_class.objects.filter(**kwargs)
    
    async def create(self, **kwargs) -> T:
        """Создать новый объект"""
        return await sync_to_async(self._create)(**kwargs)
    
    def _create(self, **kwargs) -> T:
        return self.model_class.objects.create(**kwargs)
    
    async def update(self, instance: T, **kwargs) -> T:
        """Обновить объект"""
        return await sync_to_async(self._update)(instance, **kwargs)
    
    def _update(self, instance: T, **kwargs) -> T:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save(update_fields=list(kwargs.keys()))
        return instance
    
    async def delete(self, instance: T) -> None:
        """Удалить объект"""
        await sync_to_async(self._delete)(instance)
    
    def _delete(self, instance: T) -> None:
        instance.delete()


class AsyncUnitOfWork:
    """
    Менеджер транзакций для асинхронного кода.
    Позволяет выполнять несколько операций с базой данных в рамках одной транзакции.
    """
    
    @classmethod
    async def execute(cls, func: Callable, *args, **kwargs) -> Any:
        """
        Выполняет функцию внутри транзакции.
        
        :param func: Функция, которую нужно выполнить в транзакции
        :param args: Аргументы функции
        :param kwargs: Именованные аргументы функции
        :return: Результат выполнения функции
        """
        @sync_to_async
        def _execute_in_transaction():
            with transaction.atomic():
                # Вызываем функцию синхронно в рамках транзакции
                return func(*args, **kwargs)
        
        return await _execute_in_transaction()
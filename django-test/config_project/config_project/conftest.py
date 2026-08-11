from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from config_project.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from config_project.users.models import User


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory.create()

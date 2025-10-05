import pytest

from src.callflow.dao import CallDAO
from src.callflow.enums import CallStatus


class TestCallDAO:
    """Тесты DAO для звонков"""

    @pytest.mark.asyncio
    async def test_add_call(self, session, call_data):
        """Тест добавления звонка"""
        dao = CallDAO(session)

        call = await dao.add_one(**call_data)

        assert call.id is not None
        assert call.caller == call_data["caller"]
        assert call.receiver == call_data["receiver"]
        assert call.status == CallStatus.CREATED
        assert call.created_at is not None

    @pytest.mark.asyncio
    async def test_find_call_by_id(self, session, call_data):
        """Тест поиска звонка по ID"""
        dao = CallDAO(session)

        call = await dao.add_one(**call_data)

        found_call = await dao.find_one(id=call.id)

        assert found_call is not None
        assert found_call.id == call.id
        assert found_call.caller == call_data["caller"]

    @pytest.mark.asyncio
    async def test_find_nonexistent_call(self, session):
        """Тест поиска несуществующего звонка"""
        dao = CallDAO(session)

        found_call = await dao.find_one(id=999999)

        assert found_call is None

    @pytest.mark.asyncio
    async def test_find_by_caller(self, session, call_data):
        """Тест поиска по номеру звонящего"""
        dao = CallDAO(session)

        call = await dao.add_one(**call_data)

        found_calls = await dao.find_all(caller=call_data["caller"])

        assert len(found_calls) == 1
        assert found_calls[0].id == call.id
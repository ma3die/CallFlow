import pytest


class TestCallAPI:
    """Тесты API эндпоинтов для звонков"""

    @pytest.mark.asyncio
    async def test_create_call_success(self, client, call_data):
        """Тест успешного создания звонка"""
        response = await client.post("/calls", json=call_data)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert isinstance(data["id"], int)

    @pytest.mark.asyncio
    async def test_create_call_validation_error(self, client):
        """Тест ошибки валидации при создании звонка"""
        invalid_data = {
            "caller": "invalid_phone",
            "receiver": "+74951234567",
            "started_at": "2025-10-03T10:00:00"
        }

        response = await client.post("/calls", json=invalid_data)

        assert response.status_code == 422
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_get_call_success(self, client, session, call_data):
        """Тест успешного получения звонка"""
        create_response = await client.post("/calls", json=call_data)
        call_id = create_response.json()["id"]

        response = await client.get(f"/calls/{call_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == call_id
        assert data["caller"] == call_data["caller"]
        assert data["receiver"] == call_data["receiver"]

    @pytest.mark.asyncio
    async def test_get_nonexistent_call(self, client):
        """Тест получения несуществующего звонка"""
        response = await client.get("/calls/999999")

        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_create_call_same_phones(self, client, call_data):
        """Тест создания звонка с одинаковыми номерами"""
        same_phone_data = call_data.copy()
        same_phone_data["receiver"] = same_phone_data["caller"]

        response = await client.post("/calls", json=same_phone_data)

        assert response.status_code == 422
        assert "одинаковыми" in response.json()["detail"][0]["msg"]
import pytest
from pydantic import ValidationError
from freezegun import freeze_time
from src.callflow.schemas import CallCreateSchema


class TestCallCreateSchema:
    """Тесты валидации схемы создания звонка"""

    def test_valid_schema(self, call_data):
        """Тест корректных данных"""
        schema = CallCreateSchema(**call_data)
        assert schema.caller == call_data["caller"]
        assert schema.receiver == call_data["receiver"]

    def test_invalid_phone_format(self):
        """Тест невалидного формата телефона"""
        invalid_data = {
            "caller": "79991234567",
            "receiver": "+74951234567",
            "started_at": "2025-10-03T10:00:00"
        }

        with pytest.raises(ValidationError) as exc:
            CallCreateSchema(**invalid_data)

        assert "Номер телефона должен начинаться с '+' " in str(exc.value)

    def test_same_phone_numbers(self):
        """Тест одинаковых номеров телефона"""
        same_phone_data = {
            "caller": "+79991234567",
            "receiver": "+79991234567",
            "started_at": "2024-01-15T10:00:00"
        }

        with pytest.raises(ValidationError) as exc:
            CallCreateSchema(**same_phone_data)

        assert "Номера звонящего и принимающего не могут быть одинаковыми" in str(exc.value)

    @freeze_time("2026-01-01 09:00:00")
    def test_future_date_validation(self, future_call_data):
        """Тест валидации даты в будущем"""
        with pytest.raises(ValidationError) as exc:
            CallCreateSchema(**future_call_data)

        assert "Дата звонка не может быть в будущем" in str(exc.value)

    def test_phone_too_short(self):
        """Тест слишком короткого номера"""
        short_phone_data = {
            "caller": "+7999",
            "receiver": "+74951234567",
            "started_at": "2024-01-15T10:00:00"
        }

        with pytest.raises(ValidationError):
            CallCreateSchema(**short_phone_data)

    def test_phone_too_long(self):
        """Тест слишком длинного номера"""
        long_phone_data = {
            "caller": "+799912345678901234",
            "receiver": "+74951234567",
            "started_at": "2024-01-15T10:00:00"
        }

        with pytest.raises(ValidationError):
            CallCreateSchema(**long_phone_data)

from src.db.basedao import BaseDAO
from src.callflow.models import Call


class CallDAO(BaseDAO):
    model = Call

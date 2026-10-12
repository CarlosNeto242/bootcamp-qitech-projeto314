from tests.utils.object_generator import CANTEEN_ACCOUNT_KEY


class PayloadGenerator:
    @staticmethod
    def create_transfer_payload(
        origin_account_key: str = None,
        destination_account_key: str = None,
        value: int = None,
    ) -> dict:
        if destination_account_key is None:
            destination_account_key = CANTEEN_ACCOUNT_KEY

        if value is None:
            value = 1000

        payload = {
            "origin_account_key": origin_account_key,
            "destination_account_key": destination_account_key,
            "value": value,
        }
        return payload

    @staticmethod
    def create_deposit_payload(
        account_key: str = None,
        value: int = None,
    ) -> dict:
        if value is None:
            value = 1000

        payload = {
            "account_key": account_key,
            "value": value,
        }
        return payload
from exceptions import InvalidCurrenciesException


async def validate_currencies(client, currencies):
    list_currencies = client.latest()['data'].keys()
    if not {currencies[0], currencies[-1]}.issubset(list_currencies):
        raise InvalidCurrenciesException

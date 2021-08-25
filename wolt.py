import asyncio
import typing
import pprint
import itertools
import functools
import sys
import aiohttp
import datetime
import plotly.express as px

LIMIT = 500
ORDER_DETAILS_URL = 'https://restaurant-api.wolt.com/v2/order_details/'
AUTHORIZATION_KEY = 'Bearer eyJ0eXAiOiJ4LnVzZXIrand0IiwiYWxnIjoiRVMyNTYiLCJraWQiOiJjM2RhZTA0MmZiNjkxMWViYjIyZGUyN2NkNjFmZTAzNSJ9.eyJhdWQiOlsiY291cmllcmNsaWVudCIsIndvbHRhdXRoIiwicmVzdGF1cmFudC1hcGkiXSwiaXNzIjoid29sdGF1dGgiLCJqdGkiOiJlYjUxNTFmMDAyODExMWVjYjBkNTllYWE3MzRiZDk5OCIsInVzZXIiOnsiaWQiOiI1ZGQ0M2IyZTYzOTVkNGI3OTgwMDU1YWQiLCJuYW1lIjp7ImZpcnN0X25hbWUiOiJnaWwiLCJsYXN0X25hbWUiOiJjb2hlbiJ9LCJlbWFpbCI6ImdpbGdyZWVubGVhZkBnbWFpbC5jb20iLCJyb2xlcyI6WyJ1c2VyIl0sImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaG9uZV9udW1iZXJfdmVyaWZpZWQiOnRydWUsImNvdW50cnkiOiJJU1IiLCJsYW5ndWFnZSI6ImVuIiwicHJvZmlsZV9waWN0dXJlIjp7InVybCI6Imh0dHBzOi8vY3JlZGl0b3Jub3RtZWRpYS5zMy5hbWF6b25hd3MuY29tLzA0Yjc5YzU3MDgxZDVkMjNkYjMxNDAyMjMwMTg4NjQyYzY2OWE1OTQ3YmFlNzBmNjJlNWEyYTcxMzU2ZTBhZWJlOTkzYWU3NTZiOGE2YjM0OTJhMmQ5ZGJjM2Y4MDUzZmJmY2M0ZTcyYzFiMWQxNjlmZTQzMTE1NDAyMDY3MGFlIn0sInBlcm1pc3Npb25zIjpbXSwicGhvbmVfbnVtYmVyIjoiKzk3MjUwMzk3OTYwNyJ9LCJwYXlsb2FkIjoiQzk2K2FLUTdIVTlORkV6alA1V2JHbExjSGIyY3NZNm8wb1lIdHZ3N2YzdWNsZ3pGT1dUem9Bdk94Z2s5K3pSM0psQ1d3ZE51dGlham9Yd1ZqVCt4d1BNRWlSTTlMdE5BU3dYK3J6MW85ekdHdmplaW1UTCtkS3oyUVRxZUVXY2VseTJFOXBwS0V4Mld3ZkNobUdxRExvMHFwYnRNTTZvWVkyS3J6YVJiYnpnSFViT0JYQXpLT1ZLWUo5eUlDNWppYUxacXZTN3BNNGVVZ3NNL0pYRXZzT05VbHJaMFlucmE1bDVxVzhJQW1jaWtvUGJMVXlzQVpoWjg5TTB5NWwyQjhYdjdWK2ZiWWVHeExJV2VVanRKbDZYamtJTC80UnVCMkxqakV2bHppR3RYdUlORDViZXExUT09IiwiaWF0IjoxNjI5NTUxNzU2LCJleHAiOjE2Mjk1NTM1NTYsImFtciI6W119.5yUqwlw5MrmuTGgzsIvKltjSdikds6pP_bPNPyaMvhpo_A02_-C8goNs1bFPa_5J-DIEOnk50IkbwiZvy-0ozg'


HEADERS = {
    'authorization': AUTHORIZATION_KEY,
}
PARAMS = dict(
    limit=LIMIT,
    skip=0,
)

class Order:
    def __init__(self, order: typing.Dict):
        self._order = order

    @functools.cached_property
    def date(self) -> datetime.date:
        dt = datetime.datetime.utcfromtimestamp(self._order['delivery_time']['$date'] / 1000)
        return datetime.date(year=dt.year, month=dt.month, day=1)

    @functools.cached_property
    def price_share(self) -> int:
        if self._order.get('group') is not None:
            price_share = self._order['total_price_share']
        else:
            price_share = self._order['subtotal']
        return price_share / 100

        print(item)
        return getattr(self._order, item)

def sum_orders(orders):
    return int(sum([order.price_share for order in orders]))

def plot_monthly(orders):
    orders.sort(key=lambda order: order.date)

    data = []
    for k, g in itertools.groupby(orders, key=lambda order: order.date):
        data.append(dict(
            date=k,
            total=sum_orders(g))
        )
    fig = px.bar(data, x='date', y='total')
    fig.show()

async def main():
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(ORDER_DETAILS_URL, params=PARAMS) as response:
            orders = await response.json()
            orders = [order for order in orders if 'rejection_reason' not in order]
            orders = [Order(order) for order in orders]
            # for order in orders:
            #     if get_price_share(order) > 100:
            #         try:
            #             print(get_price_share(order))
            #             # pprint.pprint(order)
            #             print(len(order['items']))
            #             print(sum([item['count'] for item in order['items']]))
            #         except:
            #             pprint.pprint(order)
            #             return

            plot_monthly(orders)
            print(sum_orders(orders), len(orders))
            


if __name__ == '__main__':
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
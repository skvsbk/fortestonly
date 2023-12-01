import json

from utils import JsonWrapper
from typing import Any

def format_order_or_task_id(data_id: Any):
    if data_id is None:
        return ''
    if type(data_id) == int:
        return str(data_id)
    if type(data_id) in (str, dict, list):
        return JsonWrapper(data_id).text
    return ''


if __name__ == '__main__':
    json_order_id = { "order": {
        "id": 31639971
      }, }

    json_task_id = {"task": {
        "id": 0,
        "state": "error"
      }}
    order_id = JsonWrapper(json_order_id).get('$.order.id')
    print(type(order_id), order_id, type(format_order_or_task_id(order_id)), format_order_or_task_id(order_id))
    # print(type(format_order_or_task_id(None)), format_order_or_task_id(None), bool(format_order_or_task_id(None)))
    # print(type(format_order_or_task_id(1)), format_order_or_task_id(1), bool(format_order_or_task_id(1)))
    # print(type(format_order_or_task_id('1')), format_order_or_task_id('1'), bool(format_order_or_task_id('1')))
    # print(type(format_order_or_task_id({'id': 1})), format_order_or_task_id({'id': 1}), bool(format_order_or_task_id({'id': 1})))
    # print(type(format_order_or_task_id([1, 2, 3])), format_order_or_task_id([1, 2, 3]), bool(format_order_or_task_id([1, 2, 3])))
    # print(type(format_order_or_task_id(1.1)), format_order_or_task_id(1.1), bool(format_order_or_task_id(1.1)))


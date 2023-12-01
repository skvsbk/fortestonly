# -*- coding: utf-8 -*-
import datetime
import decimal
import enum
import json
from functools import wraps
from logging import Logger
from typing import Union, Optional, NamedTuple, Any, Dict, Callable, Tuple

import humanize
import jsonschema
import re

import jsonpath_ng.ext as ng
from lxml import etree
from lxml.etree import XMLSyntaxError

# import config
# from conterra.dac import SQLRequest, ApiType, now_iso, DacDatasource, dac_call

LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo


class JSONEncoderExt(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, datetime.datetime):
            if o.microsecond == 0:
                return datetime.datetime.isoformat(o, timespec="seconds")
            else:
                return datetime.datetime.isoformat(o)
        return super().default(o)


def validate_json_by_schema(json_, schema):
    jsonschema.validate(instance=json_, schema=schema)


def to_json(d: dict):
    return json.dumps(d, cls=JSONEncoderExt, ensure_ascii=False, indent=2)


class JsonWrapper:
    """
    Вспомогательный класс для удобства работы с JSON сообщениями
    """

    def __init__(self, text, schema_=None):

        if isinstance(text, str):
            self.text = text
            self.json = json.loads(text, strict=False)
        elif isinstance(text, dict):
            self.text = json.dumps(text, cls=JSONEncoderExt, ensure_ascii=False, indent=2)
            self.json = text
        elif isinstance(text, list):
            self.text = json.dumps(text, cls=JSONEncoderExt, ensure_ascii=False, indent=2)
            self.json = text
        else:
            self.text = str(text)
            self.json = json.loads(text, strict=False)

        if schema_:
            self.validate(schema_)

    def __getitem__(self, path):
        return self.get(path)

    def __str__(self):
        return self.text

    def __repr__(self):
        return super().__repr__()

    def _match(self, path):
        exp = ng.parse(path)
        m = exp.find(self.json)
        return m

    def get(self, path, default=None):
        res = list(map(lambda x: x.value, self._match(path)))
        if not res:
            return default
        elif len(res) > 0:
            return res[0]

    def find(self, path):
        return list(map(lambda x: JsonWrapper(x.value), self._match(path)))

    def find_first(self, path):
        m = self.find(path)
        return m[0] if m else None

    def validate(self, schema):
        validate_json_by_schema(self.json, schema=schema)

    def has(self, path):
        return len(self._match(path)) > 0

#
# class XmlWrapper:
#     """
#     Вспомогательный класс для удобства работы с XML сообщениями
#     """
#
#     def __init__(self, input_, remove_namespaces=True, encoding="utf-8"):
#
#         if isinstance(input_, str):
#             self.text = input_
#             if remove_namespaces:
#                 # убираем все определения дефолтных наймспейсов и все namespace префиксы,
#                 # чтоб не мешали для простых xpath-тов, не учитывающих namespace
#                 r1 = re.compile(r'xmlns=".*?"', re.MULTILINE)
#                 xml_ = r1.sub("", self.text)
#                 r2 = re.compile(r'<(/?)\w+:([\s\S]+?)>', re.MULTILINE)
#                 xml_ = r2.sub(r"<\1\2>", xml_)
#             else:
#                 xml_ = input_
#             parser = etree.XMLParser()
#             try:
#                 self.bytes = xml_.encode(encoding=encoding)
#                 self.xml = etree.fromstring(self.bytes, parser=parser)
#             except Exception as e:
#                 self.bytes = xml_.encode(encoding="utf-8")
#                 self.xml = etree.fromstring(self.bytes, parser=parser)
#         else:
#             self.xml = input_
#             self.bytes = etree.tostring(element_or_tree=self.xml, encoding=encoding)
#             self.text = f"{self.bytes}"
#
#     def __getitem__(self, path):
#         return self.get(path)
#
#     def __str__(self):
#         if self.text:
#             return self.text
#         elif self.xml:
#             return etree.tostring(self.xml)
#
#     def __repr__(self):
#         return super().__repr__()
#
#     def _match(self, path):
#         return self.xml.xpath(path)
#
#     def get(self, path, default=None):
#         r = self._match(path)
#         if not r:
#             return default
#         if isinstance(r, list):
#             if len(r) > 0:
#                 if isinstance(r[0], str):
#                     return r[0]
#                 return r[0].text
#             else:
#                 return default
#         else:
#             return r
#
#     def find(self, path):
#         r = self.xml.xpath(path)
#         if not r:
#             return []
#         if isinstance(r, list):
#             return list(map(lambda v: XmlWrapper(v), r))
#         else:
#             return [r]
#
#     def find_first(self, path):
#         m = self.find(path)
#         return m[0] if m else None
#
#     def has(self, path) -> bool:
#         return len(self._match(path)) > 0
#
#
# #todo: move to bus module
# class BusLogDirection(enum.Enum):
#     income = "in"
#     outcome = "out"
#
#
# #todo: move to bus module
# class BusLogStatus(enum.Enum):
#     init = 'init'
#     success = 'success'
#     error = 'error'
#     sended = 'sended'
#     skipped = 'skipped'
#     reply_error = 'reply_error'
#
#
# #todo: move to bus module
# def bus_log_add(ds: DacDatasource, msg: Union[JsonWrapper, str, dict], is_income=True,
#                 status: BusLogStatus = BusLogStatus.init,
#                 description: Optional[str] = None, log: Logger = None,
#                 routing_key: Optional[str] = None, order_id: Optional[str] = None,
#                 shipment_id: Optional[str] = None, task_id: Optional[int] = None,
#                 sequence_no: Optional[int] = None, equipment_no: Optional[str] = None,
#                 ):
#     if isinstance(msg, JsonWrapper):
#         msg_text = msg.text
#     elif isinstance(msg, str):
#         msg_text = msg
#         msg = JsonWrapper(msg_text)
#     elif isinstance(msg, dict):
#         msg = JsonWrapper(msg)
#         msg_text = msg.text
#     else:
#         raise ValueError(f"Неизвестный тип сообщения ({type(msg)}) для логирование bus_log")
#
#     req = SQLRequest(ds, 'm_itrans_bus_log_add', {
#         "system_from": msg.get('$.system_from'),
#         "system_to": msg.get('$.system_to'),
#         "object": msg.get('$.object'),
#         "action": msg.get('$.action'),
#         "reference_id": msg.get('$.reference_id'),
#         "message_id": msg.get('$.message_id'),
#         "priority": msg.get('$.priority'),
#         "api_version": msg.get('$.api_version'),
#         "datetime_created": (msg.get('$.datetime_created'), ApiType.timestamptz),
#         "msg_date": (now_iso(), ApiType.timestamptz),
#         "who_added": config.constants.APPLICATION_ID_STR,
#         "direction": BusLogDirection.income.value if is_income else BusLogDirection.outcome.value,
#         "status": status.value,
#         "description": description,
#         "msg_data": msg_text,
#
#         "routing_key": routing_key,
#         "order_id": order_id,
#         "shipment_id": shipment_id,
#         "task_id": task_id,
#         "sequence_no": sequence_no,
#         "equipment_no": equipment_no,
#     }, use_transaction=False).execute()
#     """
#     param_no|name            |description                                          |type       |direction|required|dimensions|
#     --------+----------------+-----------------------------------------------------+-----------+---------+--------+----------+
#            1|this_bus_log_id |ID лога шины                                         |bigint     |out      |true    |         0|
#            2|system_from     |Имя сервиса отправителя                              |text       |in       |false   |         0|
#            3|system_to       |Имя сервиса получателя                               |text       |in       |false   |         0|
#            4|object          |Сущность, к которой относится сообщение              |text       |in       |false   |         0|
#            5|action          |Действие, которое нужно сделать с сущностью          |text       |in       |false   |         0|
#            6|reference_id    |Сквозной ID                                          |text       |in       |false   |         0|
#            7|message_id      |Уникальный идентификатор сообщения                   |text       |in       |false   |         0|
#            8|priority        |Приоритет сообщений                                  |bigint     |in       |false   |         0|
#            9|api_version     |Версия формата сообщений                             |text       |in       |false   |         0|
#           10|datetime_created|Дата и время отправки сообщения в шину               |timestamptz|in       |false   |         0|
#
#           11|msg_date        |Дата сообщения                                       |timestamptz|in       |false   |         0|
#           12|who_added       |Кто сформировал                                      |text       |in       |false   |         0|
#           13|direction       |Направление, допустимо in - Входящее, out - Исходящее|text       |in       |false   |         0|
#           14|status          |Статус                                               |text       |in       |false   |         0|
#           15|description     |Описание                                             |text       |in       |false   |         0|
#           16|msg_data        |Сообщение                                            |jsonb      |in       |false   |         0|
#     """
#     this_bus_log_id = req.get_out_param('this_bus_log_id')
#     if log:
#         log.info(f"### this_bus_log_id = {this_bus_log_id}")
#     return this_bus_log_id
#
#
# #todo: move to bus module
# def bus_log_upd(ds, this_bus_log_id, status: BusLogStatus, log: Logger, description=None):
#     try:
#         dac_call(logger=log, ds=ds, method='m_itrans_bus_log_update', params={
#             "this_bus_log_id": this_bus_log_id,
#             "status": status.value,
#             "description": description
#         })
#         """
#         param_no|name           |description |type  |direction|required|dimensions|
#         --------+---------------+------------+------+---------+--------+----------+
#                1|this_bus_log_id|ID лога шины|bigint|in       |true    |         0|
#                2|status         |Статус      |text  |in       |false   |         0|
#                3|description    |Описание    |text  |in       |false   |         0|
#         """
#     except Exception as e:
#         log.exception(f"Ошибка сохранения статуса приема сообщения в логе: {str(e)}\n"
#                       f"this_bus_log_id={this_bus_log_id}\n"
#                       f"status={status}\n"
#                       f"description={description}\n")
#
#
# #todo: move to bus module
# def bus_log_add_reply(ds: DacDatasource, reply: dict, log: Logger):
#     try:
#         msg = JsonWrapper(reply or {})  # little hack to avoid every call null check
#         bus_log_add(ds=ds, msg=msg, is_income=False, status=BusLogStatus.sended, log=log)
#     except Exception as e:
#         log.exception(f"Ошибка сохранения ответного сообщения в логе: {str(e)}\n reply={reply}, type={type(reply)}")
#
#
# def now_with_timezone() -> datetime.datetime:
#     return datetime.datetime.now(tz=LOCAL_TIMEZONE)
#
#
# def normalize_json(msg: str, normalize_dict: Dict[str, str]):
#
#     for field in normalize_dict:
#         msg = msg.replace(field, normalize_dict[field])
#     return msg
#
#
# #todo: move exception adapter
# def make_error_text(e: Exception) -> str:
#     try:
#         return f"Error {type(e).__module__}.{type(e).__name__}: {str(e)}"
#     except:
#         return repr(e)
#
#
# class ProcessStatus(NamedTuple):
#     reply: Any
#     status: BusLogStatus
#
#
# def time_it(log: Logger):
#     def decor(func: Callable):
#         """
#     use for time checking for methods:
#     ```
#     @conterra(...)
#     @time_it
#     def foo(...) -> ...:
#         ...
#     ```
#         """
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             log.info(f"start %s", func.__name__)
#             start = datetime.datetime.now()
#             result = func(*args, **kwargs)
#             finish = datetime.datetime.now()
#             log.info("finish %s elapsed=%s", func.__name__, humanize.precisedelta(finish - start))
#
#             return result
#         return wrapper
#     return decor
#
#
# class MessageManage(JsonWrapper):
#     DEFAULT_FIELDS = {
#         "event_code": "$.params.event.status",
#         "order_id": "$.params.order.id",
#         "cont_no": "$.params.equipment.container.number",
#         "car_no": "$.params.equipment.wagon.number",
#         "equipment_sequence": "$.params.equipment.sequence",
#         "actual": "$.params.event.actual",
#         "event_date": "$.params.event.datetime",
#     }
#
#     def __init__(self, input_: str, routing_key: Optional[str] = None):
#         super().__init__(input_)
#         # получаем тип сообщения
#         self.msg_type = self.get("$.object") + '.' + self.get("$.action")
#         self.msg_id = self.get("$.message_id")
#
#         self._msg_data = input_
#         self._routing_key = routing_key
#
#         for field in self.DEFAULT_FIELDS:
#             # создаем атрибуты заголовка сообщения
#             self.get_param_from_template(field, self.DEFAULT_FIELDS[field])
#
#     def get_param_from_template(self, field: str, field_value: Union[Tuple[str, str], str, None]):
#         if isinstance(field_value, str) and field_value.startswith("$."):
#             # сохраняем значение полученное из jsonа при помощи jsonpath ("$.**")
#             self.__setattr__(f"_{field}", self.get(field_value))
#             return
#
#         elif isinstance(field_value, tuple):
#             for variant in field_value:
#                 # сохраняем значение, если оно не нулевое, иначе проверяем следующее
#                 param = self.get(variant)
#                 if param:
#                     self.__setattr__(f"_{field}", param)
#                     return
#             else:
#                 self.__setattr__(f"_{field}", None)
#                 return
#
#         elif isinstance(field_value, list):
#             # params = []
#             # for variant in field_value:
#             #     param = self.get(variant)
#             #     if param:
#             #         params.append(param)
#             params = [param for variant in field_value if (param := self.get(variant))]
#             self.__setattr__(f"_{field}", "/".join(params))
#             return
#
#         # сохраняем значение, указанное в карте
#         self.__setattr__(f"_{field}", field_value)
#         return
#
#     def _getparam(self, name: str):
#         try:
#             return self.__getattribute__(name)
#         except AttributeError:
#             return None
#
#
# class ErrorCode(enum.Enum):
#     MSG_INVALID_FORMAT = 1
#     OBJECT_UNAVAILABLE = 2
#     QUERY_UNAVAILABLE = 3
#     MSG_INVALID_DATA = 4
#     WRONG_VALUE = 5
#     NOT_FOUND = 6
#     PROCESSING_FAULT = 7
#     NO_PERMISSION = 8
#     TOO_HIGH = 9
#     TOO_SMALL = 10
#
#
# class ServiceLogStatus(enum.Enum):
#     success = "success"
#     error = "error"
#     info = "info"
#
#
# class ServiceOperationCode(enum.Enum):
#     order_create = "executor_order_create"
#     order_receive = "executor_order_receive"
#     shipment_create = "executor_shipment_create"
#     order_planning = "executor_order_planning"
#     order_delete = "executor_order_delete"
#     order_restart = "executor_order_restart"
#     order_state = "executor_order_state"
#     shipment_state = "executor_shipment_state"
#
#
# def service_log_add(ds: DacDatasource, operation_code: ServiceOperationCode,
#                     status: ServiceLogStatus = ServiceLogStatus.info,
#                     description: Optional[str] = None, log: Logger = None,
#                     user_name: Optional[str] = None, order_id: Optional[str] = None,
#                     shipment_id: Optional[str] = None, container_no: Optional[str] = None,
#                     wagon_no: Optional[str] = None, dst_order_id: Optional[str] = None,
#                     comment: Optional[str] = None,
#                     ):
#
#     req = SQLRequest(ds, 'm_itrans_c2_service_log_add', {
#         "operation_code": operation_code.value,
#         "description": description,
#         "user_name": user_name,
#         "status": status.value,
#         "order_id": order_id,
#         "shipment_id": shipment_id,
#         "container_no": container_no,
#         "wagon_no": wagon_no,
#         "dst_order_id": dst_order_id,
#         "comment": comment
#
#     }, use_transaction=False).execute()
#     """
#     param_no|name            |description                                          |type       |direction|required|dimensions|
#     --------+----------------+-----------------------------------------------------+-----------+---------+--------+----------+
#            1|this_service_log_id |ID лога                                              |bigint     |out      |true    |         0|
#            2|operation_code      |Шифр сервисной операции                              |text       |in       |false   |         0|
#            3|description         |Описание операции                                    |text       |in       |false   |         0|
#            4|user_name           |Пользователь                                         |text       |in       |false   |         0|
#            5|status              |Статус                                               |text       |in       |false   |         0|
#            6|order_id            |Номер заказа                                         |text       |in       |false   |         0|
#            7|shipment_id         |GUID поставки                                        |text       |in       |false   |         0|
#            8|container_no        |Номер контейнера                                     |text       |in       |false   |         0|
#            9|wagon_no            |Номер вагона                                         |text       |in       |false   |         0|
#           10|dst_order_id        |Номер заказа назначения (при переносе оборудования)  |text       |in       |false   |         0|
#           11|comment             |Служебное сообщение                                  |text       |in       |false   |         0|
#           """
#     # this_bus_log_id = req.get_out_param('this_service_log_id')
#     # if log:
#     #     log.info(f"### this_service_log_id = {this_bus_log_id}")
#     # return this_bus_log_id

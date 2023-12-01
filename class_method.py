import enum

class MessageType(enum.Enum):
    task_execute = 'task.execute'
    task_status_update = 'task.status_update'
    task_decline = 'task.decline'
    task_decline_check = "task.decline_check"

    railway_instruction_reply = 'railway_instruction.print_reply'
    eta_rail_predict_reply = 'eta_rail.predict_reply'

    # @staticmethod
    # def get(json_: Union[str, JsonWrapper]):
    #     if isinstance(json_, JsonWrapper):
    #         msg = json_
    #     elif isinstance(json_, str):
    #         msg = JsonWrapper(json_)
    #     else:
    #         raise TypeError(f"Неподдерживаемый тип параметра 'json_': {type(json_)}")
    #     msg_type = msg.get('$.object') + '.' + msg.get('$.action')
    #     for known_type in MessageType:
    #         if known_type.value == msg_type:
    #             return known_type
    #     raise ValueError(f"Неизвестный тип сообщения '{msg_type}'")

    @property
    def is_task(self):
        return 'task' in self.value


if __name__ == "__main__":
    sss = MessageType()

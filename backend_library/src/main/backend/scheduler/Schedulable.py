class Schedulable:
    @property
    def user_id(self) -> int:
        return -1

    @property
    def task_id(self) -> int:
        return -1

    def do_work(self) -> None:
        return None
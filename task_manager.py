from enum import Enum
import pandas as pd
from params import params

queue_number = int(
    input('Выберете дисциплину обслуживания:\n1 - FIFO\n2 - LIFO\n3 - SJF\n'))

if queue_number == 1:
    QUEUE = 'FIFO'
elif queue_number == 2:
    QUEUE = 'LIFO'
elif queue_number == 3:
    QUEUE = 'SJF'
else:
    print('Выбрана неверная дисциплина обслуживания')
    assert ()


class Status(Enum):
    created = 0
    in_queue = 1
    inputed = 2
    ended = 3
    released = 4


class Resources():
    def __init__(self):
        self.info_line = ''
        self.ram = 16
        self.hdd = 12
        self.multitask = 0
        self.t = 0

    def clock(self):
        self.t += 1

    def add_task(self):
        self.multitask += 1

    def release(self, taken_ram, taken_hdd):
        self.ram += taken_ram
        self.hdd += taken_hdd
        self.multitask -= 1

    def seize(self, required_ram, required_hdd):
        self.ram -= required_ram
        self.hdd -= required_hdd

    def add_to_info_line(self, text: str):
        self.info_line += text

    def print(self):
        print(f'\n Время: {self.t:3d}. \n{self.info_line}\n Свободные ресурсы: ОП = {
              self.ram:2d}/16, ВП = {self.hdd:2d}/12, Km = {self.multitask:2d}\n-------------')


class Queue():
    def __init__(self):
        self.waiting_list = {}
        self.id = 1

    def add(self, task):
        self.waiting_list[self.id] = task
        self.id += 1

    def print(self):
        print([t.id for t in self.waiting_list.values()])


class Task():
    def __init__(self, task_id=0, required_ram=0, required_hdd=0, receipt_time=0, input_time=0, execution_time=0):
        self.id = task_id
        self.required_ram = required_ram
        self.required_hdd = required_hdd
        self.receipt_time = receipt_time
        self.input_time = input_time
        self.execution_time = execution_time
        self.time_to_end = execution_time
        self.status = None
        self.time_to_exec = None
        self.when_started = 0
        self.when_inputed = 0
        self.when_ended = 0
        self.time_in_queue = 0

    def execute(self, resources: Resources):
        self.time_to_end -= 1 / resources.multitask
        if self.time_to_end <= 1e-6:
            self.when_ended = resources.t
            self.status = Status.ended
            resources.release(self.required_ram, self.required_hdd)
            return Status.ended
        return None

    def input(self, resources: Resources):
        if self.time_to_exec is None:
            self.when_started = resources.t
            self.time_to_exec = resources.t + self.input_time
        if self.time_to_exec == resources.t:
            self.when_inputed = resources.t
            self.status = Status.inputed
            resources.add_task()
            self.execute(resources)
            return Status.inputed
        if self.status is Status.created:
            return None
        self.status = Status.created
        return Status.created

    def create(self, resources: Resources, queue: Queue):
        if self.receipt_time == resources.t:
            resources.add_to_info_line(f'Задание {self.id} ({self.required_ram}, {
                                       self.required_hdd}) поступило в систему. ')
            if self.required_ram > resources.ram or self.required_hdd > resources.hdd:
                queue.add(self)
                self.status = Status.in_queue
                return Status.in_queue
            resources.seize(self.required_ram, self.required_hdd)
            return self.input(resources)

        return None

    def check(self, resources: Resources, queue: Queue):
        if self.status is Status.inputed:
            return self.execute(resources)
        if self.status is Status.created:
            return self.input(resources)
        if self.status is None:
            return self.create(resources, queue)
        return None

    def search_for_released(self, resources: Resources):
        if self.status is Status.released:
            resources.add_to_info_line(f'Теперь свободных ресурсов достаточно для задания {
                                       self.id} ({self.required_ram}, {self.required_hdd}). ')
            return self.input(resources)
        return None


def draw_by_fifo(waiting_list: {}, resources: Resources):
    tasks_to_draw = {}

    for task_id, task in waiting_list.items():
        if task.required_ram <= resources.ram and task.required_hdd <= resources.hdd:
            tasks_to_draw[task_id] = task

    if len(tasks_to_draw) > 0:
        task = tasks_to_draw.get(min(tasks_to_draw))
        resources.seize(task.required_ram, task.required_hdd)
        task.status = Status.released
        waiting_list.pop(min(tasks_to_draw))
        draw_by_fifo(waiting_list, resources)


def draw_by_lifo(waiting_list: {}, resources: Resources):
    tasks_to_draw = {}

    for task_id, task in waiting_list.items():
        if task.required_ram <= resources.ram[1] and task.required_hdd <= resources.hdd[1]:
            tasks_to_draw[task_id] = task

    if len(tasks_to_draw) > 0:
        task = tasks_to_draw.get(max(tasks_to_draw))
        resources.seize(task.required_ram, task.required_hdd)
        task.status = Status.released
        waiting_list.pop(max(tasks_to_draw))
        draw_by_lifo(waiting_list, resources)


def draw_by_sjf(waiting_list: {}, resources: Resources):
    tasks_to_draw = {}

    for task_id, task in waiting_list.items():
        if task.required_ram <= resources.ram and task.required_hdd <= resources.hdd:
            tasks_to_draw[task_id] = task

    if len(tasks_to_draw) > 0:
        task = min(tasks_to_draw.values(),
                   key=lambda unit: unit.execution_time)
        resources.seize(task.required_ram, task.required_hdd)
        task.status = Status.released
        for key, value in dict(waiting_list).items():
            if value is task:
                waiting_list.pop(key)
        draw_by_sjf(waiting_list, resources)


def print_task_info(ret, task: Task, resources: Resources):
    ended = 0
    if ret is Status.created:
        resources.add_to_info_line(f'Назначается на ввод задание {task.id} ({
                                   task.required_ram}, {task.required_hdd}).\n')
    elif ret is Status.in_queue:
        resources.add_to_info_line(
            'Свободных ресурсов не хватает, и задание ожидает в очереди.\n')
    elif ret is Status.inputed:
        resources.add_to_info_line(f'Назначается на выполнение задание {
                                   task.id} ({task.required_ram}, {task.required_hdd}).\n')
    elif ret is Status.ended:
        resources.add_to_info_line(f'Завершено выполнение задания {task.id} ({
                                   task.required_ram}, {task.required_hdd}). Ресурсы, занятые им, освобождены.\n')
        ended += 1
    return ended


def main():
    ended = 0
    resources = Resources()
    tasks = [Task(*x) for x in params]
    queue = Queue()
    time = []
    info = []
    ram = []
    hdd = []
    multitask = []
    print(f'Тип очереди: {QUEUE}')

    while ended < 10:
        print_data = False
        for task in tasks:
            ret = task.check(resources, queue)
            if ret is not None:
                print_data = True
            ended += print_task_info(ret, task, resources)

        if len(queue.waiting_list) > 0:
            for key, task in queue.waiting_list.items():
                task.time_in_queue += 1
            if QUEUE == 'LIFO':
                draw_by_lifo(queue.waiting_list, resources)
            elif QUEUE == 'FIFO':
                draw_by_fifo(queue.waiting_list, resources)
            elif QUEUE == 'SJF':
                draw_by_sjf(queue.waiting_list, resources)

            for task in tasks:
                ret = task.search_for_released(resources)
                if ret is not None:
                    print_data = True
                print_task_info(ret, task, resources)

        if print_data is True:
            resources.info_line = resources.info_line[:-1]

            time.append(resources.t)
            info.append(resources.info_line)
            ram.append(resources.ram)
            hdd.append(resources.hdd)
            multitask.append(resources.multitask)
            resources.info_line = ''

        resources.clock()
        print_data = False
    excel = pd.DataFrame({'Время': time, 'Событие': info,
                         'ОП': ram, 'ВП': hdd, 'Km': multitask})
    excel.to_excel('./' + QUEUE + '.xlsx')

    actions = pd.DataFrame({'Событие': info})
    actions.to_excel('./' + QUEUE + '_actions.xlsx')
    t1 = []
    t2 = []
    t3 = []
    t4 = []
    for task in tasks:
        t1.append(task.receipt_time)
        t2.append(task.when_started)
        t3.append(task.when_inputed)
        t4.append(task.when_ended)

    exel2 = pd.DataFrame({'1': t1, '2': t2, '3': t3, '4': t4})
    exel2.to_excel('./' + QUEUE + '_2.xlsx')


if __name__ == "__main__":
    main()

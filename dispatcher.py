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
        self.info_line = ['', '']
        self.ram = [0, 16]
        self.hdd = [0, 12]
        self.multitask = [0, 0]
        self.t = [0, 0]
        self.executing_tasks = [[], []]

    def clock(self):
        self.t[1] += 1

    def add_task(self):
        self.multitask[1] += 1

    def release(self, taken_ram, taken_hdd):
        self.ram[1] += taken_ram
        self.hdd[1] += taken_hdd
        self.multitask[1] -= 1

    def seize(self, required_ram, required_hdd):
        self.ram[1] -= required_ram
        self.hdd[1] -= required_hdd

    def add_to_info_line(self, text: str):
        self.info_line[1] += text

    def set_back(self):
        self.info_line[0] = self.info_line[1]
        self.info_line[1] = ''
        self.ram[0] = self.ram[1]
        self.hdd[0] = self.hdd[1]
        self.multitask[0] = self.multitask[1]
        self.t[0] = self.t[1]
        self.executing_tasks[0] = self.executing_tasks[1]


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

    def execute(self, resources: Resources):
        self.time_to_end -= 1 / resources.multitask[1]
        if self.time_to_end <= 1e-6:
            self.when_ended = resources.t[1]
            self.status = Status.ended
            resources.release(self.required_ram, self.required_hdd)
            return Status.ended
        return None

    def input(self, resources: Resources):
        if self.time_to_exec is None:
            self.when_started = resources.t[1]
            self.time_to_exec = resources.t[1] + self.input_time
        if self.time_to_exec == resources.t[1]:
            self.when_inputed = resources.t[1]
            self.status = Status.inputed
            resources.add_task()
            self.execute(resources)
            return Status.inputed
        if self.status is Status.created:
            return None
        self.status = Status.created
        return Status.created

    def create(self, resources: Resources, queue: Queue):
        if self.receipt_time == resources.t[1]:
            if self.required_ram > resources.ram[1] or self.required_hdd > resources.hdd[1]:
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
            return self.input(resources)
        return None


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


def draw_by_fifo(waiting_list: {}, resources: Resources):
    tasks_to_draw = {}

    for task_id, task in waiting_list.items():
        if task.required_ram <= resources.ram[1] and task.required_hdd <= resources.hdd[1]:
            tasks_to_draw[task_id] = task

    if len(tasks_to_draw) > 0:
        task = tasks_to_draw.get(min(tasks_to_draw))
        resources.seize(task.required_ram, task.required_hdd)
        task.status = Status.released
        waiting_list.pop(min(tasks_to_draw))
        draw_by_fifo(waiting_list, resources)


def draw_by_sjf(waiting_list: {}, resources: Resources):
    tasks_to_draw = {}

    for task_id, task in waiting_list.items():
        if task.required_ram <= resources.ram[1] and task.required_hdd <= resources.hdd[1]:
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
    if ret is Status.inputed:
        resources.add_to_info_line(f'Поступление задания {
                                   task.id} на выполнение.\n')
    elif ret is Status.ended:
        resources.add_to_info_line(
            f'Завершено выполнение задания {task.id}.\n')
        ended += 1
    return ended


def main():
    ended = 0
    resources = Resources()
    queue = Queue()
    time = []
    info = []
    multitask = []
    max_time = 0

    tasks = [Task(*x) for x in params]
    resources.executing_tasks[0].append(tasks[0])
    print(f'Тип очереди: {QUEUE}')

    while ended < 10:
        print_data = False
        resources.executing_tasks[1] = []
        for task in tasks:
            ret = task.check(resources, queue)
            if (ret is Status.inputed) or (ret is Status.ended):
                print_data = True
            ended += print_task_info(ret, task, resources)

        if len(queue.waiting_list) > 0:
            if QUEUE == 'LIFO':
                draw_by_lifo(queue.waiting_list, resources)
            elif QUEUE == 'FIFO':
                draw_by_fifo(queue.waiting_list, resources)
            elif QUEUE == 'SJF':
                draw_by_sjf(queue.waiting_list, resources)

            for task in tasks:
                ret = task.search_for_released(resources)
                print_task_info(ret, task, resources)

        for task in tasks:
            if task.status is Status.inputed:
                resources.executing_tasks[1].append(task)

        if print_data is True:
            if len(resources.executing_tasks[0]) > 1:
                msg_1 = 'Заданиям'
                msg_2 = ' по '
            else:
                msg_1 = 'Заданию'
                msg_2 = ' '
            if resources.multitask[0] > 0:
                expression = f'выделяется {msg_2}({resources.t[1]}-{resources.t[0]}) / {resources.multitask[0]} ≈ {
                    ((resources.t[1]-resources.t[0])/resources.multitask[0]):.2f} сек'
                tasks_str = ", ".join([str(t.id)
                                      for t in resources.executing_tasks[0]])
                resources.info_line[0] += f'{msg_1} {tasks_str} {expression}'
            if resources.t[0] != 0:
                time.append(f'{resources.t[0]} - {resources.t[1]}')
                if resources.multitask[0] == 3:
                    max_time += (resources.t[1]-resources.t[0])
                info.append(resources.info_line[0])
                multitask.append(resources.multitask[0])
            resources.set_back()

        resources.clock()
        print_data = False

    time.append(f'{resources.t[0]}')
    info.append(resources.info_line[0])
    multitask.append(resources.multitask[0])
    excel = pd.DataFrame({'Время': time, 'Событие': info, 'Km': multitask})
    excel.to_excel('./dis_' + QUEUE + '.xlsx')


if __name__ == "__main__":
    main()

from enum import Enum
from prettytable import PrettyTable

QUEUE = 'SJF'
QUEUE = 'LIFO'

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


def draw_by_sjf(waiting_list: {}, resources: Resources):
    tasks_to_draw = {}

    for task_id, task in waiting_list.items():
        if task.required_ram <= resources.ram[1] and task.required_hdd <= resources.hdd[1]:
            tasks_to_draw[task_id] = task

    if len(tasks_to_draw) > 0:
        task = min(tasks_to_draw.values(), key=lambda unit: unit.execution_time)
        resources.seize(task.required_ram, task.required_hdd)
        task.status = Status.released
        for key, value in dict(waiting_list).items():
            if value is task:
                waiting_list.pop(key)
        draw_by_sjf(waiting_list, resources)

def print_task_info(ret, task: Task, resources: Resources):
    ended = 0
    if ret is Status.inputed:
        resources.add_to_info_line(f'Задание {task.id} назначается на выполнение.\n')
    elif ret is Status.ended:
        resources.add_to_info_line(f'Задание {task.id} выполнено.\n')
        ended +=1
    return ended

def main():
    ended = 0
    resources = Resources()
    task_1 = Task(1, 3,	2,	4,	10,	60)
    task_2 = Task(2, 5,	0,	9,	0,	30)
    task_3 = Task(3, 1,	3,	18,	15,	20)
    task_4 = Task(4, 2,	3,	20,	15,	20)
    task_5 = Task(5, 6,	2,	20,	10,	60)
    task_6 = Task(6, 3,	2,	24,	10, 60)
    task_7 = Task(7, 4,	1,	27,	5, 10)
    task_8 = Task(8, 4,	1,	30,	5, 10)
    task_9 = Task(9, 4,	1,	33,	5, 10)
    task_10 = Task(10, 6, 2, 33, 10, 60)
    queue = Queue()
    table = PrettyTable(['Время', 'Событие', 'ОП', 'ВП', 'Km'])

    tasks = [task_1, task_2, task_3, task_4, task_5,
             task_6, task_7, task_8, task_9, task_10]
    resources.executing_tasks[0].append(task_1)
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
            else:
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
                expression = f'выделится {msg_2}({resources.t[1]}-{resources.t[0]})/{resources.multitask[0]} ≈ {((resources.t[1]-resources.t[0])/resources.multitask[0]):.2f} сек'
                resources.info_line[0] += f'{msg_1} {[t.id for t in resources.executing_tasks[0]]} {expression}'
            if resources.t[0] != 0:
                # print(f'{((resources.t[1]-resources.t[0])/resources.multitask[0]):.2f}')
                # print(f'{resources.t[0]} - {resources.t[1]}')
                table.add_row([f'-----------\n{resources.t[0]:3d} - {resources.t[1]:3d}', f'{'-'*64}\n{resources.info_line[0]}', f'----\n{resources.ram[0]:2d}', f'----\n{resources.hdd[0]:2d}', f'----\n{resources.multitask[0]:2d}'])
            resources.set_back()
            # print(resources.ram)

        resources.clock()
        print_data = False
    # print(f'{resources.t[0]}')


    table.add_row([f'-----------\n{resources.t[0]:3d}', f'{'-'*64}\n{resources.info_line[0]}', f'----\n{resources.ram[0]:2d}', f'----\n{resources.hdd[0]:2d}', f'----\n{resources.multitask[0]:2d}'])
    # for task in tasks:
    #     print(task.when_inputed)
    # print()
    # for task in tasks:
    #     print(task.when_ended)
    print(table)


if __name__ == "__main__":
    main()

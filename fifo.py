from enum import Enum


class Status(Enum):
    created = 0
    in_queue = 1
    inputed = 2
    ended = 3
    released = 4

class Resources():
    def __init__(self):
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

    def print(self):
        print(f'\nВремя: {self.t:3d}. Свободные ресурсы: ОП = {self.ram:2d}/16, ВП = {self.hdd:2d}/12, Km = {self.multitask:2d}')

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

    def execute(self, resources: Resources):
        self.time_to_end -= 1 / resources.multitask
        if self.time_to_end <= 1e-6:
            self.status = Status.ended
            resources.release(self.required_ram, self.required_hdd)
            return Status.ended
        return None


    def input(self, resources: Resources):
        if self.time_to_exec is None:
            self.time_to_exec = resources.t + self.input_time
        if self.time_to_exec == resources.t:
            # if self.id == 10:
                # print('hello========================================================')
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
            print(f'Задание {self.id} постуило.', end=' ')
            if self.required_ram > resources.ram or self.required_hdd > resources.hdd:
                queue.add(self)
                # queue.print()
                # print('длина', len(queue.waiting_list)) #------------
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
            print(f'Задание {self.id} выходит из очереди.', end=' ')
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
        # print('до', len(waiting_list)) #----------
        waiting_list.pop(min(tasks_to_draw))
        # print('после', len(waiting_list)) #------------
        draw_by_fifo(waiting_list, resources)

def print_task_info(ret, task: Task):
    ended = 0
    if ret is Status.created:
        print(f'Задание {task.id} назначается на ввод.')
    elif ret is Status.in_queue:
        print(f'Задание {task.id} помещается в очередь из-за нехватки ресурсов.')
    # elif ret is Status.released:
    #     print(f'Задание {task.id} выходит из очереди и назначается на ввод.')
    elif ret is Status.inputed:
        # if task.input_time == 0:
        #     print(f'Задание {task.id} постуило.', end=' ')
        print(f'Задание {task.id} назначается на выполнение.')
    elif ret is Status.ended:
        print(f'Задание {task.id} выполнено.')
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

    tasks = [task_1, task_2, task_3, task_4, task_5,
             task_6, task_7, task_8, task_9, task_10]

    while ended < 10:
        print_data = False
        for task in tasks:
            ret = task.check(resources, queue)
            if ret is not None:
                print_data = True
            ended += print_task_info(ret, task)

        if len(queue.waiting_list) > 0:
            draw_by_fifo(queue.waiting_list, resources)

            for task in tasks:
                ret = task.search_for_released(resources)
                if ret is not None:
                    print_data = True
                print_task_info(ret, task)

        if print_data is True:
            resources.print()
            # print(f'Выполнено: {ended}, очередь: {queue.print()}')
            # print('101010', task_10.time_to_exec)
            # print('101010', task_10.time_to_end)
            # print('101010', task_10.status)
            print('------------------------------')

        resources.clock()
        print_data = False
        # if resources.t == 269:
        #     print('NOW')

    # a = Status.created
    # print(f'{a is Status.created}')


if __name__ == "__main__":
    main()

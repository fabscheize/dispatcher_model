from enum import Enum

RAM = 16
HDD = 12
Km = 0


class Status(Enum):
    created = 0
    in_queue = 1
    inputed = 2
    ended = 3
    released = 4

class Resourses():
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
        self.ram += required_ram
        self.hdd += required_hdd


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

    def execute(self):
        global Km
        global RAM
        global HDD
        self.time_to_end -= 1 / Km
        if self.time_to_end <= 1e-6:
            self.status = Status.ended
            RAM += self.required_ram
            HDD += self.required_hdd
            Km -= 1
            return Status.ended
        return None


    def input(self, current_time):
        global Km
        if self.time_to_exec is None:
            self.time_to_exec = current_time + self.input_time
        if self.time_to_exec is current_time:
            self.status = Status.inputed
            Km += 1
            self.execute()
            return Status.inputed
        if self.status is Status.created:
            return None
        self.status = Status.created
        return Status.created

    def create(self, current_time):
        global RAM
        global HDD
        if self.receipt_time is current_time:
            if self.required_ram > RAM or self.required_hdd > HDD:
                self.status = Status.in_queue
                return Status.in_queue
            else:
                RAM -= self.required_ram
                HDD -= self.required_hdd
                return self.input(current_time)
        else:
            return None

    def check(self, current_time):
        if self.status is Status.ended:
            return None
        if self.status is Status.inputed:
            return self.execute()
        if self.status is (Status.created or Status.released):
            return self.input(current_time)
        if self.status is Status.in_queue:
            ...

        return self.create(current_time)


def print_task_info(ret, task: Task):
    ended = 0
    if ret is Status.created:
        print(f'Задание {task.id} постуило. Задание {task.id} назначается на ввод.')
    elif ret is Status.in_queue:
        print(f'Задание {task.id} постуило. Задание {task.id} помещается в очередь из-за нехватки ресурсов.')
    elif ret is Status.released:
        print(f'Задание {task.id} выходит из очереди и назначается на ввод.')
    elif ret is Status.inputed:
        if task.input_time == 0:
            print(f'Задание {task.id} постуило.', end=' ')
        print(f'Задание {task.id} назначено на выполнение.')

    elif ret is Status.ended:
        print(f'Задание {task.id} выполнено.')
        ended +=1
    return ended

def main():
    global Km
    t = 0
    ended = 0
    print_data = False
    # Km = 0
    # ram = 16
    # hdd = 12

    task_1 = Task(1, 3,	2,	4,	10,	60)
    task_2 = Task(2, 5,	0,	9,	0,	30)
    task_3 = Task(3, 1,	3,	18,	15,	20)
    task_4 = Task(4, 2,	3,	20,	15,	20)
    task_5 = Task(5, 6,	2,	20,	10,	60)
    task_6 = Task(6, 3,	2,	24,	10, 60)
    task_7 = Task(7, 4,	1,	27,	5, 10)
    task_8 = Task(8, 4,	1,	30,	5, 10)
    task_9 = Task(9, 4,	1,	33,	5, 10)
    task_10 = Task(10, 6,	2,	33,	10,	60)

    tasks = [task_1, task_2, task_3, task_4, task_5,
             task_6, task_7, task_8, task_9, task_10]

    while ended < 10:
        for task in tasks:
            ret = task.check(t)
            if ret is not None:
                print_data = True
            ended += print_task_info(ret, task)

        if print_data is True:
            print(f'\nВремя: {t}. Свободные ресурсы: ОП = {RAM:2d}/16, ВП = {HDD:2d}/12, Km = {Km:2d}')
            print('------------------------------')
            print_data = False
        t += 1

    # a = Status.created
    # print(f'{a is Status.created}')


if __name__ == "__main__":
    main()

# dispatcher_model
Модель работы диспетчера и планировщика задач операционной системы.

Скрипты "dispatcher.py" и "task_manager" получают входные данные из модуля "params.py" в виде таблицы параметров для 10-ти заданий, послупающих в систему.

Параметры заданий:
  1) порядковый номер;
  2) потребляемая оперативная память;
  3) потребляемый объем внутреннего диска;
  4) момент послупления задания;
  5) время ввода задания в систему;
  6) время выполнения задания.

На основе входных данных скрипты стоят Excel таблицу, в которой указано время события, само событие (поступление, назначение на ввод, окончание выполения заданий), а также показатели ОП, ВУ и количество одновременно выполняемых заданий.

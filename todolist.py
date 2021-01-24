# Write your code here
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///todo.db?check_same_thread=False')
Base = declarative_base()


class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='default_value')
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return self.task


Base.metadata.create_all(engine)


class ToDo:

    def __init__(self):
        self.menu_items = {
            1: "Today's tasks",
            2: "Week's tasks",
            3: "All tasks",
            4: "Missed tasks",
            5: "Add task",
            6: "Delete task",
            0: "Exit"
        }
        self.functions = {
            1: self.show_today_tasks,
            2: self.show_week_tasks,
            3: self.all_tasks,
            4: self.missed_tasks,
            5: self.add_task,
            6: self.delete_task,
            0: self.exit
        }
        self.action_id = None
        self.keep_going = True
        self.session = None
        self.setup_session()

    def setup_session(self):
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def format_menu(self):
        menu_str = [f"{k}) {v}" for k, v in self.menu_items.items()]
        return '\n'.join(menu_str) + '\n'

    def select_action(self):
        selection = input(self.format_menu())
        print('\n')
        self.action_id = int(selection) if selection.isnumeric() else -1

        if self.action_id in range(len(self.functions)):
            self.functions[self.action_id]()
            print('\n')

    def exit(self):
        print('Bye!')
        self.keep_going = False

    def show_date_tasks(self, _date, is_today=False):
        day_name = _date.strftime('%A')
        if is_today:
            day_name = 'Today'

        message = f"{day_name} {_date.day} {_date.strftime('%b')}:"

        rows = self.session.query(Table) \
            .filter(Table.deadline == _date).all()

        self.print_tasks(rows, message=message, include_date=False)

    def print_tasks(self, tasks, message,
                    message_if_empty="Nothing to do!",
                    include_date=True):
        print(message)
        if len(tasks) == 0:
            print(message_if_empty)
        else:
            for i, row in enumerate(tasks):
                if include_date:
                    print(f"{i + 1}. {row.task}. {row.deadline.day} {row.deadline.strftime('%b')}")
                else:
                    print(f"{i + 1}. {row.task}.")

    def show_today_tasks(self):
        self.show_date_tasks(datetime.today().date(), True)

    def show_week_tasks(self):
        today = datetime.today().date()
        for day_shift in range(7):
            new_day = today + timedelta(day_shift)
            self.show_date_tasks(new_day)
            print('\n')

    def all_tasks(self):
        rows = self.session.query(Table).order_by(Table.deadline).all()
        self.print_tasks(rows, "All tasks:")

    def add_task(self):
        new_task = input('Enter task' + '\n')
        task_deadline = input('Enter deadline' + '\n')
        new_row = Table(task=new_task,
                        deadline=datetime.strptime(task_deadline, "%Y-%m-%d"))
        self.session.add(new_row)
        self.session.commit()
        print('The task has been added!')

    def missed_tasks(self):
        _date = datetime.today().date()
        rows = self.session.query(Table) \
            .filter(Table.deadline < _date).order_by(Table.deadline).all()
        self.print_tasks(rows, "Missed tasks:", message_if_empty="Nothing is missed!")

    def delete_task(self):
        rows = self.session.query(Table).order_by(Table.deadline).all()
        message = "Choose the number of the task you want to delete:"
        self.print_tasks(rows, message)
        index_str = input("")
        if index_str.isnumeric():
            task_index = int(index_str)
        else:
            task_index = len(rows) + 1
        if task_index <= len(rows):
            self.session.delete(rows[task_index - 1])
            self.session.commit()
            print('The task has been deleted!')


myToDo = ToDo()

while myToDo.keep_going:
    myToDo.select_action()

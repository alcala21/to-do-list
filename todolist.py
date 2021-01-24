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
            4: "Add task",
            0: "Exit"
        }
        self.functions = {
            1: self.show_today_tasks,
            2: self.show_week_tasks,
            3: self.all_tasks,
            4: self.add_task,
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

        if self.action_id in range(5):
            self.functions[self.action_id]()

    def exit(self):
        print('Bye!')
        self.keep_going = False

    def show_date_tasks(self, _date, is_today=False):
        day_name = _date.strftime('%A')
        if is_today:
            day_name = 'Today'

        rows = self.session.query(Table) \
            .filter(Table.deadline == _date).all()

        print(f"{day_name} {_date.day} {_date.strftime('%b')}")

        if len(rows) == 0:
            print('Nothing to do!')
        else:
            for i, row in enumerate(rows):
                print(f"{i + 1}. {row}")
        print('\n')

    def show_today_tasks(self):
        self.show_date_tasks(datetime.today().date(), True)

    def show_week_tasks(self):
        today = datetime.today().date()
        for day_shift in range(7):
            new_day = today + timedelta(day_shift)
            self.show_date_tasks(new_day)

    def all_tasks(self):
        rows = self.session.query(Table).order_by(Table.deadline).all()
        if len(rows) == 0:
            print('Nothing to do!')
        else:
            print('All tasks:')
            for i, row in enumerate(rows):
                print(f"{i + 1}. {row.task}. {row.deadline.day} {row.deadline.strftime('%b')}")
        print('\n')

    def add_task(self):
        new_task = input('Enter task' + '\n')
        task_deadline = input('Enter deadline' + '\n')
        new_row = Table(task=new_task,
                        deadline=datetime.strptime(task_deadline, "%Y-%m-%d"))
        self.session.add(new_row)
        self.session.commit()

        print('The task has been added!', '\n')


myToDo = ToDo()

while myToDo.keep_going:
    myToDo.select_action()

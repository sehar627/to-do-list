from kivymd.app import MDApp
from kivymd.uix.picker import MDDatePicker
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button

import random
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate("todolist/firebase_config.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://to-do-list-a6fe0-default-rtdb.firebaseio.com/'
})


# Dashboard screen
def build_dashboard_screen(sm):
    screen = Screen(name='dashboard')
    layout = FloatLayout()

    # App Title
    title_label = MDLabel(text="[color=00ff00][b]TO-DO LIST APP[/b][/color]", markup=True, font_style='H5',
                          halign="center", size_hint=(1, 0.1), pos_hint={'center_x': 0.5, 'top': 1})
    layout.add_widget(title_label)

    # Date Label
    today = datetime.now()
    date_text = today.strftime("%A, %d %B %Y")
    date_label = Label(text=f"[b]{date_text}[/b]", markup=True,
                       size_hint=(1, 0.05), pos_hint={'center_x': 0.5, 'top': 0.93},
                       color=(1, 1, 0, 1))
    layout.add_widget(date_label)

    # Task Table
    table = GridLayout(cols=4, spacing=5, size_hint_y=None, padding=10)
    table.bind(minimum_height=table.setter('height'))

    scroll = ScrollView(size_hint=(1, 0.65), pos_hint={'x': 0, 'y': 0.2})
    scroll.add_widget(table)
    layout.add_widget(scroll)

    def load_dashboard(*args):
        table.clear_widgets()
        headers = ['OBJECTIVE', 'DEADLINE', 'PRIORITY', 'DONE']
        for header in headers:
            lbl = Label(text=f"[b]{header}[/b]", markup=True, size_hint_y=None, height=40)
            table.add_widget(lbl)

        tasks_ref = db.reference('tasks')
        all_tasks = tasks_ref.get()

        if all_tasks:
            for task_id, task in all_tasks.items():
                done = task.get('done', False)

                def format_text(text):
                    return f"[s]{text}[/s]" if done else text

                obj_lbl = Label(text=format_text(task.get('objective', '-')), markup=True, size_hint_y=None, height=40)
                deadline_lbl = Label(text=format_text(task.get('deadline', '-')), markup=True, size_hint_y=None, height=40)
                priority_lbl = Label(text=format_text(task.get('priority', '-')), markup=True, size_hint_y=None, height=40)

                table.add_widget(obj_lbl)
                table.add_widget(deadline_lbl)
                table.add_widget(priority_lbl)

                checkbox = CheckBox(active=done, size_hint_y=None, height=40)

                def on_checkbox_active(checkbox, value, task_id=task_id):
                    db.reference(f'tasks/{task_id}/done').set(value)
                    load_dashboard()

                checkbox.bind(active=on_checkbox_active)
                table.add_widget(checkbox)

    screen.bind(on_pre_enter=load_dashboard)

    # Add Task Button
    add_btn = MDRaisedButton(text='Add Task',
                             size_hint=(0.3, 0.1),
                             pos_hint={'center_x': 0.5, 'y': 0.05})

    def switch_to_add_task(instance):
        sm.current = 'add_task'

    add_btn.bind(on_press=switch_to_add_task)
    layout.add_widget(add_btn)

    screen.add_widget(layout)
    return screen


# Add Task screen
def build_add_task_screen(sm):
    screen = Screen(name='add_task')
    layout = FloatLayout()

    # Title
    title = MDLabel(text="[color=00ff00][b]ADD NEW TASK[/b][/color]", markup=True, font_style='H5',
                    halign="center", size_hint=(1, 0.1), pos_hint={'center_x': 0.5, 'top': 1})
    layout.add_widget(title)

    # Objective
    obj_label = Label(text="Objective", size_hint=(0.3, 0.08), pos_hint={'x': 0.05, 'top': 0.85})
    layout.add_widget(obj_label)

    obj_input = TextInput(size_hint=(0.6, 0.08), pos_hint={'x': 0.35, 'top': 0.85})
    layout.add_widget(obj_input)

    # Deadline Label + Date Picker Button
    deadline_label = Label(text="Deadline", size_hint=(0.3, 0.08), pos_hint={'x': 0.05, 'top': 0.7})
    layout.add_widget(deadline_label)

    selected_deadline = {'date': ''}

    deadline_btn = MDRaisedButton(
        text="Select Date",
        size_hint=(0.6, 0.08),
        pos_hint={'x': 0.35, 'top': 0.7}
    )
    layout.add_widget(deadline_btn)

    def on_date_selected(instance, value, date_range):
        selected_deadline['date'] = value.strftime('%d-%m-%Y')
        deadline_btn.text = selected_deadline['date']

    deadline_btn.bind(on_press=lambda instance: MDDatePicker(on_save=on_date_selected).open())

    # Priority
    priority_label = Label(text="Priority", size_hint=(0.3, 0.08), pos_hint={'x': 0.05, 'top': 0.55})
    layout.add_widget(priority_label)

    priority_input = Spinner(
        text='Select Priority',
        values=('High', 'Medium', 'Low'),
        size_hint=(0.6, 0.08),
        pos_hint={'x': 0.35, 'top': 0.55}
    )
    layout.add_widget(priority_input)

    # Save Task Button
    add_btn = MDRaisedButton(text="Save Task",
                             size_hint=(0.3, 0.1),
                             pos_hint={'center_x': 0.7, 'y': 0.05})
    layout.add_widget(add_btn)

    # Back Button
    back_btn = MDRaisedButton(text="Back",
                              size_hint=(0.3, 0.1),
                              pos_hint={'x': 0.2, 'y': 0.05})
    layout.add_widget(back_btn)

    def go_back(instance):
        sm.current = 'dashboard'

    back_btn.bind(on_press=go_back)

    def save_task(instance):
        objective = obj_input.text.strip()
        deadline = selected_deadline['date']
        priority = priority_input.text.strip()

        if objective:
            task_data = {
                'objective': objective,
                'deadline': deadline,
                'priority': priority,
                'done': False
            }
            task_id = f"task_{random.randint(1000, 9999)}"
            db.reference(f"tasks/{task_id}").set(task_data)

            # Reset fields
            obj_input.text = ""
            selected_deadline['date'] = ""
            deadline_btn.text = "Select Date"
            priority_input.text = "Select Priority"

            sm.current = 'dashboard'

    add_btn.bind(on_press=save_task)

    return screen


# Build app
def build():
    sm = ScreenManager()
    sm.add_widget(build_dashboard_screen(sm))
    sm.add_widget(build_add_task_screen(sm))
    return sm


# Main app class
class MyApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Dark"
        return build()


if __name__ == "__main__":
    MyApp().run()

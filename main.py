# TK -> OBJECT(TASK) -> SHOW -> CRUD
import tkinter
import json

class EditMenu(tkinter.Toplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.geometry("300x250")
        self.title("editing task")
        self.lbl1 = tkinter.Label(self, text="Name of the task")
        self.lbl2 = tkinter.Label(self, text="Description")
        self.lbl3 = tkinter.Label(self, text="Date")

        self.E_name = tkinter.Entry(self)
        self.E_desc = tkinter.Text(self, wrap="word", height=3, width=100)
        self.E_date = tkinter.Entry(self)
        self.E_confirm_btn = tkinter.Button(self, text="Confirm", command=lambda: callback(self))

        self.lbl1.pack()
        self.E_name.pack()
        self.lbl2.pack()
        self.E_desc.pack()
        self.lbl3.pack()
        self.E_date.pack()
        self.E_confirm_btn.pack()

        self.grab_set()

    def end_life(self):
        data = {
            "Name": self.E_name.get(),
            "Desc": self.E_desc.get("1.0", "end"),
            "Date": self.E_date.get()
        }
        self.destroy()
        return data

class Task(tkinter.Frame):
    def __init__(self, _name, _date, _desc, _importance, _owner):
        super().__init__(_owner.tmui.scrollable_tasks_container, height=120, width=280, bg="green")
        self.name = _name
        self.date = _date
        self.desc = _desc
        self.importance = _importance
        self.owner = _owner
        self._create_ui()

    def _create_ui(self):

        self.U_name = tkinter.LabelFrame(self, text = self.name, width=200, height=100)
        self.U_desc = tkinter.Label(self.U_name, text = self.desc, wraplength=200, justify="center")
        self.Controller = tkinter.Frame(self, bg = "grey", width=80, height=100)
        self.U_edit = tkinter.Button(self.Controller, text="Edit", width=4, height=1, command=self._interrogate_for_edit)
        self.U_I_up = tkinter.Button(self.Controller, text="▲", width=1, height=1, command=self.upper)
        self.U_I_down = tkinter.Button(self.Controller, text="▼", width=1, height=1, command=self.downer)
        self.U_delete = tkinter.Button(self.Controller, text="∅", width=1, height=1, command=lambda: self.owner.delete_task(self))
        self.U_date = tkinter.Label(self, text = self.date)

        self.pack_propagate(False)
        self.U_name.pack_propagate(False)
        self.Controller.pack_propagate(False)

        self.U_name.pack(side="left", fill='y')
        self.U_desc.pack()
        self.U_edit.pack()
        self.U_delete.pack()
        self.U_I_up.pack()
        self.U_I_down.pack()
        self.U_date.pack()

        self.Controller.pack()

    def upper(self):
        self.importance -= 1.5
        self.owner.rebuild()

    def downer(self):
        self.importance += 1.5
        self.owner.rebuild()

    def update(self):
        self.U_name.configure(text=self.name)
        self.U_desc.configure(text=self.desc)
        self.U_date.configure(text=self.date)

    def cb_edit_em(self, askit):
        data = askit.end_life()
        self.name = data["Name"]
        self.date = data["Date"]
        self.desc = data["Desc"]
        self.update()

    def _interrogate_for_edit(self):
        EditMenu(self.owner.root, self.cb_edit_em)

    def pack(self):
        super().pack(pady=10)


class TaskManager:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.resizable(False, False)
        self._tasks = []
        self.tmui = TaskManagerUI(self.root)
        self.tmui.control_menu.add_btn.configure(command=self.interrogate_for_task)
        self.tmui.control_menu.delete_all_btn.configure(command=self.delete_all)

    def create_task(self, _name, _date, _desc, _importance):
        task = Task(_name, _date, _desc, _importance, self)
        self._tasks.append(task)
        task.pack()
        self.rebuild()

    def rebuild(self):
        for task in self._tasks:
            task.pack_forget()
        self._tasks = sorted(self._tasks, key=lambda x: x.importance)
        c = 0
        for task in self._tasks:
            task.importance = c
            task.pack()
            c+=1

    def delete_all(self):
        for task in self._tasks:
            task.destroy()
        self._tasks.clear()
        self.rebuild()

    def delete_task(self, task):
        self._tasks.remove(task)
        task.destroy()
        self.rebuild()

    def create_task_from_em(self, askit):
        data = askit.end_life()
        self.create_task(data["Name"],data["Date"],data["Desc"],999)
        self.rebuild()

    def interrogate_for_task(self):
        EditMenu(self.root, self.create_task_from_em)

    def save_tasks(self, filename="tasks.json"):
        with open(filename, "w", encoding="utf-8") as f:
            tasks = []
            for task in self._tasks:
                part = {"Name": task.name,
                        "Date": task.date,
                        "Desc": task.desc,
                        "Impo": task.importance}
                tasks.append(part)
            json.dump(tasks, f, indent=4)

    def load_tasks(self,filename="tasks.json"):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                simpler_tasks = json.load(f)
                for data in simpler_tasks:
                    self.create_task(data["Name"],data["Date"],data["Desc"],data["Impo"])
                self.rebuild()
        except FileNotFoundError:
            print("NoFile")

class TaskManagerUI(tkinter.Frame):
    def __init__(self, master):
        master.geometry("300x500")
        super().__init__(master)
        self._build_control_menu()
        self._build_scroll_frame()
        self.pack(expand=1, fill="both")

    def _build_control_menu(self):
        self.control_menu = tkinter.Frame(self, bg='grey', height=100, width = 300)
        self.control_menu.add_btn = tkinter.Button(self.control_menu, width = 5, height = 3, text = "Add")
        self.control_menu.delete_all_btn = tkinter.Button(self.control_menu, width = 9, height = 3, text = "delete all")
        self.control_menu.pack(fill="x", side='top')
        self.control_menu.pack_propagate(False)
        self.control_menu.add_btn.pack(side='left', padx=15)
        self.control_menu.delete_all_btn.pack(side='right', padx=15)

    def _build_scroll_frame(self):
        self.cont_for_task_menu = tkinter.Frame(self, height=400, width=300)
        self.tasks_canvas = tkinter.Canvas(self.cont_for_task_menu, height=400, width=280, bg="white")
        self.scrollbar = tkinter.Scrollbar(self.cont_for_task_menu, orient="vertical", command=self.tasks_canvas.yview)
        self.scrollable_tasks_container = tkinter.Frame(self.tasks_canvas, bg="white")
        self.scrollable_tasks_container.bind(
            "<Configure>",
            lambda e: self.tasks_canvas.configure(scrollregion=self.tasks_canvas.bbox("all"))
        )
        self.tasks_canvas.create_window((0, 0), window=self.scrollable_tasks_container, anchor="nw")
        self.tasks_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.tasks_canvas.bind_all("<MouseWheel>", lambda e: self.tasks_canvas.yview_scroll(-e.delta // 120, "units"))
        self.tasks_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.cont_for_task_menu.pack()

if __name__ == '__main__':
    run = TaskManager()
    run.load_tasks()
    run.rebuild()
    run.root.mainloop()
    run.save_tasks()

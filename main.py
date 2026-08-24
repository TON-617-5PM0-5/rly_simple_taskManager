import os
import json
import tkinter
from pathlib import Path
from tkinter import ttk, messagebox

# Set up a dedicated app directory in the user's home/appdata folder
APP_DATA_DIR = Path(os.getenv("LOCALAPPDATA", Path.home())) / "TaskManagerApp"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_SAVE_PATH = APP_DATA_DIR / "tasks.json"


class EditMenu(tkinter.Toplevel):
    def __init__(self, master, callback, name="", date="", desc=""):
        super().__init__(master)
        self.geometry("320x300")
        self.title("Task Details")
        self.resizable(False, False)

        tkinter.Label(self, text="Name of the task").pack(pady=(10, 0))
        self.E_name = tkinter.Entry(self, width=35)
        self.E_name.insert(0, name)
        self.E_name.pack(pady=5)

        tkinter.Label(self, text="Date").pack(pady=(5, 0))
        self.E_date = tkinter.Entry(self, width=35)
        self.E_date.insert(0, date)
        self.E_date.pack(pady=5)

        tkinter.Label(self, text="Description").pack(pady=(5, 0))
        self.E_desc = tkinter.Text(self, wrap="word", height=5, width=30)
        self.E_desc.insert("1.0", desc)
        self.E_desc.pack(pady=5)

        self.E_confirm_btn = tkinter.Button(
            self, text="Confirm", width=15, command=lambda: callback(self)
        )
        self.E_confirm_btn.pack(pady=10)

        self.grab_set()

    def end_life(self):
        data = {
            "Name": self.E_name.get().strip(),
            "Date": self.E_date.get().strip(),
            "Desc": self.E_desc.get("1.0", "end-1c").strip(),
        }
        self.destroy()
        return data


class Task(tkinter.Frame):
    def __init__(self, name, date, desc, importance, folder, owner):
        super().__init__(
            owner.tmui.scrollable_tasks_container,
            height=110,
            bd=1,
            relief="solid",
            bg="#f0f0f0",
        )
        self.name = name
        self.date = date
        self.desc = desc
        self.importance = importance
        self.folder = folder
        self.owner = owner
        self._create_ui()

    def _create_ui(self):
        self.pack_propagate(False)

        self.U_info_frame = tkinter.Frame(self, bg="#f0f0f0")
        self.U_info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.U_name = tkinter.Label(
            self.U_info_frame,
            text=self.name,
            font=("Arial", 10, "bold"),
            anchor="w",
            bg="#f0f0f0",
        )
        self.U_name.pack(fill="x")

        self.U_date = tkinter.Label(
            self.U_info_frame,
            text=self.date,
            font=("Arial", 8, "italic"),
            fg="gray",
            anchor="w",
            bg="#f0f0f0",
        )
        self.U_date.pack(fill="x")

        self.U_desc = tkinter.Label(
            self.U_info_frame,
            text=self.desc,
            wraplength=200,
            justify="left",
            anchor="nw",
            bg="#f0f0f0",
        )
        self.U_desc.pack(fill="both", expand=True, pady=(2, 0))

        self.Controller = tkinter.Frame(self, bg="#d9d9d9", width=60)
        self.Controller.pack(side="right", fill="y")

        self.U_I_up = tkinter.Button(
            self.Controller, text="▲", width=2, command=self.upper
        )
        self.U_I_up.pack(side="top", pady=2)

        self.U_I_down = tkinter.Button(
            self.Controller, text="▼", width=2, command=self.downer
        )
        self.U_I_down.pack(side="top", pady=2)

        self.U_edit = tkinter.Button(
            self.Controller, text="Edit", width=4, command=self._interrogate_for_edit
        )
        self.U_edit.pack(side="top", pady=2)

        self.U_delete = tkinter.Button(
            self.Controller,
            text="✕",
            width=2,
            fg="red",
            command=lambda: self.owner.delete_task(self),
        )
        self.U_delete.pack(side="top", pady=2)

    def upper(self):
        self.owner.move_task(self, -1)

    def downer(self):
        self.owner.move_task(self, 1)

    def update_ui(self):
        self.U_name.configure(text=self.name)
        self.U_desc.configure(text=self.desc)
        self.U_date.configure(text=self.date)

    def cb_edit_em(self, askit):
        data = askit.end_life()
        self.name = data["Name"]
        self.date = data["Date"]
        self.desc = data["Desc"]
        self.update_ui()

    def _interrogate_for_edit(self):
        EditMenu(
            self.owner.root,
            self.cb_edit_em,
            name=self.name,
            date=self.date,
            desc=self.desc,
        )

    def pack(self):
        super().pack(pady=5, padx=5, fill="x")


class TaskManager:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("Task Manager")
        self.root.geometry("500x500")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.folders = ["General"]
        self.current_folder = "General"
        self._tasks = []

        self.tmui = TaskManagerUI(self.root, self)
        self.refresh_folder_list()

    def create_task(self, name, date, desc, importance=None, folder=None):
        if folder is None:
            folder = self.current_folder
        if importance is None:
            importance = len(self._tasks)

        task = Task(name, date, desc, importance, folder, self)
        self._tasks.append(task)
        self.rebuild()

    def move_task(self, task, direction):
        visible_tasks = [t for t in self._tasks if t.folder == self.current_folder]
        if task not in visible_tasks:
            return

        idx = visible_tasks.index(task)
        new_idx = idx + direction

        if 0 <= new_idx < len(visible_tasks):
            g_idx1 = self._tasks.index(visible_tasks[idx])
            g_idx2 = self._tasks.index(visible_tasks[new_idx])
            self._tasks[g_idx1], self._tasks[g_idx2] = (
                self._tasks[g_idx2],
                self._tasks[g_idx1],
            )
            self.rebuild()

    def rebuild(self):
        for task in self._tasks:
            task.pack_forget()

        visible_tasks = [t for t in self._tasks if t.folder == self.current_folder]
        for idx, task in enumerate(visible_tasks):
            task.importance = idx
            task.pack()

    def add_folder(self, folder_name):
        folder_name = folder_name.strip()
        if folder_name and folder_name not in self.folders:
            self.folders.append(folder_name)
            self.refresh_folder_list()

    def delete_folder(self):
        if self.current_folder == "General":
            messagebox.showwarning(
                "Warning", "Cannot delete the default 'General' folder."
            )
            return

        if messagebox.askyesno(
            "Confirm",
            f"Delete folder '{self.current_folder}' and all its tasks?",
        ):
            self._tasks = [
                t for t in self._tasks if t.folder != self.current_folder
            ]
            self.folders.remove(self.current_folder)
            self.current_folder = "General"
            self.refresh_folder_list()

    def refresh_folder_list(self):
        self.tmui.folder_listbox.delete(0, "end")
        for f in self.folders:
            self.tmui.folder_listbox.insert("end", f)

        idx = self.folders.index(self.current_folder)
        self.tmui.folder_listbox.selection_set(idx)
        self.rebuild()

    def select_folder(self, event):
        selection = self.tmui.folder_listbox.curselection()
        if selection:
            self.current_folder = self.folders[selection[0]]
            self.rebuild()

    def delete_all(self):
        self._tasks = [t for t in self._tasks if t.folder != self.current_folder]
        self.rebuild()

    def delete_task(self, task):
        self._tasks.remove(task)
        task.destroy()
        self.rebuild()

    def create_task_from_em(self, askit):
        data = askit.end_life()
        if data["Name"]:
            self.create_task(data["Name"], data["Date"], data["Desc"])

    def interrogate_for_task(self):
        EditMenu(self.root, self.create_task_from_em)

    def save_tasks(self, filepath=DEFAULT_SAVE_PATH):
        data = {
            "folders": self.folders,
            "tasks": [
                {
                    "Name": task.name,
                    "Date": task.date,
                    "Desc": task.desc,
                    "Impo": task.importance,
                    "Folder": task.folder,
                }
                for task in self._tasks
            ],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_tasks(self, filepath=DEFAULT_SAVE_PATH):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)

                if isinstance(content, dict):
                    self.folders = content.get("folders", ["General"])
                    raw_tasks = content.get("tasks", [])
                else:
                    self.folders = ["General"]
                    raw_tasks = content

                raw_tasks.sort(key=lambda x: x.get("Impo", 0))
                for data in raw_tasks:
                    folder = data.get("Folder", "General")
                    if folder not in self.folders:
                        self.folders.append(folder)
                    self.create_task(
                        data["Name"],
                        data["Date"],
                        data["Desc"],
                        data.get("Impo"),
                        folder,
                    )
                self.refresh_folder_list()
        except FileNotFoundError:
            pass

    def on_close(self):
        self.save_tasks()
        self.root.destroy()


class TaskManagerUI(tkinter.Frame):
    def __init__(self, master, manager):
        super().__init__(master)
        self.manager = manager
        self.pack(expand=True, fill="both")

        self._build_folder_sidebar()
        self._build_main_area()

    def _build_folder_sidebar(self):
        sidebar = tkinter.Frame(self, width=130, bg="#e8e8e8")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tkinter.Label(
            sidebar, text="Folders", bg="#e8e8e8", font=("Arial", 9, "bold")
        ).pack(pady=(10, 5))

        self.folder_listbox = tkinter.Listbox(
            sidebar, bd=0, bg="white", selectbackground="#0078d7"
        )
        self.folder_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.folder_listbox.bind("<<ListboxSelect>>", self.manager.select_folder)

        self.new_folder_entry = tkinter.Entry(sidebar, width=15)
        self.new_folder_entry.pack(padx=5, pady=2)

        add_f_btn = tkinter.Button(
            sidebar, text="+ Add Folder", command=self._add_folder_action
        )
        add_f_btn.pack(fill="x", padx=5, pady=2)

        del_f_btn = tkinter.Button(
            sidebar,
            text="- Delete Folder",
            fg="red",
            command=self.manager.delete_folder,
        )
        del_f_btn.pack(fill="x", padx=5, pady=(2, 10))

    def _add_folder_action(self):
        name = self.new_folder_entry.get()
        if name:
            self.manager.add_folder(name)
            self.new_folder_entry.delete(0, "end")

    def _build_main_area(self):
        main_area = tkinter.Frame(self)
        main_area.pack(side="right", fill="both", expand=True)

        self.control_menu = tkinter.Frame(main_area, bg="#d0d0d0", height=45)
        self.control_menu.pack(fill="x", side="top")
        self.control_menu.pack_propagate(False)

        self.control_menu.add_btn = tkinter.Button(
            self.control_menu,
            text="Add Task",
            width=10,
            command=self.manager.interrogate_for_task,
        )
        self.control_menu.delete_all_btn = tkinter.Button(
            self.control_menu,
            text="Delete All",
            width=10,
            command=self.manager.delete_all,
        )

        self.control_menu.add_btn.pack(side="left", padx=10, pady=8)
        self.control_menu.delete_all_btn.pack(side="right", padx=10, pady=8)

        self.cont_for_task_menu = tkinter.Frame(main_area)
        self.cont_for_task_menu.pack(fill="both", expand=True)

        self.tasks_canvas = tkinter.Canvas(
            self.cont_for_task_menu, bg="white", highlightthickness=0
        )
        self.scrollbar = tkinter.Scrollbar(
            self.cont_for_task_menu, orient="vertical", command=self.tasks_canvas.yview
        )

        self.scrollable_tasks_container = tkinter.Frame(
            self.tasks_canvas, bg="white"
        )
        self.scrollable_tasks_container.bind(
            "<Configure>",
            lambda e: self.tasks_canvas.configure(
                scrollregion=self.tasks_canvas.bbox("all")
            ),
        )

        self.canvas_window = self.tasks_canvas.create_window(
            (0, 0), window=self.scrollable_tasks_container, anchor="nw"
        )

        self.tasks_canvas.bind(
            "<Configure>",
            lambda e: self.tasks_canvas.itemconfig(self.canvas_window, width=e.width),
        )

        self.tasks_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.tasks_canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.tasks_canvas.yview_scroll(-1 * (e.delta // 120), "units"),
        )
        self.tasks_canvas.bind_all(
            "<Button-4>", lambda e: self.tasks_canvas.yview_scroll(-1, "units")
        )
        self.tasks_canvas.bind_all(
            "<Button-5>", lambda e: self.tasks_canvas.yview_scroll(1, "units")
        )

        self.tasks_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")


if __name__ == "__main__":
    run = TaskManager()
    run.load_tasks()
    run.root.mainloop()
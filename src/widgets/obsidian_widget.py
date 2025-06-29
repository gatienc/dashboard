from src.logger import logger
from src.utils import API_URL, API_KEY
from textual.widget import Widget
from textual.widgets import SelectionList, Static
from textual.app import ComposeResult
from datetime import datetime
from textual.reactive import reactive
from textual import on
import requests

DEFAULT_CALENDAR = """
| 08:00| Morning Meeting |
| 09:30| Project Work    |
| 12:00| Lunch Break      |
| 13:00| Team Collaboration|
| 14:30| Client Call      |
| 16:00| Review Session   |
| 17:30| Wrap-up          |
"""


def todo_list_formatting(daily_todo: str) -> list[(str, int, bool)]:
    """
    Gets the Todo list section from the provided data string and returns a list of tuples formatted as (text, index, done).
    You can use this to populate a SelectionList widget in Textual.
    """

    selection_list = []
    count = 0

    for line in daily_todo.splitlines():
        if not line:
            continue
        if line.startswith("- ["):
            done = line.startswith("- [x]")
            # Remove "- [ ]" or "- [x]" and any extra brackets
            text = line[6:].replace("]", "").replace("[", "").strip()
            selection_list.append((text, count, done))
            count += 1
        # Stop if we reach a new section (e.g., a line starting with "####")
        elif line.startswith("####"):
            break
    logger.debug(f"Converted data to todo list: {selection_list}")
    return selection_list


class DailyStats(Widget):
    """A widget to display the daily stats in a static format."""

    def __init__(self, routine_dict: dict) -> None:
        super().__init__()
        self.routine_dict = routine_dict
        self.text = self.get_text(routine_dict)
        self.border_title = "Daily Stats"

    def get_text(self, routine_dict: dict) -> None:
        logger.debug(routine_dict)
        if "error" in routine_dict:
            return "Error fetching data."
        return (
            f"Journal Wrote: {'✅' if routine_dict.get('journal_wrote', False) else '❌'}\n" +
            f"Wake Early:    {'✅' if routine_dict.get('wake_early', False) else '❌'}\n" +
            f"Trained:       {'✅' if routine_dict.get('trained', False) else '❌'}\n" +
            f"Stretched:     {'✅' if routine_dict.get('stretched', False) else '❌'}\n" +
            f"Anki:          {'✅' if routine_dict.get('anki', False) else '❌'}\n" +
            f"City:          {routine_dict.get('city', 'Unknown')}")

    def update_data(self, routine_dict: str) -> None:
        self.routine_dict = routine_dict
        self.text = self.get_text(routine_dict)
        self.query_one(Static).update(self.text)

    def compose(self):
        yield Static(self.text)


class DailyCalendar(Widget):
    """A widget to display a daily calendar with events.
    TODO: add as a subtitle the current thing your supposed to do
    """

    def __init__(self, data: str = DEFAULT_CALENDAR) -> None:
        super().__init__()
        self.data = data
        self.border_title = "Daily Calendar"

    def compose(self) -> ComposeResult:
        yield Static(self.data, classes="calendar")

    def update_data(self, new_data: str) -> None:
        """Update the calendar data."""
        self.data = new_data
        self.query_one(Static).update(new_data)


class ObsidianWidget(Widget):
    """A widget to display my obsidian related todo, planning and stats """

    time: reactive[datetime] = reactive(datetime.now)

    def __init__(self) -> None:
        self.BORDER_TITLE = "Obsidian Dashboard"
        self.data = self._get_data()
        self.uploading = False  # When data is being uploaded, no new data can be fetched
        super().__init__()

    def _get_data(self) -> dict:
        """Get the data to be displayed in the widget by calling a FastAPI endpoint."""
        try:
            response = requests.get(f"{API_URL}/daily/{datetime.now().strftime('%Y-%m-%d')}",
                                    headers={"X-API-KEY": API_KEY})
            response.raise_for_status()
            logger.debug(
                f"Fetched data from FastAPI endpoint: {response.text}")

            todo_response = requests.get(f"{API_URL}/to_do_list",
                                         headers={"X-API-KEY": API_KEY})
            todo_response.raise_for_status()
            # add merged data to response
            response_data = response.json()
            todo_data = todo_response.json()
            response_data["todo"] = todo_data.get("todo_list", "")
            return response_data
        except requests.RequestException as e:
            logger.error(f"Failed to fetch data from FastAPI endpoint: {e}")
            return {"error": str(e)}

    def update_data(self, new_data: dict) -> None:
        """Update the data and refresh the widget's content."""
        if self.uploading:
            logger.warning(
                "Data is currently being uploaded, skipping update.")
            return
        self.data = new_data
        if "error" in self.data:
            return
        # Update SelectionList
        daily_todo_list = self.query_one("#daily_todo_list", SelectionList)
        daily_todo_list.clear_options()
        for item in todo_list_formatting(self.data["daily_todo"]):
            daily_todo_list.add_option(item)
        # Update DailyStats
        daily_stats = self.query_one(DailyStats)
        daily_stats.update_data(self.data["routine"])

    def compose(self) -> ComposeResult:
        if "error" in self.data:
            yield DailyStats(routine_dict={"error": "Error fetching data."})
            yield SelectionList[int](("Error fetching daily todo list.", 0, False), id="daily_todo_list", compact=True)
            yield DailyCalendar(data="Error fetching calendar data.")
            yield SelectionList[int](("Error fetching todo list.", 0, False), id="todo_list", compact=True)
        else:
            yield DailyStats(routine_dict=self.data["routine"])
            yield SelectionList[int](*todo_list_formatting(self.data["daily_todo"]), id="daily_todo_list", compact=True)
            yield DailyCalendar(data=DEFAULT_CALENDAR)
            yield SelectionList[int](*todo_list_formatting(self.data["todo"]), id="todo_list", compact=True)

    def _get_new_todo_list(self, id: str) -> str:
        """Get the current todo list from the SelectionList."""
        self.uploading = True
        selected_list = self.query_one(id, SelectionList).selected
        if id == "#daily_todo_list":
            key = "daily_todo"
        elif id == "#todo_list":
            key = "todo"
        # loop trough the todo list text and find the selected item
        selection_list = todo_list_formatting(self.data[key])
        new_todo = self.data[key].splitlines()
        current_index = 0
        for index, line in enumerate(self.data[key].splitlines()):
            logger.debug(selection_list[current_index][0])
            line_matching = selection_list[current_index][0] in line.replace(
                "[", "").replace("]", "")

            if line.startswith("- ["):
                if line.startswith("- [ ]"):
                    if line_matching and current_index in selected_list:
                        new_todo[index] = new_todo[index].replace(
                            "- [ ]", "- [x]")

                if line.startswith("- [x]"):
                    if line_matching and current_index not in selected_list:
                        new_todo[index] = new_todo[index].replace(
                            "- [x]", "- [ ]")
                current_index += 1

        return "\n".join(new_todo)

    @on(SelectionList.SelectedChanged, "#daily_todo_list")
    def upload_daily_todo_list_change(self) -> None:
        if "error" in self.data:
            logger.error("No data available to update todo list.")
            return

        self.data["daily_todo"] = self._get_new_todo_list("#daily_todo_list")
        self._get_new_todo_list("#daily_todo_list")

        try:
            response = requests.post(
                f"{API_URL}/daily/{datetime.now().strftime('%Y-%m-%d')}/update_todo",
                headers={"X-API-KEY": API_KEY,
                         "Content-Type": "application/json"},
                json={"daily_todo": self.data["daily_todo"]},
            )
            response.raise_for_status()
            logger.debug("Todo list updated successfully.")
        except requests.RequestException as e:
            logger.error(f"Failed to update todo list: {e}")

        self.uploading = False

    @on(SelectionList.SelectedChanged, "#todo_list")
    def upload_todo_list_change(self) -> None:
        if "error" in self.data:
            logger.error("No data available to update todo list.")
            return

        self.data["todo"] = self._get_new_todo_list("#todo_list")

        try:
            response = requests.post(
                f"{API_URL}/to_do_list/update",
                headers={"X-API-KEY": API_KEY,
                         "Content-Type": "application/json"},
                json={"todo": self.data["todo"]},
            )
            response.raise_for_status()
            logger.debug("Todo list updated successfully.")
        except requests.RequestException as e:
            logger.error(f"Failed to update todo list: {e}")

        self.uploading = False

    def on_mount(self) -> None:
        self.query_one("#daily_todo_list",
                       SelectionList).border_title = "Daily Todo List"
        self.query_one("#todo_list", SelectionList).border_title = "Todo List"

    def watch_time(self, time: datetime) -> None:
        """Update the widget's content based on the current time."""
        if time.second % 15 == 0:  # Update every 15 seconds
            if not self.uploading:
                logger.debug(f"Updating data at {time}")
                self.data = self._get_data()
                self.update_data(self.data)

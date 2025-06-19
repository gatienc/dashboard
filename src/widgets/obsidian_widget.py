import datetime
from src.logger import logger
from textual.widget import Widget
from textual.widgets import SelectionList, Placeholder, Static
from textual.containers import Horizontal
from textual.widgets.selection_list import Selection
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

DEFAULT_DATA = """
---
date: 2025-06-19T15:58
tags:
    - Daily
cssclasses:
    - daily
    - friday
wake_early: false
trained: false
stretched: false
anki: false
city: undefined
emoji:
---
**Friday, June 20th, 2025**
#### Tracker

😀 `INPUT[text:emoji]`
😴 : `INPUT[time:sleepin]`
⏰ : `INPUT[time():sleepout]`
Entrainement ? `INPUT[toggle:trained]`
Etirement ? `INPUT[toggle:stretched]`
Médité ? `INPUT[toggle:meditate]`
Révisé Anki ? `INPUT[toggle:anki]`
Ville actuel : `INPUT[suggester(option(Roubaix),option(Karlsruhe),option(Strasbourg),option(Londres),allowOther(True)):city]`
#### Journal

#### Things consumed

#### Daily Todo
- [ ] mail TalkTalk


- [ ] Faire Widget obsidian pour dashboard

Apprentissage :

- [ ] Relire cours apprentissage de formes

- [ ] [[cours wekeo]]

- [ ] apprendre les différents satellites disponibles et leurs spécificités et utilités

- [ ] ficher hydroponies et ses variantes

- [ ] lire grand papier et ficher

- [ ] lire 100 page ai book
- [ ] Relire cours apprentissage de formes

- [ ] [[cours wekeo]]

- [ ] apprendre les différents satellites disponibles et leurs spécificités et utilités

- [ ] ficher hydroponies et ses variantes

- [ ] lire grand papier et ficher

- [ ] lire 100 page ai book
- [ ] Relire cours apprentissage de formes

- [ ] [[cours wekeo]]

- [ ] apprendre les différents satellites disponibles et leurs spécificités et utilités

- [ ] ficher hydroponies et ses variantes

- [ ] lire grand papier et ficher

- [ ] lire 100 page ai book
- [ ] Relire cours apprentissage de formes

- [ ] [[cours wekeo]]

- [ ] apprendre les différents satellites disponibles et leurs spécificités et utilités

- [ ] ficher hydroponies et ses variantes

- [ ] lire grand papier et ficher

- [ ] lire 100 page ai book
- [ ] Relire cours apprentissage de formes

- [ ] [[cours wekeo]]

- [ ] apprendre les différents satellites disponibles et leurs spécificités et utilités

- [ ] ficher hydroponies et ses variantes

- [ ] lire grand papier et ficher

- [ ] lire 100 page ai book
- [ ] Relire cours apprentissage de formes

- [ ] [[cours wekeo]]

- [ ] apprendre les différents satellites disponibles et leurs spécificités et utilités

- [ ] ficher hydroponies et ses variantes

- [ ] lire grand papier et ficher

- [ ] lire 100 page ai book
- [ ] Relire cours apprentissage de formes

- [ ] [[cours wekeo]]

- [ ] apprendre les différents satellites disponibles et leurs spécificités et utilités

- [ ] ficher hydroponies et ses variantes

- [ ] lire grand papier et ficher

- [ ] lire 100 page ai book


"""


def data_to_daily_info(data: str) -> dict:
    """
    Parses the provided data string and returns a dictionary with the daily information.
    The data should be in a specific format, including date, tags, cssclasses, and various toggles.
    """
    # cut the data lines between the "---" lines
    lines = data.splitlines()
    daily_info = {}
    try:
        start = lines.index("---") + 1
        end = lines.index("---", start)
    except ValueError:
        return {}
    # Is there something between #### Journal and #### Things consumed
    if "#### Journal" in lines and "#### Things consumed" in lines:
        journal_start = lines.index("#### Journal") + 1
        journal_end = lines.index("#### Things consumed", journal_start)
        daily_info["journal"] = "\n".join(
            lines[journal_start:journal_end]).strip()
        daily_info["journal_wrote"] = bool(daily_info["journal"].strip())

    properties_lines = lines[start:end]
    for line in properties_lines:
        if line.startswith("date:"):
            daily_info["date"] = line.split(":", 1)[1].strip()
        elif line.startswith(("tags:", "cssclasses:")):
            continue
        else:
            if len(line.split(":", 1)) < 2:
                key = line.replace(":", "")
                value = ""
            else:
                key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key in ["wake_early", "trained", "stretched", "anki"]:
                daily_info[key] = value.lower() == "true"
            elif key == "city":
                daily_info[key] = value if value != "undefined" else None
            else:
                daily_info[key] = value

    return daily_info


def data_to_todo_list(data: str) -> list[(str, int, bool)]:
    """
    Gets the Todo list section from the provided data string and returns a list of tuples formatted as (text, index, done).
    You can use this to populate a SelectionList widget in Textual.
    """

    selection_list = []
    count = 0
    # Only process lines after "#### Daily Todo"
    lines = data.splitlines()
    try:
        start = lines.index("#### Daily Todo") + 1
    except ValueError:
        return selection_list  # "#### Daily Todo" not found

    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- ["):
            done = stripped.startswith("- [x]")
            # Remove "- [ ]" or "- [x]" and any extra brackets
            text = stripped[6:].replace("]", "").replace("[", "").strip()
            selection_list.append((text, count, done))
            count += 1
        # Stop if we reach a new section (e.g., a line starting with "####")
        elif stripped.startswith("####"):
            break
    return selection_list


class DailyStats(Widget):
    """A widget to display the daily stats in a static format."""

    def __init__(self, data: str) -> None:
        super().__init__()
        self.data = data
        self.text = self.get_text()
        self.border_title = "Daily Stats"

    def get_text(self) -> None:
        daily_info = data_to_daily_info(self.data)
        return (f"Journal Wrote: {'✅' if daily_info.get('journal_wrote', False) else '❌'}\n" +
                f"Wake Early:    {'✅' if daily_info.get('wake_early', False) else '❌'}\n" +
                f"Trained:       {'✅' if daily_info.get('trained', False) else '❌'}\n" +
                f"Stretched:     {'✅' if daily_info.get('stretched', False) else '❌'}\n" +
                f"Anki:          {'✅' if daily_info.get('anki', False) else '❌'}")
        # f"City:          {daily_info.get('city', 'Unknown')}")

    def update_data(self, data: str) -> None:
        self.data = data
        self.text = self.get_text()
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

    def __init__(self, data: str = DEFAULT_DATA) -> None:
        self.BORDER_TITLE = "Obsidian Dashboard"
        self.data = data
        super().__init__()

    def _get_data(self) -> str:
        """Get the data to be displayed in the widget by calling a FastAPI endpoint."""
        # TODO: rework it
        try:
            response = requests.get(
                "https://gatien.chenu.me/api/obsidian/daily")
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch data from FastAPI endpoint: {e}")
            return self.data

    def update_data(self, new_data: str) -> None:
        """Update the data and refresh the widget's content."""
        self.data = new_data
        # Update SelectionList
        todo_list = self.query_one("#todo_list", SelectionList)
        todo_list.clear()
        for item in data_to_todo_list(self.data):
            todo_list.add_option(*item)
        # Update DailyStats
        daily_stats = self.query_one(DailyStats)
        daily_stats.update_data(self.data)

    def on_click(self) -> None:
        pass

    def compose(self) -> ComposeResult:
        yield DailyStats(data=self.data)
        yield SelectionList[int](*data_to_todo_list(self.data), id="todo_list")
        yield DailyCalendar(data=DEFAULT_CALENDAR)

    @on(SelectionList.SelectedChanged)
    def update_selected_view(self) -> None:
        logger.debug("Selection changed")
        selected = self.query_one(SelectionList).selected
        logger.debug(f"Selected item: {selected}")

    def on_mount(self) -> None:
        self.query_one("#todo_list", SelectionList).border_title = "Todo List"

    def watch_time(self, time: datetime) -> None:
        """Update the widget's content based on the current time."""
        # This method can be used to update the widget periodically if needed
        logger.debug(f"Current time: {time}")
        # For example, you could refresh the data or update the display based on the time
        # self.update_data(self.data)  # Uncomment to refresh data every time time changes

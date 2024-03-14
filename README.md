# ShutUpImOnARun

ShutUpImOnARun is a Python script for OBS designed to assist speedrunners by automatically managing stream alerts during critical moments of their runs. It connects to LiveSplit, and enables users to hide or mute specified sources in OBS when reaching a predefined split in their speedrun. This helps runners maintain focus and avoid distractions during crucial segments of their gameplay.

## Installation Guide

1. If you haven't already installed Python on your system, download and install it from the [official Python website](https://www.python.org/downloads/).
2. Open OBS.
3. Go to the "Tools" menu and select "Scripts", then click on the "Python Settings" tab.
4. Click on the "Browse" button next to the "Python install path" field.
5. Navigate to the directory where Python is installed and press "Select Folder".

   On Windows, this could be ```C:/Users/CurrentUser/AppData/Local/Programs/Python/Python310```

   On Mac OS, this could be ```/usr/local/bin/python3```

6. Download the script file (ShutUpImOnARun.py) and place it in your OBS Studio scripts directory.
7. Go to Tools > Scripts.
8. Click the + button to add a new script.
9. Select ShutUpImOnARun.py from the file selection dialog and click Open.

## Usage

1. In LiveSplit right-click and go to "Controll" and click "Start Server" (Yes you will have to do this every time)
2. Go to Tools > Scripts and select ShutUpImOnARun.py
3. Configure the plugin settings:
   - **Enabled**: Check this box to activate the plugin.
   - **Only for PB Pace**: Check this box if you want the script to only be active when you're on PB pace.
     - If the run reaches PB pace at any point after the selected split, the source will be hidden/muted.
     - If the run slows down, the source will stay hidden/muted until the next reset.
   - **Split Index**: Specify the index of the split where sources should be toggled. (The first split has an index of 0.)
   - **Source to hide/mute**: Choose the source that you want to hide or mute when the specified split is reached.
   - **Mute Only**: Check this box if you want to only mute the source instead of hiding it as well.
   - **Source to show**: Choose the source that you want to show when the specified split is reached.
4. Start your run in LiveSplit.
5. The plugin will automatically monitor your progress and control the specified sources in OBS accordingly.
6. When a run is stopped or reset, sources will be reverted to their initial state.

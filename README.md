# task-tracker

A simple task tracker built with FastAPI.

## Quick Start Guide

Follow these steps to get started ASAP:

1. Clone this repository
2. Switch to the directory you cloned to (if not already in it)
3. Run `pip install -r requirements.txt` to install all needed packages
4. Run `pythonw main.py` using Python >= 3.12
5. Alternatively, run `python main.py` to open a CLI

If ran with pythonw (aka. in the background), you can exit using the system tray menu (right-click on the tt icon).

Visit [https://nihilne.github.io/task-tracker](https://enitoxy.github.io/task-tracker/) to access the task-tracker frontend. The webpage will attempt to communicate with localhost:8080 to access the API and its local database that is created automatically when first running `app.py`.

Alternatively, you can host the frontend on your own, for which you can find all the code in the `gh-pages` branch.

If you want to interact with the API in another way, see the auto-generated FastAPI docs at `localhost:8080/docs`

## Contributions

Contributions are more than welcome! Consider creating issues for new features or bug fixes, and pull requests if you wish to improve the code directly.

# MealPlanner
Automatically plans meals, generates shopping lists, and adapts to your tastes.

# Contents
- [MealPlanner](#mealplanner)
- [Contents](#contents)
- [Installation](#installation)
  - [Option 2: Installation in a virtual environment](#option-2-installation-in-a-virtual-environment)
    - [1. Create the virtual environment](#1-create-the-virtual-environment)
      - [Windows](#windows)
      - [Linux/MacOS](#linuxmacos)
      - [2. Install meal\_planner](#2-install-meal_planner)
      - [NOTE](#note)
- [Usage](#usage)
  - [Option 1: .env (recommended, all platforms)](#option-1-env-recommended-all-platforms)
  - [Option 2: Setting the environment variable manually](#option-2-setting-the-environment-variable-manually)
    - [Windows](#windows-1)
    - [Linux/MacOS](#linuxmacos-1)


# Installation

## Option 2: Installation in a virtual environment

### 1. Create the virtual environment

#### Windows


```ps
> md MealPlanner
> cd MealPlanner
> py -m venv .venv
...
> .\.venv\Scripts\activate
```

Depending on your machine's configuration, you may need to change your [Execution Policy](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy). If that is the case, run the following command before re-running the `.\.venv\Scripts\activate` command:

```ps
> Set-ExcecutionPolicy Unrestricted -Scope CurrentUser
```

#### Linux/MacOS
```bash
$ python3 -m venv .venv
...
$ source .venv/bin/activate
```


#### 2. Install meal_planner
(Ask me (Kian) for help here because I haven't actually uploaded the package yet)
```ps
> pip install meal_planner
```

#### NOTE

If you install `meal_planner` this way, you must activate the virtual environment before running the command (the same way you activated in when you [created the environment](#1-create-the-virtual-environment))

# Usage

To use `meal_planner`, run it as a script (preferrably in its own folder):

```ps
> meal_planner
```

If this is your first time running it, it will create a `database.db` file, which is necessary to store your preferences and program data.

You will need to give the program your Tasty API key by setting it as an environment variable. You have two options for doing that:

## Option 1: .env (recommended, all platforms)

Create a .env file in the folder where you're running the script and enter the following in it, but replace "(your api key)" with your actual [api key](https://rapidapi.com/apidojo/api/tasty/pricing):

```
TASTY_API_KEY=(your api key)
```

## Option 2: Setting the environment variable manually

### Windows

1. Open Run by clicking Win+R or searching Run in the search bar.
2. In the Run box, type `control userpasswords`. This will bring you to the control panel page for your account.
3. On the left panel, click on "Change my environment variables".
4. Under "User variables for (your account)", click the "New" button.
5. For the "Variable name", put `TASTY_API_KEY`. For the "Variable value", put your [api key](https://rapidapi.com/apidojo/api/tasty/pricing).
6. Click "OK".

### Linux/MacOS

1. Open `~/.bash_profile` file
```bash
touch ~/.bash_profile; nano ~/.bash_profile
```
2. Add the following line to the end:
```bash
export TASTY_API_KEY=(your api key)
```
---
After running the program, you'll enter one of two modes. The first time you run it, it will ask you for the number of recipes you want. After inputting those recipes, it will generate a shopping list and recipe list. Those lists will be opened up as .txt files in your default text editor.

The next time you run the program it will ask you what you thought of those recipes so over time it can adapt to your tastes. You can answer 'dislike', 'none' (if you had no opinion), 'like', or 'love'.

# User manual

## Program Interface
The main window of the text editor consists of the following elements: 
1. **Window Title** — displays the program name and current file name
2. **Main Menu** — contains all available commands
3. **Toolbar** — quick access buttons
4. **Editing Area** — text field for entering and editing text
5. **Output Area** — area for displaying analyzer results
6. **Status Bar** — displays application status information

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/interface.png" width="450">

## Menu «File»
Menu «File» contains commands for working with files.

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/ru/file.png" width="450">

|    Command    |      Hotkey     |                                                   Photo                                                    |                   Description                   |
|---------------|-----------------|------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| New           | `Ctrl+N`        | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/new_document.png" width="450">    | Creates a new document in a new tab             |
| Open          | `Ctrl+O`        | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/open.png" width="450">            | Opens an existing text file                     |
| Save          | `Ctrl+S`        | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/saved.png" width="450">           | Saves the current document                      |
| Save as       | `Ctrl+Shift+S`  | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/save_as.png" width="450">         | Saves the document under a new name             |
| Exit          | `Ctrl+Q`        | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/save_before_exit.png" width="450">| Exits the program. When trying to close an unsaved document, the program will prompt to save changes.|

## Menu «Edit»
Menu «Edit» contains commands for text editing.

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/edit.png" width="450">

|    Command    |     Hotkey      |                                                   Photo                                                    |                     Description                   |
|---------------|-----------------| -----------------------------------------------------------------------------------------------------------|---------------------------------------------------|
| Undo          | `Ctrl+Z`        | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/undo.png" width="450">            | Revers the last action                            |
| Redo          | `Ctrl+Y`        | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/redo.png" width="450">            | Repeats the previously undone action              |
| Cut           | `Ctrl+X`        | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/cut.png" width="450">             | Copies selected text to the buffer and deletes it |
| Copy          | `Ctrl+C`        | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/copy.png" width="450">            | Copies selected text to the clipboard             |
| Paste         | `Ctrl+V`        | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/paste.png" width="450">           | Pastes text from the clipboard                    |
| Delete        | `Del`           | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/delete.png" width="450">          | Deletes selected text                             |
| Select all    | `Ctrl+A`        | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/select_all.png" width="450">      | Selects all text in the document                  |

## Menu «Text»
> [!NOTE]
> **`In development but assumes:`**

Menu «Text» contains informational sections about the language and grammar.

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/text.png" width="450">

1. **Problem Statement** — description of the work's purpose and objectives
2. **Grammar** — formal description of the language grammar
3. **Grammar Classification** — Chomsky grammar type
4. **Analysis Method** — description of the syntax analysis method
5. **Test Example** — example of input string parsing
6. **References** — sources used
7. **Program Source Code** — application code

Selecting any item opens a window with the corresponding information.

## Menu «Run»

> [!NOTE]
> **`In development but assumes:`**

**Run Analyzer** (`F5`) — starts syntax analysis of the text from the editing area.

Analysis results:
1. Erroneous lines are marked in red with the error position indicated
2. Clicking on an error message moves the cursor to the erroneous fragment
                    
## Menu «Help»
Menu «Help» contains commands for obtaining information about the program.

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/help.png" width="450">

|    Command    |     Hotkey      |                                                   Photo                                                    |                    Description                  |
|---------------|-----------------| -----------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| Call Help     | `F1`            | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/user_manual.png" width="450">     | Opens this user manual                          |
| About         | `F2`            | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/about.png" width="450">           | Information about the program and developer     |

## Menu «Settings»
Menu «Settings» contains commands for changing the interface.

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/settings.png" width="450">

|    Command      |      Hotkey     |                                                   Photo                                                    |                     Description                 |
|-----------------|-----------------| -----------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| Change Language |                 | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/translate.png" width="450">       | Changes the program interface language          |

## Working with Editing and Output Areas

> [!NOTE]
> **Editing Area:** designed for entering and editing text. All standard editing operations are supported.
> 
> **Output Area:** displays the results of the syntax analyzer. This area is read-only.
> 
> **Resizing Areas:** drag the separator between areas with the mouse.
> 
> **Changing font size in the editing area:** use the mouse wheel to adjust the text scale.

**To zoom in** hold down the `Ctrl` key and scroll the mouse wheel forward (away from you) - the text size will increase smoothly:

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/approximation.png" width="450">

**To zoom out** hold down the `Ctrl` key and scroll the mouse wheel backward (toward you) - the text size will decrease smoothly:

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/distancing.png" width="450">

## Syntax Highlighting
The editor supports syntax highlighting for the `Python` language:
1. Keywords (if, else, def, class, import, etc.)
2. Strings and numbers
3. Comments
4. Functions and methods
5. Built-in exceptions and decorators

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/syntaxis.png" width="450">

## Tooltips
When hovering the mouse cursor over any toolbar button, a tooltip appears with a brief description of the action.

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/en/tooltip.png" width="450">

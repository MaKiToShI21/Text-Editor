<h1 align="center">Text-Editor</h1>

## Contents
1. **[Title and Objective of the Laboratory Work](#title-and-objective-of-the-laboratory-work)**
2. **[Author Information](#author-information)**
3. **[Project Description](#project-description)**
4. **[Technologies Used](#technologies-used)**
5. **[Build and Launch Instructions](#build-and-launch-instructions)**
6. **[User Manual](#user-manual)**

___

<h2 align="center">Title and Objective of the Laboratory Work</h2>

**Laboratory Work 1.** Development of a Graphical User Interface (GUI) for a Language Processor

**Objective:** Creation of a cross-platform graphical interface (GUI) for a language processor in the form of a specialized text.

<h2 align="center">Author Information</h2>

Work completed by ***MaKiToShI*** 😃.

<h2 align="center">Project Description</h2>
Text Editor is a graphical interface application developed in Python using the PyQt6 library. The application is a specialized text editor that will later be enhanced with syntax analyzer functions.

<h2 align="center">Technologies Used</h2>

**Programming Language:**
Python 3.12

**GUI Framework:**
PyQt6 + Qt Designer

**Development Environment:**
VS Code (Visual Studio Code)

**Additional Tools:**

* PyQt6.uic - module for loading .ui files into Python
* PyInstaller - tool for packaging Python applications into executable files
* Git - version control system

<h2 align="center">Build and Launch Instructions</h2>

**Installing Python**

Download and install Python 3.8 or higher from the official website.

**Clone the Repository**

```bash
git clone https://github.com/MaKiToShI21/Text-Editor.git
```

**Or download ZIP and extract**
![ZIP](https://github.com/MaKiToShI21/Text-Editor/blob/main/images/ZIP.png)

**Create and Activate a Virtual Environment**
```bash
python -m venv venv
venv\Scripts\activate
```

**Install Dependencies**
```bash
pip install -r requirements.txt
```

**Run**
```bash
python main.py
```

___

### Building the Project

If you have changed `text_editor.ui`, you need to execute the following command:
```bash
pyuic6 text_editor.ui -o ui_editor.py
```

To create an executable file, run the PyInstaller command:
```bash
pyinstaller --onefile --windowed main.py
```

After successful build, the executable file is located in the folder: `/dist/main.exe`

___

### **Running Without Python Installation**

Download [Text-Editor.exe](https://github.com/MaKiToShI21/Text-Editor/releases/tag/v1.0.0) and run it. No additional installations are required.

<h2 align="center">User Manual</h2>

***<p align="center">[In Russian](./docs/ru/user_manual.md) or [In English](./docs/en/user_manual.md)</p>*** 

___

**This project uses the [MIT](https://github.com/MaKiToShI21/Text-Editor/blob/main/LICENSE) license.**

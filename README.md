<h1 align="center">Text-Editor</h1>

## Contents
1. **[Title and Objective of the Laboratory Work 1](#title-and-objective-of-the-laboratory-work-1)**
2. **[Author Information](#author-information)**
3. **[Project Description](#project-description)**
4. **[Technologies Used](#technologies-used)**
5. **[Build and Launch Instructions](#build-and-launch-instructions)**
6. **[Title and Objective of the Laboratory Work 2](#title-and-objective-of-the-laboratory-work-2)**
7. **[Title and Objective of the Laboratory Work 3](#title-and-objective-of-the-laboratory-work-3)**
9. **[User Manual](#user-manual)**

___

<h2 align="center">Title and Objective of the Laboratory Work 1</h2>

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

<h2 align="center">Title and Objective of the Laboratory Work 2</h2>

**Laboratory Work 2.** Development of a lexical analyzer (scanner)

**Objective:** Study the purpose and operating principles of a lexical analyzer within a compiler. Design an algorithm (state diagram) and implement a software implementation of a scanner for extracting lexemes from input text.

A state diagram was developed.

<div align="center">
  <img src="https://github.com/MaKiToShI21/Text-Editor/blob/semantic-analysis/images/lab2/state_diagram.png" width="450">
</div>

A lexer was created based on it to parse the string "**`std::complex<double> my_complex(10.0, 2.0);`**" into tokens, which are then output as a table.

| Correct line | Invalid char | multi-line |
|--------------|--------------|------------|
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/semantic-analysis/images/lab2/correct_line.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/semantic-analysis/images/lab2/invalid_char.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/semantic-analysis/images/lab2/multi-line.png" width="500"> |

<h2 align="center">Title and Objective of the Laboratory Work 3</h2>

**Laboratory Work 3.** Development of a syntactic analyzer (parser)

**Objective:** Study the purpose and operating principles of a parser within a compiler. Design a grammar, construct a corresponding grammar analysis method, and implement a parser with Irons's method for eliminating syntax errors. Integrate the developed module into the previously created graphical interface of the language processor.

Let us define a grammar of complex numbers in the C++ language G[‹Std›] in Chomsky notation with productions P:

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/semantic-analysis/images/lab3/grammar.png" width="500">

According to Chomsky's classification, the grammar G[‹Std›] is automata-based.

Graph of automata grammar:

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/semantic-analysis/images/lab3/graph.png" width="500">

Test examples:

|  No errors   | Some errors  | multi-line errors |
|--------------|--------------|-------------------|
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/semantic-analysis/images/lab3/no_errors.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/semantic-analysis/images/lab3/lots_of_errors.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/semantic-analysis/images/lab3/multi-line_errors.png" width="500"> |
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/semantic-analysis/images/lab3/no_errors2.png" width="500"> |
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/semantic-analysis/images/lab3/no_errors3.png" width="500"> |

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
pyuic6 text_editor.ui -o ui.py
```

To create an executable file, run the PyInstaller command:
```bash
pyinstaller --onefile --windowed --add-data "information;information" --add-data "icons;icons" --add-data "example.txt;." main.py
```

After successful build, the executable file is located in the folder: `/dist/main.exe`

___

### **Running Without Python Installation**

Download [Text-Editor.exe](https://github.com/MaKiToShI21/Text-Editor/releases/tag/v2.0.0) and run it. No additional installations are required.

<h2 align="center">User Manual</h2>

***<p align="center">[In Russian](./docs/ru/user_manual.md) or [In English](./docs/en/user_manual.md)</p>*** 

___

**This project uses the [MIT](https://github.com/MaKiToShI21/Text-Editor/blob/main/LICENSE) license.**

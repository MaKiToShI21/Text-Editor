<h1 align="center">Text-Editor</h1>

## Contents
1. **[Title and Objective of the Laboratory Work 1](#title-and-objective-of-the-laboratory-work-1)**
2. **[Author Information](#author-information)**
3. **[Project Description](#project-description)**
4. **[Technologies Used](#technologies-used)**
5. **[Build and Launch Instructions](#build-and-launch-instructions)**
6. **[Title and Objective of the Laboratory Work 2](#title-and-objective-of-the-laboratory-work-2)**
7. **[Title and Objective of the Laboratory Work 3](#title-and-objective-of-the-laboratory-work-3)**
8. **[Title and Objective of the Laboratory Work 4](#title-and-objective-of-the-laboratory-work-4)**
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
  <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/state_diagram.png" width="450">
</div>

A lexer was created based on it to parse the string "**`std::complex<double> my_complex(10.0, 2.0);`**" into tokens, which are then output as a table.

| Correct line | Invalid char | multi-line |
|--------------|--------------|------------|
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/correct_line.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/invalid_char.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/multi-line.png" width="500"> |

<h2 align="center">Title and Objective of the Laboratory Work 3</h2>

**Laboratory Work 3.** Development of a syntactic analyzer (parser)

**Objective:** Study the purpose and operating principles of a parser within a compiler. Design a grammar, construct a corresponding grammar analysis method, and implement a parser with Irons's method for eliminating syntax errors. Integrate the developed module into the previously created graphical interface of the language processor.

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/parser/images/grammar.png" width="400">

According to Chomsky's classification, the grammar G[‹Std›] is automata-based.

Graph of automata grammar:

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/parser/images/graph.png" width="500">

Test examples:

|  No errors   | Some errors  | multi-line errors |
|--------------|--------------|-------------------|
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/parser/images/no_errors.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/parser/images/lots_of_errors.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/parser/images/multi-line_errors.png" width="500"> |

<h2 align="center">Title and Objective of the Laboratory Work 4</h2>

**Laboratory Work 4.** Implementation of a substring search algorithm using regular expressions

**Objective:** Explore the theoretical foundations of regular expressions and their application to searching and extracting substrings from text. Develop practical skills in using library tools for working with regular expressions, as well as integrating search algorithms into the application's graphical interface.

**Statement of the problem:** Develop a substring search module using regular expressions, integrate it into an existing application (text editor), and provide visual output of the results.

1) Regular expression describing XML comments: ``r'<!--(.*?)-->'``

|     Symbol    |                     Description                          |
|---------------|----------------------------------------------------------|
|   ``<!--``    | XML comment opening tag                                  |
|     ``(``     | Beginning of capturing group                             |
|     ``.``     | Any character (except newline)                           |
|     ``*?``    | Lazy quantifier (zero or more repetitions)               |
|     ``)``     | End of capturing group                                   |
|    ``-->``    | XML comment closing tag                                  |

```re.DOTALL``` was also used - it allows the dot to match newline characters, which is necessary for searching multi-line comments.

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/regular-expressions/images/regular-expressions/xml_comments.png" width="550">

2) Regular expression to check if a file name is correct: ``r'\b[^\\/:*?"<>|\s]+\.[^\\/:*?"<>|\s]+\b'``

|     Symbol     |                                    Description                                      |
|----------------|-------------------------------------------------------------------------------------|
|   ``\b``       | Word boundary (beginning or end of word)                                            |
| ``[^...]``     | Negated character class (any character EXCEPT those specified)                      |
| ``\/:*?"<>\|`` | listed signs                                                                        |
|    ``\s``      | Whitespace character (space, tab, newline)                                          |
|    ``+``       | The quantifier "one or more"                                                        |
|    ``\.``      | Point (shielded)                                                                    |

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/regular-expressions/images/regular-expressions/filename.png" width="550">

Graph automaton:

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/regular-expressions/images/regular-expressions/graph_automaton.png" width="550">

3) Regular expression describing a URL link to a web page in Latin with support for subdomains and ports (with various protocols HTTP, HTTPS, FTP): ``r'\b(?:https?|ftp)://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d{1,5})?(?:/[^\s]*)?\b'``

|     Symbol          |                                    Description                                      |
|---------------------|-------------------------------------------------------------------------------------|
| ``\b``              | Word boundary (beginning or end of word)                                            |
| ``(?:...)``         | Non-capturing group (grouping without saving to the result)                         |
| ``https?``          | ``http`` with an optional ``s`` character (i.e. ``http`` or ``https)``              |
| ``\|``               | The "or" operator                                                                   |
| ``ftp`` and ``://`` | Literal match                                                                       |
| ``[a-zA-Z0-9-]+``   | One or more characters: Latin (upper and lower case), numbers, hyphen               |
| ``\.``              | Dot (subdomain separator)                                                           |
| ``(?:...)+``        | Repeat a group of subdomains one or more times                                      |
| ``[a-zA-Z]{2,}``    | Two or more Latin letters (top-level domain)                                        |
| ``(?::\d{1,5})?``   | Optional port group: colon and 1 to 5 digits                                        |
| ``(?:/[^\s]*)?``    | Optional path group: slash and zero or more characters except spaces                |

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/regular-expressions/images/regular-expressions/URL.png" width="550">

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

To create an executable file with flex lexer, run the PyInstaller command:
```bash
pyinstaller --onefile --windowed --add-data "lexer/lexer.exe;lexer" main.py
```

After successful build, the executable file is located in the folder: `/dist/main.exe`

___

### **Running Without Python Installation**

Download [Text-Editor.exe](https://github.com/MaKiToShI21/Text-Editor/releases/tag/v1.1.0) and run it. No additional installations are required.

<h2 align="center">User Manual</h2>

***<p align="center">[In Russian](./docs/ru/user_manual.md) or [In English](./docs/en/user_manual.md)</p>*** 

___

**This project uses the [MIT](https://github.com/MaKiToShI21/Text-Editor/blob/main/LICENSE) license.**

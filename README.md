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
8. **[Title and Objective of the Laboratory Work 5](#title-and-objective-of-the-laboratory-work-5)**
8. **[Title and Objective of the Laboratory Work 6](#title-and-objective-of-the-laboratory-work-6)**
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
  <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab2/state_diagram.png" width="450">
</div>

A lexer was created based on it to parse the string "**`std::complex<double> my_complex(10.0, 2.0);`**" into tokens, which are then output as a table.

| Correct line | Invalid char | multi-line |
|--------------|--------------|------------|
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab2/correct_line.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab2/invalid_char.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab2/multi-line.png" width="500"> |

<h2 align="center">Title and Objective of the Laboratory Work 3</h2>

**Laboratory Work 3.** Development of a syntactic analyzer (parser)

**Objective:** Study the purpose and operating principles of a parser within a compiler. Design a grammar, construct a corresponding grammar analysis method, and implement a parser with Irons's method for eliminating syntax errors. Integrate the developed module into the previously created graphical interface of the language processor.

Let us define a grammar of complex numbers in the C++ language G[‹Std›] in Chomsky notation with productions P:

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab3/grammar.png" width="500">

According to Chomsky's classification, the grammar G[‹Std›] is automata-based.

Graph of automata grammar:

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab3/graph.png" width="500">

Test examples:

|  No errors   | Some errors  | multi-line errors |
|--------------|--------------|-------------------|
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab3/no_errors.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab3/lots_of_errors.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab3/multi-line_errors.png" width="500"> |
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab3/no_errors2.png" width="500"> |
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab3/no_errors3.png" width="500"> |

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

<h2 align="center">Title and Objective of the Laboratory Work 5</h2>

**Laboratory Work 5.** Building an AST and checking context-sensitive conditions

**Objective:** Explore the purpose and operating principles of a semantic analyzer within a compiler. Master methods for constructing an abstract syntax tree (AST) and checking context-sensitive conditions (semantic rules) for a given syntactic construct.

**Statement of the problem:** Develop a previously created syntactic analyzer (parser) into a semantic one: construct an abstract syntax tree (AST) and implement checking of context-dependent conditions in accordance with the individual version of the coursework.

**Context-sensitive conditions**
The semantic analyzer implements the following checks:

1. Name uniqueness (repeated declaration)
Example:
```bash
std::complex<double> my_complex(-10.0, 2.0);
std::complex<double> my_complex(-1.0, 3.0);
```
Expected message: `Error: identifier "my_complex" was already declared before (line 1)`.

2. Type compatibility (expected double)
Example:
```bash
std::complex<double> my_complex(-10.0, 2);
```
Expected message: `Error: The value "2" has int type, expected double`.

3. Valid values ​​(double range, C++)
Checked for values ​​within the double range (including subnormal values ​​except 0).
Example:
```bash
std::complex<double> my_complex(1.7*10^309, 2.0);
```

>[!NOTE]
>1.7*10^309 is used to show an example of a large number, in reality such a line would be incorrect.

Expected message: `Error: value "17000..." is out of range for double`.

**AST structure**
AST nodes with attributes and child elements are used. The basic idea is:

-  `AstNode` — base node (`node_type`, `attributes`, `children`).
-  `ComplexDeclNode` — complex variable declaration.
-  `DoubleNode` — type `double`.
-  `DoubleLiteralNode` — initialization values.

![output AST](https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab5/ast_graph.png)

Example:

![output AST](https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab5/output_AST.png)

AST graph:

![show AST](https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab5/show_AST.png)

|  No errors   | Name uniqueness  | Type compatibility | Valid values |
|--------------|------------------|--------------------|--------------|
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab5/no_errors_1.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab5/name_uniqueness.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab5/type_compatibility.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab5/valid_values.png" width="500"> |
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab5/no_errors_2.png" width="500"> |

The `PyQt6 Graphics View Framework` is used to display the AST:

- `QDialog` — a separate AST window
- `QGraphicsScene` — a scene for the graph
- `QGraphicsView` — displaying the scene
- `QGraphicsTextItem` — node/terminal labels
- `QPen + scene.addLine(...)` — edges and arrows
- `fitInView(...), wheel/key zoom, and + / - / 100% buttons` — scaling the image.

<h2 align="center">Title and Objective of the Laboratory Work 6</h2>

**Laboratory Work 6.** Creating an internal presentation form for the program

**Objective:** To study methods for constructing an internal representation of a program (IRP) based on a context-free grammar, implement a syntactic analyzer using the recursive descent method, and transform arithmetic expressions into tetrads and POLYSIS.

**Statement of the problem:**
1. Implement a recursive descent method to detect lexical and syntactic errors for a given context-sensitive grammar.
2. Represent the program's internal form as tetrads (op, arg1, arg2, result) for arithmetic expressions (only for valid strings).
3. Convert the expression to POLIZ (Polish inverse notation) and evaluate it (only for arithmetic expressions consisting of integers).

**Task option:**
Programming language: `C/C++`
Complete definition of the KS grammar for the programming language:
<img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/grammar.png" width="500">

Examples of correct strings:
1. (17 + 3 * 5) % 7 - 2
2. a1 + b2 * (c3 - 4)
3. 8 / 2 + 10 % 3

Lexer diagram:
<img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/state_diagram.png" width="500">

Recursive descent scheme for a parser:
<img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/graph.png" width="500">

Test lexer:
| Without errors | With errors |
|----------------|-------------|
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/correct_lexer_example_1.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/incorrect_lexer_example_1.png" width="500"> |
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/correct_lexer_example_2.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/incorrect_lexer_example_1.png" width="500"> |


Test parser:
| Without errors | With errors |
|----------------|-------------|
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/correct_parser_example_1.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/incorrect_parser_example_1.png" width="500"> |
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/correct_parser_example_2.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/incorrect_parser_example_1.png" width="500"> |

Internal form of program presentation (tetrads and POLIZ):
| tetrads with poliz | tetrads without poliz |
|----------------|-------------|
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/with_poliz.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/without_poliz.png" width="500">

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

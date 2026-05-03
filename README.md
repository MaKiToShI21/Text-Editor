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
9. **[Title and Objective of the Laboratory Work 7](#title-and-objective-of-the-laboratory-work-7)**
10. **[User Manual](#user-manual)**

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

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/grammar.png" width="400">

Examples of correct strings:
1. (17 + 3 * 5) % 7 - 2
2. a1 + b2 * (c3 - 4)
3. 8 / 2 + 10 % 3

Lexer diagram:

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/state_diagram.png" width="400">

Recursive descent scheme for a parser:

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/graph.png" width="200">

Test lexer:
| Without errors | With errors |
|----------------|-------------|
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/correct_lexer_example_1.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/incorrect_lexer_example_1.png" width="500"> |
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/correct_lexer_example_2.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/incorrect_lexer_example_2.png" width="500"> |

Test parser:
| Without errors | With errors |
|----------------|-------------|
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/correct_parser_example_1.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/incorrect_parser_example_1.png" width="500"> |
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/correct_parser_example_2.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/incorrect_parser_example_2.png" width="500"> |

Internal form of program presentation (tetrads and POLIZ):
| tetrads + poliz + value | tetrads + poliz - value | incorrect line |
|-------------------------|-------------------------|----------------|
| <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/with_value.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/without_value.png" width="500"> | <img src="https://github.com/MaKiToShI21/Text-Editor/blob/internal-representation-of-the-program/images/lab6/nothing.png" width="500"> | 

<h2 align="center">Лабораторная работа №7</h2>

**Лабораторная работа №7.** Исследование инфраструктуры Clang/LLVM: AST, LLVM IR, оптимизации и граф потока управления

**Цель работы:** Изучить инфраструктуру компилятора Clang/LLVM: получить абстрактное синтаксическое дерево (AST), сгенерировать LLVM IR на различных уровнях оптимизации, применить оптимизации и построить граф потока управления (CFG) для программы на C++.

**Постановка задачи:** С помощью инструментов Clang/LLVM проанализировать программу на C++, работающую с комплексными числами: получить её AST, сгенерировать и сравнить LLVM IR до и после оптимизации, а также визуализировать CFG.

---

### 1. Общая часть работы

**1.1. Установка и подготовка среды**

Работа выполнялась в среде Ubuntu 22.04. Установлены следующие инструменты:
- `clang` — компилятор языка C/C++;
- `llvm` — инструменты анализа и оптимизации кода;
- `opt` — инструмент для работы с LLVM IR и применения оптимизаций;
- `Graphviz` — инструмент для визуализации графов.

```bash
sudo apt install clang llvm graphviz
```

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab7/install_libraries.png" width="550">

**1.2. Исходный код**

Программа на языке C++:

```cpp
#include <iostream>
#include <complex>

int main() {
    std::complex<double> z1(3.0, 4.0);
    std::complex<double> z2(1.0, 2.0);
    auto z3 = z1 * z2 + z1;
    std::cout << z3.real() << " " << z3.imag() << std::endl;
    return 0;
}
```

Программа демонстрирует работу с пользовательскими операторами `*` и `+` для комплексных чисел. Сохранена в файл `complex.cpp`.

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab7/complex_cpp.png" width="550">

**1.3. Получение AST**

Команда:
```bash
clang++ -Xclang -ast-dump -fsyntax-only complex.cpp
```

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab7/ast_dump.png" width="550">

Ключевые наблюдения:
- Функция `main` представлена узлом `FunctionDecl`.
- Переменные `z1`, `z2` инициализируются через `CXXConstructExpr` (вызов конструктора).
- Операторы `*` и `+` представлены узлами `CXXOperatorCallExpr`, что доказывает: пользовательские операторы являются вызовами функций, а не встроенными операциями.
- Для выражения `z1 * z2 + z1` AST имеет иерархическую структуру: сначала умножение, затем сложение.

**1.4. Генерация LLVM IR**

Неоптимизированный IR (`-O0`):
```bash
clang++ -O0 -S -emit-llvm complex.cpp -o complex_O0.ll
```

В неоптимизированном IR наблюдаются следующие характерные черты:
- Все переменные (`z1`, `z2`, `z3`) размещены в памяти через `alloca`;
- Множество операций `load` и `store` для работы с переменными;
- Операторы `*` и `+` вызываются как обычные функции.

На уровне `-O0` компилятор не выполняет никаких оптимизаций. Пользовательские операторы компилируются в обычные вызовы функций, что делает код наглядным для анализа.

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab7/ir_O0.png" width="550">

Оптимизированный IR (`-O2`):
```bash
clang++ -O2 -S -emit-llvm complex.cpp -o complex_O2.ll
```

В файле с IR после оптимизации:
- Все функции `operator*` и `operator+` исчезли — они были встроены (`-inline`) и их вычисления свёрнуты (`-constprop`);
- Никаких инструкций `alloca`, `store`, `load` — всё удалено оптимизациями `-mem2reg`, `-sroa`, `-dce`;
- Вместо вызовов функций — прямые арифметические инструкции `fmul`, `fadd`, `fsub`.

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab7/ir_O2.png" width="550">

Сравнение двух файлов:
```bash
diff complex_O0.ll complex_O2.ll
```

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab7/ir_diff.png" width="550">

После оптимизации произошли следующие изменения:
- Переменные типа `alloca` были удалены;
- Код переведён в SSA-форму;
- Оптимизация улучшила читаемость и упростила поток управления.

Уже на уровне `-O2` компилятор LLVM способен «заглянуть внутрь» функций-операторов комплексных чисел и оптимизировать их так же эффективно, как и встроенные типы.

**1.5. Граф потока управления программы**

Команды:
```bash
# Генерация оптимизированного LLVM IR
clang++ -O2 -S -emit-llvm complex.cpp -o complex_O0.ll
# Генерация .dot-файлов CFG для функций
opt -dot-cfg -disable-output complex_O0.ll
# Преобразование .dot-файлов в .png с помощью Graphviz
dot -Tpng .main.dot -o cfg_main_O2.png
# Просмотр CFG
xdg-open cfg_main_O2.png
```

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab7/cfg_main_O2.png" width="400">

>[!NOTE]
>Утилита `opt` не создаёт файл `.main.dot` для неоптимизированной версии (`-O0`). При уровне оптимизации `-O0` в IR-файле сохраняется весь служебный код C++: функции глобальной инициализации (`__cxx_global_var_init`), конструкторы модуля (`_GLOBAL__sub_I_complex.cpp`), код инициализации `std::cout` и `std::endl`. Функция `main` оказывается «окружена» этим служебным кодом, что мешает `opt` выделить её в отдельный `.dot`-файл. Это особенность работы `opt` с C++ кодом, содержащим глобальные объекты, а не ошибка выполнения команд.

В LLVM каждый граф потока управления (CFG) строится на уровне функции, поскольку структура управления всегда локальна для тела функции. Для получения полного представления о программе нужно построить CFG для всех функций и анализировать их совокупность.

**1.6. Выводы**

- С помощью Clang можно получить полную структуру AST и LLVM IR, а также построить CFG.
- LLVM предоставляет гибкие инструменты анализа и оптимизации кода.
- Промежуточное представление (IR) удобно для написания компиляторных трансформаций.
- На примере комплексных чисел показано, как пользовательские операторы (синтаксический сахар) преобразуются в вызовы функций на уровне AST и IR, а затем могут быть полностью оптимизированы (встроены) на уровнях `-O2` и выше.

---

### 2. Дополнительное задание: локальные оптимизации

Исходная конструкция:
```cpp
#include <complex>
void foo() {
    std::complex<double> my_complex(-10.0, 2.0);
}
```

**Построение AST конструкции:**

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab7/additional_ast.png" width="550">

**Трёхадресный код (TAC):**
```
t1 = -10.0
t2 = 2.0
my_complex.real = t1
my_complex.imag = t2
```

**LLVM IR (неоптимизированный):**
```llvm
%my_complex = alloca %"class.std::complex", align 8
%0 = bitcast %"class.std::complex"* %my_complex to { double, double }*
%1 = getelementptr inbounds { double, double }, { double, double }* %0, i32 0, i32 0
store double -1.000000e+01, double* %1, align 8
%2 = getelementptr inbounds { double, double }, { double, double }* %0, i32 0, i32 1
store double 2.000000e+00, double* %2, align 8
```

**Оптимизация №1: Свёртка нулевой мнимой части**

Если мнимая часть комплексного числа равна нулю, то хранение нуля является избыточным. Данная оптимизация заменяет комплексное число с нулевой мнимой частью на обычное вещественное число в IR — удаляет инструкцию `store` для мнимой части.

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab7/scheme_1.png" width="550">

Правило преобразования: если `imag == 0.0`, то инструкция `store` для мнимой части может быть удалена.

```llvm
; Входной IR (с мнимой частью = 0.0)
store double -1.000000e+01, double* %1, align 8
store double 0.000000e+00, double* %2, align 8   ; ← избыточная инструкция

; Выходной IR (после оптимизации)
%my_complex_real = alloca double, align 8
store double -1.000000e+01, double* %my_complex_real, align 8
; мнимая часть не хранится (подразумевается 0.0)
```

Тестовый пример: `std::complex<double> my_complex(-10.0, 0.0);`

| До оптимизации | После оптимизации |
|----------------|-------------------|
| Две store инструкции (real и imag) | Одна store инструкция (только real) |

**Оптимизация №2: Упрощение сложения с нулём**

При выполнении операции сложения комплексных чисел, если одно из слагаемых имеет нулевую мнимую часть, операцию можно упростить. Данная оптимизация заменяет `fadd %x, 0.0` на `%x`, устраняя избыточную арифметическую инструкцию.

<img src="https://github.com/MaKiToShI21/Text-Editor/blob/main/images/lab7/scheme_2.png" width="550">

Правило преобразования:
```
fadd %x, 0.0  →  %x
fadd 0.0, %x  →  %x
```

```llvm
; Входной IR
%imag1 = load double, double* %z1_imag, align 8
%imag2 = load double, double* %z2_imag, align 8   ; imag2 = 0.0
%imag_sum = fadd double %imag1, %imag2            ; избыточная операция

; Выходной IR (после оптимизации)
%imag1 = load double, double* %z1_imag, align 8
; загрузка imag2 пропущена
%imag_sum = %imag1                                ; прямая передача
```

Тестовый пример:
```cpp
std::complex<double> z1(3.0, 4.0);
std::complex<double> z2(5.0, 0.0);   // мнимая часть = 0
auto z3 = z1 + z2;
```

| До оптимизации | После оптимизации |
|----------------|-------------------|
| ```%sum = fadd double %imag1, %imag2 (где %imag2 = 0.0)``` | ```%sum = %imag1``` |
| Две операции: `fadd` для `real` и `fadd` для `imag` | Одна операция `fadd` только для `real` |

**Вывод:** В ходе выполнения дополнительного задания были реализованы две локальные оптимизации для конструкций с комплексными числами:
1. **Свёртка нулевой мнимой части** — позволяет сократить память и количество инструкций при хранении комплексных чисел с нулевой мнимой частью.
2. **Упрощение сложения с нулём** — устраняет избыточные арифметические операции, повышая производительность.

Обе оптимизации являются локальными (работают в пределах одной конструкции/инструкции), сохраняют семантику и упрощают код.

---

### 3. Ответы на контрольные вопросы

**1. Что такое Clang, и какова его роль в процессе компиляции программ?**
Clang — это фронтенд компилятора LLVM для языков C, C++ и Objective-C. Его роль: выполнение лексического, синтаксического и семантического анализа исходного кода, построение AST, генерация LLVM IR и выдача диагностических сообщений (ошибки, предупреждения).

**2. Что представляет собой LLVM и как он используется в современных компиляторах?**
LLVM (Low Level Virtual Machine) — это набор модульных инструментов для компиляции, оптимизации и генерации машинного кода. Он используется как промежуточный слой между фронтендом (Clang) и бэкендом. Современные компиляторы (Clang, Rustc, Swift) используют LLVM для оптимизаций и генерации кода под различные архитектуры (x86, ARM, RISC-V).

**3. Чем отличается AST от промежуточного представления LLVM IR?**

| | AST | LLVM IR |
|---|---|---|
| Уровень | Высокоуровневое, близко к исходному коду | Низкоуровневое, похоже на ассемблер |
| Сохраняет | Имена переменных, типы, структуру языка | Упрощённые типы, виртуальные регистры |
| Используется для | Семантического анализа | Оптимизаций |
| Генерация машинного кода | Не пригоден напрямую | Легко транслируется |

**4. Для чего необходимо промежуточное представление (IR) в процессе компиляции?**
IR необходимо для: независимости от языка (один IR от разных языков C++, Rust, Swift), независимости от платформы (один IR под разные архитектуры x86, ARM), модульности оптимизаций и упрощения анализа через SSA-форму.

**5. Что делает инструкция `alloca` в LLVM IR, и зачем она используется в функциях?**
`alloca` выделяет память на стеке для локальной переменной. Используется в неоптимизированном коде (`-O0`) для хранения переменных в памяти, позволяя легко отлаживать код. При оптимизациях (`-O2`) `alloca` заменяется на регистры (SSA-форма) через оптимизацию `-mem2reg`.

**6. Зачем нужна оптимизация кода в компиляторе, и какие основные цели она преследует?**

| Цель | Описание |
|---|---|
| Увеличение скорости | Уменьшение времени выполнения |
| Уменьшение размера | Сжатие кода для встраиваемых систем |
| Снижение энергопотребления | Меньше инструкций → меньше энергии |
| Устранение избыточности | Удаление мёртвого кода, свёртка констант |

**7. Что такое SSA-форма и почему она важна при оптимизации программ?**
SSA (Static Single Assignment) — форма представления кода, где каждая переменная присваивается ровно один раз. При повторном присваивании создаётся новая «версия» переменной (например, `x1`, `x2`). SSA важна, потому что упрощает анализ потока данных, позволяет выполнять глобальные оптимизации (GVN, constant propagation) и облегчает определение живых переменных.

**8. Что такое граф потока управления (CFG) и как он помогает анализировать поведение программы?**
CFG (Control Flow Graph) — ориентированный граф, где узлы — базовые блоки (линейные последовательности инструкций без переходов), а рёбра — переходы между блоками (`if`, `goto`, вызовы). CFG помогает визуализировать структуру программы, анализировать достижимость блоков и выполнять оптимизации (удаление мёртвого кода, свёртка условных переходов).

**9. Как устроено представление арифметических операций в LLVM IR?**

| Тип операндов | Инструкции |
|---|---|
| Целые числа | `add`, `sub`, `mul`, `div`, `rem` |
| Числа с плавающей точкой | `fadd`, `fsub`, `fmul`, `fdiv`, `frem` |

```llvm
%sum_int   = add  i32    %a, %b   ; сложение целых 32-битных
%sum_float = fadd double %x, %y   ; сложение double
%mul       = fmul double %a, %b   ; умножение double
```

**10. Почему функции в LLVM IR обычно представляют собой отдельные единицы анализа и оптимизации?**
Функции имеют чёткие границы (вход, выход, локальные переменные), могут анализироваться и оптимизироваться изолированно, поддерживают встраивание (inlining) — замену вызова функции её телом, а также упрощают параллельную компиляцию.

**11. Что происходит с функцией в LLVM IR, если она вызывается один раз и очень короткая?**
Такая функция встраивается (inlined). Компилятор удаляет инструкцию `call`, копирует тело функции в место вызова и применяет дополнительные оптимизации (`-constprop`, `-mem2reg`, `-dce`). Пример: функция `square(int x) { return x * x; }` при вызове `square(5)` будет заменена на `25` (свёртка констант).

**12. Какие преимущества даёт использование IR и CFG для автоматических оптимизаций по сравнению с анализом исходного текста на C?**

| Анализ исходного C-кода | Анализ LLVM IR |
|---|---|
| Сложный парсинг | Простой, линейный формат |
| Много синтаксического сахара | Унифицированное представление |
| Нет SSA-формы (переменные перезаписываются) | SSA-форма (каждая переменная — один раз) |
| Типы абстрактные (структуры, классы) | Типы низкоуровневые (указатели, числа) |
| CFG нужно строить заново | CFG легко извлекается из IR |

Главное преимущество: IR уже привёл код к простому, унифицированному виду. Оптимизациям не нужно «понимать» особенности языка C++ (перегрузку операторов, шаблоны, наследование) — всё уже развёрнуто в простые инструкции. CFG даёт чёткую структуру, которую можно алгоритмически анализировать.

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

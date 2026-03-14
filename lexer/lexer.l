%{
#include <stdio.h>

#define KW_INT       1
#define KW_FLOAT     2
#define KW_DOUBLE    3
#define KW_STD       4
#define KW_COMPLEX   5
#define IDENTIFIER   6
#define SPACE        7
#define INTEGER      8
#define FLOAT        9
#define DOUBLE_COLON 10
#define OPEN_ANGLE   11
#define CLOSE_ANGLE  12
#define OPEN_PAREN   13
#define CLOSE_PAREN  14
#define MINUS        15
#define COMMA        16
#define SEMICOLON    17

int line_num = 1;
int column_num = 1;
%}

%option noyywrap

%%
"int"       { printf("[%d:%d-%d] - code=%d: keyword int\n", 
               line_num, column_num, column_num + 2, KW_INT); column_num += 3; }
"float"     { printf("[%d:%d-%d] - code=%d: keyword float\n", 
               line_num, column_num, column_num + 4, KW_FLOAT); column_num += 5; }
"double"    { printf("[%d:%d-%d] - code=%d: keyword double\n", 
               line_num, column_num, column_num + 5, KW_DOUBLE); column_num += 6; }
"std"       { printf("[%d:%d-%d] - code=%d: keyword std\n", 
               line_num, column_num, column_num + 2, KW_STD); column_num += 3; }
"complex"   { printf("[%d:%d-%d] - code=%d: keyword complex\n", 
               line_num, column_num, column_num + 6, KW_COMPLEX); column_num += 7; }

[a-zA-Z_][a-zA-Z0-9_]* { 
    printf("[%d:%d-%d] - code=%d: identifier %s\n", 
           line_num, column_num, column_num + yyleng - 1, IDENTIFIER, yytext); 
    column_num += yyleng; 
}

[ \t]+      { 
    printf("[%d:%d-%d] - code=%d: space\n", 
           line_num, column_num, column_num, SPACE); 
    column_num += yyleng; 
}

[0-9]+\.[0-9]+ { 
    printf("[%d:%d-%d] - code=%d: float %s\n", 
           line_num, column_num, column_num + yyleng - 1, FLOAT, yytext); 
    column_num += yyleng; 
}
[0-9]+      { 
    printf("[%d:%d-%d] - code=%d: integer %s\n", 
           line_num, column_num, column_num + yyleng, INTEGER, yytext); 
    column_num += yyleng; 
}

"::"        { 
    printf("[%d:%d-%d] - code=%d: double colon ::\n", 
           line_num, column_num, column_num + 1, DOUBLE_COLON); 
    column_num += 2; 
}
"<"         { 
    printf("[%d:%d-%d] - code=%d: open angle <\n", 
           line_num, column_num, column_num, OPEN_ANGLE); 
    column_num += 1; 
}
">"         { 
    printf("[%d:%d-%d] - code=%d: close angel >\n", 
           line_num, column_num, column_num, CLOSE_ANGLE); 
    column_num += 1; 
}
"("         { 
    printf("[%d:%d-%d] - code=%d: open paren (\n", 
           line_num, column_num, column_num, OPEN_PAREN); 
    column_num += 1; 
}
")"         { 
    printf("[%d:%d-%d] - code=%d: close paren )\n", 
           line_num, column_num, column_num, CLOSE_PAREN);
    column_num += 1; 
}
"-"         { 
    printf("[%d:%d-%d] - code=%d: minus -\n", 
           line_num, column_num, column_num, MINUS); 
    column_num += 1; 
}
","         { 
    printf("[%d:%d-%d] - code=%d: comma ,\n", 
           line_num, column_num, column_num, COMMA); 
    column_num += 1; 
}
";"         { 
    printf("[%d:%d-%d] - code=%d: semicolon ;\n", 
           line_num, column_num, column_num, SEMICOLON); 
    column_num += 1; 
}

\n          { line_num++; column_num = 1; }

.           { 
    printf("[%d:%d-%d] - ERROR: invalid character %s\n", 
           line_num, column_num, column_num, yytext); 
    column_num += 1; 
}

%%

int main() {
    printf("line:start-end code=code: description\n\n");
    yylex();
    return 0;
}
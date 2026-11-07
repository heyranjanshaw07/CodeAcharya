/**
 * CodeAcharya Monaco Editor VS Code-Style IntelliSense & Auto-Completion Engine
 *
 * Provides:
 * 1. Rich built-in IntelliSense, APIs & snippets for Python 3, C, C++20, and Java (OpenJDK 21).
 * 2. Real-time extraction of user-declared functions with parameter placeholders.
 * 3. Extraction of declared variables, constants, and function parameters (with active-scope priority).
 * 4. Context-aware signature help & documentation on '(' and ',' trigger characters.
 * 5. Member-access auto-completion on '.' and '::'.
 * 6. Native Monaco CompletionItemProvider & SignatureHelpProvider integration.
 * 7. Safe idempotent registration and clean IDisposable lifecycle management (no memory leaks / duplicates).
 * 8. Strict lock-state enforcement (never bypasses read-only or fullscreen restriction).
 */

// Track registered disposables to guarantee clean unregistration and avoid duplicate providers across re-renders
let activeIntelliSenseDisposables = [];
let isIntelliSenseInitialized = false;

// =============================================================================
// 1. BUILT-IN COMPLETIONS CATALOG (Python, C, C++, Java)
// =============================================================================

export const BUILTIN_COMPLETIONS = {
  python: [
    // Built-in functions
    {
      label: 'print',
      kind: 'Function',
      detail: 'print(*values, sep=" ", end="\\n")',
      documentation: 'Prints values to a stream, or to sys.stdout by default.',
      insertText: 'print(${1:object})$0',
      isSnippet: true
    },
    {
      label: 'len',
      kind: 'Function',
      detail: 'len(s) -> int',
      documentation: 'Return the number of items in a container (string, list, tuple, dict, set).',
      insertText: 'len(${1:container})$0',
      isSnippet: true
    },
    {
      label: 'range',
      kind: 'Function',
      detail: 'range(stop) or range(start, stop[, step])',
      documentation: 'Return an object that produces a sequence of integers from start (inclusive) to stop (exclusive).',
      insertText: 'range(${1:stop})$0',
      isSnippet: true
    },
    {
      label: 'enumerate',
      kind: 'Function',
      detail: 'enumerate(iterable, start=0)',
      documentation: 'Return an enumerate object yielding (index, value) pairs.',
      insertText: 'enumerate(${1:iterable})$0',
      isSnippet: true
    },
    {
      label: 'zip',
      kind: 'Function',
      detail: 'zip(*iterables, strict=False)',
      documentation: 'Iterate over several iterables in parallel, producing tuples with an item from each one.',
      insertText: 'zip(${1:iter1}, ${2:iter2})$0',
      isSnippet: true
    },
    {
      label: 'sorted',
      kind: 'Function',
      detail: 'sorted(iterable, *, key=None, reverse=False) -> list',
      documentation: 'Return a new list containing all items from the iterable in ascending order.',
      insertText: 'sorted(${1:iterable})$0',
      isSnippet: true
    },
    {
      label: 'sum',
      kind: 'Function',
      detail: 'sum(iterable, /, start=0)',
      documentation: 'Return the sum of a "start" value plus an iterable of numbers.',
      insertText: 'sum(${1:iterable})$0',
      isSnippet: true
    },
    {
      label: 'min',
      kind: 'Function',
      detail: 'min(iterable) or min(arg1, arg2, ...)',
      documentation: 'Return the smallest item in an iterable or the smallest of two or more arguments.',
      insertText: 'min(${1:a}, ${2:b})$0',
      isSnippet: true
    },
    {
      label: 'max',
      kind: 'Function',
      detail: 'max(iterable) or max(arg1, arg2, ...)',
      documentation: 'Return the largest item in an iterable or the largest of two or more arguments.',
      insertText: 'max(${1:a}, ${2:b})$0',
      isSnippet: true
    },
    {
      label: 'abs',
      kind: 'Function',
      detail: 'abs(x) -> number',
      documentation: 'Return the absolute value of the argument.',
      insertText: 'abs(${1:x})$0',
      isSnippet: true
    },
    {
      label: 'round',
      kind: 'Function',
      detail: 'round(number, ndigits=None)',
      documentation: 'Round a number to a given precision in decimal digits.',
      insertText: 'round(${1:number}${2:, ndigits})$0',
      isSnippet: true
    },
    {
      label: 'isinstance',
      kind: 'Function',
      detail: 'isinstance(object, classinfo) -> bool',
      documentation: 'Return whether an object is an instance of a class or of a subclass thereof.',
      insertText: 'isinstance(${1:object}, ${2:classinfo})$0',
      isSnippet: true
    },
    {
      label: 'issubclass',
      kind: 'Function',
      detail: 'issubclass(class, classinfo) -> bool',
      documentation: 'Return whether "class" is a derived class of "classinfo".',
      insertText: 'issubclass(${1:class}, ${2:classinfo})$0',
      isSnippet: true
    },
    {
      label: 'type',
      kind: 'Function',
      detail: 'type(object) -> type',
      documentation: 'Return the type of an object.',
      insertText: 'type(${1:object})$0',
      isSnippet: true
    },
    {
      label: 'any',
      kind: 'Function',
      detail: 'any(iterable) -> bool',
      documentation: 'Return True if bool(x) is True for any x in the iterable. If the iterable is empty, return False.',
      insertText: 'any(${1:iterable})$0',
      isSnippet: true
    },
    {
      label: 'all',
      kind: 'Function',
      detail: 'all(iterable) -> bool',
      documentation: 'Return True if bool(x) is True for all values x in the iterable. If iterable is empty, return True.',
      insertText: 'all(${1:iterable})$0',
      isSnippet: true
    },
    {
      label: 'int',
      kind: 'Function',
      detail: 'int(x=0, base=10) -> int',
      documentation: 'Convert a number or string to an integer.',
      insertText: 'int(${1:x})$0',
      isSnippet: true
    },
    {
      label: 'float',
      kind: 'Function',
      detail: 'float(x=0.0) -> float',
      documentation: 'Convert a string or number to a floating point number.',
      insertText: 'float(${1:x})$0',
      isSnippet: true
    },
    {
      label: 'str',
      kind: 'Function',
      detail: 'str(object="") -> str',
      documentation: 'Create a new string object from the given object.',
      insertText: 'str(${1:object})$0',
      isSnippet: true
    },
    {
      label: 'bool',
      kind: 'Function',
      detail: 'bool(x) -> bool',
      documentation: 'Returns True when the argument x is true, False otherwise.',
      insertText: 'bool(${1:x})$0',
      isSnippet: true
    },
    {
      label: 'list',
      kind: 'Function',
      detail: 'list(iterable=()) -> list',
      documentation: 'Built-in mutable sequence constructor.',
      insertText: 'list(${1:iterable})$0',
      isSnippet: true
    },
    {
      label: 'dict',
      kind: 'Function',
      detail: 'dict(**kwargs) -> dict',
      documentation: 'Built-in mapping type constructor.',
      insertText: 'dict(${1:iterable})$0',
      isSnippet: true
    },
    {
      label: 'set',
      kind: 'Function',
      detail: 'set(iterable=()) -> set',
      documentation: 'Built-in mutable unordered collection of unique elements.',
      insertText: 'set(${1:iterable})$0',
      isSnippet: true
    },
    {
      label: 'tuple',
      kind: 'Function',
      detail: 'tuple(iterable=()) -> tuple',
      documentation: 'Built-in immutable sequence constructor.',
      insertText: 'tuple(${1:iterable})$0',
      isSnippet: true
    },
    {
      label: 'map',
      kind: 'Function',
      detail: 'map(function, *iterables)',
      documentation: 'Make an iterator that computes the function using arguments from each of the iterables.',
      insertText: 'map(${1:function}, ${2:iterable})$0',
      isSnippet: true
    },
    {
      label: 'filter',
      kind: 'Function',
      detail: 'filter(function, iterable)',
      documentation: 'Construct an iterator from elements of iterable for which function returns True.',
      insertText: 'filter(${1:function}, ${2:iterable})$0',
      isSnippet: true
    },
    {
      label: 'reversed',
      kind: 'Function',
      detail: 'reversed(sequence)',
      documentation: 'Return a reverse iterator over the values of the given sequence.',
      insertText: 'reversed(${1:sequence})$0',
      isSnippet: true
    },
    {
      label: 'open',
      kind: 'Function',
      detail: 'open(file, mode="r", encoding=None)',
      documentation: 'Open file and return a stream.',
      insertText: 'open(${1:"filename"}, "${2:r}")$0',
      isSnippet: true
    },
    {
      label: 'input',
      kind: 'Function',
      detail: 'input(prompt="") -> str',
      documentation: 'Read a string from standard input. The trailing newline is stripped.',
      insertText: 'input(${1:"Enter: "})$0',
      isSnippet: true
    },

    // Standard Library Helpers
    {
      label: 'math.sqrt',
      kind: 'Function',
      detail: 'math.sqrt(x) -> float',
      documentation: 'Return the square root of x.',
      insertText: 'math.sqrt(${1:x})$0',
      isSnippet: true
    },
    {
      label: 'math.floor',
      kind: 'Function',
      detail: 'math.floor(x) -> int',
      documentation: 'Return the floor of x as an Integral.',
      insertText: 'math.floor(${1:x})$0',
      isSnippet: true
    },
    {
      label: 'math.ceil',
      kind: 'Function',
      detail: 'math.ceil(x) -> int',
      documentation: 'Return the ceiling of x as an Integral.',
      insertText: 'math.ceil(${1:x})$0',
      isSnippet: true
    },
    {
      label: 'math.gcd',
      kind: 'Function',
      detail: 'math.gcd(*integers) -> int',
      documentation: 'Greatest Common Divisor.',
      insertText: 'math.gcd(${1:a}, ${2:b})$0',
      isSnippet: true
    },
    {
      label: 'collections.defaultdict',
      kind: 'Class',
      detail: 'defaultdict(default_factory=None, /[, ...])',
      documentation: 'Dict-like object that provides a default value for non-existent keys.',
      insertText: 'defaultdict(${1:list})$0',
      isSnippet: true
    },
    {
      label: 'collections.Counter',
      kind: 'Class',
      detail: 'Counter(iterable=None)',
      documentation: 'Dict subclass for counting hashable items.',
      insertText: 'Counter(${1:iterable})$0',
      isSnippet: true
    },
    {
      label: 'collections.deque',
      kind: 'Class',
      detail: 'deque(iterable=(), maxlen=None)',
      documentation: 'Fast O(1) double-ended queue.',
      insertText: 'deque(${1:iterable})$0',
      isSnippet: true
    },
    {
      label: 'heapq.heappush',
      kind: 'Function',
      detail: 'heapq.heappush(heap, item)',
      documentation: 'Push item onto heap, maintaining the heap invariant.',
      insertText: 'heapq.heappush(${1:heap}, ${2:item})$0',
      isSnippet: true
    },
    {
      label: 'heapq.heappop',
      kind: 'Function',
      detail: 'heapq.heappop(heap) -> item',
      documentation: 'Pop the smallest item off the heap, maintaining the heap invariant.',
      insertText: 'heapq.heappop(${1:heap})$0',
      isSnippet: true
    },
    {
      label: 'heapq.heapify',
      kind: 'Function',
      detail: 'heapq.heapify(x)',
      documentation: 'Transform list x into a heap in-place, in O(n) time.',
      insertText: 'heapq.heapify(${1:x})$0',
      isSnippet: true
    },
    {
      label: 'bisect.bisect_left',
      kind: 'Function',
      detail: 'bisect_left(a, x, lo=0, hi=len(a))',
      documentation: 'Locate the insertion point for x in a to maintain sorted order.',
      insertText: 'bisect_left(${1:a}, ${2:x})$0',
      isSnippet: true
    },
    {
      label: 'sys.maxsize',
      kind: 'Constant',
      detail: 'sys.maxsize: int',
      documentation: 'An integer giving the maximum value a variable of type Py_ssize_t can take.',
      insertText: 'sys.maxsize'
    },

    // Python Snippets & Control Flow
    {
      label: 'def',
      kind: 'Snippet',
      detail: 'Function definition snippet',
      documentation: 'Defines a Python function with parameter placeholders.',
      insertText: 'def ${1:function_name}(${2:params}):\n\t${0:pass}',
      isSnippet: true
    },
    {
      label: 'defmain',
      kind: 'Snippet',
      detail: 'Standard main entrypoint snippet',
      documentation: 'Defines main() and the __name__ == "__main__" guard.',
      insertText: 'def main():\n\t${0:pass}\n\nif __name__ == "__main__":\n\tmain()',
      isSnippet: true
    },
    {
      label: 'class',
      kind: 'Snippet',
      detail: 'Class declaration snippet',
      documentation: 'Creates a Python class with __init__ constructor.',
      insertText: 'class ${1:ClassName}:\n\tdef __init__(self, ${2:params}):\n\t\tself.${3:prop} = ${3:prop}\n\t\t${0:pass}',
      isSnippet: true
    },
    {
      label: 'if',
      kind: 'Snippet',
      detail: 'if statement snippet',
      documentation: 'Conditional if block.',
      insertText: 'if ${1:condition}:\n\t${0:pass}',
      isSnippet: true
    },
    {
      label: 'ifelse',
      kind: 'Snippet',
      detail: 'if-else statement snippet',
      documentation: 'Conditional if-else block.',
      insertText: 'if ${1:condition}:\n\t${2:pass}\nelse:\n\t${0:pass}',
      isSnippet: true
    },
    {
      label: 'elif',
      kind: 'Snippet',
      detail: 'elif statement snippet',
      documentation: 'Conditional elif block.',
      insertText: 'elif ${1:condition}:\n\t${0:pass}',
      isSnippet: true
    },
    {
      label: 'for',
      kind: 'Snippet',
      detail: 'for-in loop snippet',
      documentation: 'Iterates over elements in an iterable.',
      insertText: 'for ${1:item} in ${2:iterable}:\n\t${0:pass}',
      isSnippet: true
    },
    {
      label: 'forrange',
      kind: 'Snippet',
      detail: 'for i in range(n) loop snippet',
      documentation: 'Iterates over numerical indices using range().',
      insertText: 'for ${1:i} in range(${2:n}):\n\t${0:pass}',
      isSnippet: true
    },
    {
      label: 'forenum',
      kind: 'Snippet',
      detail: 'for i, val in enumerate() snippet',
      documentation: 'Iterates over indices and values simultaneously.',
      insertText: 'for ${1:i}, ${2:val} in enumerate(${3:iterable}):\n\t${0:pass}',
      isSnippet: true
    },
    {
      label: 'while',
      kind: 'Snippet',
      detail: 'while loop snippet',
      documentation: 'Loop while condition evaluates to True.',
      insertText: 'while ${1:condition}:\n\t${0:pass}',
      isSnippet: true
    },
    {
      label: 'try',
      kind: 'Snippet',
      detail: 'try-except block snippet',
      documentation: 'Exception handling try-except construct.',
      insertText: 'try:\n\t${1:pass}\nexcept ${2:Exception} as ${3:e}:\n\t${0:pass}',
      isSnippet: true
    },
    {
      label: 'with',
      kind: 'Snippet',
      detail: 'with context manager snippet',
      documentation: 'Executes block with context manager cleanups.',
      insertText: 'with open(${1:"file.txt"}, "${2:r}") as ${3:f}:\n\t${0:pass}',
      isSnippet: true
    },
    {
      label: 'listcomp',
      kind: 'Snippet',
      detail: 'List comprehension snippet',
      documentation: 'Generates a new list based on existing sequence.',
      insertText: '[${1:x} for ${1:x} in ${2:iterable} if ${3:condition}]',
      isSnippet: true
    },
    {
      label: 'lambda',
      kind: 'Snippet',
      detail: 'Anonymous lambda expression',
      documentation: 'Creates an inline lambda function.',
      insertText: 'lambda ${1:x}: ${0:x}',
      isSnippet: true
    }
  ],

  c: [
    // Standard I/O & Memory Functions
    {
      label: 'printf',
      kind: 'Function',
      detail: 'int printf(const char *format, ...)',
      documentation: 'Prints formatted output to stdout.',
      insertText: 'printf("${1:%s\\n}", ${2:var});$0',
      isSnippet: true
    },
    {
      label: 'scanf',
      kind: 'Function',
      detail: 'int scanf(const char *format, ...)',
      documentation: 'Reads formatted input from stdin.',
      insertText: 'scanf("${1:%d}", &${2:var});$0',
      isSnippet: true
    },
    {
      label: 'puts',
      kind: 'Function',
      detail: 'int puts(const char *s)',
      documentation: 'Writes string s and a trailing newline to stdout.',
      insertText: 'puts(${1:"string"});$0',
      isSnippet: true
    },
    {
      label: 'malloc',
      kind: 'Function',
      detail: 'void* malloc(size_t size)',
      documentation: 'Allocates uninitialized dynamic memory on the heap.',
      insertText: '(${1:type}*)malloc(${2:size} * sizeof(${1:type}))$0',
      isSnippet: true
    },
    {
      label: 'calloc',
      kind: 'Function',
      detail: 'void* calloc(size_t num, size_t size)',
      documentation: 'Allocates and zeroes out memory for an array.',
      insertText: '(${1:type}*)calloc(${2:num}, sizeof(${1:type}))$0',
      isSnippet: true
    },
    {
      label: 'realloc',
      kind: 'Function',
      detail: 'void* realloc(void *ptr, size_t new_size)',
      documentation: 'Reallocates previously allocated heap memory buffer.',
      insertText: 'realloc(${1:ptr}, ${2:new_size})$0',
      isSnippet: true
    },
    {
      label: 'free',
      kind: 'Function',
      detail: 'void free(void *ptr)',
      documentation: 'Deallocates memory block previously allocated by malloc/calloc/realloc.',
      insertText: 'free(${1:ptr});$0',
      isSnippet: true
    },
    {
      label: 'strlen',
      kind: 'Function',
      detail: 'size_t strlen(const char *str)',
      documentation: 'Calculates length of null-terminated string.',
      insertText: 'strlen(${1:str})$0',
      isSnippet: true
    },
    {
      label: 'strcpy',
      kind: 'Function',
      detail: 'char* strcpy(char *dest, const char *src)',
      documentation: 'Copies string src into dest buffer.',
      insertText: 'strcpy(${1:dest}, ${2:src});$0',
      isSnippet: true
    },
    {
      label: 'strcmp',
      kind: 'Function',
      detail: 'int strcmp(const char *s1, const char *s2)',
      documentation: 'Compares two strings lexicographically.',
      insertText: 'strcmp(${1:s1}, ${2:s2})$0',
      isSnippet: true
    },
    {
      label: 'memset',
      kind: 'Function',
      detail: 'void* memset(void *s, int c, size_t n)',
      documentation: 'Fills first n bytes of memory area with constant byte c.',
      insertText: 'memset(${1:ptr}, ${2:0}, ${3:sizeof(arr)});$0',
      isSnippet: true
    },
    {
      label: 'memcpy',
      kind: 'Function',
      detail: 'void* memcpy(void *dest, const void *src, size_t n)',
      documentation: 'Copies n bytes from memory area src to dest.',
      insertText: 'memcpy(${1:dest}, ${2:src}, ${3:size});$0',
      isSnippet: true
    },
    {
      label: 'qsort',
      kind: 'Function',
      detail: 'void qsort(void *base, size_t nel, size_t width, int (*cmp)(const void*, const void*))',
      documentation: 'Sorts an array using the quicksort algorithm.',
      insertText: 'qsort(${1:base}, ${2:n}, sizeof(${3:type}), ${4:cmp_func});$0',
      isSnippet: true
    },
    {
      label: 'abs',
      kind: 'Function',
      detail: 'int abs(int n)',
      documentation: 'Computes absolute value of integer.',
      insertText: 'abs(${1:n})$0',
      isSnippet: true
    },
    {
      label: 'sqrt',
      kind: 'Function',
      detail: 'double sqrt(double x)',
      documentation: 'Computes square root from math.h.',
      insertText: 'sqrt(${1:x})$0',
      isSnippet: true
    },
    {
      label: 'pow',
      kind: 'Function',
      detail: 'double pow(double base, double exp)',
      documentation: 'Computes base raised to power exp.',
      insertText: 'pow(${1:base}, ${2:exp})$0',
      isSnippet: true
    },

    // C Snippets & Keywords
    {
      label: 'inc',
      kind: 'Snippet',
      detail: '#include <header.h> snippet',
      documentation: 'Includes a C standard library header.',
      insertText: '#include <${1:stdio.h}>$0',
      isSnippet: true
    },
    {
      label: 'incstd',
      kind: 'Snippet',
      detail: 'Include standard C competitive headers',
      documentation: 'Includes stdio, stdlib, string, stdbool, and math.',
      insertText: '#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <stdbool.h>\n#include <math.h>\n\n$0',
      isSnippet: true
    },
    {
      label: 'main',
      kind: 'Snippet',
      detail: 'int main() entrypoint',
      documentation: 'C standard main entrypoint function.',
      insertText: 'int main(int argc, char *argv[]) {\n\t${0:/* code */}\n\treturn 0;\n}',
      isSnippet: true
    },
    {
      label: 'for',
      kind: 'Snippet',
      detail: 'for loop snippet',
      documentation: 'Standard index-based for loop.',
      insertText: 'for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'while',
      kind: 'Snippet',
      detail: 'while loop snippet',
      documentation: 'Loop while expression is non-zero.',
      insertText: 'while (${1:condition}) {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'if',
      kind: 'Snippet',
      detail: 'if statement snippet',
      documentation: 'Conditional if block.',
      insertText: 'if (${1:condition}) {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'ifelse',
      kind: 'Snippet',
      detail: 'if-else statement snippet',
      documentation: 'Conditional if-else block.',
      insertText: 'if (${1:condition}) {\n\t${2:/* code */}\n} else {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'switch',
      kind: 'Snippet',
      detail: 'switch-case statement',
      documentation: 'Multi-branch selection control structure.',
      insertText: 'switch (${1:expression}) {\n\tcase ${2:constant}:\n\t\t${3:/* code */}\n\t\tbreak;\n\tdefault:\n\t\t${0:/* code */}\n\t\tbreak;\n}',
      isSnippet: true
    },
    {
      label: 'struct',
      kind: 'Snippet',
      detail: 'struct definition snippet',
      documentation: 'Defines a C composite structure.',
      insertText: 'struct ${1:Name} {\n\t${2:int id;}\n};',
      isSnippet: true
    },
    {
      label: 'typedef',
      kind: 'Snippet',
      detail: 'typedef struct snippet',
      documentation: 'Defines a type alias for struct.',
      insertText: 'typedef struct {\n\t${2:int id;}\n} ${1:Name};',
      isSnippet: true
    }
  ],

  cpp: [
    // Standard Streams & I/O
    {
      label: 'cout',
      kind: 'Variable',
      detail: 'std::cout (character output stream)',
      documentation: 'Standard output stream tied to stdout.',
      insertText: 'std::cout << ${1:value} << "\\n";$0',
      isSnippet: true
    },
    {
      label: 'cin',
      kind: 'Variable',
      detail: 'std::cin (character input stream)',
      documentation: 'Standard input stream tied to stdin.',
      insertText: 'std::cin >> ${1:var};$0',
      isSnippet: true
    },
    {
      label: 'endl',
      kind: 'Constant',
      detail: 'std::endl',
      documentation: 'Inserts newline character and flushes the stream.',
      insertText: 'std::endl'
    },

    // STL Containers
    {
      label: 'vector',
      kind: 'Class',
      detail: 'std::vector<T>',
      documentation: 'Contiguous dynamic sequence container.',
      insertText: 'std::vector<${1:int}> ${2:v};$0',
      isSnippet: true
    },
    {
      label: 'string',
      kind: 'Class',
      detail: 'std::string',
      documentation: 'Standard string class managing dynamic character arrays.',
      insertText: 'std::string ${1:s};$0',
      isSnippet: true
    },
    {
      label: 'unordered_map',
      kind: 'Class',
      detail: 'std::unordered_map<Key, Val>',
      documentation: 'Hash-table based associative key-value map with O(1) average lookup.',
      insertText: 'std::unordered_map<${1:int}, ${2:int}> ${3:mp};$0',
      isSnippet: true
    },
    {
      label: 'map',
      kind: 'Class',
      detail: 'std::map<Key, Val>',
      documentation: 'Sorted associative key-value map (Red-Black Tree) with O(log n) lookup.',
      insertText: 'std::map<${1:int}, ${2:int}> ${3:mp};$0',
      isSnippet: true
    },
    {
      label: 'unordered_set',
      kind: 'Class',
      detail: 'std::unordered_set<Key>',
      documentation: 'Hash-table based unique key container.',
      insertText: 'std::unordered_set<${1:int}> ${2:st};$0',
      isSnippet: true
    },
    {
      label: 'set',
      kind: 'Class',
      detail: 'std::set<Key>',
      documentation: 'Sorted collection of unique keys (O(log n) operations).',
      insertText: 'std::set<${1:int}> ${2:st};$0',
      isSnippet: true
    },
    {
      label: 'queue',
      kind: 'Class',
      detail: 'std::queue<T>',
      documentation: 'FIFO queue adapter.',
      insertText: 'std::queue<${1:int}> ${2:q};$0',
      isSnippet: true
    },
    {
      label: 'priority_queue',
      kind: 'Class',
      detail: 'std::priority_queue<T>',
      documentation: 'Max-heap container adapter with O(log n) insertions/deletions.',
      insertText: 'std::priority_queue<${1:int}> ${2:pq};$0',
      isSnippet: true
    },
    {
      label: 'stack',
      kind: 'Class',
      detail: 'std::stack<T>',
      documentation: 'LIFO stack adapter.',
      insertText: 'std::stack<${1:int}> ${2:stk};$0',
      isSnippet: true
    },
    {
      label: 'pair',
      kind: 'Class',
      detail: 'std::pair<T1, T2>',
      documentation: 'Couples together a pair of values.',
      insertText: 'std::pair<${1:int}, ${2:int}> ${3:p};$0',
      isSnippet: true
    },

    // STL Algorithms
    {
      label: 'std::sort',
      kind: 'Function',
      detail: 'std::sort(first, last[, comp])',
      documentation: 'Sorts elements in range [first, last) in non-descending order in O(n log n) time.',
      insertText: 'std::sort(${1:v}.begin(), ${1:v}.end());$0',
      isSnippet: true
    },
    {
      label: 'std::reverse',
      kind: 'Function',
      detail: 'std::reverse(first, last)',
      documentation: 'Reverses the order of the elements in the range [first, last).',
      insertText: 'std::reverse(${1:v}.begin(), ${1:v}.end());$0',
      isSnippet: true
    },
    {
      label: 'std::min',
      kind: 'Function',
      detail: 'std::min(a, b)',
      documentation: 'Returns the smaller of two values.',
      insertText: 'std::min(${1:a}, ${2:b})$0',
      isSnippet: true
    },
    {
      label: 'std::max',
      kind: 'Function',
      detail: 'std::max(a, b)',
      documentation: 'Returns the greater of two values.',
      insertText: 'std::max(${1:a}, ${2:b})$0',
      isSnippet: true
    },
    {
      label: 'std::swap',
      kind: 'Function',
      detail: 'std::swap(a, b)',
      documentation: 'Exchanges the values of two objects.',
      insertText: 'std::swap(${1:a}, ${2:b});$0',
      isSnippet: true
    },
    {
      label: 'std::binary_search',
      kind: 'Function',
      detail: 'std::binary_search(first, last, val)',
      documentation: 'Tests if value exists in sorted sequence [first, last).',
      insertText: 'std::binary_search(${1:v}.begin(), ${1:v}.end(), ${2:val})$0',
      isSnippet: true
    },
    {
      label: 'std::lower_bound',
      kind: 'Function',
      detail: 'std::lower_bound(first, last, val)',
      documentation: 'Returns iterator to the first element not less than val.',
      insertText: 'std::lower_bound(${1:v}.begin(), ${1:v}.end(), ${2:val})$0',
      isSnippet: true
    },
    {
      label: 'std::upper_bound',
      kind: 'Function',
      detail: 'std::upper_bound(first, last, val)',
      documentation: 'Returns iterator to the first element greater than val.',
      insertText: 'std::upper_bound(${1:v}.begin(), ${1:v}.end(), ${2:val})$0',
      isSnippet: true
    },
    {
      label: 'std::accumulate',
      kind: 'Function',
      detail: 'std::accumulate(first, last, init)',
      documentation: 'Computes sum of given value and elements across range [first, last).',
      insertText: 'std::accumulate(${1:v}.begin(), ${1:v}.end(), ${2:0})$0',
      isSnippet: true
    },

    // C++ Snippets
    {
      label: 'cou',
      kind: 'Snippet',
      detail: 'std::cout print snippet',
      documentation: 'Outputs value with newline to std::cout.',
      insertText: 'std::cout << ${1:value} << "\\n";$0',
      isSnippet: true
    },
    {
      label: 'cin',
      kind: 'Snippet',
      detail: 'std::cin input snippet',
      documentation: 'Reads input from std::cin.',
      insertText: 'std::cin >> ${1:var};$0',
      isSnippet: true
    },
    {
      label: 'vec',
      kind: 'Snippet',
      detail: 'std::vector declaration snippet',
      documentation: 'Declares an STL vector.',
      insertText: 'std::vector<${1:int}> ${2:v};$0',
      isSnippet: true
    },
    {
      label: 'for',
      kind: 'Snippet',
      detail: 'Standard index loop',
      documentation: 'for (int i = 0; i < n; ++i)',
      insertText: 'for (int ${1:i} = 0; ${1:i} < ${2:n}; ++${1:i}) {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'forrange',
      kind: 'Snippet',
      detail: 'C++ range-based for loop',
      documentation: 'for (const auto& item : container)',
      insertText: 'for (const auto& ${1:item} : ${2:container}) {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'pqmin',
      kind: 'Snippet',
      detail: 'Min-heap priority_queue snippet',
      documentation: 'Declares a min-heap priority queue using std::greater.',
      insertText: 'std::priority_queue<${1:int}, std::vector<${1:int}>, std::greater<${1:int}>> ${2:min_pq};$0',
      isSnippet: true
    },
    {
      label: 'fastio',
      kind: 'Snippet',
      detail: 'Fast I/O optimization snippet',
      documentation: 'Disables synchronization with C stdio for fast I/O.',
      insertText: 'std::ios_base::sync_with_stdio(false);\nstd::cin.tie(NULL);\n$0',
      isSnippet: true
    },
    {
      label: 'incall',
      kind: 'Snippet',
      detail: 'Standard competitive C++ includes',
      documentation: 'Includes iostream, vector, string, algorithm, map, set, queue.',
      insertText: '#include <iostream>\n#include <vector>\n#include <string>\n#include <algorithm>\n#include <unordered_map>\n#include <unordered_set>\n#include <queue>\n\n$0',
      isSnippet: true
    },
    {
      label: 'class',
      kind: 'Snippet',
      detail: 'Class declaration snippet',
      documentation: 'Declares a C++ class with public/private sections.',
      insertText: 'class ${1:Solution} {\npublic:\n\t${0:/* methods */}\n};',
      isSnippet: true
    },
    {
      label: 'template',
      kind: 'Snippet',
      detail: 'template <typename T> snippet',
      documentation: 'C++ template declaration.',
      insertText: 'template <typename ${1:T}>\n${0:/* code */}',
      isSnippet: true
    }
  ],

  java: [
    // Standard Print & Output
    {
      label: 'System.out.println',
      kind: 'Function',
      detail: 'void System.out.println(String x)',
      documentation: 'Prints a string to stdout and then terminates the line.',
      insertText: 'System.out.println(${1:value});$0',
      isSnippet: true
    },
    {
      label: 'System.out.print',
      kind: 'Function',
      detail: 'void System.out.print(String x)',
      documentation: 'Prints a string to stdout without line termination.',
      insertText: 'System.out.print(${1:value});$0',
      isSnippet: true
    },
    {
      label: 'System.err.println',
      kind: 'Function',
      detail: 'void System.err.println(String x)',
      documentation: 'Prints to standard error.',
      insertText: 'System.err.println(${1:value});$0',
      isSnippet: true
    },

    // Math methods
    {
      label: 'Math.max',
      kind: 'Function',
      detail: 'Math.max(a, b)',
      documentation: 'Returns the greater of two values.',
      insertText: 'Math.max(${1:a}, ${2:b})$0',
      isSnippet: true
    },
    {
      label: 'Math.min',
      kind: 'Function',
      detail: 'Math.min(a, b)',
      documentation: 'Returns the smaller of two values.',
      insertText: 'Math.min(${1:a}, ${2:b})$0',
      isSnippet: true
    },
    {
      label: 'Math.abs',
      kind: 'Function',
      detail: 'Math.abs(a)',
      documentation: 'Returns the absolute value of the argument.',
      insertText: 'Math.abs(${1:a})$0',
      isSnippet: true
    },
    {
      label: 'Math.sqrt',
      kind: 'Function',
      detail: 'Math.sqrt(double a)',
      documentation: 'Returns the correctly rounded positive square root of a double value.',
      insertText: 'Math.sqrt(${1:a})$0',
      isSnippet: true
    },
    {
      label: 'Math.pow',
      kind: 'Function',
      detail: 'Math.pow(double a, double b)',
      documentation: 'Returns value of first argument raised to power of second argument.',
      insertText: 'Math.pow(${1:base}, ${2:exp})$0',
      isSnippet: true
    },

    // Arrays & Collections Utilities
    {
      label: 'Arrays.sort',
      kind: 'Function',
      detail: 'Arrays.sort(T[] a)',
      documentation: 'Sorts specified array into ascending numerical order.',
      insertText: 'Arrays.sort(${1:arr});$0',
      isSnippet: true
    },
    {
      label: 'Arrays.fill',
      kind: 'Function',
      detail: 'Arrays.fill(T[] a, T val)',
      documentation: 'Assigns the specified value to each element of the array.',
      insertText: 'Arrays.fill(${1:arr}, ${2:val});$0',
      isSnippet: true
    },
    {
      label: 'Arrays.toString',
      kind: 'Function',
      detail: 'Arrays.toString(T[] a) -> String',
      documentation: 'Returns a string representation of the contents of the specified array.',
      insertText: 'Arrays.toString(${1:arr})$0',
      isSnippet: true
    },
    {
      label: 'Arrays.binarySearch',
      kind: 'Function',
      detail: 'Arrays.binarySearch(T[] a, T key)',
      documentation: 'Searches sorted array for the specified value using binary search.',
      insertText: 'Arrays.binarySearch(${1:arr}, ${2:key})$0',
      isSnippet: true
    },
    {
      label: 'Collections.sort',
      kind: 'Function',
      detail: 'Collections.sort(List<T> list)',
      documentation: 'Sorts specified list into ascending order.',
      insertText: 'Collections.sort(${1:list});$0',
      isSnippet: true
    },
    {
      label: 'Collections.reverse',
      kind: 'Function',
      detail: 'Collections.reverse(List<?> list)',
      documentation: 'Reverses the order of the elements in the specified list.',
      insertText: 'Collections.reverse(${1:list});$0',
      isSnippet: true
    },

    // Standard Java Types
    {
      label: 'String',
      kind: 'Class',
      detail: 'java.lang.String',
      documentation: 'Immutable character sequence.',
      insertText: 'String ${1:s} = "${2:text}";$0',
      isSnippet: true
    },
    {
      label: 'StringBuilder',
      kind: 'Class',
      detail: 'java.lang.StringBuilder',
      documentation: 'Mutable sequence of characters with efficient append/insert operations.',
      insertText: 'StringBuilder ${1:sb} = new StringBuilder();$0',
      isSnippet: true
    },
    {
      label: 'ArrayList',
      kind: 'Class',
      detail: 'java.util.ArrayList<E>',
      documentation: 'Resizable-array implementation of the List interface.',
      insertText: 'List<${1:Integer}> ${2:list} = new ArrayList<>();$0',
      isSnippet: true
    },
    {
      label: 'HashMap',
      kind: 'Class',
      detail: 'java.util.HashMap<K, V>',
      documentation: 'Hash table based implementation of the Map interface.',
      insertText: 'Map<${1:String}, ${2:Integer}> ${3:map} = new HashMap<>();$0',
      isSnippet: true
    },
    {
      label: 'HashSet',
      kind: 'Class',
      detail: 'java.util.HashSet<E>',
      documentation: 'Hash table backed Set implementation of unique elements.',
      insertText: 'Set<${1:Integer}> ${2:set} = new HashSet<>();$0',
      isSnippet: true
    },
    {
      label: 'PriorityQueue',
      kind: 'Class',
      detail: 'java.util.PriorityQueue<E>',
      documentation: 'An unbounded priority queue based on a priority heap.',
      insertText: 'PriorityQueue<${1:Integer}> ${2:pq} = new PriorityQueue<>();$0',
      isSnippet: true
    },

    // Java Snippets
    {
      label: 'sout',
      kind: 'Snippet',
      detail: 'System.out.println() snippet',
      documentation: 'Prints value to stdout.',
      insertText: 'System.out.println(${1:value});$0',
      isSnippet: true
    },
    {
      label: 'souf',
      kind: 'Snippet',
      detail: 'System.out.printf() snippet',
      documentation: 'Prints formatted output to stdout.',
      insertText: 'System.out.printf("${1:%s\\n}", ${2:args});$0',
      isSnippet: true
    },
    {
      label: 'main',
      kind: 'Snippet',
      detail: 'public static void main() snippet',
      documentation: 'Standard Java main entrypoint method.',
      insertText: 'public static void main(String[] args) {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'psvm',
      kind: 'Snippet',
      detail: 'public static void main() shortcut',
      documentation: 'Standard Java main method shortcut.',
      insertText: 'public static void main(String[] args) {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'pub',
      kind: 'Snippet',
      detail: 'public method snippet',
      documentation: 'Creates a public method declaration.',
      insertText: 'public ${1:void} ${2:methodName}(${3:params}) {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'class',
      kind: 'Snippet',
      detail: 'public class declaration',
      documentation: 'Creates a public class declaration.',
      insertText: 'public class ${1:Main} {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'for',
      kind: 'Snippet',
      detail: 'Index-based for loop',
      documentation: 'for (int i = 0; i < n; i++)',
      insertText: 'for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'fore',
      kind: 'Snippet',
      detail: 'Enhanced for-each loop',
      documentation: 'for (Type item : collection)',
      insertText: 'for (${1:Object} ${2:item} : ${3:collection}) {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'while',
      kind: 'Snippet',
      detail: 'while loop snippet',
      documentation: 'Executes block while boolean condition is true.',
      insertText: 'while (${1:condition}) {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'if',
      kind: 'Snippet',
      detail: 'if statement snippet',
      documentation: 'Conditional if block.',
      insertText: 'if (${1:condition}) {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'ifelse',
      kind: 'Snippet',
      detail: 'if-else statement snippet',
      documentation: 'Conditional if-else block.',
      insertText: 'if (${1:condition}) {\n\t${2:/* code */}\n} else {\n\t${0:/* code */}\n}',
      isSnippet: true
    },
    {
      label: 'try',
      kind: 'Snippet',
      detail: 'try-catch block snippet',
      documentation: 'Exception handling try-catch block.',
      insertText: 'try {\n\t${1:/* code */}\n} catch (Exception ${2:e}) {\n\t${2:e}.printStackTrace();$0\n}',
      isSnippet: true
    },
    {
      label: 'new',
      kind: 'Snippet',
      detail: 'Object instantiation snippet',
      documentation: 'Creates and initializes a new object instance.',
      insertText: '${1:Type} ${2:obj} = new ${1:Type}(${3:args});$0',
      isSnippet: true
    }
  ]
};

// =============================================================================
// 2. MEMBER ACCESS COMPLETIONS CATALOG (Methods triggered on '.')
// =============================================================================

export const MEMBER_COMPLETIONS = {
  python: [
    // List & Sequence methods
    { label: 'append', kind: 'Method', detail: 'list.append(x)', insertText: 'append(${1:x})$0', isSnippet: true },
    { label: 'extend', kind: 'Method', detail: 'list.extend(iterable)', insertText: 'extend(${1:iterable})$0', isSnippet: true },
    { label: 'insert', kind: 'Method', detail: 'list.insert(i, x)', insertText: 'insert(${1:index}, ${2:x})$0', isSnippet: true },
    { label: 'remove', kind: 'Method', detail: 'list.remove(x)', insertText: 'remove(${1:x})$0', isSnippet: true },
    { label: 'pop', kind: 'Method', detail: 'list.pop([i]) -> item', insertText: 'pop(${1:})$0', isSnippet: true },
    { label: 'clear', kind: 'Method', detail: 'list.clear()', insertText: 'clear()$0', isSnippet: true },
    { label: 'index', kind: 'Method', detail: 'list.index(x)', insertText: 'index(${1:x})$0', isSnippet: true },
    { label: 'count', kind: 'Method', detail: 'sequence.count(x)', insertText: 'count(${1:x})$0', isSnippet: true },
    { label: 'sort', kind: 'Method', detail: 'list.sort(*, key=None, reverse=False)', insertText: 'sort()$0', isSnippet: true },
    { label: 'reverse', kind: 'Method', detail: 'list.reverse()', insertText: 'reverse()$0', isSnippet: true },
    { label: 'copy', kind: 'Method', detail: 'container.copy()', insertText: 'copy()$0', isSnippet: true },

    // Dict methods
    { label: 'keys', kind: 'Method', detail: 'dict.keys()', insertText: 'keys()$0', isSnippet: true },
    { label: 'values', kind: 'Method', detail: 'dict.values()', insertText: 'values()$0', isSnippet: true },
    { label: 'items', kind: 'Method', detail: 'dict.items()', insertText: 'items()$0', isSnippet: true },
    { label: 'get', kind: 'Method', detail: 'dict.get(key[, default])', insertText: 'get(${1:key}${2:, default})$0', isSnippet: true },
    { label: 'update', kind: 'Method', detail: 'dict.update([other])', insertText: 'update(${1:other})$0', isSnippet: true },

    // String methods
    { label: 'split', kind: 'Method', detail: 'str.split(sep=None)', insertText: 'split(${1:sep})$0', isSnippet: true },
    { label: 'join', kind: 'Method', detail: 'str.join(iterable)', insertText: 'join(${1:iterable})$0', isSnippet: true },
    { label: 'strip', kind: 'Method', detail: 'str.strip([chars])', insertText: 'strip()$0', isSnippet: true },
    { label: 'replace', kind: 'Method', detail: 'str.replace(old, new[, count])', insertText: 'replace(${1:old}, ${2:new})$0', isSnippet: true },
    { label: 'lower', kind: 'Method', detail: 'str.lower()', insertText: 'lower()$0', isSnippet: true },
    { label: 'upper', kind: 'Method', detail: 'str.upper()', insertText: 'upper()$0', isSnippet: true },
    { label: 'startswith', kind: 'Method', detail: 'str.startswith(prefix)', insertText: 'startswith(${1:prefix})$0', isSnippet: true },
    { label: 'endswith', kind: 'Method', detail: 'str.endswith(suffix)', insertText: 'endswith(${1:suffix})$0', isSnippet: true },
    { label: 'find', kind: 'Method', detail: 'str.find(sub)', insertText: 'find(${1:sub})$0', isSnippet: true },

    // Set methods
    { label: 'add', kind: 'Method', detail: 'set.add(elem)', insertText: 'add(${1:elem})$0', isSnippet: true },
    { label: 'discard', kind: 'Method', detail: 'set.discard(elem)', insertText: 'discard(${1:elem})$0', isSnippet: true }
  ],

  cpp: [
    { label: 'push_back', kind: 'Method', detail: 'void push_back(const T& val)', insertText: 'push_back(${1:val});$0', isSnippet: true },
    { label: 'emplace_back', kind: 'Method', detail: 'void emplace_back(Args&&... args)', insertText: 'emplace_back(${1:args});$0', isSnippet: true },
    { label: 'pop_back', kind: 'Method', detail: 'void pop_back()', insertText: 'pop_back();$0', isSnippet: true },
    { label: 'size', kind: 'Method', detail: 'size_t size() const', insertText: 'size()$0', isSnippet: true },
    { label: 'empty', kind: 'Method', detail: 'bool empty() const', insertText: 'empty()$0', isSnippet: true },
    { label: 'clear', kind: 'Method', detail: 'void clear()', insertText: 'clear();$0', isSnippet: true },
    { label: 'begin', kind: 'Method', detail: 'iterator begin()', insertText: 'begin()$0', isSnippet: true },
    { label: 'end', kind: 'Method', detail: 'iterator end()', insertText: 'end()$0', isSnippet: true },
    { label: 'front', kind: 'Method', detail: 'reference front()', insertText: 'front()$0', isSnippet: true },
    { label: 'back', kind: 'Method', detail: 'reference back()', insertText: 'back()$0', isSnippet: true },
    { label: 'top', kind: 'Method', detail: 'const_reference top() const', insertText: 'top()$0', isSnippet: true },
    { label: 'push', kind: 'Method', detail: 'void push(const T& val)', insertText: 'push(${1:val});$0', isSnippet: true },
    { label: 'pop', kind: 'Method', detail: 'void pop()', insertText: 'pop();$0', isSnippet: true },
    { label: 'insert', kind: 'Method', detail: 'pair<iterator, bool> insert(const T& val)', insertText: 'insert(${1:val});$0', isSnippet: true },
    { label: 'erase', kind: 'Method', detail: 'size_t erase(const key_type& key)', insertText: 'erase(${1:key});$0', isSnippet: true },
    { label: 'find', kind: 'Method', detail: 'iterator find(const key_type& key)', insertText: 'find(${1:key})$0', isSnippet: true },
    { label: 'count', kind: 'Method', detail: 'size_t count(const key_type& key) const', insertText: 'count(${1:key})$0', isSnippet: true },
    { label: 'substr', kind: 'Method', detail: 'string substr(size_t pos = 0, size_t count = npos) const', insertText: 'substr(${1:pos}${2:, len})$0', isSnippet: true },
    { label: 'length', kind: 'Method', detail: 'size_t length() const', insertText: 'length()$0', isSnippet: true },
    { label: 'c_str', kind: 'Method', detail: 'const char* c_str() const', insertText: 'c_str()$0', isSnippet: true }
  ],

  java: [
    { label: 'length', kind: 'Method', detail: 'int length()', insertText: 'length()$0', isSnippet: true },
    { label: 'charAt', kind: 'Method', detail: 'char charAt(int index)', insertText: 'charAt(${1:index})$0', isSnippet: true },
    { label: 'substring', kind: 'Method', detail: 'String substring(int beginIndex[, int endIndex])', insertText: 'substring(${1:beginIndex}${2:, endIndex})$0', isSnippet: true },
    { label: 'equals', kind: 'Method', detail: 'boolean equals(Object anObject)', insertText: 'equals(${1:other})$0', isSnippet: true },
    { label: 'equalsIgnoreCase', kind: 'Method', detail: 'boolean equalsIgnoreCase(String anotherString)', insertText: 'equalsIgnoreCase(${1:other})$0', isSnippet: true },
    { label: 'toLowerCase', kind: 'Method', detail: 'String toLowerCase()', insertText: 'toLowerCase()$0', isSnippet: true },
    { label: 'toUpperCase', kind: 'Method', detail: 'String toUpperCase()', insertText: 'toUpperCase()$0', isSnippet: true },
    { label: 'trim', kind: 'Method', detail: 'String trim()', insertText: 'trim()$0', isSnippet: true },
    { label: 'replace', kind: 'Method', detail: 'String replace(CharSequence target, CharSequence replacement)', insertText: 'replace(${1:target}, ${2:replacement})$0', isSnippet: true },
    { label: 'contains', kind: 'Method', detail: 'boolean contains(CharSequence s)', insertText: 'contains(${1:s})$0', isSnippet: true },
    { label: 'startsWith', kind: 'Method', detail: 'boolean startsWith(String prefix)', insertText: 'startsWith(${1:prefix})$0', isSnippet: true },
    { label: 'endsWith', kind: 'Method', detail: 'boolean endsWith(String suffix)', insertText: 'endsWith(${1:suffix})$0', isSnippet: true },
    { label: 'indexOf', kind: 'Method', detail: 'int indexOf(String str)', insertText: 'indexOf(${1:str})$0', isSnippet: true },
    { label: 'add', kind: 'Method', detail: 'boolean add(E e)', insertText: 'add(${1:e});$0', isSnippet: true },
    { label: 'remove', kind: 'Method', detail: 'E remove(int index) / boolean remove(Object o)', insertText: 'remove(${1:target});$0', isSnippet: true },
    { label: 'get', kind: 'Method', detail: 'E get(int index)', insertText: 'get(${1:index})$0', isSnippet: true },
    { label: 'put', kind: 'Method', detail: 'V put(K key, V value)', insertText: 'put(${1:key}, ${2:value});$0', isSnippet: true },
    { label: 'getOrDefault', kind: 'Method', detail: 'V getOrDefault(Object key, V defaultValue)', insertText: 'getOrDefault(${1:key}, ${2:defaultValue})$0', isSnippet: true },
    { label: 'containsKey', kind: 'Method', detail: 'boolean containsKey(Object key)', insertText: 'containsKey(${1:key})$0', isSnippet: true },
    { label: 'size', kind: 'Method', detail: 'int size()', insertText: 'size()$0', isSnippet: true },
    { label: 'isEmpty', kind: 'Method', detail: 'boolean isEmpty()', insertText: 'isEmpty()$0', isSnippet: true },
    { label: 'clear', kind: 'Method', detail: 'void clear()', insertText: 'clear();$0', isSnippet: true },
    { label: 'toString', kind: 'Method', detail: 'String toString()', insertText: 'toString()$0', isSnippet: true }
  ]
};

// =============================================================================
// 3. BUILT-IN SIGNATURE HELP CATALOG
// =============================================================================

export const BUILTIN_SIGNATURES = {
  python: {
    print: {
      label: 'print(*values, sep=" ", end="\\n", file=sys.stdout, flush=False)',
      documentation: 'Prints the values to a stream, or to sys.stdout by default.',
      parameters: [
        { label: '*values', documentation: 'Values to be printed.' },
        { label: 'sep', documentation: 'String inserted between values, default space.' },
        { label: 'end', documentation: 'String appended after the last value, default newline.' },
        { label: 'file', documentation: 'Stream object (defaults to current sys.stdout).' },
        { label: 'flush', documentation: 'Whether to forcibly flush the stream.' }
      ]
    },
    len: {
      label: 'len(s) -> int',
      documentation: 'Return the number of items in a container.',
      parameters: [
        { label: 's', documentation: 'Container or sequence whose length to return.' }
      ]
    },
    range: {
      label: 'range(start, stop[, step])',
      documentation: 'Returns an object that produces integers from start to stop by step.',
      parameters: [
        { label: 'start', documentation: 'The starting number of the sequence.' },
        { label: 'stop', documentation: 'Generate numbers up to, but not including this number.' },
        { label: 'step', documentation: 'Difference between each number in the sequence.' }
      ]
    },
    enumerate: {
      label: 'enumerate(iterable, start=0)',
      documentation: 'Yields pairs containing a count and the values obtained from iterating over iterable.',
      parameters: [
        { label: 'iterable', documentation: 'Any sequence, iterator, or supporting iteration.' },
        { label: 'start', documentation: 'Index start value (defaults to 0).' }
      ]
    },
    zip: {
      label: 'zip(*iterables, strict=False)',
      documentation: 'Iterate over several iterables in parallel.',
      parameters: [
        { label: '*iterables', documentation: 'Iterables to zip together.' },
        { label: 'strict', documentation: 'When True, raises ValueError if an argument is exhausted before others.' }
      ]
    },
    sorted: {
      label: 'sorted(iterable, *, key=None, reverse=False) -> list',
      documentation: 'Return a new list containing all items from the iterable in ascending order.',
      parameters: [
        { label: 'iterable', documentation: 'Sequence or collection to sort.' },
        { label: 'key', documentation: 'Function of one argument used to extract comparison key.' },
        { label: 'reverse', documentation: 'If set to True, the list elements are sorted in reverse order.' }
      ]
    },
    min: {
      label: 'min(arg1, arg2, *args, key=None)',
      documentation: 'With a single iterable argument, return its smallest item. With multiple arguments, return the smallest.',
      parameters: [
        { label: 'arg1', documentation: 'First argument or iterable.' },
        { label: 'arg2', documentation: 'Second argument.' },
        { label: '*args', documentation: 'Additional arguments.' }
      ]
    },
    max: {
      label: 'max(arg1, arg2, *args, key=None)',
      documentation: 'With a single iterable argument, return its largest item. With multiple arguments, return the largest.',
      parameters: [
        { label: 'arg1', documentation: 'First argument or iterable.' },
        { label: 'arg2', documentation: 'Second argument.' },
        { label: '*args', documentation: 'Additional arguments.' }
      ]
    },
    isinstance: {
      label: 'isinstance(object, classinfo) -> bool',
      documentation: 'Return whether an object is an instance of a class or of a subclass thereof.',
      parameters: [
        { label: 'object', documentation: 'Object to check.' },
        { label: 'classinfo', documentation: 'A class, type, or tuple of classes and types.' }
      ]
    },
    open: {
      label: 'open(file, mode="r", encoding=None)',
      documentation: 'Open file and return a stream.',
      parameters: [
        { label: 'file', documentation: 'Path-like object giving pathname of the file to be opened.' },
        { label: 'mode', documentation: 'String specifying mode in which file is opened ("r", "w", "a", etc.).' },
        { label: 'encoding', documentation: 'Name of encoding used to decode/encode the file.' }
      ]
    }
  },

  c: {
    printf: {
      label: 'int printf(const char *format, ...)',
      documentation: 'Sends formatted output to stdout.',
      parameters: [
        { label: 'const char *format', documentation: 'Format control string containing conversion specifiers.' },
        { label: '...', documentation: 'Arguments matching the conversion specifiers.' }
      ]
    },
    scanf: {
      label: 'int scanf(const char *format, ...)',
      documentation: 'Reads data from stdin and stores them according to the format specification.',
      parameters: [
        { label: 'const char *format', documentation: 'Format control string.' },
        { label: '...', documentation: 'Pointers to variables where read values are written.' }
      ]
    },
    malloc: {
      label: 'void* malloc(size_t size)',
      documentation: 'Allocates a memory block of size bytes.',
      parameters: [
        { label: 'size_t size', documentation: 'Number of bytes to allocate on heap.' }
      ]
    },
    free: {
      label: 'void free(void *ptr)',
      documentation: 'Deallocates the memory previously allocated by a call to calloc, malloc, or realloc.',
      parameters: [
        { label: 'void *ptr', documentation: 'Pointer to memory block to release.' }
      ]
    },
    strlen: {
      label: 'size_t strlen(const char *str)',
      documentation: 'Calculates the length of the string up to, but not including the terminating null character.',
      parameters: [
        { label: 'const char *str', documentation: 'Null-terminated byte string.' }
      ]
    },
    strcpy: {
      label: 'char* strcpy(char *dest, const char *src)',
      documentation: 'Copies string pointed by src into array pointed by dest.',
      parameters: [
        { label: 'char *dest', documentation: 'Destination buffer.' },
        { label: 'const char *src', documentation: 'Source string.' }
      ]
    },
    strcmp: {
      label: 'int strcmp(const char *s1, const char *s2)',
      documentation: 'Compares two null-terminated strings lexicographically.',
      parameters: [
        { label: 'const char *s1', documentation: 'First string to compare.' },
        { label: 'const char *s2', documentation: 'Second string to compare.' }
      ]
    },
    memset: {
      label: 'void* memset(void *s, int c, size_t n)',
      documentation: 'Copies the character c (converted to unsigned char) into each of the first n characters of s.',
      parameters: [
        { label: 'void *s', documentation: 'Pointer to block of memory to fill.' },
        { label: 'int c', documentation: 'Byte value to set.' },
        { label: 'size_t n', documentation: 'Number of bytes to be set to the value.' }
      ]
    }
  },

  cpp: {
    'std::sort': {
      label: 'std::sort(RandomAccessIterator first, RandomAccessIterator last[, Compare comp])',
      documentation: 'Sorts the elements in the range [first, last) in non-descending order.',
      parameters: [
        { label: 'first', documentation: 'Iterator pointing to the initial position.' },
        { label: 'last', documentation: 'Iterator pointing to the final position.' },
        { label: 'comp', documentation: 'Binary function taking two elements and returning bool.' }
      ]
    },
    'std::min': {
      label: 'std::min(const T& a, const T& b)',
      documentation: 'Returns the smaller of a and b.',
      parameters: [
        { label: 'const T& a', documentation: 'First value.' },
        { label: 'const T& b', documentation: 'Second value.' }
      ]
    },
    'std::max': {
      label: 'std::max(const T& a, const T& b)',
      documentation: 'Returns the greater of a and b.',
      parameters: [
        { label: 'const T& a', documentation: 'First value.' },
        { label: 'const T& b', documentation: 'Second value.' }
      ]
    },
    'std::swap': {
      label: 'std::swap(T& a, T& b)',
      documentation: 'Exchanges the values of a and b.',
      parameters: [
        { label: 'T& a', documentation: 'First argument.' },
        { label: 'T& b', documentation: 'Second argument.' }
      ]
    },
    'std::lower_bound': {
      label: 'std::lower_bound(ForwardIterator first, ForwardIterator last, const T& val)',
      documentation: 'Returns iterator to the first element in [first, last) which does not compare less than val.',
      parameters: [
        { label: 'first', documentation: 'Beginning of partitioned range.' },
        { label: 'last', documentation: 'End of partitioned range.' },
        { label: 'val', documentation: 'Value to compare elements to.' }
      ]
    }
  },

  java: {
    'System.out.println': {
      label: 'void System.out.println(String x)',
      documentation: 'Prints a String and then terminates the line.',
      parameters: [
        { label: 'x', documentation: 'The String value to be printed.' }
      ]
    },
    'Math.max': {
      label: 'Math.max(a, b)',
      documentation: 'Returns the greater of two arguments.',
      parameters: [
        { label: 'a', documentation: 'An argument.' },
        { label: 'b', documentation: 'Another argument.' }
      ]
    },
    'Math.min': {
      label: 'Math.min(a, b)',
      documentation: 'Returns the smaller of two arguments.',
      parameters: [
        { label: 'a', documentation: 'An argument.' },
        { label: 'b', documentation: 'Another argument.' }
      ]
    },
    'Math.pow': {
      label: 'Math.pow(double a, double b)',
      documentation: 'Returns the value of the first argument raised to the power of the second argument.',
      parameters: [
        { label: 'double a', documentation: 'The base.' },
        { label: 'double b', documentation: 'The exponent.' }
      ]
    },
    'Arrays.sort': {
      label: 'Arrays.sort(T[] a)',
      documentation: 'Sorts the specified array into ascending order.',
      parameters: [
        { label: 'a', documentation: 'The array to be sorted.' }
      ]
    },
    'Arrays.fill': {
      label: 'Arrays.fill(T[] a, T val)',
      documentation: 'Assigns the specified value to each element of the specified array.',
      parameters: [
        { label: 'a', documentation: 'The array to be filled.' },
        { label: 'val', documentation: 'The value to be stored in all elements.' }
      ]
    }
  }
};

// =============================================================================
// 4. USER SYMBOL EXTRACTION (Functions, Variables, Parameters, Classes)
// =============================================================================

/**
 * Extracts declared functions, variables, parameters, and classes from the active code in real time.
 * Identifies active function scope based on cursorLine to give parameters in current scope priority.
 */
export function extractUserSymbols(code, language, cursorLine = 1) {
  if (!code || typeof code !== 'string') {
    return { functions: [], variables: [], parameters: [], classes: [] };
  }

  const lines = code.split('\n');
  const lang = (language || 'python').toLowerCase();

  const userFunctions = [];
  const userVariables = [];
  const userParameters = [];
  const userClasses = [];

  const seenFunctions = new Set();
  const seenVariables = new Set();
  const seenParameters = new Set();
  const seenClasses = new Set();

  // Helper to extract clean parameter tokens
  const cleanParamToken = (token) => {
    let p = token.trim();
    if (!p) return null;
    // strip default values (= ...)
    if (p.includes('=')) p = p.split('=')[0].trim();
    // strip type annotations (: ...) in Python
    if (p.includes(':')) p = p.split(':')[0].trim();
    // strip pointer / reference markers in C / C++
    p = p.replace(/[*&]/g, ' ').trim();
    // take the last word token (e.g. "int age" -> "age", "const string& name" -> "name")
    const words = p.split(/\s+/).filter(Boolean);
    const identifier = words[words.length - 1] || '';
    if (!/^[a-zA-Z_]\w*$/.test(identifier)) return null;
    // Avoid keywords
    if (['void', 'int', 'float', 'double', 'char', 'bool', 'auto', 'const', 'unsigned', 'signed', 'self', 'cls'].includes(identifier)) {
      return null;
    }
    return identifier;
  };

  if (lang === 'python') {
    // 1. Python Function Definitions: def func_name(a, b=10):
    const funcRegex = /^[ \t]*def[ \t]+([a-zA-Z_]\w*)[ \t]*\(([^)]*)\)/;
    // 2. Python Class Definitions: class ClassName:
    const classRegex = /^[ \t]*class[ \t]+([a-zA-Z_]\w*)/;
    // 3. Python Variable Assignments: var_name = ... or a, b = ...
    const assignRegex = /^[ \t]*([a-zA-Z_]\w*(?:[ \t]*,[ \t]*[a-zA-Z_]\w*)*)[ \t]*(?::[ \t]*[a-zA-Z_0-9[\], ]+)?[ \t]*=(?!=)/;
    // 4. Python For Loops: for item in items:
    const forRegex = /^[ \t]*for[ \t]+([a-zA-Z_]\w*(?:[ \t]*,[ \t]*[a-zA-Z_]\w*)*)[ \t]+in/;

    let activeFuncScope = null;

    lines.forEach((line, idx) => {
      const lineNum = idx + 1;
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) return;

      // Match Function
      const fMatch = line.match(funcRegex);
      if (fMatch) {
        const name = fMatch[1];
        const rawParams = fMatch[2] ? fMatch[2].split(',').map(cleanParamToken).filter(Boolean) : [];
        const isCurrentScope = cursorLine >= lineNum;

        if (isCurrentScope) {
          activeFuncScope = name;
        }

        if (!seenFunctions.has(name)) {
          seenFunctions.add(name);
          userFunctions.push({
            name,
            params: rawParams,
            line: lineNum,
            documentation: `User-defined function at line ${lineNum}`,
            detail: `(${rawParams.join(', ')})`,
            insertSnippet: `${name}(${rawParams.map((p, i) => `\${${i + 1}:${p}}`).join(', ')})$0`
          });
        }

        rawParams.forEach((paramName) => {
          const key = `${name}_${paramName}`;
          if (!seenParameters.has(key)) {
            seenParameters.add(key);
            userParameters.push({
              name: paramName,
              functionName: name,
              line: lineNum,
              isCurrentScope: activeFuncScope === name
            });
          }
        });
        return;
      }

      // Match Class
      const cMatch = line.match(classRegex);
      if (cMatch) {
        const name = cMatch[1];
        if (!seenClasses.has(name)) {
          seenClasses.add(name);
          userClasses.push({
            name,
            line: lineNum,
            documentation: `User-defined class at line ${lineNum}`
          });
        }
        return;
      }

      // Match Variables from assignment
      const aMatch = line.match(assignRegex);
      if (aMatch) {
        const varList = aMatch[1].split(',').map(s => s.trim()).filter(s => /^[a-zA-Z_]\w*$/.test(s));
        varList.forEach((v) => {
          if (!seenVariables.has(v) && !seenFunctions.has(v)) {
            seenVariables.add(v);
            const isConst = v === v.toUpperCase() && v.length > 1;
            userVariables.push({
              name: v,
              line: lineNum,
              isConstant: isConst,
              detail: isConst ? 'Constant' : 'Variable',
              documentation: `User-declared ${isConst ? 'constant' : 'variable'} at line ${lineNum}`
            });
          }
        });
      }

      // Match Variables from for-loops
      const forMatch = line.match(forRegex);
      if (forMatch) {
        const loopVars = forMatch[1].split(',').map(s => s.trim()).filter(s => /^[a-zA-Z_]\w*$/.test(s));
        loopVars.forEach((v) => {
          if (!seenVariables.has(v)) {
            seenVariables.add(v);
            userVariables.push({
              name: v,
              line: lineNum,
              isConstant: false,
              detail: 'Loop variable',
              documentation: `Loop variable declared at line ${lineNum}`
            });
          }
        });
      }
    });
  } else if (lang === 'c' || lang === 'cpp') {
    // C / C++ functions: e.g. int calculate_sum(int a, int b) { or void solve() {
    const cFuncRegex = /^[ \t]*(?:(?:inline|static|virtual|const|extern|unsigned|signed|long|short|void|int|float|double|char|bool|auto|vector<[^>]+>|string|pair<[^>]+>|[\w:]+)[*&\s]+)+([a-zA-Z_]\w*)[ \t]*\(([^;{)]*)\)[ \t]*(?:const)?[ \t]*\{/;
    // C / C++ structs / classes
    const structRegex = /^[ \t]*(?:struct|class)[ \t]+([a-zA-Z_]\w*)/;
    // C / C++ variable declarations: int x = 10; or double max_val;
    const cVarRegex = /^[ \t]*(?:const\s+)?(?:unsigned\s+|signed\s+|long\s+|short\s+)?(?:int|float|double|char|bool|auto|string|vector<[^>]+>|[\w:]+)[*&\s]+([a-zA-Z_]\w*)(?:[ \t]*=[^;]+|[ \t]*\(.*?\))?[ \t]*;/;

    let activeFuncScope = null;

    lines.forEach((line, idx) => {
      const lineNum = idx + 1;
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('//') || trimmed.startsWith('/*')) return;

      const fMatch = line.match(cFuncRegex);
      if (fMatch) {
        const name = fMatch[1];
        if (!['if', 'while', 'for', 'switch', 'catch'].includes(name)) {
          const rawParams = fMatch[2] ? fMatch[2].split(',').map(cleanParamToken).filter(Boolean) : [];
          if (cursorLine >= lineNum) activeFuncScope = name;

          if (!seenFunctions.has(name)) {
            seenFunctions.add(name);
            userFunctions.push({
              name,
              params: rawParams,
              line: lineNum,
              documentation: `User-defined function at line ${lineNum}`,
              detail: `(${rawParams.join(', ')})`,
              insertSnippet: `${name}(${rawParams.map((p, i) => `\${${i + 1}:${p}}`).join(', ')})$0`
            });
          }

          rawParams.forEach((paramName) => {
            const key = `${name}_${paramName}`;
            if (!seenParameters.has(key)) {
              seenParameters.add(key);
              userParameters.push({
                name: paramName,
                functionName: name,
                line: lineNum,
                isCurrentScope: activeFuncScope === name
              });
            }
          });
          return;
        }
      }

      const sMatch = line.match(structRegex);
      if (sMatch) {
        const name = sMatch[1];
        if (!seenClasses.has(name)) {
          seenClasses.add(name);
          userClasses.push({
            name,
            line: lineNum,
            documentation: `User-defined structure/class at line ${lineNum}`
          });
        }
        return;
      }

      const vMatch = line.match(cVarRegex);
      if (vMatch) {
        const name = vMatch[1];
        if (!seenVariables.has(name) && !['return', 'break', 'continue'].includes(name)) {
          seenVariables.add(name);
          const isConst = name === name.toUpperCase() && name.length > 1;
          userVariables.push({
            name,
            line: lineNum,
            isConstant: isConst,
            detail: isConst ? 'Constant' : 'Variable',
            documentation: `Declared ${isConst ? 'constant' : 'variable'} at line ${lineNum}`
          });
        }
      }
    });
  } else if (lang === 'java') {
    // Java methods: public int calculateSum(int a, int b) { or static void helper(int n) {
    const javaMethodRegex = /^[ \t]*(?:(?:public|protected|private|static|final|abstract|synchronized)\s+)*(?:<[^>]+>\s+)?([a-zA-Z_0-9<>[\]]+)\s+([a-zA-Z_]\w*)\s*\(([^;{)]*)\)\s*(?:throws\s+[\w\s,]+)?\s*\{/;
    // Java classes
    const javaClassRegex = /^[ \t]*(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:class|interface|enum|record)\s+([a-zA-Z_]\w*)/;
    // Java variable declarations: int age = 21; or String name = "Ranjan";
    const javaVarRegex = /^[ \t]*(?:final\s+)?(?:static\s+)?(?:[a-zA-Z_0-9<>[\]]+)\s+([a-zA-Z_]\w*)\s*(?:=[^;]+)?[ \t]*;/;

    let activeFuncScope = null;

    lines.forEach((line, idx) => {
      const lineNum = idx + 1;
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('//') || trimmed.startsWith('/*')) return;

      const mMatch = line.match(javaMethodRegex);
      if (mMatch) {
        const name = mMatch[2];
        if (!['if', 'while', 'for', 'switch', 'catch'].includes(name)) {
          const rawParams = mMatch[3] ? mMatch[3].split(',').map(cleanParamToken).filter(Boolean) : [];
          if (cursorLine >= lineNum) activeFuncScope = name;

          if (!seenFunctions.has(name)) {
            seenFunctions.add(name);
            userFunctions.push({
              name,
              params: rawParams,
              line: lineNum,
              documentation: `User-defined method at line ${lineNum}`,
              detail: `(${rawParams.join(', ')})`,
              insertSnippet: `${name}(${rawParams.map((p, i) => `\${${i + 1}:${p}}`).join(', ')})$0`
            });
          }

          rawParams.forEach((paramName) => {
            const key = `${name}_${paramName}`;
            if (!seenParameters.has(key)) {
              seenParameters.add(key);
              userParameters.push({
                name: paramName,
                functionName: name,
                line: lineNum,
                isCurrentScope: activeFuncScope === name
              });
            }
          });
          return;
        }
      }

      const cMatch = line.match(javaClassRegex);
      if (cMatch) {
        const name = cMatch[1];
        if (!seenClasses.has(name)) {
          seenClasses.add(name);
          userClasses.push({
            name,
            line: lineNum,
            documentation: `User-defined class at line ${lineNum}`
          });
        }
        return;
      }

      const vMatch = line.match(javaVarRegex);
      if (vMatch) {
        const name = vMatch[1];
        if (!seenVariables.has(name) && !['return', 'break', 'continue', 'package', 'import'].includes(name)) {
          seenVariables.add(name);
          const isConst = name === name.toUpperCase() && name.length > 1;
          userVariables.push({
            name,
            line: lineNum,
            isConstant: isConst,
            detail: isConst ? 'Constant' : 'Variable',
            documentation: `Declared ${isConst ? 'constant' : 'variable'} at line ${lineNum}`
          });
        }
      }
    });
  }

  return {
    functions: userFunctions,
    variables: userVariables,
    parameters: userParameters,
    classes: userClasses
  };
}

// =============================================================================
// 5. SIGNATURE HELP PARSER & LOOKUP
// =============================================================================

/**
 * Scans backwards from current cursor position across lines to find the enclosing function call
 * and counts parameter index based on commas at depth 0.
 */
export function parseCallBeforeCursor(text) {
  if (!text || typeof text !== 'string') return null;

  let depth = 0;
  let paramIndex = 0;
  let openParenIndex = -1;

  for (let i = text.length - 1; i >= 0; i--) {
    const ch = text[i];
    if (ch === ')') {
      depth++;
    } else if (ch === '(') {
      if (depth === 0) {
        openParenIndex = i;
        break;
      } else {
        depth--;
      }
    } else if (ch === ',' && depth === 0) {
      paramIndex++;
    }
  }

  if (openParenIndex === -1) return null;

  // Extract function identifier immediately preceding the open parenthesis
  const beforeParen = text.substring(0, openParenIndex).trimEnd();
  const idMatch = beforeParen.match(/([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)$/);
  if (!idMatch) return null;

  return {
    funcName: idMatch[1],
    paramIndex
  };
}

/**
 * Returns signature information for a function name, checking both user-defined functions and built-in catalogs.
 */
export function getFunctionSignature(funcName, language, userSymbols = null) {
  const lang = (language || 'python').toLowerCase();

  // 1. Check user-defined functions first
  if (userSymbols && Array.isArray(userSymbols.functions)) {
    const userFn = userSymbols.functions.find(f => f.name === funcName);
    if (userFn) {
      return {
        label: `${userFn.name}(${userFn.params.join(', ')})`,
        documentation: `User-defined function declared at line ${userFn.line}`,
        parameters: userFn.params.map(p => ({
          label: p,
          documentation: `Parameter: ${p}`
        }))
      };
    }
  }

  // 2. Check built-in signatures
  const builtins = BUILTIN_SIGNATURES[lang];
  if (builtins && builtins[funcName]) {
    return builtins[funcName];
  }

  return null;
}

// =============================================================================
// 6. MONACO COMPLETION ITEM CONVERTER
// =============================================================================

function mapCompletionKind(kindStr, monaco) {
  if (!monaco || !monaco.languages || !monaco.languages.CompletionItemKind) {
    return 1; // Default to Function
  }
  const K = monaco.languages.CompletionItemKind;
  switch (kindStr) {
    case 'Function': return K.Function;
    case 'Method': return K.Method;
    case 'Variable': return K.Variable;
    case 'Constant': return K.Constant;
    case 'Class': return K.Class;
    case 'Snippet': return K.Snippet;
    case 'Keyword': return K.Keyword;
    case 'Field': return K.Field;
    case 'Module': return K.Module;
    default: return K.Text;
  }
}

// =============================================================================
// 7. MONACO INTELLISENSE INITIALIZATION & REGISTRATION
// =============================================================================

/**
 * Registers VS Code-like IntelliSense and auto-completion providers for all 4 supported languages.
 * Safe and idempotent: cleanly disposes previously registered providers to avoid duplicate suggestions.
 */
export function registerCodeAcharyaIntelliSense(monaco) {
  if (!monaco || !monaco.languages) {
    console.warn('[CodeAcharyaIntelliSense] Monaco languages API not available.');
    return () => {};
  }

  // If already initialized on this monaco instance, clean up prior disposables first
  if (isIntelliSenseInitialized) {
    disposeCodeAcharyaIntelliSense();
  }

  const supportedLanguages = ['python', 'c', 'cpp', 'java'];
  const disposables = [];

  supportedLanguages.forEach((languageId) => {
    // -------------------------------------------------------------------------
    // A. COMPLETION ITEM PROVIDER
    // -------------------------------------------------------------------------
    const completionProvider = monaco.languages.registerCompletionItemProvider(languageId, {
      triggerCharacters: ['.', '(', ' ', '#', ':', '<', '"', "'"],
      provideCompletionItems(model, position) {
        // Enforce lock-state restriction: Never provide completions if editor is locked
        if (typeof window !== 'undefined' && window.__codeAcharyaIsLocked) {
          return { suggestions: [] };
        }

        const code = model.getValue();
        const wordInfo = model.getWordUntilPosition(position);
        const range = {
          startLineNumber: position.lineNumber,
          endLineNumber: position.lineNumber,
          startColumn: wordInfo.startColumn,
          endColumn: wordInfo.endColumn
        };

        const lineContent = model.getLineContent(position.lineNumber);
        const charBeforeWord = position.column > 1 ? lineContent.charAt(position.column - 2) : '';
        const isMemberAccess = charBeforeWord === '.';

        const suggestions = [];
        const seenLabels = new Set();

        const insertRule = monaco.languages.CompletionItemInsertTextRule
          ? monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
          : 4;

        // 1. If triggered by '.', provide member access completions (methods & properties)
        if (isMemberAccess) {
          const members = MEMBER_COMPLETIONS[languageId] || [];
          members.forEach((m) => {
            if (!seenLabels.has(m.label)) {
              seenLabels.add(m.label);
              suggestions.push({
                label: m.label,
                kind: mapCompletionKind(m.kind, monaco),
                detail: m.detail,
                documentation: m.documentation || '',
                insertText: m.insertText,
                insertTextRules: m.isSnippet ? insertRule : 0,
                range,
                sortText: `00_${m.label}`
              });
            }
          });
          return { suggestions };
        }

        // 2. Extract dynamic user symbols from the active code
        const userSymbols = extractUserSymbols(code, languageId, position.lineNumber);

        // User Parameters (promoted if inside current function scope)
        userSymbols.parameters.forEach((param) => {
          if (!seenLabels.has(param.name)) {
            seenLabels.add(param.name);
            suggestions.push({
              label: param.name,
              kind: mapCompletionKind('Variable', monaco),
              detail: param.isCurrentScope ? `Parameter (in ${param.functionName})` : `Parameter (${param.functionName})`,
              documentation: `Function parameter declared at line ${param.line}`,
              insertText: param.name,
              range,
              sortText: param.isCurrentScope ? `01_${param.name}` : `05_${param.name}`
            });
          }
        });

        // User Variables & Constants
        userSymbols.variables.forEach((v) => {
          if (!seenLabels.has(v.name)) {
            seenLabels.add(v.name);
            suggestions.push({
              label: v.name,
              kind: mapCompletionKind(v.isConstant ? 'Constant' : 'Variable', monaco),
              detail: v.detail,
              documentation: v.documentation,
              insertText: v.name,
              range,
              sortText: `02_${v.name}`
            });
          }
        });

        // User Functions (with parameter placeholders snippet)
        userSymbols.functions.forEach((fn) => {
          if (!seenLabels.has(fn.name)) {
            seenLabels.add(fn.name);
            suggestions.push({
              label: fn.name,
              kind: mapCompletionKind('Function', monaco),
              detail: fn.detail,
              documentation: fn.documentation,
              insertText: fn.insertSnippet,
              insertTextRules: insertRule,
              range,
              sortText: `03_${fn.name}`
            });
          }
        });

        // User Classes
        userSymbols.classes.forEach((cls) => {
          if (!seenLabels.has(cls.name)) {
            seenLabels.add(cls.name);
            suggestions.push({
              label: cls.name,
              kind: mapCompletionKind('Class', monaco),
              detail: 'Class',
              documentation: cls.documentation,
              insertText: cls.name,
              range,
              sortText: `04_${cls.name}`
            });
          }
        });

        // 3. Language-specific Built-in functions, APIs, and snippets
        const builtins = BUILTIN_COMPLETIONS[languageId] || [];
        builtins.forEach((item) => {
          if (!seenLabels.has(item.label)) {
            seenLabels.add(item.label);
            suggestions.push({
              label: item.label,
              kind: mapCompletionKind(item.kind, monaco),
              detail: item.detail,
              documentation: item.documentation,
              insertText: item.insertText,
              insertTextRules: item.isSnippet ? insertRule : 0,
              range,
              sortText: `10_${item.label}`
            });
          }
        });

        return { suggestions };
      }
    });
    disposables.push(completionProvider);

    // -------------------------------------------------------------------------
    // B. SIGNATURE HELP PROVIDER
    // -------------------------------------------------------------------------
    const signatureProvider = monaco.languages.registerSignatureHelpProvider(languageId, {
      signatureHelpTriggerCharacters: ['(', ','],
      signatureHelpRetriggerCharacters: [','],
      provideSignatureHelp(model, position) {
        if (typeof window !== 'undefined' && window.__codeAcharyaIsLocked) {
          return null;
        }

        // Build text context scanning backwards up to 10 lines
        const startLine = Math.max(1, position.lineNumber - 10);
        let text = '';
        for (let l = startLine; l < position.lineNumber; l++) {
          text += model.getLineContent(l) + '\n';
        }
        text += model.getLineContent(position.lineNumber).substring(0, position.column - 1);

        const callInfo = parseCallBeforeCursor(text);
        if (!callInfo) return null;

        const { funcName, paramIndex } = callInfo;
        const userSymbols = extractUserSymbols(model.getValue(), languageId, position.lineNumber);
        const sig = getFunctionSignature(funcName, languageId, userSymbols);
        if (!sig) return null;

        const activeParam = Math.min(
          paramIndex,
          Math.max(0, sig.parameters ? sig.parameters.length - 1 : 0)
        );

        return {
          value: {
            signatures: [
              {
                label: sig.label,
                documentation: sig.documentation,
                parameters: sig.parameters.map(p => ({
                  label: p.label,
                  documentation: p.documentation || ''
                }))
              }
            ],
            activeSignature: 0,
            activeParameter: activeParam
          },
          dispose: () => {}
        };
      }
    });
    disposables.push(signatureProvider);
  });

  activeIntelliSenseDisposables = disposables;
  isIntelliSenseInitialized = true;

  return () => {
    disposeCodeAcharyaIntelliSense();
  };
}

/**
 * Disposes all active Monaco completion and signature providers to prevent memory leaks and duplication.
 */
export function disposeCodeAcharyaIntelliSense() {
  if (Array.isArray(activeIntelliSenseDisposables)) {
    activeIntelliSenseDisposables.forEach((d) => {
      try {
        if (d && typeof d.dispose === 'function') {
          d.dispose();
        }
      } catch (err) {
        console.debug('[CodeAcharyaIntelliSense] Error during disposal:', err);
      }
    });
  }
  activeIntelliSenseDisposables = [];
  isIntelliSenseInitialized = false;
}

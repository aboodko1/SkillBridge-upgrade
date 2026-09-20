"""Small, curated CS knowledge base used by the Learning system.

This module is deliberately data-first: canonical curriculum, prerequisites, and
lesson facts live here, never in an LLM prompt.  Only entries marked ``complete``
can be served as a canonical lesson.  Planned entries document the extension
shape without pretending that their content has shipped.
"""
from copy import deepcopy
import re


KNOWLEDGE_BASE_VERSION = "cs-kb-v2"


def _key(value):
    # Competencies are persisted both as display labels and as path identifiers
    # (for example ``python_error_handling``).  Treat those representations as
    # the same canonical lookup key so a stored path cannot fall back to a
    # generic generated lesson.
    return re.sub(r"\s+", " ", str(value or "").replace("_", " ").strip()).lower()


PYTHON_FUNCTIONS = {
    "status": "complete",
    "skill_aliases": ("python", "python programming"),
    "competency": "Python Functions",
    "objective": "Define a Python function with parameters and return a reusable value.",
    "prerequisites": [
        {
            "competency": "Python values, variables, and expressions",
            "relationship": "required foundation",
            "why": "Function arguments and return values are ordinary Python values; you need to read assignments and expressions to follow a function call.",
        },
    ],
    "roadmap_rationale": (
        "Python Functions appears in this roadmap because it is the first reusable-unit skill: "
        "it lets you turn repeated steps into a named, testable behavior. The canonical Python "
        "curriculum places it after values, variables, and expressions, not because a role demands it."
    ),
    "learn": {
        "title": "Python Functions",
        "explanation": (
            "A **function** is a named recipe for a small job. `def` creates the recipe, "
            "parameters receive input, and `return` sends a result back to the caller."
        ),
        "key_ideas": [
            "Define a function with `def name(parameters):` and an indented body.",
            "Arguments are the values supplied at a call; parameters are the names inside the definition.",
            "Use `return` when later code needs the computed value; `print` only displays text.",
            "Keep one function focused on one clear responsibility so it is easy to test and reuse.",
        ],
        "key_terms": {
            "function": "A named block of reusable code.",
            "parameter": "A variable in the function definition that receives an input.",
            "argument": "A concrete value passed when calling a function.",
            "return value": "The value a function sends back to its caller.",
        },
        "job_relevance": "Functions make small pieces of application, data, and automation code reusable and independently testable.",
        "common_mistake": "Do not confuse `print(total)` with `return total`: printed output cannot be used by the next line of program logic.",
        "worked_example": "The example calculates a delivery total from two inputs, then checks the returned value with several inputs.",
        "depth_note": "Canonical beginner content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use Python 3 syntax and the standard library only.",
        "grounding_sources": [{"title": "Python tutorial: defining functions", "url": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions", "source": "Python documentation"}],
    },
    "example": {
        "title": "A reusable delivery-total function",
        "type": "code",
        "content": (
            "def delivery_total(price, delivery_fee):\n"
            "    return price + delivery_fee\n\n"
            "assert delivery_total(20, 5) == 25\n"
            "assert delivery_total(0, 5) == 5\n"
            "assert delivery_total(12.5, 2.5) == 15.0\n\n"
            "print(delivery_total(20, 5))  # 25"
        ),
        "explanation": "`price` and `delivery_fee` are parameters. Each call provides arguments, and `return` makes the sum available to `assert` and `print`.",
    },
    "practice": {
        "type": "practical",
        "title": "Write a temperature conversion function",
        "task": "Write `celsius_to_fahrenheit(celsius)` that returns the Fahrenheit value using `(celsius * 9 / 5) + 32`. Do not print inside the function. Include your function and a short note explaining why `return` is needed.",
        "response_type": "code",
        "competency": "Python Functions",
        "starter_code": "def celsius_to_fahrenheit(celsius):\n    # write your code here\n    pass\n",
        "automated_tests": [
            {"input": [0], "expected": 32},
            {"input": [100], "expected": 212},
            {"input": [-40], "expected": -40},
            {"input": [37.5], "expected": 99.5},
        ],
    },
    "mini_check": {
        "questions": [
            {"id": "m1", "type": "mcq", "question": "Which line sends a computed value back to the caller?", "options": ["print(total)", "return total", "def total", "total = input()"], "correct_answer": "return total", "competency": "Python Functions", "difficulty": "beginner", "misconception_hint": "Compare what each construct does after the function call finishes."},
            {"id": "m2", "type": "mcq", "question": "In `def greet(name):`, what is `name`?", "options": ["An argument", "A parameter", "A return value", "A module"], "correct_answer": "A parameter", "competency": "Python Functions", "difficulty": "beginner", "misconception_hint": "Look at whether the name appears in the definition or at a call site."},
            {"id": "m3", "type": "mcq", "question": "What does `delivery_total(20, 5)` evaluate to in the lesson example?", "options": ["20", "5", "25", "It only prints a value"], "correct_answer": "25", "competency": "Python Functions", "difficulty": "beginner", "misconception_hint": "Follow the arithmetic in the function body using both supplied values."},
        ]
    },
    # Display translations deliberately retain canonical English answer values.
    # The client uses these question strings/options only for presentation; the
    # persisted Mini Check continues to grade its immutable canonical set.
    "locales": {
        "ar": {
            "learn": {
                "title": "دوال بايثون",
                "explanation": "الدالة هي وصفة لها اسم لمهمة صغيرة. نستخدم `def` لتعريفها، والمعاملات تستقبل المدخلات، و`return` يرجّع النتيجة للكود الذي استدعى الدالة.",
                "key_ideas": ["عرّف الدالة بـ `def name(parameters):` واكتب جسمها بمسافة بادئة.", "المعامل اسمه داخل تعريف الدالة، أما القيمة التي نمررها عند الاستدعاء فهي argument.", "استخدم `return` عندما يحتاج الكود التالي للنتيجة؛ `print` يعرضها فقط."],
                "key_terms": {"دالة": "كتلة كود لها اسم ويمكن إعادة استخدامها.", "معامل": "اسم داخل تعريف الدالة يستقبل مدخلاً.", "قيمة مُعادة": "قيمة ترسلها الدالة إلى المستدعي."},
                "job_relevance": "الدوال تجعل أجزاء الكود في التطبيقات والتحليل والأتمتة قابلة لإعادة الاستخدام والاختبار.",
                "common_mistake": "لا تخلط بين `print(total)` و`return total`: الأولى تعرض القيمة فقط، والثانية تسمح للكود التالي باستخدامها.",
                "worked_example": "المثال يحسب إجمالي التوصيل من سعر ورسوم، ثم يتحقق من القيمة المعادة بأكثر من مدخل.",
            },
            "example": {"title": "دالة قابلة لإعادة الاستخدام لحساب إجمالي التوصيل", "type": "code", "content": "def delivery_total(price, delivery_fee):\n    return price + delivery_fee\n\nassert delivery_total(20, 5) == 25\nassert delivery_total(0, 5) == 5\nassert delivery_total(12.5, 2.5) == 15.0\n\nprint(delivery_total(20, 5))  # 25", "explanation": "`price` و`delivery_fee` معاملان. كل استدعاء يمرر قيماً، و`return` يجعل المجموع متاحاً لـ `assert` و`print`."},
            "practice": {"title": "اكتب دالة لتحويل الحرارة", "task": "اكتب `celsius_to_fahrenheit(celsius)` لترجع قيمة فهرنهايت باستخدام `(celsius * 9 / 5) + 32`. لا تستخدم `print` داخل الدالة. أضف الدالة وجملة قصيرة تشرح لماذا نستخدم `return`.", "response_type": "code", "competency": "Python Functions", "starter_code": "def celsius_to_fahrenheit(celsius):\n    # اكتب الكود هنا\n    pass\n"},
            "mini_check": {"questions": [
                {"id": "m1", "question": "أي سطر يرسل قيمة محسوبة للكود اللي استدعى الدالة؟", "options": ["print(total)", "return total", "def total", "total = input()"], "misconception_hint": "قارن وظيفة كل تركيب بعد ما ينتهي استدعاء الدالة."},
                {"id": "m2", "question": "في `def greet(name):`، إيه وصف `name`؟", "options": ["قيمة مرّرتها عند الاستدعاء", "معامل في تعريف الدالة", "قيمة راجعة", "وحدة برمجية"], "misconception_hint": "بصّ: الاسم مكتوب في تعريف الدالة ولا وقت استدعائها؟"},
                {"id": "m3", "question": "إيه قيمة `delivery_total(20, 5)` في مثال الدرس؟", "options": ["20", "5", "25", "بتطبع قيمة بس"], "misconception_hint": "اتبع العملية الحسابية جوه جسم الدالة باستخدام القيمتين."},
            ]},
        },
    },
}


PYTHON_ERROR_HANDLING = {
    "status": "complete",
    "skill_aliases": ("python", "python programming"),
    "competency": "Python Error Handling",
    "objective": "Handle an expected conversion error with try/except and return a clear result.",
    "prerequisites": [{
        "competency": "Python Functions",
        "relationship": "required foundation",
        "why": "Handling an error inside a function is easier to follow after you can read parameters and return values.",
    }],
    "roadmap_rationale": "Python Error Handling follows Python Functions because programs need a safe response when real input cannot be converted or processed.",
    "learn": {
        "title": "Python Error Handling",
        "explanation": "An **exception** is Python's signal that an operation cannot continue normally. Put code that may fail in `try`; use `except ValueError` for a value in the wrong format. Handle the specific error you expect, then return a useful result instead of letting the program stop.",
        "key_ideas": ["`try` contains an operation that may raise an exception.", "`except ValueError` handles invalid numeric text; it should not hide unrelated errors.", "Return a value from both the success and error paths so the caller can decide what to do."],
        "key_terms": {"exception": "A runtime problem Python reports.", "try": "The block containing an operation that may fail.", "except": "The block that handles one expected exception."},
        "job_relevance": "Programs receive incomplete and incorrectly formatted input. Specific handling keeps a small failure from crashing the whole task.",
        "common_mistake": "Do not write bare `except:` here: it can hide programming mistakes that should be fixed.",
        "worked_example": "The example turns a text age into an integer. `\"24\"` returns `24`; `\"twenty\"` returns `None` without crashing.",
        "grounding_sources": [{"title": "Python documentation: Errors and Exceptions", "url": "https://docs.python.org/3/tutorial/errors.html", "source": "Python documentation"}],
    },
    "example": {
        "title": "Convert an age safely",
        "type": "code",
        "content": "def parse_age(text):\n    try:\n        return int(text)\n    except ValueError:\n        return None\n\nprint(parse_age(\"24\"))      # 24\nprint(parse_age(\"twenty\"))  # None",
        "explanation": "`int(\"24\")` succeeds, so the function returns `24`. `int(\"twenty\")` raises `ValueError`, so the matching `except` returns `None`. The code is not executed by SkillBridge; these outputs explain Python's expected behavior.",
    },
    "practice": {
        "type": "practical", "title": "Parse a score without crashing",
        "task": "Write `parse_score(text)`. It should return `int(text)` for numeric text such as `\"85\"`. If the text is not an integer such as `\"eighty\"`, catch only `ValueError` and return `None`. Add one sentence explaining why a bare `except:` is not used.",
        "response_type": "code", "competency": "Python Error Handling",
        "starter_code": "def parse_score(text):\n    # convert text safely\n    pass\n",
        "automated_tests": [{"input": ["85"], "expected": 85}, {"input": ["0"], "expected": 0}, {"input": ["eighty"], "expected": None}],
    },
    "mini_check": {"questions": [
        {"id": "e1", "type": "mcq", "question": "Which exception does `int(\"eighty\")` raise?", "options": ["ValueError", "TypeError", "KeyError", "No exception"], "correct_answer": "ValueError", "competency": "Python Error Handling", "difficulty": "beginner", "misconception_hint": "Consider what kind of conversion the expression attempts and why the input cannot satisfy it."},
        {"id": "e2", "type": "mcq", "question": "What does `parse_age(\"twenty\")` return in the worked example?", "options": ["24", "None", "\"twenty\"", "The program must crash"], "correct_answer": "None", "competency": "Python Error Handling", "difficulty": "beginner", "misconception_hint": "Trace the error path in the function after the conversion cannot succeed."},
        {"id": "e3", "type": "mcq", "question": "Why is `except ValueError:` safer than a bare `except:` here?", "options": ["It handles the expected invalid-number input without hiding every other bug", "It runs faster", "It converts all text to integers", "It removes the need for try"], "correct_answer": "It handles the expected invalid-number input without hiding every other bug", "competency": "Python Error Handling", "difficulty": "beginner", "misconception_hint": "Think about which problems should still be visible to the developer."},
    ]},
    # Presentation-only reviewed Arabic fields.  Question answer values remain
    # canonical so a persisted Mini Check is evaluated against exactly the
    # content it was issued with.
    "locales": {
        "ar": {
            "learn": {
                "title": "التعامل مع أخطاء بايثون",
                "explanation": "الاستثناء هو إشارة من بايثون إلى أن العملية لا يمكن أن تستمر بشكل طبيعي. ضع السطر الذي قد يفشل داخل `try`، واستخدم `except ValueError` عندما تكون قيمة النص بصيغة غير صحيحة. تعامل مع الخطأ المتوقع تحديدًا، ثم أعد نتيجة مفيدة بدل أن يتوقف البرنامج.",
                "key_ideas": ["يحتوي `try` على عملية قد تثير استثناءً.", "يتعامل `except ValueError` مع النص الرقمي غير الصحيح من دون إخفاء أخطاء أخرى.", "أعد قيمة في مسار النجاح ومسار الخطأ كي يقرر المستدعي ما يفعله."],
                "key_terms": {"استثناء": "مشكلة وقت تشغيل يبلغ عنها بايثون.", "try": "كتلة تحتوي على عملية قد تفشل.", "except": "كتلة تعالج استثناءً متوقعًا."},
                "job_relevance": "تصل البرامج مدخلات ناقصة أو بصيغة خاطئة؛ التعامل المحدد مع الخطأ يمنع فشلًا صغيرًا من إيقاف المهمة كلها.",
                "common_mistake": "لا تستخدم `except:` بلا اسم هنا؛ فقد يخفي خطأً برمجيًا يجب إصلاحه.",
                "worked_example": "يحوّل المثال نص العمر إلى عدد صحيح. تعيد `\"24\"` القيمة `24`، وتعطي `\"twenty\"` القيمة `None` من دون توقف البرنامج.",
            },
            "example": {
                "title": "تحويل العمر بأمان",
                "type": "code",
                "content": "def parse_age(text):\n    try:\n        return int(text)\n    except ValueError:\n        return None\n\nprint(parse_age(\"24\"))      # 24\nprint(parse_age(\"twenty\"))  # None",
                "explanation": "ينجح `int(\"24\")` فتُعاد `24`. أما `int(\"twenty\")` فيثير `ValueError`، لذلك تعيد كتلة `except` القيمة `None`. هذا المثال للشرح؛ SkillBridge لا ينفذ هذا الكود.",
            },
            "practice": {
                "title": "حلّل درجة من دون توقف البرنامج",
                "task": "اكتب `parse_score(text)`. يجب أن تعيد `int(text)` للنص الرقمي مثل `\"85\"`. إذا لم يكن النص عددًا صحيحًا مثل `\"eighty\"`، التقط `ValueError` فقط وأعد `None`. أضف جملة تشرح لماذا لا نستخدم `except:` بلا اسم.",
                "response_type": "code", "competency": "Python Error Handling",
                "starter_code": "def parse_score(text):\n    # حوّل النص بأمان هنا\n    pass\n",
            },
            "mini_check": {"questions": [
                {"id": "e1", "question": "أي استثناء بينتج من `int(\"eighty\")`؟", "options": ["ValueError", "TypeError", "KeyError", "مفيش استثناء"], "misconception_hint": "فكّر التحويل ده بيحاول يعمل إيه وليه النص المدخل مش مناسب له."},
                {"id": "e2", "question": "إيه اللي بترجعه `parse_age(\"twenty\")` في المثال؟", "options": ["24", "None", "\"twenty\"", "البرنامج لازم يقف بخطأ"], "misconception_hint": "اتبع مسار الخطأ في الدالة بعد ما التحويل ما ينجحش."},
                {"id": "e3", "question": "ليه `except ValueError:` أأمن من `except:` من غير اسم هنا؟", "options": ["بيعالج إدخال الرقم الغلط من غير ما يخفي باقي الأخطاء", "أسرع", "بيحوّل كل النصوص لأرقام", "بيغني عن try"], "misconception_hint": "فكّر في المشاكل اللي المفروض تفضل ظاهرة للمطوّر."},
            ]},
        },
    },
}


# Read-only SQL topics are marked complete only once their curated content ships
# here (Queries & Filtering, Sorting & Limiting, Aggregation, Joins, Subqueries,
# Indexing basics, and Window functions).  The remaining SQL blueprint
# competencies stay useful for diagnostics/planning, but have no canonical lesson
# and must therefore stay experimental/unverified.
SQL_QUERIES_FILTERING = {
    "status": "complete",
    "skill_aliases": ("sql", "structured query language"),
    "competency": "SQL Queries & Filtering",
    "objective": "Retrieve named columns with SELECT and narrow rows with a precise WHERE condition.",
    "prerequisites": [{
        "competency": "Tables, rows, and columns",
        "relationship": "required foundation",
        "why": "A SELECT query names columns from a table, and a WHERE condition compares values stored in its rows.",
    }],
    "roadmap_rationale": (
        "SQL Queries & Filtering is the first complete SQL topic because reliable data work starts by "
        "requesting only the columns and rows needed. Sorting, aggregation, joins, and all other SQL "
        "topics remain separately scoped and are not represented as completed lessons here."
    ),
    "learn": {
        "title": "SQL Queries & Filtering",
        "explanation": (
            "`SELECT` chooses the columns you want to read, `FROM` names the table, and `WHERE` keeps "
            "only rows that meet a condition. Start with named columns instead of `SELECT *` when you know "
            "what the task needs. A string value is written in single quotes."
        ),
        "key_ideas": [
            "`SELECT name, email` returns only those two columns, in that order.",
            "`FROM customers` identifies the table being queried.",
            "`WHERE city = 'Cairo'` filters rows; it does not change the table.",
            "Use `=` for equality and quote text values; numbers are normally written without quotes.",
        ],
        "key_terms": {
            "query": "An instruction that asks a database for data.",
            "column": "A named field such as `name` or `city` in a table.",
            "row": "One record in a table.",
            "filter": "A condition in `WHERE` that decides which rows are returned.",
        },
        "job_relevance": "Analysts and developers use small, precise queries to inspect the right records without changing source data.",
        "common_mistake": "Do not use `=` without quotes for text such as Cairo, and do not confuse `WHERE` with a command that edits rows.",
        "worked_example": "The example reads each matching customer's name and email from the `customers` table; it does not insert, update, delete, or execute anything in SkillBridge.",
        "depth_note": "Canonical SQL foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard SELECT/FROM/WHERE syntax. SkillBridge does not provide a SQL database or execute learner queries.",
        "grounding_sources": [
            {"title": "PostgreSQL documentation: Querying a Table", "url": "https://www.postgresql.org/docs/current/tutorial-select.html", "source": "PostgreSQL documentation"},
            {"title": "SQLite documentation: SELECT", "url": "https://sqlite.org/lang_select.html", "source": "SQLite documentation"},
        ],
    },
    "example": {
        "title": "Find Cairo customers",
        "type": "sql",
        "content": "SELECT name, email\nFROM customers\nWHERE city = 'Cairo';",
        "explanation": "This query asks for the `name` and `email` columns only, from rows whose `city` is exactly `Cairo`. It is a worked example, not a query that SkillBridge runs.",
    },
    "practice": {
        "type": "practical",
        "title": "Filter active Cairo customers",
        "task": "Write one read-only SQL query that returns `name` and `email` from `customers` only for rows where `city` is `Cairo` and `status` is `active`. Add one short sentence explaining what each WHERE condition filters.",
        "response_type": "sql",
        "language": "sql",
        "competency": "SQL Queries & Filtering",
        "starter_code": "SELECT name, email\nFROM customers\nWHERE city = 'Cairo'\n  AND status = 'active';",
        "evaluation_note": "SkillBridge performs a static text/structure review only: it checks for a read-only SELECT, the expected table, requested columns, and both filters. It does not connect to a database or execute SQL, so the review cannot prove runtime results.",
    },
    "mini_check": {"questions": [
        {"id": "s1", "type": "mcq", "question": "Which clause narrows a query to rows where `city` is `Cairo`?", "options": ["WHERE city = 'Cairo'", "SELECT city", "FROM Cairo", "ORDER BY city"], "correct_answer": "WHERE city = 'Cairo'", "competency": "SQL Queries & Filtering", "difficulty": "beginner", "misconception_hint": "Choose the clause whose role is deciding which records stay in the result."},
        {"id": "s2", "type": "mcq", "question": "What does `SELECT name, email` request?", "options": ["Only the name and email columns", "Every column in the table", "Only rows with an email", "A new table"], "correct_answer": "Only the name and email columns", "competency": "SQL Queries & Filtering", "difficulty": "beginner", "misconception_hint": "Distinguish a list of requested fields from a condition that filters rows."},
        {"id": "s3", "type": "mcq", "question": "Which query is a read-only request for active Cairo customers?", "options": ["SELECT name, email FROM customers WHERE city = 'Cairo' AND status = 'active';", "DELETE FROM customers WHERE city = 'Cairo';", "UPDATE customers SET status = 'active';", "INSERT INTO customers (city) VALUES ('Cairo');"], "correct_answer": "SELECT name, email FROM customers WHERE city = 'Cairo' AND status = 'active';", "competency": "SQL Queries & Filtering", "difficulty": "beginner", "misconception_hint": "Check whether the statement reads existing records or attempts to change them."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "استعلامات SQL والتصفية",
                "explanation": "`SELECT` بتحدد الأعمدة اللي عايز تقراها، و`FROM` بتحدد الجدول، و`WHERE` بتحتفظ بالصفوف اللي تحقق شرط. لما تعرف الأعمدة المطلوبة، سمِّيها بدل `SELECT *`. النصوص بتتكتب بين علامتي اقتباس مفردتين.",
                "key_ideas": ["`SELECT name, email` بترجع العمودين دول فقط وبالترتيب ده.", "`FROM customers` بتحدد الجدول اللي بنسأل عنه.", "`WHERE city = 'Cairo'` بتفلتر الصفوف ولا تعدّل الجدول.", "استخدم `=` للمساواة وحط النص بين اقتباس مفرد؛ الأرقام غالباً من غير اقتباس."],
                "key_terms": {"استعلام": "تعليمة بتطلب بيانات من قاعدة البيانات.", "عمود": "حقل له اسم مثل `name` أو `city` داخل جدول.", "صف": "سجل واحد داخل الجدول.", "تصفية": "شرط في `WHERE` يحدد الصفوف الراجعة."},
                "job_relevance": "المحللون والمطورون يستخدمون استعلامات صغيرة ودقيقة لقراءة السجلات المطلوبة من غير تعديل البيانات المصدرية.",
                "common_mistake": "ما تكتبش نص مثل Cairo من غير اقتباس، وما تخلطش بين `WHERE` وبين أمر بيعدّل الصفوف.",
                "worked_example": "المثال بيقرأ الاسم والبريد للعملاء المطابقين من جدول `customers`؛ SkillBridge لا ينفذ الاستعلام ولا يعدّل بيانات.",
                "depth_note": "محتوى تأسيسي ثابت لـ SQL من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة SELECT/FROM/WHERE القياسية. SkillBridge لا يوفر قاعدة بيانات SQL ولا ينفذ استعلامات المتعلم.",
            },
            "example": {"title": "ابحث عن عملاء القاهرة", "type": "sql", "content": "SELECT name, email\nFROM customers\nWHERE city = 'Cairo';", "explanation": "الاستعلام يطلب عمودي `name` و`email` فقط من الصفوف اللي قيمة `city` فيها Cairo. ده مثال للشرح وليس استعلاماً ينفذه SkillBridge."},
            "practice": {"title": "فلتر العملاء النشطين في القاهرة", "task": "اكتب استعلام SQL واحد للقراءة فقط يرجع `name` و`email` من `customers` للصفوف اللي `city` فيها Cairo و`status` فيها active. أضف جملة قصيرة تشرح كل شرط في WHERE بيصفي إيه.", "response_type": "sql", "language": "sql", "competency": "SQL Queries & Filtering", "starter_code": "SELECT name, email\nFROM customers\nWHERE city = 'Cairo'\n  AND status = 'active';", "evaluation_note": "SkillBridge يعمل مراجعة ثابتة للنص والبنية فقط: بيتأكد من SELECT للقراءة، والجدول، والأعمدة، والشرطين. لا يتصل بقاعدة بيانات ولا ينفذ SQL، لذلك المراجعة لا تثبت نتيجة وقت التشغيل."},
            "mini_check": {"questions": [
                {"id": "s1", "question": "أي جزء بيحدد الصفوف اللي `city` فيها Cairo؟", "options": ["WHERE city = 'Cairo'", "SELECT city", "FROM Cairo", "ORDER BY city"], "misconception_hint": "اختار الجزء اللي وظيفته يقرر السجلات اللي تفضل في النتيجة."},
                {"id": "s2", "question": "`SELECT name, email` بيطلب إيه؟", "options": ["عمودي الاسم والبريد بس", "كل أعمدة الجدول", "الصفوف اللي فيها بريد بس", "جدول جديد"], "misconception_hint": "فرّق بين قائمة أعمدة بنطلبها وشرط بيصفي الصفوف."},
                {"id": "s3", "question": "أي استعلام للقراءة بس عن عملاء القاهرة النشطين؟", "options": ["SELECT name, email FROM customers WHERE city = 'Cairo' AND status = 'active';", "DELETE FROM customers WHERE city = 'Cairo';", "UPDATE customers SET status = 'active';", "INSERT INTO customers (city) VALUES ('Cairo');"], "misconception_hint": "شوف الاستعلام بيقرأ سجلات موجودة ولا بيحاول يغيرها."},
            ]},
        },
    },
}


SQL_SORTING_LIMITING = {
    "status": "complete",
    "skill_aliases": ("sql", "structured query language"),
    "competency": "Sorting & limiting",
    "objective": "Order a SELECT result with ORDER BY and return a bounded slice with LIMIT.",
    "prerequisites": [{
        "competency": "sql_queries_filtering",
        "relationship": "required foundation",
        "why": "ORDER BY and LIMIT shape the result of a SELECT, so you first need a filtered read that decides which rows are produced.",
    }, {
        "competency": "SQL Queries & Filtering",
        "relationship": "required foundation",
        "why": "Ordering makes a bounded preview useful only after the WHERE clause has decided which rows are in the result.",
    }],
    "roadmap_rationale": (
        "Sorting & Limiting is the second complete SQL topic because a useful "
        "SELECT is rarely read without an ordering decision, and bounded results are "
        "readable previews of large tables. Aggregation is the third complete topic, "
        "and the SQL roadmap concludes with query optimization, transactions, and "
        "schema design as its final three competencies."
    ),
    "learn": {
        "title": "SQL Sorting & Limiting",
        "explanation": (
            "`ORDER BY` sorts the rows of a query result, and `LIMIT` keeps only a small "
            "number of them. Together they turn a full result into the most useful reading "
            "order, such as the highest totals or the first few rows of a preview."
        ),
        "key_ideas": [
            "`ORDER BY total DESC` sorts rows from the largest `total` down; omitting `DESC` sorts ascending.",
            "`LIMIT 3` keeps only the first three rows of the sorted result.",
            "`ORDER BY` and `LIMIT` come after `WHERE`, and `LIMIT` follows `ORDER BY`.",
            "Sorting and limiting shape the result you see; they never change the rows in the table.",
        ],
        "key_terms": {
            "sort": "Arranging the returned rows with `ORDER BY`.",
            "descending": "Largest values first, written as `DESC`.",
            "limit": "Returning only the first N rows with `LIMIT N`.",
            "ascending": "Smallest values first; the default order.",
        },
        "job_relevance": "Real queries usually name an ordering and a bound, so the few rows an analyst reads are the relevant ones instead of a whole table.",
        "common_mistake": "Writing `LIMIT` without an `ORDER BY` (the kept rows are then arbitrary), or placing `ORDER BY` or `LIMIT` before the `WHERE` filter.",
        "worked_example": "The example reads each Cairo customer's name and total, sorts from the largest total down, and keeps the top three rows; it does not insert, update, delete, or execute anything in SkillBridge.",
        "depth_note": "Canonical SQL foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard SELECT/ORDER BY/LIMIT syntax. SkillBridge does not provide a SQL database or execute learner queries.",
        "grounding_sources": [
            {"title": "PostgreSQL documentation: Querying a Table", "url": "https://www.postgresql.org/docs/current/tutorial-select.html", "source": "PostgreSQL documentation"},
            {"title": "SQLite documentation: SELECT", "url": "https://sqlite.org/lang_select.html", "source": "SQLite documentation"},
        ],
    },
    "example": {
        "title": "Top three Cairo customers by total",
        "type": "sql",
        "content": "SELECT name, total\nFROM customers\nWHERE city = 'Cairo'\nORDER BY total DESC\nLIMIT 3;",
        "explanation": "This query asks only for the `name` and `total` columns, keeps Cairo rows, orders `total` from largest to smallest, and returns the first three rows. It is a worked example, not a query that SkillBridge runs.",
    },
    "practice": {
        "type": "practical",
        "title": "Order and bound the top customers",
        "task": "Write one read-only SQL query that returns `name` and `total` from `customers`, sorts the result by `total` from largest to smallest, and keeps only the three highest rows. Add one short sentence explaining what ORDER BY and LIMIT do.",
        "response_type": "sql",
        "language": "sql",
        "competency": "Sorting & limiting",
        "starter_code": "SELECT name, total\nFROM customers\nORDER BY total DESC\nLIMIT 3;",
        "evaluation_note": "SkillBridge performs a static text/structure review only: it checks for a read-only SELECT, the expected table and columns, a descending ORDER BY on the total column, and a LIMIT of three rows. It does not connect to a database or execute SQL, so the review cannot prove runtime results.",
    },
    "mini_check": {"questions": [
        {"id": "s1", "type": "mcq", "question": "Which clause sorts a query result from the highest `total` down?", "options": ["ORDER BY total DESC", "LIMIT 3", "WHERE city = 'Cairo'", "SELECT total"], "correct_answer": "ORDER BY total DESC", "competency": "Sorting & limiting", "difficulty": "beginner", "misconception_hint": "Pick the clause whose job is deciding the order of the returned rows."},
        {"id": "s2", "type": "mcq", "question": "What does `LIMIT 3` after an ORDER BY do?", "options": ["Returns only the first three rows of the sorted result", "Keeps three filters in WHERE", "Sums the first three rows", "Limits the query to three columns"], "correct_answer": "Returns only the first three rows of the sorted result", "competency": "Sorting & limiting", "difficulty": "beginner", "misconception_hint": "LIMIT bounds the size of the result; it does not sort, sum, or change stored data."},
        {"id": "s3", "type": "mcq", "question": "Which query previews the three highest totals for Cairo customers?", "options": ["SELECT name, total FROM customers WHERE city = 'Cairo' ORDER BY total DESC LIMIT 3;", "SELECT name FROM customers ORDER BY total;", "UPDATE customers SET total = 0;", "DELETE FROM customers ORDER BY total DESC LIMIT 3;"], "correct_answer": "SELECT name, total FROM customers WHERE city = 'Cairo' ORDER BY total DESC LIMIT 3;", "competency": "Sorting & limiting", "difficulty": "beginner", "misconception_hint": "Check that the statement reads rows, applies the filter, orders descending, and bounds the result to three rows without changing data."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "ترتيب نتائج SQL وتحديد عددها",
                "explanation": "`ORDER BY` بترتب صفوف النتيجة، و`LIMIT` بتخلي النتيجة محدودة بعدد صغير. الاتنين مع بعض بيطلعوا النتيجة بالترتيب الأكثر فايدة: أعلى القيم أو أول الصفوف في معاينة.",
                "key_ideas": ["`ORDER BY total DESC` بترتب الصفوف من أكبر `total` للأصغر؛ ولو شلت DESC الترتيب بيبقى تصاعدي.", "`LIMIT 3` بتحتفظ بأول تلاتة صفوف بس من النتيجة المرتبة.", "`ORDER BY` و`LIMIT` بييجوا بعد `WHERE`، و`LIMIT` بييجي بعد `ORDER BY`.", "الترتيب وتحديد العدد بيشكلوا النتيجة اللي بتشوفها بس؛ عمرهم ما بيغيروا الصفوف الموجودة في الجدول."],
                "key_terms": {"ترتيب": "ترتيب الصفوف الراجعة باستخدام `ORDER BY`.", "تنازلي": "القيم الأكبر الأول، وتتكتب `DESC`.", "تحديد عدد": "ترجيع أول N صف بس باستخدام `LIMIT N`.", "تصاعدي": "القيم الأصغر الأول، وهو الترتيب الافتراضي."},
                "job_relevance": "الاستعلامات الحقيقية بتحدد ترتيب وعدد، عشان الصفوف القليلة اللي بيقريها المحلل تكون هي المطلوبة بدل الجدول كله.",
                "common_mistake": "كتابة `LIMIT` من غير `ORDER BY` (الصفوف المحتفظ بيها ساعتها عشوائية)، أو لوضع `ORDER BY` أو `LIMIT` قبل فلتر `WHERE`.",
                "worked_example": "المثال بيقري اسم وإجمالي كل عميل في القاهرة، بترتب من أكبر `total` للأصغر، وياخد أول تلاتة صفوف؛ SkillBridge لا ينفذ الاستعلام ولا يعدّل بيانات.",
                "depth_note": "محتوى تأسيسي ثابت لـ SQL من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة SELECT/ORDER BY/LIMIT القياسية. SkillBridge لا يوفر قاعدة بيانات SQL ولا ينفذ استعلامات المتعلم.",
            },
            "example": {"title": "أعلى تلاتة عملاء في القاهرة حسب الإجمالي", "type": "sql", "content": "SELECT name, total\nFROM customers\nWHERE city = 'Cairo'\nORDER BY total DESC\nLIMIT 3;", "explanation": "الاستعلام بيلبّي عمودي `name` و`total` بس، بيصفي صفوف القاهرة، بترتب `total` من الأكبر للأصغر، ويرجع أول تلاتة صفوف. ده مثال للشرح وليس استعلاماً ينفذه SkillBridge."},
            "practice": {"title": "رتّب وحدد أعلى العملاء", "task": "اكتب استعلام SQL واحد للقراءة فقط يرجع `name` و`total` من `customers`، مرتبين حسب `total` من الأكبر للأصغر، ويحتفظ بأعلى تلاتة صفوف بس. أضف جملة قصيرة تشرح إيه اللي بيعمله ORDER BY وLIMIT.", "response_type": "sql", "language": "sql", "competency": "Sorting & limiting", "starter_code": "SELECT name, total\nFROM customers\nORDER BY total DESC\nLIMIT 3;", "evaluation_note": "SkillBridge يعمل مراجعة ثابتة للنص والبنية فقط: بيتأكد من SELECT للقراءة، والجدول والأعمدة المطلوبة، وترتيب تنازلي على عمود total، وحد أقصى تلاتة صفوف. لا يتصل بقاعدة بيانات ولا ينفذ SQL، لذلك المراجعة لا تثبت نتيجة وقت التشغيل."},
            "mini_check": {"questions": [
                {"id": "s1", "question": "أي جزء بترتب نتيجة الاستعلام من أعلى `total` للأقل؟", "options": ["ORDER BY total DESC", "LIMIT 3", "WHERE city = 'Cairo'", "SELECT total"], "misconception_hint": "اختار الجزء اللي وظيفته يحدد ترتيب الصفوف الراجعة."},
                {"id": "s2", "question": "`LIMIT 3` بعد ORDER BY بتعمل إيه؟", "options": ["بترجع أول تلاتة صفوف بس من النتيجة المرتبة", "بتحتفظ بتلات فلاتر في WHERE", "بتحسب مجموع أول تلاتة صفوف", "بتحدد إن الاستعلام تلات أعمدة بس"], "misconception_hint": "LIMIT بتحدد حجم النتيجة؛ مش بترتب ولا بتجمع ولا بتغير بيانات محفوظة."},
                {"id": "s3", "question": "أي استعلام بيعرض معاينة لأعلى تلاتة إجماليات لعملاء القاهرة؟", "options": ["SELECT name, total FROM customers WHERE city = 'Cairo' ORDER BY total DESC LIMIT 3;", "SELECT name FROM customers ORDER BY total;", "UPDATE customers SET total = 0;", "DELETE FROM customers ORDER BY total DESC LIMIT 3;"], "misconception_hint": "تأكد إن الاستعلام بيقرأ صفوف، وبيطبق الفلتر، وبيترتب تنازلي، وبيحدد النتيجة بتلاتة صفوف من غير تعديل بيانات."},
            ]},
        },
    },
}


SQL_AGGREGATION = {
    "status": "complete",
    "skill_aliases": ("sql", "structured query language"),
    "competency": "Aggregation",
    "objective": "Summarize rows into groups with GROUP BY and COUNT, SUM, AVG, MIN, or MAX.",
    "prerequisites": [{
        "competency": "sql_sorting_limiting",
        "relationship": "required foundation",
        "why": "Aggregation groups rows and then orders the summarized result, so reading ordered and bounded SELECT results first is the natural foundation.",
    }, {
        "competency": "sql_queries_filtering",
        "relationship": "required foundation",
        "why": "GROUP BY summarizes rows that a WHERE clause has already narrowed.",
    }, {
        "competency": "SQL Sorting & Limiting",
        "relationship": "required foundation",
        "why": "Setting an order and a bound on plain reads comes before reasoning about grouped summary reads.",
    }, {
        "competency": "SQL Queries & Filtering",
        "relationship": "required foundation",
        "why": "A filter describes the rows that a group summary will count or add up.",
    }],
    "roadmap_rationale": (
        "Aggregation is the third complete SQL topic because summarizing groups is the "
        "primary analytical step after reading rows: 'how many', 'how much', and 'on "
        "average' questions all depend on GROUP BY and aggregate functions. The "
        "remaining SQL roadmap concludes with query optimization, transactions, and "
        "schema design."
    ),
    "learn": {
        "title": "SQL Aggregation",
        "explanation": (
            "`GROUP BY` collects rows that share a value into one group, and aggregate "
            "functions such as `COUNT`, `SUM`, `AVG`, `MIN`, and `MAX` summarize each group "
            "into a single number."
        ),
        "key_ideas": [
            "`COUNT(*)` counts rows; `SUM(total)` adds a numeric column; `AVG(total)` averages it.",
            "`GROUP BY city` creates one summary row per distinct city.",
            "`HAVING` filters groups after aggregation; `WHERE` filters rows before it.",
            "Grouping summarizes many rows into few; it does not change the stored table.",
        ],
        "key_terms": {
            "group by": "A clause that bundles rows sharing a value into one group per value.",
            "aggregate function": "A summary such as COUNT, SUM, AVG, MIN, or MAX computed per group.",
            "having": "A filter applied to summarized groups rather than raw rows.",
        },
        "job_relevance": "Analysts answer how many, how much, and on-average questions by turning thousands of rows into a small summary table.",
        "common_mistake": "Filtering groups with `WHERE` instead of `HAVING`, or selecting an ungrouped column that is neither grouped nor summarized.",
        "worked_example": "The example turns the `customers` table into one summary row per city showing how many customers it has; it does not insert, update, delete, or execute anything in SkillBridge.",
        "depth_note": "Canonical SQL foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard GROUP BY/aggregate syntax. SkillBridge does not provide a SQL database or execute learner queries.",
        "grounding_sources": [
            {"title": "PostgreSQL documentation: Aggregate Functions", "url": "https://www.postgresql.org/docs/current/tutorial-agg.html", "source": "PostgreSQL documentation"},
            {"title": "SQLite documentation: Aggregate Functions", "url": "https://sqlite.org/lang_aggfunc.html", "source": "SQLite documentation"},
        ],
    },
    "example": {
        "title": "Customer count per city",
        "type": "sql",
        "content": "SELECT city, COUNT(*) AS customer_count\nFROM customers\nGROUP BY city;",
        "explanation": "This query returns one row per distinct `city` with the number of customers in it. It is a worked example, not a query that SkillBridge runs.",
    },
    "practice": {
        "type": "practical",
        "title": "Count customers per city with a group filter",
        "task": "Write one read-only SQL query that returns `city` and a count of customers per city, keeping only cities with at least 2 customers. Add one short sentence explaining what GROUP BY and HAVING do.",
        "response_type": "sql",
        "language": "sql",
        "competency": "Aggregation",
        "starter_code": "SELECT city, COUNT(*) AS customer_count\nFROM customers\nGROUP BY city\nHAVING COUNT(*) >= 2;",
        "evaluation_note": "SkillBridge performs a static text/structure review only: it checks for a read-only SELECT, the expected table, a GROUP BY on the city column, and a HAVING filter requiring at least 2 rows per group. It does not connect to a database or execute SQL, so the review cannot prove runtime results.",
    },
    "mini_check": {"questions": [
        {"id": "s1", "type": "mcq", "question": "Which clause bundles rows that share the same `city` value into one group?", "options": ["GROUP BY city", "ORDER BY city", "WHERE city", "LIMIT city"], "correct_answer": "GROUP BY city", "competency": "Aggregation", "difficulty": "intermediate", "misconception_hint": "Pick the clause that creates one summary row per distinct value."},
        {"id": "s2", "type": "mcq", "question": "What does `COUNT(*)` return for each group?", "options": ["The number of rows in that group", "The sum of a numeric column", "A random sample", "The first row only"], "correct_answer": "The number of rows in that group", "competency": "Aggregation", "difficulty": "intermediate", "misconception_hint": "COUNT always reports a row count; SUM or AVG summarize column values instead."},
        {"id": "s3", "type": "mcq", "question": "Which query lists cities with at least 2 customers?", "options": ["SELECT city, COUNT(*) FROM customers GROUP BY city HAVING COUNT(*) >= 2;", "SELECT city FROM customers WHERE COUNT(*) >= 2;", "DELETE FROM customers WHERE city = 'Cairo';", "SELECT COUNT(*) FROM customers GROUP BY city WHERE COUNT(*) >= 2;"], "correct_answer": "SELECT city, COUNT(*) FROM customers GROUP BY city HAVING COUNT(*) >= 2;", "competency": "Aggregation", "difficulty": "intermediate", "misconception_hint": "Summary filters belong in HAVING, not WHERE, and the statement must be read-only."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "تجميع بيانات SQL",
                "explanation": "`GROUP BY` بتجمع الصفوف اللي بتشارك نفس القيمة في مجموعة واحدة، ودوال التجميع زي `COUNT` و`SUM` و`AVG` و`MIN` و`MAX` بيلخصوا كل مجموعة في رقم واحد.",
                "key_ideas": ["`COUNT(*)` بتعد الصفوف؛ `SUM(total)` بجمع عمود رقمي؛ و`AVG(total)` بيحسب المتوسط.", "`GROUP BY city` بتعمل صف ملخص واحد لكل مدينة مختلفة.", "`HAVING` بترشح المجموعات بعد التجميع، أما `WHERE` بترشح الصفوف قبله.", "التجميع بيحول صفوف كثيرة لصفوف قليلة؛ ولا يعدّل الجدول."],
                "key_terms": {"group by": "جملة بتجمع الصفوف اللي بتشارك نفس القيمة في مجموعة لكل قيمة.", "دالة تجميع": "ملخص زي COUNT أو SUM أو AVG أو MIN أو MAX بيتحسب لكل مجموعة.", "having": "فلتر بيتطبق على المجموعات الملخصة مش على الصفوف الخام."},
                "job_relevance": "المحللون بجاوبوا على أسئلة قد إيه وكم بأقصى وبالمتوسط عن طريق تحويل آلاف الصفوف لجدول ملخص صغير.",
                "common_mistake": "تصفية المجموعات بـ `WHERE` بدل `HAVING`، أو اختيار عمود مش مجمّع ولا مقسوم عليه في GROUP BY.",
                "worked_example": "المثال بيحول جدول `customers` لصف ملخص واحد لكل مدينة بيعرض عدد عملائها؛ SkillBridge لا ينفذ الاستعلام ولا يعدّل بيانات.",
                "depth_note": "محتوى تأسيسي ثابت لـ SQL من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة GROUP BY ودوال التجميع القياسية. SkillBridge لا يوفر قاعدة بيانات SQL ولا ينفذ استعلامات المتعلم.",
            },
            "example": {"title": "عدد العملاء لكل مدينة", "type": "sql", "content": "SELECT city, COUNT(*) AS customer_count\nFROM customers\nGROUP BY city;", "explanation": "الاستعلام بيرجع صف واحد لكل `city` مختلفة ومعاه عدد عملائها. ده مثال للشرح وليس استعلاماً ينفذه SkillBridge."},
            "practice": {"title": "عدّ العملاء لكل مدينة مع فلتر على المجموعة", "task": "اكتب استعلام SQL واحد للقراءة فقط يرجع `city` وعدد عملاء لكل مدينة، ويحتفظ بالمدن اللي فيها عميلان على الأقل. أضف جملة قصيرة تشرح إيه اللي بيعمله GROUP BY وHAVING.", "response_type": "sql", "language": "sql", "competency": "Aggregation", "starter_code": "SELECT city, COUNT(*) AS customer_count\nFROM customers\nGROUP BY city\nHAVING COUNT(*) >= 2;", "evaluation_note": "SkillBridge يعمل مراجعة ثابتة للنص والبنية فقط: بيتأكد من SELECT للقراءة، والجدول المطلوب، وGROUP BY على عمود city، وفلتر HAVING يطلب عميلين على الأقل في المجموعة. لا يتصل بقاعدة بيانات ولا ينفذ SQL، لذلك المراجعة لا تثبت نتيجة وقت التشغيل."},
            "mini_check": {"questions": [
                {"id": "s1", "question": "أي جزء بيجمع الصفوف اللي بتشارك نفس قيمة `city` في مجموعة واحدة؟", "options": ["GROUP BY city", "ORDER BY city", "WHERE city", "LIMIT city"], "misconception_hint": "اختار الجزء اللي بيعمل صف ملخص واحد لكل قيمة مختلفة."},
                {"id": "s2", "question": "`COUNT(*)` بترجع إيه لكل مجموعة؟", "options": ["عدد الصفوف في المجموعة", "مجموع عمود رقمي", "عينة عشوائية", "أول صف بس"], "misconception_hint": "COUNT دايمًا بتعد صفوف؛ SUM أو AVG هما اللي بيلخصوا قيم الأعمدة."},
                {"id": "s3", "question": "أي استعلام بيعرض المدن اللي فيها عميلان على الأقل؟", "options": ["SELECT city, COUNT(*) FROM customers GROUP BY city HAVING COUNT(*) >= 2;", "SELECT city FROM customers WHERE COUNT(*) >= 2;", "DELETE FROM customers WHERE city = 'Cairo';", "SELECT COUNT(*) FROM customers GROUP BY city WHERE COUNT(*) >= 2;"], "misconception_hint": "فلاتر الملخصات بتتحط في HAVING مش WHERE، والاستعلام لازم يكون للقراءة بس."},
            ]},
        },
    },
}


SQL_JOINS = {
    "status": "complete",
    "skill_aliases": ("sql", "structured query language"),
    "competency": "Joins",
    "objective": "Combine rows from two or more tables on a shared column with JOIN.",
    "prerequisites": [{
        "competency": "sql_queries_filtering",
        "relationship": "required foundation",
        "why": "A JOIN starts from a read of one table, so filtering the rows of a single SELECT comes first.",
    }, {
        "competency": "sql_sorting_limiting",
        "relationship": "required foundation",
        "why": "Ordering and bounding a joined result is only useful once each source read is already under control.",
    }, {
        "competency": "sql_aggregation",
        "relationship": "required foundation",
        "why": "Groups summarize one table before related rows from a second table are paired into one result.",
    }, {
        "competency": "SQL Queries & Filtering",
        "relationship": "required foundation",
        "why": "The column list and WHERE filtering of a single-table SELECT are the pieces JOIN builds on.",
    }, {
        "competency": "Sorting & limiting",
        "relationship": "required foundation",
        "why": "A sorted, bounded preview reads cleanly before a join adds columns from a second table.",
    }, {
        "competency": "Aggregation",
        "relationship": "required foundation",
        "why": "Grouping is the analytical step between single tables and pairing related rows across tables.",
    }],
    "roadmap_rationale": (
        "Joins is the fourth complete SQL topic because relating rows across "
        "tables is the next analytical step after summarizing: once reads are "
        "filtered, ordered, and grouped, pairing customers with their orders "
        "becomes the natural question. The SQL roadmap then concludes with query "
        "optimization, transactions, and schema design as its final three "
        "competencies."
    ),
    "learn": {
        "title": "SQL Joins",
        "explanation": (
            "`JOIN` combines rows from two tables that share a matching value. "
            "`INNER JOIN` keeps only rows that match in both tables, while `LEFT "
            "JOIN` keeps every row from the first table and adds matching data from "
            "the second. The `ON` clause names the columns the join compares."
        ),
        "key_ideas": [
            "`ON customers.id = orders.customer_id` names the matching columns between the two tables.",
            "`INNER JOIN` returns only rows where the join condition matches in both tables.",
            "`LEFT JOIN` keeps every row of the first table even when the second table has no match.",
            "A join combines data for reading; it never changes the source tables.",
        ],
        "key_terms": {
            "join": "A clause that pairs rows from two or more tables on a common value.",
            "inner join": "A join that keeps only rows with a match in both tables.",
            "left join": "A join that keeps every row of the first table and adds matching rows from the second.",
            "on": "The condition that says which columns the join compares.",
        },
        "job_relevance": "Analysts combine related data living in separate tables — customers and orders, users and payments — into one readable result.",
        "common_mistake": "Writing the join condition with `WHERE` instead of `ON`, or forgetting to qualify a column with its table when both tables use the same name.",
        "worked_example": "The example pairs each customer with their order date by matching `customers.id` to `orders.customer_id`; it does not insert, update, delete, or execute anything in SkillBridge.",
        "depth_note": "Canonical SQL foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard JOIN syntax. SkillBridge does not provide a SQL database or execute learner queries.",
        "grounding_sources": [
            {"title": "PostgreSQL documentation: Joining Tables", "url": "https://www.postgresql.org/docs/current/tutorial-join.html", "source": "PostgreSQL documentation"},
            {"title": "SQLite documentation: SELECT", "url": "https://sqlite.org/lang_select.html", "source": "SQLite documentation"},
        ],
    },
    "example": {
        "title": "Customers with their orders",
        "type": "sql",
        "content": "SELECT customers.name, orders.order_date\nFROM customers\nINNER JOIN orders\nON customers.id = orders.customer_id;",
        "explanation": "This query returns each customer's name with each matching order date by joining `customers` to `orders` on the customer id. It is a worked example, not a query that SkillBridge runs.",
    },
    "practice": {
        "type": "practical",
        "title": "Join customers to orders",
        "task": "Write one read-only SQL query that returns `name` from `customers` and `order_date` from `orders` for every customer who has placed an order, using an INNER JOIN on the matching customer id. Add one short sentence explaining what the ON clause does.",
        "response_type": "sql",
        "language": "sql",
        "competency": "Joins",
        "starter_code": "SELECT customers.name, orders.order_date\nFROM customers\nINNER JOIN orders\nON customers.id = orders.customer_id;",
        "evaluation_note": "SkillBridge performs a static text/structure review only: it checks for a read-only SELECT, the expected tables, an INNER JOIN (a plain JOIN is accepted as inner), an ON condition linking customers.id to orders.customer_id, and the requested columns. It does not connect to a database or execute SQL, so the review cannot prove runtime results.",
    },
    "mini_check": {"questions": [
        {"id": "j1", "type": "mcq", "question": "Which clause tells JOIN which columns to compare?", "options": ["ON customers.id = orders.customer_id", "WHERE orders = customers", "LIMIT orders", "GROUP BY customers"], "correct_answer": "ON customers.id = orders.customer_id", "competency": "Joins", "difficulty": "intermediate", "misconception_hint": "Pick the clause that describes the matching pair of columns, not a filter or an ordering."},
        {"id": "j2", "type": "mcq", "question": "Which JOIN keeps only rows that have a match in both tables?", "options": ["INNER JOIN", "LEFT JOIN", "CROSS JOIN", "FULL OUTER JOIN"], "correct_answer": "INNER JOIN", "competency": "Joins", "difficulty": "intermediate", "misconception_hint": "A join that requires a matching row on each side is the inner join."},
        {"id": "j3", "type": "mcq", "question": "Which query pairs each customer with their orders without changing data?", "options": ["SELECT customers.name, orders.order_date FROM customers INNER JOIN orders ON customers.id = orders.customer_id;", "DELETE FROM orders;", "UPDATE customers SET name = 'x';", "SELECT name FROM customers FULL OUTER JOIN orders;"], "correct_answer": "SELECT customers.name, orders.order_date FROM customers INNER JOIN orders ON customers.id = orders.customer_id;", "competency": "Joins", "difficulty": "intermediate", "misconception_hint": "Check that the statement reads both tables, links them with an inner join condition, and never writes."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "الانضمام بين جداول SQL",
                "explanation": "`JOIN` بيوصل صفوف جدولين بشتركو في قيمة واحدة. `INNER JOIN` بيحتفظ بالصفوف اللي ليها تطابق في الجدولين، و`LEFT JOIN` بيحتفظ بكل صفوف الجدول الأول ويضيف بيانات الجدول التاني المطابقة. وجملة `ON` بتسمّي الأعمدة اللي بيتم المقارنة بينهم.",
                "key_ideas": ["`ON customers.id = orders.customer_id` بيسمّي أعمدة التطابق بين الجدولين.", "`INNER JOIN` بيرجع بس الصفوف اللي فيها تطابق في الجدولين.", "`LEFT JOIN` بيحتفظ بكل صفوف الجدول الأول حتى لو مفيش تطابق في الجدول التاني.", "الضم بيجمع البيانات للقراءة بس؛ وعمره ما بيغير الجداول المصدرية."],
                "key_terms": {"join": "جملة بتوصل صفوف من جدولين أو أكتر على قيمة مشتركة.", "inner join": "ضم بيحتفظ بالصفوف اللي ليها تطابق في الجدولين.", "left join": "ضم بيحتفظ بكل صفوف الجدول الأول ويضيف الصفوف المطابقة من الجدول التاني.", "on": "الشرط اللي بيقول الجداول الأعمدة اللي بيتم المقارنة بينها."},
                "job_relevance": "المحللون بيجمعوا بيانات متعلقة في جداول مختلفة — زي العملاء والطلبات أو المستخدمين والمدفوعات — في نتيجة واحدة سهلة القراية.",
                "common_mistake": "كتابة شرط الضم بـ `WHERE` بدل `ON`، أو نسيان توضيح اسم الجدول قدام العمود لما نفس الاسم يظهر في الجدولين.",
                "worked_example": "المثال بيوصل كل عميل بتاريخ طلبه عن طريق مطابقة `customers.id` مع `orders.customer_id`؛ SkillBridge لا ينفذ الاستعلام ولا يعدّل بيانات.",
                "depth_note": "محتوى تأسيسي ثابت لـ SQL من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة JOIN القياسية. SkillBridge لا يوفر قاعدة بيانات SQL ولا ينفذ استعلامات المتعلم.",
            },
            "example": {"title": "العملاء ومعهم طلباتهم", "type": "sql", "content": "SELECT customers.name, orders.order_date\nFROM customers\nINNER JOIN orders\nON customers.id = orders.customer_id;", "explanation": "الاستعلام بيرجع اسم كل عميل مع تاريخ طلبه عن طريق ضم `customers` لـ `orders` على رقم العميل. ده مثال للشرح وليس استعلاماً ينفذه SkillBridge."},
            "practice": {"title": "اضمَّ العملاء لطلباتهم", "task": "اكتب استعلام SQL واحد للقراءة فقط يرجع `name` من `customers` و`order_date` من `orders` لكل عميل عمل طلب، باستخدام INNER JOIN على رقم العميل المطابق. أضف جملة قصيرة تشرح إيه اللي بيعمله شرط ON.", "response_type": "sql", "language": "sql", "competency": "Joins", "starter_code": "SELECT customers.name, orders.order_date\nFROM customers\nINNER JOIN orders\nON customers.id = orders.customer_id;", "evaluation_note": "SkillBridge يعمل مراجعة ثابتة للنص والبنية فقط: بيتأكد من SELECT للقراءة، والجدولين المطلوبين، وINNER JOIN، وشرط ON بيربط customers.id بـ orders.customer_id، والأعمدة المطلوبة. لا يتصل بقاعدة بيانات ولا ينفذ SQL، لذلك المراجعة لا تثبت نتيجة وقت التشغيل."},
            "mini_check": {"questions": [
                {"id": "j1", "question": "أي جزء بيقول لـ JOIN إيه الأعمدة اللي بيتم مقارنتها؟", "options": ["ON customers.id = orders.customer_id", "WHERE orders = customers", "LIMIT orders", "GROUP BY customers"], "misconception_hint": "اختار الجزء اللي بيوصف زوج الأعمدة المتطابق، مش فلتر أو ترتيب."},
                {"id": "j2", "question": "أي نوع JOIN بيحتفظ بالصفوف اللي ليها تطابق في الجدولين بس؟", "options": ["INNER JOIN", "LEFT JOIN", "CROSS JOIN", "FULL OUTER JOIN"], "misconception_hint": "الضم اللي بيطلب صف مطابق في كل جانب هو الـ inner join."},
                {"id": "j3", "question": "أي استعلام بيوصل كل عميل بطلباته من غير ما يعدّل بيانات؟", "options": ["SELECT customers.name, orders.order_date FROM customers INNER JOIN orders ON customers.id = orders.customer_id;", "DELETE FROM orders;", "UPDATE customers SET name = 'x';", "SELECT name FROM customers FULL OUTER JOIN orders;"], "misconception_hint": "تأكد إن الاستعلام بيقرأ الجدولين وبيوصلهم بشرط ضم داخلي وبيبعتش أي حاجة."},
            ]},
        },
    },
}


SQL_SUBQUERIES = {
    "status": "complete",
    "skill_aliases": ("sql", "structured query language"),
    "competency": "Subqueries",
    "objective": "Use a subquery inside SELECT, FROM, or WHERE to filter or derive values from an inner result.",
    "prerequisites": [{
        "competency": "sql_queries_filtering",
        "relationship": "required foundation",
        "why": "A subquery is itself a SELECT, so a filtered single-table read is the first building block.",
    }, {
        "competency": "sql_sorting_limiting",
        "relationship": "required foundation",
        "why": "Reading sorted, bounded results makes it clear the inner SELECT produces a result the outer query consumes.",
    }, {
        "competency": "sql_aggregation",
        "relationship": "required foundation",
        "why": "Subqueries commonly feed an average or count into the outer comparison, so aggregation comes first.",
    }, {
        "competency": "sql_joins",
        "relationship": "required foundation",
        "why": "Relating two tables with JOIN comes before nesting one query inside another for the same questions.",
    }, {
        "competency": "SQL Queries & Filtering",
        "relationship": "required foundation",
        "why": "The column list and WHERE of a SELECT apply to the inner query exactly as they do to the outer one.",
    }, {
        "competency": "Sorting & limiting",
        "relationship": "required foundation",
        "why": "An inner SELECT may itself be ordered and bounded while the outer query consumes its result.",
    }, {
        "competency": "Aggregation",
        "relationship": "required foundation",
        "why": "Comparing a column to an average or count computed by an inner query builds directly on grouping.",
    }, {
        "competency": "Joins",
        "relationship": "required foundation",
        "why": "A subquery answers the same cross-table questions a join answers, so joins are learned first.",
    }],
    "roadmap_rationale": (
        "Subqueries is the fifth complete SQL topic because an inner query powers "
        "filters and derived values that single-table reads cannot express: 'above "
        "the average', 'in this list'. Joins relate rows across tables; subqueries "
        "reuse one query as the input to another. The SQL roadmap then concludes "
        "with query optimization, transactions, and schema design."
    ),
    "learn": {
        "title": "SQL Subqueries",
        "explanation": (
            "A subquery is a SELECT statement written inside another statement, in "
            "parentheses. It runs first, and the outer query uses its result — for "
            "example, filtering rows with `WHERE ... IN (subquery)` or comparing a "
            "column to an average computed by an inner query."
        ),
        "key_ideas": [
            "A subquery runs before the outer query and supplies one value or a list of values.",
            "`WHERE total > (SELECT AVG(total) FROM customers)` compares each row to the inner average.",
            "A subquery needs parentheses and its own SELECT; the outer statement keeps the lead clause.",
            "Reading with subqueries never changes the stored tables.",
        ],
        "key_terms": {
            "subquery": "A SELECT statement written inside another statement.",
            "inner query": "The subquery that runs first and prepares a value or list for the outer query.",
            "outer query": "The statement that consumes the result of the inner query.",
        },
        "job_relevance": "Analysts express questions like 'above the average' or 'in this list' as one query instead of running separate steps by hand.",
        "common_mistake": "Writing a subquery that returns many rows where a single value is expected, or forgetting the parentheses around the inner query.",
        "worked_example": "The example reads customer names for customers who appear in the `orders` table by filtering with a subquery that returns their ids; it does not insert, update, delete, or execute anything in SkillBridge.",
        "depth_note": "Canonical SQL foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard subquery syntax. SkillBridge does not provide a SQL database or execute learner queries.",
        "grounding_sources": [
            {"title": "PostgreSQL documentation: Subquery Expressions", "url": "https://www.postgresql.org/docs/current/functions-subquery.html", "source": "PostgreSQL documentation"},
            {"title": "SQLite documentation: SELECT", "url": "https://sqlite.org/lang_select.html", "source": "SQLite documentation"},
        ],
    },
    "example": {
        "title": "Customers who have ordered",
        "type": "sql",
        "content": "SELECT name\nFROM customers\nWHERE id IN\n  (SELECT customer_id FROM orders);",
        "explanation": "The inner query returns customer ids that appear in `orders`; the outer query reads only customers whose id is in that list. It is a worked example, not a query that SkillBridge runs.",
    },
    "practice": {
        "type": "practical",
        "title": "Customers above the average total",
        "task": "Write one read-only SQL query that returns `name` from `customers` for customers whose `total` is above the average total, using a subquery to compute the average. Add one short sentence explaining what the inner query returns.",
        "response_type": "sql",
        "language": "sql",
        "competency": "Subqueries",
        "starter_code": "SELECT name\nFROM customers\nWHERE total >\n  (SELECT AVG(total) FROM customers);",
        "evaluation_note": "SkillBridge performs a static text/structure review only: it checks for a read-only SELECT, the expected table and column, a subquery in parentheses, and a comparison of total against an average computed by the inner query. It does not connect to a database or execute SQL, so the review cannot prove runtime results.",
    },
    "mini_check": {"questions": [
        {"id": "sub1", "type": "mcq", "question": "What is a subquery?", "options": ["A SELECT statement written inside another statement", "A table stored inside a column", "An index on a column", "A command that deletes rows"], "correct_answer": "A SELECT statement written inside another statement", "competency": "Subqueries", "difficulty": "intermediate", "misconception_hint": "Pick the definition of a SELECT reused as an input to a surrounding statement."},
        {"id": "sub2", "type": "mcq", "question": "What does the subquery in `WHERE total > (SELECT AVG(total) FROM customers)` return?", "options": ["A single average value", "Every customer id", "A new table", "A list of customer names"], "correct_answer": "A single average value", "competency": "Subqueries", "difficulty": "intermediate", "misconception_hint": "Because the outer query compares one value, the inner query must supply one value."},
        {"id": "sub3", "type": "mcq", "question": "Which query reads customers above the average total without changing data?", "options": ["SELECT name FROM customers WHERE total > (SELECT AVG(total) FROM customers);", "SELECT name FROM customers WHERE total > AVG(total);", "DELETE FROM customers WHERE total > 100;", "SELECT name FROM customers ORDER BY total;"], "correct_answer": "SELECT name FROM customers WHERE total > (SELECT AVG(total) FROM customers);", "competency": "Subqueries", "difficulty": "intermediate", "misconception_hint": "The average must live in a parenthesized subquery and the statement must be read-only."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "الاستعلامات الفرعية في SQL",
                "explanation": "الاستعلام الفرعي هو جملة SELECT مكتوبة جوه جملة تانية بين قوسين. بيشتغل الأول، والاستعلام الخارجي بيستخدم نتيجتها — زي تصفية صفوف بـ `WHERE ... IN (subquery)` أو مقارنة عمود بمتوسط محسوب من جملة داخلية.",
                "key_ideas": ["الاستعلام الفرعي بيشتغل قبل الاستعلام الخارجي وبيدي قيمة واحدة أو قايمة قيم.", "`WHERE total > (SELECT AVG(total) FROM customers)` بيقارن كل صف بالمتوسط الداخلي.", "الاستعلام الفرعي محتاج قوسين وSELECT بتاعه، والاستعلام الخارجي هو اللي بيفتتح.", "القراءة بالاستعلامات الفرعية عمرها ما تعدّل الجداول المخزنة."],
                "key_terms": {"استعلام فرعي": "جملة SELECT مكتوبة جوه جملة تانية.", "استعلام داخلي": "الجملة اللي بتشتغل الأول وبتحضّر قيمة أو قايمة للاستعلام الخارجي.", "استعلام خارجي": "الجملة اللي بتستخدم ناتج الاستعلام الداخلي."},
                "job_relevance": "المحللون بيعبّروا عن أسئلة زي «أكتر من المتوسط» أو «اللي في القايمة دي» في استعلام واحد بدل خطوات منفصلة.",
                "common_mistake": "كتابة استعلام بسرجع صفوف كتيرة في موضع بيستنى قيمة واحدة، أو نسيان القوسين حوالين الجملة الداخلية.",
                "worked_example": "المثال بيقري أسماء العملاء اللي ظهروا في جدول `orders` عن طريق تصفية باستعلام فرعي بيرجع أرقامهم؛ SkillBridge لا ينفذ الاستعلام ولا يعدّل بيانات.",
                "depth_note": "محتوى تأسيسي ثابت لـ SQL من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة الاستعلامات الفرعية القياسية. SkillBridge لا يوفر قاعدة بيانات SQL ولا ينفذ استعلامات المتعلم.",
            },
            "example": {"title": "العملاء اللي عملوا طلبات", "type": "sql", "content": "SELECT name\nFROM customers\nWHERE id IN\n  (SELECT customer_id FROM orders);", "explanation": "الاستعلام الداخلي بيرجع أرقام العملاء اللي ظهروا في الطلبات، والاستعلام الخارجي بيقرأ العملاء اللي أرقامهم في القايمة دي. ده مثال للشرح وليس استعلاماً ينفذه SkillBridge."},
            "practice": {"title": "العملاء فوق متوسط الإجمالي", "task": "اكتب استعلام SQL واحد للقراءة فقط يرجع `name` من `customers` للعملاء اللي `total` بتاعهم أكبر من المتوسط، باستخدام استعلام فرعي لحساب المتوسط. أضف جملة قصيرة تشرح إيه اللي بيرجعه الاستعلام الداخلي.", "response_type": "sql", "language": "sql", "competency": "Subqueries", "starter_code": "SELECT name\nFROM customers\nWHERE total >\n  (SELECT AVG(total) FROM customers);", "evaluation_note": "SkillBridge يعمل مراجعة ثابتة للنص والبنية فقط: بيتأكد من SELECT للقراءة، والجدول والعمود المطلوبين، واستعلام فرعي بين قوسين، ومقارنة total بمتوسط محسوب من الجملة الداخلية. لا يتصل بقاعدة بيانات ولا ينفذ SQL، لذلك المراجعة لا تثبت نتيجة وقت التشغيل."},
            "mini_check": {"questions": [
                {"id": "sub1", "question": "إيه هو الاستعلام الفرعي؟", "options": ["جملة SELECT مكتوبة جوه جملة تانية", "جدول متخزن جوه عمود", "فهرس على عمود", "أمر بيحذف صفوف"], "misconception_hint": "اختار التعريف اللي بيوصف جملة SELECT مستخدمة كمدخل لجملة حوالينها."},
                {"id": "sub2", "question": "الاستعلام الفرعي في `WHERE total > (SELECT AVG(total) FROM customers)` بيرجع إيه؟", "options": ["متوسط واحد", "كل أرقام العملاء", "جدول جديد", "قايمة من أسماء العملاء"], "misconception_hint": "لما الاستعلام الخارجي بيقارن قيمة واحدة، لازم الجملة الداخلية تدي قيمة واحدة."},
                {"id": "sub3", "question": "أي استعلام بيقرأ العملاء فوق متوسط الإجمالي من غير ما يعدّل بيانات؟", "options": ["SELECT name FROM customers WHERE total > (SELECT AVG(total) FROM customers);", "SELECT name FROM customers WHERE total > AVG(total);", "DELETE FROM customers WHERE total > 100;", "SELECT name FROM customers ORDER BY total;"], "misconception_hint": "المتوسط لازم يكون جوه استعلام فرعي بين قوسين والاستعلام لازم يبقى للقراءة بس."},
            ]},
        },
    },
}


SQL_INDEXING_BASICS = {
    "status": "complete",
    "skill_aliases": ("sql", "structured query language"),
    "competency": "Indexing basics",
    "objective": "Explain and use database indexes: a separate data structure that makes value lookups faster without changing the stored tables.",
    "prerequisites": [{
        "competency": "sql_queries_filtering",
        "relationship": "required foundation",
        "why": "An index speeds up a WHERE lookup on a column, so reading a filtered single table comes first.",
    }, {
        "competency": "sql_sorting_limiting",
        "relationship": "required foundation",
        "why": "An index can also serve an ordered or bounded read, which builds on ordering a SELECT result.",
    }, {
        "competency": "sql_aggregation",
        "relationship": "required foundation",
        "why": "Indexes speed up the row access behind grouping, so summarizing groups is understood before the access strategy.",
    }, {
        "competency": "sql_joins",
        "relationship": "required foundation",
        "why": "A join on the indexed key column is a common real lookup, so pairing rows across tables comes first.",
    }, {
        "competency": "sql_subqueries",
        "relationship": "required foundation",
        "why": "Filtering rows against an inner result is where indexed lookups pay off, so subqueries come first.",
    }, {
        "competency": "SQL Queries & Filtering",
        "relationship": "required foundation",
        "why": "The WHERE condition is the query phrase an index answers faster.",
    }, {
        "competency": "Sorting & limiting",
        "relationship": "required foundation",
        "why": "An index may serve the ordering and bound of a read, so those read shapes are known first.",
    }, {
        "competency": "Aggregation",
        "relationship": "required foundation",
        "why": "Grouped reads touch many rows per key, so the trade-off of index access is judged against summarized reads.",
    }, {
        "competency": "Joins",
        "relationship": "required foundation",
        "why": "The join key is the classic indexed column, so reading two related tables precedes reasoning about the access path.",
    }, {
        "competency": "Subqueries",
        "relationship": "required foundation",
        "why": "A WHERE IN (subquery) lookup benefits from an index on the compared column, so subqueries precede the optimization layer.",
    }],
    "roadmap_rationale": (
        "Indexing basics is the sixth complete SQL topic because indexes are the "
        "first adjustment an analyst or developer makes after the five read shapes "
        "are under control: a filtered, ordered, grouped, joined, and subquery read "
        "is what an index makes faster. Query optimization, transactions, and "
        "schema design complete the SQL roadmap in this final batch, building on "
        "the access and ordering decisions indexes introduce."
    ),
    "learn": {
        "title": "SQL Indexing Basics",
        "explanation": (
            "An index is a separate data structure the database keeps for one or "
            "more columns. When a `WHERE` or `JOIN` compares a column to a value, "
            "the database can use the index to jump to the matching rows instead of "
            "reading the whole table. The query itself still only reads data — the "
            "index never changes the stored tables."
        ),
        "key_ideas": [
            "An index is a separate sorted lookup structure; it is not part of the table's visible rows.",
            "`WHERE email = 'sara@example.com'` can use an index on the `email` column to find the row directly.",
            "An index trades extra storage and slower writes for faster reads on the indexed column.",
            "Creating or reading with an index never changes the rows stored in the tables.",
        ],
        "key_terms": {
            "index": "A separate data structure that lets the database find rows by a column value faster.",
            "lookup": "Finding the rows whose column equals a given value, as in a `WHERE` comparison.",
            "primary key": "A unique identifier column that usually gets an index as part of the table.",
            "trade-off": "Faster reads on the indexed column at the cost of storage and slower inserts/updates.",
        },
        "job_relevance": "Applications and dashboards answer value lookups constantly; a good index turns a table scan into a direct find for the exact requested rows.",
        "common_mistake": "Expecting an index on one column to speed up every query, or thinking an index rewrites or reorders the rows in the table.",
        "worked_example": "The example reads the single row whose email matches, the exact pattern an index on `email` speeds up; it does not insert, update, delete, or execute anything in SkillBridge.",
        "depth_note": "Canonical SQL foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard SELECT syntax and refer to standard index behavior. SkillBridge does not provide a SQL database or execute learner queries.",
        "grounding_sources": [
            {"title": "PostgreSQL documentation: Indexes", "url": "https://www.postgresql.org/docs/current/indexes.html", "source": "PostgreSQL documentation"},
            {"title": "SQLite documentation: CREATE INDEX", "url": "https://sqlite.org/lang_createindex.html", "source": "SQLite documentation"},
        ],
    },
    "example": {
        "title": "Find one customer by email",
        "type": "sql",
        "content": "SELECT name, email\nFROM customers\nWHERE email = 'sara@example.com';",
        "explanation": "This query asks for the customer with exactly that email. With an index on the `email` column the database finds that row directly instead of scanning every row. It is a worked example, not a query that SkillBridge runs.",
    },
    "practice": {
        "type": "practical",
        "title": "Write the lookup an index would serve",
        "task": "Write one read-only SQL query that returns `name` and `email` from `customers` for the single row whose `email` is `sara@example.com`. Add one short sentence explaining how an index on the `email` column would help this lookup.",
        "response_type": "sql",
        "language": "sql",
        "competency": "Indexing basics",
        "starter_code": "SELECT name, email\nFROM customers\nWHERE email = 'sara@example.com';",
        "evaluation_note": "SkillBridge performs a static text/structure review only: it checks for a read-only SELECT, the expected table and columns, and an equality lookup on the email column, and that the explanation mentions an index. It does not connect to a database or execute SQL, so the review cannot prove runtime results.",
    },
    "mini_check": {"questions": [
        {"id": "i1", "type": "mcq", "question": "What is an index on a column?", "options": ["A separate data structure the database uses to find rows by that column faster", "The column headings shown in the result", "A copy of the whole table the user can edit", "A filter that deletes unused rows"], "correct_answer": "A separate data structure the database uses to find rows by that column faster", "competency": "Indexing basics", "difficulty": "intermediate", "misconception_hint": "Pick the option that describes an internal lookup helper, not a visible layout or a data change."},
        {"id": "i2", "type": "mcq", "question": "What does an index typically trade off?", "options": ["Faster reads on the indexed column against extra storage and slower writes", "Slower reads against faster inserts", "Nothing; indexes are free", "Fewer columns from every query"], "correct_answer": "Faster reads on the indexed column against extra storage and slower writes", "competency": "Indexing basics", "difficulty": "intermediate", "misconception_hint": "An index costs space and write effort to buy read speed on its column."},
        {"id": "i3", "type": "mcq", "question": "Which statement is true of reading with an index?", "options": ["The index can speed up the read but never changes the rows in the table", "The index inserts new rows into the result", "The index deletes rows that are not indexed", "The index permanently reorders the table"], "correct_answer": "The index can speed up the read but never changes the rows in the table", "competency": "Indexing basics", "difficulty": "intermediate", "misconception_hint": "An index is an access strategy; reading with it stays read-only."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "أساسيات الفهارس في SQL",
                "explanation": "الفهرس هيكل بيانات منفصل بتخليه قاعدة البيانات لعمود أو أكتر. لما `WHERE` أو `JOIN` بيقارن عمود بقيمة، قاعدة البيانات تقدر تستخدم الفهرس عشان توصل للصفوف المطابقة مباشرة بدل قراية الجدول كله. الاستعلام نفسه بيقرا بيانات بس — الفهرس عمره ما بيغير الجداول المخزنة.",
                "key_ideas": ["الفهرس هيكل بحث منفصل ومرتب؛ مش جزء من الصفوف اللي بتتشوف في الجدول.", "`WHERE email = 'sara@example.com'` تقدر تستخدم فهرس على عمود `email` عشان تلاقي الصف مباشرة.", "الفهرس بيوازن: تخزين زيادة وكتابة أبطأ مقابل قراية أسرع على العمود المفهرس.", "الإنشاء أو القراية بالفهرس عمرهم ما بيغيروا الصفوف المخزنة في الجداول."],
                "key_terms": {"فهرس": "هيكل بيانات منفصل بيخلي قاعدة البيانات تلاقي الصفوف بقيمة العمود أسرع.", "بحث": "إيجاد الصفوف اللي العمود فيها بيساوي قيمة معينة، زي مقارنة في `WHERE`.", "مفتاح أساسي": "عمود مميز للأرقام بيكون له فهرس كجزء من الجدول.", "موازنة": "قراية أسرع على العمود المفهرس على حساب تخزين زيادة وكتابة أبطأ."},
                "job_relevance": "التطبيقات والداشبوردات بتحتاج بحث بالقيم باستمرار؛ الفهرس الجيد بيحول فحص الجدول كله لبحث مباشر عن الصفوف المطلوبة.",
                "common_mistake": "توقع إن فهرس على عمود بيسرّع أي استعلام، أو فكرة إن الفهرس بيعيد كتابة أو ترتيب الجدول نفسه.",
                "worked_example": "المثال بيقرا الصف اللي إيميله مطابق، وده بالظبط النمط اللي فهرس على `email` بيسرّعه؛ SkillBridge لا ينفذ الاستعلام ولا يعدّل بيانات.",
                "depth_note": "محتوى تأسيسي ثابت لـ SQL من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة SELECT القياسية وبتشير لسلوك الفهارس القياسي. SkillBridge لا يوفر قاعدة بيانات SQL ولا ينفذ استعلامات المتعلم.",
            },
            "example": {"title": "لاقي عميل واحد بالإيميل", "type": "sql", "content": "SELECT name, email\nFROM customers\nWHERE email = 'sara@example.com';", "explanation": "الاستعلام بيطلب العميل اللي إيميله بالظبط كده. مع وجود فهرس على عمود `email` قاعدة البيانات بتلاقي الصف مباشرة بدل فحص كل الصفوف. ده مثال للشرح وليس استعلاماً ينفذه SkillBridge."},
            "practice": {"title": "اكتب البحث اللي الفهرس هيخدمه", "task": "اكتب استعلام SQL واحد للقراءة فقط يرجع `name` و`email` من `customers` للصف الوحيد اللي إيميله `sara@example.com`. أضف جملة قصيرة تشرح إزاي فهرس على عمود `email` هيساعد في البحث ده.", "response_type": "sql", "language": "sql", "competency": "Indexing basics", "starter_code": "SELECT name, email\nFROM customers\nWHERE email = 'sara@example.com';", "evaluation_note": "SkillBridge يعمل مراجعة ثابتة للنص والبنية فقط: بيتأكد من SELECT للقراءة، والجدول والأعمدة المطلوبين، وشرط مساواة على عمود email، وأن الشرح بيذكر فهرساً. لا يتصل بقاعدة بيانات ولا ينفذ SQL، لذلك المراجعة لا تثبت نتيجة وقت التشغيل."},
            "mini_check": {"questions": [
                {"id": "i1", "question": "إيه هو الفهرس على عمود؟", "options": ["هيكل بيانات منفصل بتستخدمه قاعدة البيانات عشان تلاقي الصفوف بالعمود ده أسرع", "عناوين الأعمدة اللي بتظهر في النتيجة", "نسخة من الجدول كله يقدر يعدّلها المستخدم", "فلتر بيحذف الصفوف غير المستخدمة"], "misconception_hint": "اختار الخيار اللي بيوصف أداة بحث داخلية، مش شكل مرئي أو تغيير بيانات."},
                {"id": "i2", "question": "الفهرس بيوازن عادةً بين إيه وإيه؟", "options": ["قراية أسرع على العمود المفهرس مقابل تخزين زيادة وكتابة أبطأ", "قراية أبطأ مقابل إدراج أسرع", "مافيش حاجة؛ الفهارس مجانية", "أعمدة أقل في كل استعلام"], "misconception_hint": "الفهرس بيكلف مساحة وجهد كتابة عشان يكسب سرعة قراية على عموده."},
                {"id": "i3", "question": "أي جملة صحيحة عن القراية بفهرس؟", "options": ["الفهرس بيقدر يسرّع القراية لكن عمره ما بيغير الصفوف في الجدول", "الفهرس بيضيف صفوف جديدة للنتيجة", "الفهرس بيحذف الصفوف غير المفهرسة", "الفهرس بيرتّب الجدول نهائياً"], "misconception_hint": "الفهرس استراتيجية وصول؛ القراية بيه تفضل للقراءة بس."},
            ]},
        },
    },
}


SQL_WINDOW_FUNCTIONS = {
    "status": "complete",
    "skill_aliases": ("sql", "structured query language"),
    "competency": "Window functions",
    "objective": "Compute a value over a set of related rows with OVER while keeping every row of the result.",
    "prerequisites": [{
        "competency": "sql_queries_filtering",
        "relationship": "required foundation",
        "why": "A window function runs over the rows a SELECT has already filtered, so a filtered read comes first.",
    }, {
        "competency": "sql_sorting_limiting",
        "relationship": "required foundation",
        "why": "ORDER BY inside OVER reuses the ordering vocabulary and preview shapes of bounded reads.",
    }, {
        "competency": "sql_aggregation",
        "relationship": "required foundation",
        "why": "Window functions generalize grouping: they compute aggregate-like values without collapsing the rows.",
    }, {
        "competency": "sql_joins",
        "relationship": "required foundation",
        "why": "The rows fed to a window function often come from a joined read, so joining tables comes first.",
    }, {
        "competency": "sql_subqueries",
        "relationship": "required foundation",
        "why": "Ranked or filtered window results are read with the same inner/outer sentence shapes subqueries teach.",
    }, {
        "competency": "sql_indexing_basics",
        "relationship": "required foundation",
        "why": "A window function reads many rows at once, so the index trade-offs behind those reads are understood first.",
    }, {
        "competency": "SQL Queries & Filtering",
        "relationship": "required foundation",
        "why": "The column list and WHERE of a SELECT are the frame the window function runs over.",
    }, {
        "competency": "Sorting & limiting",
        "relationship": "required foundation",
        "why": "ORDER BY inside OVER orders each window the same way ORDER BY orders a result.",
    }, {
        "competency": "Aggregation",
        "relationship": "required foundation",
        "why": "COUNT/SUM/AVG over a window behave like their grouped versions while keeping every row.",
    }, {
        "competency": "Joins",
        "relationship": "required foundation",
        "why": "The result a window function numbers is often a joined read, so pairing tables precedes ranking.",
    }, {
        "competency": "Subqueries",
        "relationship": "required foundation",
        "why": "A window result is consumed like any inner result, so nested reads come before OVER.",
    }, {
        "competency": "Indexing basics",
        "relationship": "required foundation",
        "why": "Window functions scan the relevant rows of a table, so knowing index access and its trade-offs comes first.",
    }],
    "roadmap_rationale": (
        "Window functions is the seventh complete SQL topic because it is the "
        "next analytical step after indexing: ranking customers, running totals, and "
        "moving averages describe each row against its neighbors without collapsing "
        "the rows the earlier topics taught how to read. The SQL roadmap then "
        "completes with query optimization, transactions, and schema design, which "
        "build on the analytical read shapes above."
    ),
    "learn": {
        "title": "SQL Window Functions",
        "explanation": (
            "A window function computes a value over a set (a window) of related "
            "rows using `OVER (...)`, while keeping every row of the result. "
            "`ROW_NUMBER() OVER (ORDER BY total DESC)` ranks customers by total "
            "without grouping them into one row, which is the key difference from "
            "a filtered, grouped read."
        ),
        "key_ideas": [
            "`OVER (...)` defines the window of rows the function is computed against.",
            "`ROW_NUMBER() OVER (ORDER BY total DESC)` ranks each row while keeping it in the result.",
            "`PARTITION BY` splits the window into groups, such as per city.",
            "Reading with window functions never changes the stored tables.",
        ],
        "key_terms": {
            "window": "The set of rows a function is computed over, named by `OVER`.",
            "over": "The clause that opens the window the function sees.",
            "row number": "A value counting each row's position inside the window.",
            "partition by": "Splitting the window into groups so the function restarts per group.",
        },
        "job_relevance": "Analysts number, rank, and total rows in context — the highest total per city, a running total by month — in one query instead of separate steps.",
        "common_mistake": "Using `ROW_NUMBER()` without `OVER`, which is a syntax error, or expecting `ORDER BY` inside `OVER` to collapse rows the way `GROUP BY` does.",
        "worked_example": "The example numbers each customer by total from largest to smallest while keeping every customer row; it does not insert, update, delete, or execute anything in SkillBridge.",
        "depth_note": "Canonical SQL foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard OVER/window syntax, available in modern PostgreSQL and SQLite. SkillBridge does not provide a SQL database or execute learner queries.",
        "grounding_sources": [
            {"title": "PostgreSQL documentation: Window Functions", "url": "https://www.postgresql.org/docs/current/tutorial-window.html", "source": "PostgreSQL documentation"},
            {"title": "SQLite documentation: Window Functions", "url": "https://sqlite.org/windowfunctions.html", "source": "SQLite documentation"},
        ],
    },
    "example": {
        "title": "Rank customers by total",
        "type": "sql",
        "content": "SELECT name, total,\n       ROW_NUMBER() OVER (ORDER BY total DESC) AS position\nFROM customers;",
        "explanation": "This query numbers each customer from the largest `total` down while keeping every customer row in the result. It is a worked example, not a query that SkillBridge runs.",
    },
    "practice": {
        "type": "practical",
        "title": "Rank customers with a window function",
        "task": "Write one read-only SQL query that returns `name`, `total`, and a `position` value from `customers`, where `position` is a row number over the window ordered by `total` from largest to smallest. Use `ROW_NUMBER() OVER (ORDER BY total DESC) AS position`. Add one short sentence explaining that OVER keeps every row.",
        "response_type": "sql",
        "language": "sql",
        "competency": "Window functions",
        "starter_code": "SELECT name, total,\n       ROW_NUMBER() OVER (ORDER BY total DESC) AS position\nFROM customers;",
        "evaluation_note": "SkillBridge performs a static text/structure review only: it checks for a read-only SELECT, the expected table and columns, a ROW_NUMBER() window function with OVER, an ORDER BY total descending inside the window, and the position alias, and that the explanation says OVER keeps every row. It does not connect to a database or execute SQL, so the review cannot prove runtime results.",
    },
    "mini_check": {"questions": [
        {"id": "w1", "type": "mcq", "question": "What does `OVER (...)` do in a query?", "options": ["Defines the window of rows the function is computed over while every row stays in the result", "Splits each row into a new table", "Sorts the stored table permanently", "Deletes rows outside the window"], "correct_answer": "Defines the window of rows the function is computed over while every row stays in the result", "competency": "Window functions", "difficulty": "advanced", "misconception_hint": "OVER names the rows the function sees but never collapses the result the way GROUP BY does."},
        {"id": "w2", "type": "mcq", "question": "Which fragment ranks customers by total from largest to smallest?", "options": ["ROW_NUMBER() OVER (ORDER BY total DESC)", "COUNT(*) GROUP BY total", "LIMIT total DESC", "WHERE total DESC"], "correct_answer": "ROW_NUMBER() OVER (ORDER BY total DESC)", "competency": "Window functions", "difficulty": "advanced", "misconception_hint": "Ranking needs an OVER clause that orders the window by total descending."},
        {"id": "w3", "type": "mcq", "question": "Which query numbers each customer by total without changing data?", "options": ["SELECT name, total, ROW_NUMBER() OVER (ORDER BY total DESC) AS position FROM customers;", "UPDATE customers SET position = 1;", "DELETE FROM customers;", "SELECT name, total FROM customers GROUP BY total;"], "correct_answer": "SELECT name, total, ROW_NUMBER() OVER (ORDER BY total DESC) AS position FROM customers;", "competency": "Window functions", "difficulty": "advanced", "misconception_hint": "The statement must read the customers table, rank with OVER, and never write."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "دوال النوافذ في SQL",
                "explanation": "دالة النافذة بتحسب قيمة على مجموعة (نافذة) من الصفوف المتصلة باستخدام `OVER (...)`, مع الحفاظ على كل الصفوف في النتيجة. `ROW_NUMBER() OVER (ORDER BY total DESC)` بيرتّب العملاء حسب الإجمالي من غير ما يدمجهم في صف واحد، وده الفرق الأساسي عن القراية المجمعة.",
                "key_ideas": ["`(...) OVER` بيعرّف نافذة الصفوف اللي الدالة بتتحسب عليها.", "`ROW_NUMBER() OVER (ORDER BY total DESC)` بيرتّب كل صف مع إبقائه في النتيجة.", "`PARTITION BY` بيقسم النافذة لمجموعات، زي لكل مدينة.", "القراية بدوال النوافذ عمرها ما تعدّل الجداول المخزنة."],
                "key_terms": {"نافذة": "مجموعة الصفوف اللي الدالة بتتحسب عليها، وبيحددها `OVER`.", "over": "الجزء اللي بيفتح النافذة اللي الدالة بتشوفها.", "ترقيم الصفوف": "قيمة بتحسب موضع كل صف جوه النافذة.", "تقسيم بالنافذة": "تقسيم النافذة لمجموعات عشان الدالة تبدأ من جديد في كل مجموعة."},
                "job_relevance": "المحللون بيرقّموا ويرتّبوا الصفوف في سياقها — أعلى إجمالي لكل مدينة، إجمالي متزايد بالشهر — في استعلام واحد بدل خطوات منفصلة.",
                "common_mistake": "استخدام `ROW_NUMBER()` من غير `OVER` (وده خطأ صياغة)، أو توقع إن `ORDER BY` جوه `OVER` بيدمج الصفوف زي `GROUP BY`.",
                "worked_example": "المثال بيرقّم كل عميل حسب الإجمالي من الأكبر للأصغر مع إبقاء كل صف عميل في النتيجة؛ SkillBridge لا ينفذ الاستعلام ولا يعدّل بيانات.",
                "depth_note": "محتوى تأسيسي ثابت لـ SQL من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة OVER/النوافذ القياسية المتاحة في PostgreSQL وSQLite الحديثين. SkillBridge لا يوفر قاعدة بيانات SQL ولا ينفذ استعلامات المتعلم.",
            },
            "example": {"title": "رتّب العملاء حسب الإجمالي", "type": "sql", "content": "SELECT name, total,\n       ROW_NUMBER() OVER (ORDER BY total DESC) AS position\nFROM customers;", "explanation": "الاستعلام بيرقّم كل عميل من أكبر `total` للأصغر مع إبقاء كل صف في النتيجة. ده مثال للشرح وليس استعلاماً ينفذه SkillBridge."},
            "practice": {"title": "رتّب العملاء بدالة نافذة", "task": "اكتب استعلام SQL واحد للقراءة فقط يرجع `name` و`total` و`position` من `customers`، حيث `position` رقم صف فوق نافذة مرتبة بـ `total` من الأكبر للأصغر. استخدم `ROW_NUMBER() OVER (ORDER BY total DESC) AS position`. أضف جملة قصيرة تشرح إن OVER بيحتفظ بكل الصفوف.", "response_type": "sql", "language": "sql", "competency": "Window functions", "starter_code": "SELECT name, total,\n       ROW_NUMBER() OVER (ORDER BY total DESC) AS position\nFROM customers;", "evaluation_note": "SkillBridge يعمل مراجعة ثابتة للنص والبنية فقط: بيتأكد من SELECT للقراءة، والجدول والأعمدة المطلوبين، ودالة ROW_NUMBER() مع OVER، وترتيب تنازلي على total جوه النافذة، والاسم المستعار position، وأن الشرح بيقول إن OVER بيحتفظ بكل الصفوف. لا يتصل بقاعدة بيانات ولا ينفذ SQL، لذلك المراجعة لا تثبت نتيجة وقت التشغيل."},
            "mini_check": {"questions": [
                {"id": "w1", "question": "`OVER (...)` بتعمل إيه في استعلام؟", "options": ["بتعرّف نافذة الصفوف اللي الدالة بتتحسب عليها مع إبقاء كل صف في النتيجة", "بتقسم كل صف لجدول جديد", "بترتّب الجدول المخزن نهائياً", "بتحذف الصفوف اللي برا النافذة"], "misconception_hint": "OVER بيسمي الصفوف اللي الدالة بتشوفها لكن عمره ما بيطوي النتيجة زي GROUP BY."},
                {"id": "w2", "question": "أي جزء بيرتّب العملاء حسب الإجمالي من الأكبر للأصغر؟", "options": ["ROW_NUMBER() OVER (ORDER BY total DESC)", "COUNT(*) GROUP BY total", "LIMIT total DESC", "WHERE total DESC"], "misconception_hint": "الترقيم محتاج جملة OVER بترتب النافذة حسب total تنازلي."},
                {"id": "w3", "question": "أي استعلام بيرقّم كل عميل حسب إجماليه من غير ما يعدّل بيانات؟", "options": ["SELECT name, total, ROW_NUMBER() OVER (ORDER BY total DESC) AS position FROM customers;", "UPDATE customers SET position = 1;", "DELETE FROM customers;", "SELECT name, total FROM customers GROUP BY total;"], "misconception_hint": "الاستعلام لازم يقرا جدول العملاء، ويرقّم بـ OVER، ويكتبش أي حاجة."},
            ]},
        },
    },
}


SQL_QUERY_OPTIMIZATION = {
    "status": "complete",
    "skill_aliases": ("sql", "structured query language"),
    "competency": "Query optimization",
    "objective": "Reason about how a database serves a read — filters, indexed columns, and query plans — without claiming that a static text review measures actual performance.",
    "prerequisites": [{
        "competency": "sql_queries_filtering",
        "relationship": "required foundation",
        "why": "A filtered read is the shape an optimizer plans first, so WHERE semantics come before execution-plan reasoning.",
    }, {
        "competency": "sql_sorting_limiting",
        "relationship": "required foundation",
        "why": "ORDER BY and LIMIT change the rows an optimizer handles, so bounded reads precede plan reasoning.",
    }, {
        "competency": "sql_aggregation",
        "relationship": "required foundation",
        "why": "Grouped reads change how the planner accesses rows, so aggregate shapes come before optimization.",
    }, {
        "competency": "sql_joins",
        "relationship": "required foundation",
        "why": "Join order is a central optimizer decision, so joining tables comes first.",
    }, {
        "competency": "sql_subqueries",
        "relationship": "required foundation",
        "why": "The planner rewrites and executes inner results, so nested reads precede optimization.",
    }, {
        "competency": "sql_indexing_basics",
        "relationship": "required foundation",
        "why": "Indexes are the main read lever the planner chooses among, so index trade-offs come first.",
    }, {
        "competency": "sql_window_functions",
        "relationship": "required foundation",
        "why": "Window reads touch many rows at once, so the analytical read shapes are understood before tuning them.",
    }, {
        "competency": "SQL Queries & Filtering",
        "relationship": "required foundation",
        "why": "The WHERE condition shapes the rows the planner can skip.",
    }, {
        "competency": "Sorting & limiting",
        "relationship": "required foundation",
        "why": "ORDER BY and LIMIT describe the read budget the optimizer plans for.",
    }, {
        "competency": "Aggregation",
        "relationship": "required foundation",
        "why": "A grouped read is a larger row-access pattern the optimizer handles.",
    }, {
        "competency": "Joins",
        "relationship": "required foundation",
        "why": "Join plans and indexes are decided together by the optimizer.",
    }, {
        "competency": "Subqueries",
        "relationship": "required foundation",
        "why": "The optimizer executes inner results before applying the outer plan.",
    }, {
        "competency": "Indexing basics",
        "relationship": "required foundation",
        "why": "An index is the main tool a query plan can choose for a read.",
    }, {
        "competency": "Window functions",
        "relationship": "required foundation",
        "why": "Window reads scan many rows, which is the access shape optimization tries to shrink.",
    }],
    "roadmap_rationale": (
        "Query optimization is the eighth complete SQL topic because it is the "
        "first conversation about how the database serves the read shapes the "
        "earlier topics taught: filters, ordering, grouping, joins, subqueries, "
        "indexes, and window reads. It is honest about the boundary — SkillBridge "
        "reviews query text statically and never executes SQL, so it cannot claim "
        "measured performance. The final two SQL competencies ship with their "
        "curated content."
    ),
    "learn": {
        "title": "SQL Query Optimization",
        "explanation": (
            "A database optimizer chooses how to serve a query: which index to "
            "use, which tables to read, and in what order. Writing a query that "
            "makes that choice easy — a filter on an indexed column, an explicit "
            "`ORDER BY`, a bounded `LIMIT` — usually gives the database more "
            "options. SkillBridge reviews the query text only, so none of this "
            "claims a measured runtime speed."
        ),
        "key_ideas": [
            "The optimizer chooses access paths; the query text states the intended read.",
            "A filter on an indexed column lets the optimizer skip a full table scan.",
            "Metrics like actual execution time require a real database and a benchmark.",
            "A static text review checks structure only and never measures performance.",
        ],
        "key_terms": {
            "optimizer": "The part of the database that decides how to execute a query.",
            "query plan": "The execution steps (index choice, scan order) the optimizer picks.",
            "index": "A structure that makes value lookups on a column faster.",
            "benchmark": "A real, measured run of queries against a database.",
        },
        "job_relevance": "Analysts and developers tune the reads behind dashboards and reports; knowing which index or filter helps is the difference between a query that scales and one that scans everything.",
        "common_mistake": "Claiming a query 'runs faster' from reading its text, when actual performance can only be established by measurement on a real database.",
        "worked_example": "The example shows an ordered, bounded read the optimizer can serve with an index; SkillBridge does not measure or run this query.",
        "depth_note": "Canonical SQL foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard SELECT syntax and standard index/planning vocabulary. SkillBridge does not provide a SQL database, execute learner queries, or measure their performance.",
        "grounding_sources": [
            {"title": "PostgreSQL documentation: Using EXPLAIN", "url": "https://www.postgresql.org/docs/current/using-explain.html", "source": "PostgreSQL documentation"},
            {"title": "SQLite documentation: EXPLAIN", "url": "https://sqlite.org/lang_explain.html", "source": "SQLite documentation"},
        ],
    },
    "example": {
        "title": "A bounded read an optimizer can serve simply",
        "type": "sql",
        "content": "SELECT name, total\nFROM customers\nORDER BY total DESC\nLIMIT 3;",
        "explanation": "This query asks for the three rows with the largest `total`. An optimizer can serve the ordering with an index and stop at the bound. It is a worked example — SkillBridge does not run it or measure it.",
    },
    "practice": {
        "type": "practical",
        "title": "Write a bounded read and describe the static review honestly",
        "task": "Write one read-only SQL query that returns `name` and `total` from `customers`, ordered by `total` from largest to smallest, kept to the top 3 rows with `LIMIT 3`. Add one short sentence explaining that while an index on `total` may help the optimizer, a static review cannot measure query performance.",
        "response_type": "sql",
        "language": "sql",
        "competency": "Query optimization",
        "starter_code": "SELECT name, total\nFROM customers\nORDER BY total DESC\nLIMIT 3;",
        "evaluation_note": "SkillBridge performs a static text/structure review only: it checks for a read-only SELECT, the expected table and columns, a descending order, and a limit of 3 rows. It does not connect to a database, execute SQL, or measure query time, so it cannot claim actual performance.",
    },
    "mini_check": {"questions": [
        {"id": "qo1", "type": "mcq", "question": "What does a database optimizer do?", "options": ["Chooses how to execute a query, such as which index or scan to use", "Rewrites the stored tables automatically", "Deletes slow queries", "Adds columns to every table"], "correct_answer": "Chooses how to execute a query, such as which index or scan to use", "competency": "Query optimization", "difficulty": "advanced", "misconception_hint": "The optimizer decides the access strategy; it does not change the stored schema."},
        {"id": "qo2", "type": "mcq", "question": "Which SQL statement can inspect the steps a database plans for a query?", "options": ["EXPLAIN", "SELECT * FROM users", "DELETE FROM users", "INSERT INTO users (id) VALUES (1)"], "correct_answer": "EXPLAIN", "competency": "Query optimization", "difficulty": "advanced", "misconception_hint": "EXPLAIN describes the plan; the other statements read or change data without showing the plan."},
        {"id": "qo3", "type": "mcq", "question": "Which statement about query performance is accurate?", "options": ["Actual performance can only be measured on a real database, not by reading the query text", "Reading the SQL proves exactly how fast it will run", "A longer query is always faster", "A static review measures execution time"], "correct_answer": "Actual performance can only be measured on a real database, not by reading the query text", "competency": "Query optimization", "difficulty": "advanced", "misconception_hint": "Structure can be reviewed on paper, but speed is an empirical result from measurement."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "تحسين أداء استعلامات SQL",
                "explanation": "مُحسِّن قاعدة البيانات بيفضل إزاي يخدم الاستعلام: يختار الفهرس اللي هيستخدمه، وترتيب قراية الجداول. كتابة استعلام بيسهّل الاختيار ده — فلتر على عمود مفهرس، `ORDER BY` واضح، `LIMIT` محدود — بتدي قاعدة البيانات خيارات أكتر عادةً. SkillBridge بيراجع نص الاستعلام بس، فمفيش أي ادعاء بسرعة قياسية وقت التشغيل.",
                "key_ideas": ["المُحسِّن بيختار طرق الوصول؛ نص الاستعلام بيعبّر عن القراية المقصودة.", "فلتر على عمود مفهرس بيسيب المُحسِّن يتخطى فحص الجدول كله.", "مقاييس زي زمن التنفيذ الفعلي محتاجة قاعدة بيانات حقيقية وقياس في الواقع.", "المراجعة الثابتة للنص بتبينة البنية بس وعمرها ما بتقيس الأداء."],
                "key_terms": {"محسّن": "الجزء اللي في قاعدة البيانات بيفضل إزاي ينفّذ الاستعلام.", "خطة الاستعلام": "خطوات التنفيذ (اختيار الفهرس، ترتيب الفحص) اللي المُحسِّن بيلتقطها.", "فهرس": "هيكل بيخلي البحث بالقيمة في عمود أسرع.", "قياس أداء": "تشغيل حقيقي مقاس للاستعلامات على قاعدة بيانات."},
                "job_relevance": "المحللون والمطورون بيضبطوا القرايات اللي ورا الداشبوردات والتقارير؛ معرفة مين الفهرس أو الفلتر اللي بينفع هي الفرق بين استعلام بيتمدد واستعلام بيفحص كل حاجة.",
                "common_mistake": "الادعاء إن الاستعلام 'أسرع' من قراية نصوصه، مع إن الأداء الفعلي بيتأسس بالقياس على قاعدة بيانات حقيقية.",
                "worked_example": "المثال بيوضح قراية مرتبة ومحدودة يقدر المُحسِّن يخدمها بفهرس؛ SkillBridge لا يقيس هذا الاستعلام ولا ينفذه.",
                "depth_note": "محتوى تأسيسي ثابت لـ SQL من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة SELECT القياسية ومصطلحات فهارس وتخطيط قياسية. SkillBridge لا يوفر قاعدة بيانات SQL ولا ينفذ استعلامات المتعلم ولا يقيس أداءها.",
            },
            "example": {"title": "قراية محدودة يقدر مُحسِّن يخدمها ببساطة", "type": "sql", "content": "SELECT name, total\nFROM customers\nORDER BY total DESC\nLIMIT 3;", "explanation": "الاستعلام بيطلب تلات صفوف عندهم أكبر `total`. المُحسِّن يقدر يخدم الترتيب بفهرس ويوقف عند الحد. ده مثال للشرح — SkillBridge لا ينفذه ولا يقيسه."},
            "practice": {"title": "اكتب قراية محدودة وصِف المراجعة الثابتة بصدق", "task": "اكتب استعلام SQL واحد للقراءة فقط يرجع `name` و`total` من `customers`, مرتباً حسب `total` من الأكبر للأصغر، واقتصاره على أعلى 3 صفوف بـ `LIMIT 3`. أضف جملة قصيرة توضح إنه حتى لو فهرس على `total` ممكن يساعد المُحسِّن، فالمراجعة الثابتة مش بتقيس الأداء.", "response_type": "sql", "language": "sql", "competency": "Query optimization", "starter_code": "SELECT name, total\nFROM customers\nORDER BY total DESC\nLIMIT 3;", "evaluation_note": "SkillBridge يعمل مراجعة ثابتة للنص والبنية فقط: بيتأكد من SELECT للقراءة، والجدول والأعمدة المطلوبين، وترتيب تنازلي، وحد أقصى 3 صفوف. لا يتصل بقاعدة بيانات، ولا ينفذ SQL، ولا يقيس وقت الاستعلام، لذلك لا يستطيع الادعاء بأداء فعلي."},
            "mini_check": {"questions": [
                {"id": "qo1", "question": "مُحسِّن قاعدة البيانات بيعمل إيه؟", "options": ["بيختار طريقة تنفيذ الاستعلام، زي استخدام أي فهرس أو فحص", "بيعيد كتابة الجداول المخزنة تلقائياً", "بيحذف الاستعلامات البطيئة", "بيضيف أعمدة لكل جدول"], "misconception_hint": "المُحسِّن بيقرر استراتيجية الوصول؛ هو مش بيغيّر المخطط المخزن."},
                {"id": "qo2", "question": "أي جملة SQL بتقدر تفحص الخطوات اللي قاعدة البيانات بتخطط ليها لاستعلام؟", "options": ["EXPLAIN", "SELECT * FROM users", "DELETE FROM users", "INSERT INTO users (id) VALUES (1)"], "misconception_hint": "EXPLAIN بيوصف الخطة؛ باقي الجمل بتقرا أو تعدّل بيانات من غير ما تِعرض الخطة."},
                {"id": "qo3", "question": "أي جملة عن أداء الاستعلامات دقيقة؟", "options": ["الأداء الفعلي ممكن يتقاس بس على قاعدة بيانات حقيقية، مش بقراية نص الاستعلام", "قراية الـ SQL بتثبت بالظبط قد إيه هيبقى سريع", "الاستعلام الأطول دايماً أسرع", "المراجعة الثابتة بتقيس زمن التنفيذ"], "misconception_hint": "البنية ممكن تتقيم على الورق، لكن السرعة نتيجة قياس في الواقع."},
            ]},
        },
    },
}


SQL_TRANSACTIONS = {
    "status": "complete",
    "skill_aliases": ("sql", "structured query language"),
    "competency": "Transactions",
    "objective": "Describe transactions as a group of statements treated as one unit, using BEGIN and COMMIT, without claiming that static inspection proves actual commit, rollback, isolation, or atomicity at runtime.",
    "prerequisites": [{
        "competency": "sql_queries_filtering",
        "relationship": "required foundation",
        "why": "The read inside a transaction is still a filtered SELECT, so reading comes first.",
    }, {
        "competency": "sql_sorting_limiting",
        "relationship": "required foundation",
        "why": "The statements a transaction groups often include ordered or bounded reads.",
    }, {
        "competency": "sql_aggregation",
        "relationship": "required foundation",
        "why": "A transaction may wrap summarized reads, so aggregate shapes come first.",
    }, {
        "competency": "sql_joins",
        "relationship": "required foundation",
        "why": "Multi-table statements often run inside one transaction for consistency.",
    }, {
        "competency": "sql_subqueries",
        "relationship": "required foundation",
        "why": "A transaction may contain reads against inner results, so nested reads come first.",
    }, {
        "competency": "sql_indexing_basics",
        "relationship": "required foundation",
        "why": "Indexed reads inside transactions are still ordinary reads, so index access is understood first.",
    }, {
        "competency": "sql_window_functions",
        "relationship": "required foundation",
        "why": "Analytical reads may be grouped inside transactions, so window reads are known first.",
    }, {
        "competency": "sql_query_optimization",
        "relationship": "required foundation",
        "why": "Transactions group statements whose plans the optimizer serves, so optimization precedes transaction grouping.",
    }, {
        "competency": "SQL Queries & Filtering",
        "relationship": "required foundation",
        "why": "The SELECT that transaction statements wrap is the read vocabulary of this topic.",
    }, {
        "competency": "Sorting & limiting",
        "relationship": "required foundation",
        "why": "Bounded reads can appear inside a transaction.",
    }, {
        "competency": "Aggregation",
        "relationship": "required foundation",
        "why": "Summaries may be part of a transactional statement group.",
    }, {
        "competency": "Joins",
        "relationship": "required foundation",
        "why": "Transactional consistency spans the related tables joins read.",
    }, {
        "competency": "Subqueries",
        "relationship": "required foundation",
        "why": "Inner results may be read within a transactional statement group.",
    }, {
        "competency": "Indexing basics",
        "relationship": "required foundation",
        "why": "The reads inside a transaction use the same index access decisions as any read.",
    }, {
        "competency": "Window functions",
        "relationship": "required foundation",
        "why": "Analytical reads can be grouped inside a transaction.",
    }, {
        "competency": "Query optimization",
        "relationship": "required foundation",
        "why": "Transactional statement groups are planned reads, so optimization precedes grouping semantics.",
    }],
    "roadmap_rationale": (
        "Transactions is the ninth complete SQL topic because grouping statements "
        "as one unit is the bridge between writing reads and protecting changes: "
        "the earlier topics produced read shapes, and this topic explains how a "
        "database treats a group of statements atomically. It is honest about the "
        "boundary — SkillBridge never executes SQL, so static inspection cannot "
        "prove actual commit, rollback, isolation, or atomicity. The final SQL "
        "competency, schema design, ships with this batch."
    ),
    "learn": {
        "title": "SQL Transactions",
        "explanation": (
            "A transaction is a group of SQL statements treated as one unit. "
            "`BEGIN` starts the group and `COMMIT` makes its statements permanent, "
            "so either the whole group takes effect or none of it does (atomicity), "
            "with isolation and durability as additional guarantees. The exact "
            "runtime behavior can only be observed on a real database — reading the "
            "script statically does not prove any of these guarantees happened."
        ),
        "key_ideas": [
            "`BEGIN` starts a transaction; `COMMIT` makes its statements permanent.",
            "Transactions give a group of statements atomicity: all or nothing.",
            "Isolation and durability are runtime guarantees, not text properties.",
            "Static inspection of the script cannot prove commit, rollback, isolation, or atomicity.",
        ],
        "key_terms": {
            "transaction": "A group of SQL statements treated as one unit.",
            "begin": "The statement that starts a transaction.",
            "commit": "The statement that makes a transaction's work permanent.",
            "rollback": "The statement that undoes a transaction's work.",
        },
        "job_relevance": "Payments, transfers, and stock edits must succeed or fail as one unit; knowing the transaction boundary is how developers keep multi-step changes consistent.",
        "common_mistake": "Believing that writing BEGIN/COMMIT in a script proves the statements executed atomically, when atomicity is a runtime property of the real database.",
        "worked_example": "The example shows BEGIN, a read-only SELECT, and COMMIT as the transaction boundary; SkillBridge does not run it, so it cannot prove the transaction's runtime guarantees.",
        "depth_note": "Canonical SQL foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard BEGIN/COMMIT syntax. SkillBridge does not provide a SQL database or execute learner queries.",
        "grounding_sources": [
            {"title": "PostgreSQL documentation: Transactions", "url": "https://www.postgresql.org/docs/current/tutorial-transactions.html", "source": "PostgreSQL documentation"},
            {"title": "SQLite documentation: Transactions", "url": "https://sqlite.org/lang_transaction.html", "source": "SQLite documentation"},
        ],
    },
    "example": {
        "title": "Wrap a read in a transaction",
        "type": "sql",
        "content": "BEGIN;\n\nSELECT name, total\nFROM customers\nWHERE name = 'amira';\n\nCOMMIT;",
        "explanation": "The script opens a transaction, reads one customer's current values, then commits. On a real database this groups the statements as one unit. It is a worked example — SkillBridge does not execute it, so it does not prove the transaction's runtime behavior.",
    },
    "practice": {
        "type": "practical",
        "title": "Write a transaction boundary",
        "task": "Write one SQL fragment that starts a transaction with `BEGIN;`, includes one read-only `SELECT name, total FROM customers WHERE name = 'amira';`, and ends it with `COMMIT;`. Add one short sentence explaining that a transaction groups statements as one unit, and that a static review cannot prove commit, rollback, isolation, or atomicity.",
        "response_type": "sql",
        "language": "sql",
        "competency": "Transactions",
        "starter_code": "BEGIN;\n\nSELECT name, total\nFROM customers\nWHERE name = 'amira';\n\nCOMMIT;",
        "evaluation_note": "SkillBridge performs a static text/structure review only: it checks for BEGIN, a read-only SELECT on customers, and COMMIT. It does not connect to a database or execute SQL, so it cannot prove that any commit, rollback, isolation, or atomicity actually happened at runtime.",
    },
    "mini_check": {"questions": [
        {"id": "t1", "type": "mcq", "question": "What does `BEGIN` do in SQL?", "options": ["Starts a transaction: a group of statements treated as one unit", "Deletes the current session's data", "Ends the connection", "Sorts the table permanently"], "correct_answer": "Starts a transaction: a group of statements treated as one unit", "competency": "Transactions", "difficulty": "advanced", "misconception_hint": "BEGIN opens the boundary of the statement group; it does not modify stored data."},
        {"id": "t2", "type": "mcq", "question": "Which property means all statements in a transaction take effect together or none do?", "options": ["Atomicity", "Normalization", "Indexing", "Partitioning"], "correct_answer": "Atomicity", "competency": "Transactions", "difficulty": "advanced", "misconception_hint": "The all-or-nothing property is atomicity; it is a runtime guarantee, not a text property."},
        {"id": "t3", "type": "mcq", "question": "Which statement ends a transaction by making its changes permanent?", "options": ["COMMIT", "SELECT", "LIMIT", "DELETE"], "correct_answer": "COMMIT", "competency": "Transactions", "difficulty": "advanced", "misconception_hint": "COMMIT finalizes the group; DELETE only removes rows and does not define the transaction boundary."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "المعاملات في SQL",
                "explanation": "المعاملة (transaction) مجموعة من جُمل SQL بيتعاملوا كوحدة واحدة. `BEGIN` بيفتح المجموعة و`COMMIT` بيثبّت جُمَلها، يعني الإما المجموعة كلها تتحقق الإما مافيش منها حاجة تتحقق، مع ضمانات عزل ومتانة زيادة. السلوك الفعلي وقت التشغيل ممكن يُلاحَظ بس على قاعدة بيانات حقيقية — قراية السكربت ثابت على الورق مش بتثبت أي ضمان من دول حصل فعلاً.",
                "key_ideas": ["`BEGIN` بيفتح معاملة؛ `COMMIT` بيثبّت جُمَلها.", "المعاملات بتدي مجموعة الجُمل خاصية الذرية: كلها أو مافيش.", "العزل والمتانة ضمانات وقت التشغيل، مش خصائص نصية.", "الفحص الثابت للسكربت عمره ما بيُثبت commit أو rollback أو عزل أو ذرية."],
                "key_terms": {"معاملة": "مجموعة جُمَل SQL بيتعاملوا كوحدة واحدة.", "begin": "الجملة اللي بتفتح معاملة.", "commit": "الجملة اللي بتثبّت شغل المعاملة نهائياً.", "rollback": "الجملة اللي بترجع شغل المعاملة."},
                "job_relevance": "المدفوعات والتحويلات وتعديلات المخزون لازم تنجح أو تفشل كوحدة واحدة؛ معرفة حدود المعاملة هي إزاي المطورين بيخلوا التغييرات متعددة الخطوات متناسقة.",
                "common_mistake": "الاعتقاد إن كتابة BEGIN/COMMIT في سكربت بتثبت إن الجُمل نفذت بذرية، مع إن الذرية خاصية وقت تشغيل في قاعدة البيانات الحقيقية.",
                "worked_example": "المثال بيوضح BEGIN وقراية SELECT للقراءة بس وCOMMIT كحدود للمعاملة؛ SkillBridge لا ينفذه، فلذلك لا يستطيع إثبات ضمانات التشغيل للمعاملة.",
                "depth_note": "محتوى تأسيسي ثابت لـ SQL من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة BEGIN/COMMIT القياسية. SkillBridge لا يوفر قاعدة بيانات SQL ولا ينفذ استعلامات المتعلم.",
            },
            "example": {"title": "لفّ قراية جوه معاملة", "type": "sql", "content": "BEGIN;\n\nSELECT name, total\nFROM customers\nWHERE name = 'amira';\n\nCOMMIT;", "explanation": "السكربت بيفتح معاملة، بيقرا قيم عميل حالي، وبعدين بيثبّت بـ COMMIT. على قاعدة بيانات حقيقية ده بيدمج الجُمل كوحدة واحدة. ده مثال للشرح — SkillBridge لا ينفذه، فلذلك لا يثبت سلوك المعاملة وقت التشغيل."},
            "practice": {"title": "اكتب حدود معاملة", "task": "اكتب جزء SQL واحد يبدأ معاملة بـ `BEGIN;`, ويشمل قراءة واحدة `SELECT name, total FROM customers WHERE name = 'amira';`, وينهيها بـ `COMMIT;`. أضف جملة قصيرة توضح إن المعاملة بتدعم الجُمل كوحدة واحدة، وإن المراجعة الثابتة مش بتقدر تثبت commit أو rollback أو عزل أو ذرية.", "response_type": "sql", "language": "sql", "competency": "Transactions", "starter_code": "BEGIN;\n\nSELECT name, total\nFROM customers\nWHERE name = 'amira';\n\nCOMMIT;", "evaluation_note": "SkillBridge يعمل مراجعة ثابتة للنص والبنية فقط: بيتأكد من BEGIN، وقراءة SELECT على customers، وCOMMIT. لا يتصل بقاعدة بيانات ولا ينفذ SQL، لذلك لا يستطيع إثبات إن commit أو rollback أو عزل أو ذرية حصلوا فعلاً وقت التشغيل."},
            "mini_check": {"questions": [
                {"id": "t1", "question": "`BEGIN` بتعمل إيه في SQL؟", "options": ["بتفتح معاملة: مجموعة جُمل بيتعاملوا كوحدة واحدة", "بتحذف بيانات الجلسة الحالية", "بتنهي الاتصال", "بترتّب الجدول نهائياً"], "misconception_hint": "BEGIN بيفتح حدود مجموعة الجُمل؛ هو مش بيعدّل البيانات المخزنة."},
                {"id": "t2", "question": "أي خاصية معناها إن كل جُمَل المعاملة بتتحقق مع بعض الإما مافيش منهم حاجة؟", "options": ["الذرية (Atomicity)", "التطبيع (Normalization)", "الفهرسة (Indexing)", "التقسيم (Partitioning)"], "misconception_hint": "خاصية كل شيء أو لا شيء هي الذرية؛ وهي ضمان وقت التشغيل مش خاصية نصية."},
                {"id": "t3", "question": "أي جملة بتنهي المعاملة بتثبيت تغييراتها؟", "options": ["COMMIT", "SELECT", "LIMIT", "DELETE"], "misconception_hint": "COMMIT بيخلّص المجموعة؛ DELETE بيحذف صفوف بس وهو مش بيحدد حدود المعاملة."},
            ]},
        },
    },
}


SQL_SCHEMA_DESIGN = {
    "status": "complete",
    "skill_aliases": ("sql", "structured query language"),
    "competency": "Schema design",
    "objective": "Define a table's intended structure and constraints in SQL, without claiming the schema was deployed or validated against a running database.",
    "prerequisites": [{
        "competency": "sql_queries_filtering",
        "relationship": "required foundation",
        "why": "A schema exists to answer filtered reads, so the read shapes come first.",
    }, {
        "competency": "sql_sorting_limiting",
        "relationship": "required foundation",
        "why": "Columns a schema stores serve ordered and bounded reads.",
    }, {
        "competency": "sql_aggregation",
        "relationship": "required foundation",
        "why": "Summaries over a schema's columns are grouped reads, so aggregation comes first.",
    }, {
        "competency": "sql_joins",
        "relationship": "required foundation",
        "why": "Foreign keys in a schema model the joins across tables.",
    }, {
        "competency": "sql_subqueries",
        "relationship": "required foundation",
        "why": "A schema's columns are read inside nested queries too, so subqueries come first.",
    }, {
        "competency": "sql_indexing_basics",
        "relationship": "required foundation",
        "why": "Keys usually become indexes, so index trade-offs inform the schema.",
    }, {
        "competency": "sql_window_functions",
        "relationship": "required foundation",
        "why": "A schema's table shape supports window reads too, so those reads are known first.",
    }, {
        "competency": "sql_query_optimization",
        "relationship": "required foundation",
        "why": "Schema choices (keys and indexes) determine the plans the optimizer builds.",
    }, {
        "competency": "sql_transactions",
        "relationship": "required foundation",
        "why": "Constraints keep grouped statements consistent, so transactions precede schema definition.",
    }, {
        "competency": "SQL Queries & Filtering",
        "relationship": "required foundation",
        "why": "The schema stores the columns those queries read and filter.",
    }, {
        "competency": "Sorting & limiting",
        "relationship": "required foundation",
        "why": "The schema's columns support the ordering and bounds reads need.",
    }, {
        "competency": "Aggregation",
        "relationship": "required foundation",
        "why": "The schema's table shape supports grouped summaries.",
    }, {
        "competency": "Joins",
        "relationship": "required foundation",
        "why": "Foreign keys encode the relationships joins traverse.",
    }, {
        "competency": "Subqueries",
        "relationship": "required foundation",
        "why": "Schema columns are read by inner queries as well.",
    }, {
        "competency": "Indexing basics",
        "relationship": "required foundation",
        "why": "Key columns commonly become indexes, so design decisions consider index trade-offs.",
    }, {
        "competency": "Window functions",
        "relationship": "required foundation",
        "why": "Analytical reads run over the schema's tables.",
    }, {
        "competency": "Query optimization",
        "relationship": "required foundation",
        "why": "The schema's keys and constraints are the inputs the optimizer plans with.",
    }, {
        "competency": "Transactions",
        "relationship": "required foundation",
        "why": "Constraints keep the statement groups transactions wrap consistent.",
    }],
    "roadmap_rationale": (
        "Schema design is the tenth and final complete SQL topic because it is the "
        "capstone of the SQL track: after reading, aggregating, joining, "
        "subquerying, indexing, windowing, optimizing, and grouping statements as "
        "transactions, this topic defines the very structure those statements "
        "read. It is honest about the boundary — SkillBridge reviews the intended "
        "schema text statically and never creates or validates it against a "
        "running database. With this topic, all ten SQL blueprint competencies "
        "ship as complete curated content."
    ),
    "learn": {
        "title": "SQL Schema Design",
        "explanation": (
            "A schema describes the structure and constraints of your tables: "
            "column types, a `PRIMARY KEY` to identify each row, `NOT NULL` to "
            "require a value, and `UNIQUE` to prevent duplicates. Writing the "
            "schema is a design statement; deploying or validating it against a "
            "running database is a separate step that a static review cannot do."
        ),
        "key_ideas": [
            "`CREATE TABLE` states the intended structure with column types and constraints.",
            "A `PRIMARY KEY` uniquely identifies every row in a table.",
            "`NOT NULL` requires a value; `UNIQUE` prevents duplicate values in a column.",
            "Reviewing a schema on paper does not deploy it or validate it on a running database.",
        ],
        "key_terms": {
            "schema": "The structure and constraints of the tables in a database.",
            "primary key": "The column or columns that uniquely identify a row.",
            "not null": "A constraint requiring the column to hold a value.",
            "unique": "A constraint preventing duplicate values in a column.",
        },
        "job_relevance": "Engineers translate business rules into tables and constraints; a clear schema with a primary key and uniqueness is what keeps application data trustworthy over time.",
        "common_mistake": "Thinking that writing CREATE TABLE proves the schema exists or works, when creating and validating it against a real database is a separate runtime step.",
        "worked_example": "The example declares a customers table with a primary key and value constraints; SkillBridge does not create or validate this schema on a database.",
        "depth_note": "Canonical SQL foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard CREATE TABLE syntax. SkillBridge does not provide a SQL database, create tables, or execute learner queries.",
        "grounding_sources": [
            {"title": "PostgreSQL documentation: Data Definition", "url": "https://www.postgresql.org/docs/current/ddl-constraints.html", "source": "PostgreSQL documentation"},
            {"title": "SQLite documentation: CREATE TABLE", "url": "https://sqlite.org/lang_createtable.html", "source": "SQLite documentation"},
        ],
    },
    "example": {
        "title": "Define the customers table",
        "type": "sql",
        "content": "CREATE TABLE customers (\n  id INTEGER PRIMARY KEY,\n  name TEXT NOT NULL,\n  email TEXT NOT NULL UNIQUE,\n  city TEXT,\n  status TEXT\n);",
        "explanation": "The statement defines the intended structure: an identifying `id`, a required `name`, a unique `email`, and optional `city`/`status`. It is a design statement — SkillBridge does not create this table on any database.",
    },
    "practice": {
        "type": "practical",
        "title": "Write the intended schema",
        "task": "Write one `CREATE TABLE customers` statement with columns `id INTEGER PRIMARY KEY`, `name TEXT NOT NULL`, `email TEXT NOT NULL UNIQUE`, and `city TEXT`/`status TEXT`. Add one short sentence explaining that this defines the intended structure and that a static review does not prove the schema was deployed or validated on a running database.",
        "response_type": "sql",
        "language": "sql",
        "competency": "Schema design",
        "starter_code": "CREATE TABLE customers (\n  id INTEGER PRIMARY KEY,\n  name TEXT NOT NULL,\n  email TEXT NOT NULL UNIQUE,\n  city TEXT,\n  status TEXT\n);",
        "evaluation_note": "SkillBridge performs a static text/structure review only: it checks for a CREATE TABLE statement, the customers table, a PRIMARY KEY, and NOT NULL/UNIQUE constraints. It does not create tables or connect to a database, so it cannot claim the schema was deployed or validated.",
    },
    "mini_check": {"questions": [
        {"id": "s1", "type": "mcq", "question": "What does a `PRIMARY KEY` do for a table?", "options": ["Uniquely identifies each row in the table", "Sorts every column automatically", "Deletes duplicate rows", "Stores the query history"], "correct_answer": "Uniquely identifies each row in the table", "competency": "Schema design", "difficulty": "advanced", "misconception_hint": "The primary key is the row identity; it is not a sorting or cleanup tool."},
        {"id": "s2", "type": "mcq", "question": "Which constraint prevents two customers from sharing the same email?", "options": ["UNIQUE on the email column", "NOT NULL on the email column", "A DEFAULT email value", "ORDER BY email"], "correct_answer": "UNIQUE on the email column", "competency": "Schema design", "difficulty": "advanced", "misconception_hint": "Uniqueness is enforced by a UNIQUE constraint; NOT NULL only requires a value to exist."},
        {"id": "s3", "type": "mcq", "question": "Which statement about schema design is accurate?", "options": ["A CREATE TABLE statement describes the intended structure; it does not by itself prove the schema works on a running database", "Writing DDL deploys the schema to a live database immediately", "Constraints have no effect on data integrity", "A schema is validated by reading documentation about it"], "correct_answer": "A CREATE TABLE statement describes the intended structure; it does not by itself prove the schema works on a running database", "competency": "Schema design", "difficulty": "advanced", "misconception_hint": "DDL text states intent; deploying and validating against a real database is a separate runtime step."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "تصميم مخطط قواعد البيانات في SQL",
                "explanation": "المخطط (schema) بيوصف بنية جداولك وقيودها: أنواع الأعمدة، و`PRIMARY KEY` لهوية كل صف، و`NOT NULL` عشان يشترط قيمة، و`UNIQUE` عشان يمنع التكرار. كتابة المخطط بيان تصميم؛ نشر الصحة أو التحقق منه على قاعدة بيانات شغالة خطوة منفصلة المراجعة الثابتة مش بتقدر تعملها.",
                "key_ideas": ["`CREATE TABLE` بيعبّر عن البنية المقصودة بأنواع أعمدة وقيود.", "`PRIMARY KEY` بيميّز هوية كل صف في الجدول.", "`NOT NULL` بيشترط قيمة؛ و`UNIQUE` بيمنع تكرار القيم في عمود.", "مراجعة مخطط على الورق مش بنشره ولا بتتحقق منه على قاعدة بيانات شغالة."],
                "key_terms": {"مخطط": "بنية وقيود الجداول في قاعدة بيانات.", "مفتاح أساسي": "العمود أو الأعمدة اللي بتميّز الصف.", "not null": "قيد بيشترط إن العمود يحمل قيمة.", "unique": "قيد بيمنع تكرار القيم في عمود."},
                "job_relevance": "المهندسون بيترجموا قواعد العمل لجداول وقيود؛ مخطط واضح بمفتاح أساسي وتفرد هو اللي بيحافظ على ثقة بيانات التطبيق بمرور الوقت.",
                "common_mistake": "الاعتقاد إن كتابة CREATE TABLE بتثبت إن المخطط موجود أو شغال، مع إن إنشاؤه والتحقق منه على قاعدة بيانات حقيقية خطوة تشغيل منفصلة.",
                "worked_example": "المثال بيعرّف جدول العملاء بمفتاح أساسي وقيود قيم؛ SkillBridge لا ينشئ هذا المخطط على قاعدة بيانات ولا يتحقق منه.",
                "depth_note": "محتوى تأسيسي ثابت لـ SQL من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة CREATE TABLE القياسية. SkillBridge لا يوفر قاعدة بيانات SQL ولا ينشئ جداول ولا ينفذ استعلامات المتعلم.",
            },
            "example": {"title": "عرّف جدول العملاء", "type": "sql", "content": "CREATE TABLE customers (\n  id INTEGER PRIMARY KEY,\n  name TEXT NOT NULL,\n  email TEXT NOT NULL UNIQUE,\n  city TEXT,\n  status TEXT\n);", "explanation": "الجملة بتحدد البنية المقصودة: `id` للهوية، و`name` مطلوب، و`email` فريد، و`city`/`status` اختياريين. ده بيان تصميم — SkillBridge لا ينشئ هذا الجدول على أي قاعدة بيانات."},
            "practice": {"title": "اكتب المخطط المقصود", "task": "اكتب جملة `CREATE TABLE customers` واحد بأعمدة `id INTEGER PRIMARY KEY`, `name TEXT NOT NULL`, `email TEXT NOT NULL UNIQUE`, و`city TEXT`/`status TEXT`. أضف جملة قصيرة توضح إن ده بيحدد البنية المقصودة وإن المراجعة الثابتة مش بتثبت إن المخطط اتنتشر أو اتتحقق منه على قاعدة بيانات شغالة.", "response_type": "sql", "language": "sql", "competency": "Schema design", "starter_code": "CREATE TABLE customers (\n  id INTEGER PRIMARY KEY,\n  name TEXT NOT NULL,\n  email TEXT NOT NULL UNIQUE,\n  city TEXT,\n  status TEXT\n);", "evaluation_note": "SkillBridge يعمل مراجعة ثابتة للنص والبنية فقط: بيتأكد من جملة CREATE TABLE، وجدول customers، ومفتاح أساسي PRIMARY KEY، وقيود NOT NULL/UNIQUE. لا ينشئ جداول ولا يتصل بقاعدة بيانات، لذلك لا يستطيع الادعاء إن المخطط اتنتشر أو اتتحقق منه."},
            "mini_check": {"questions": [
                {"id": "s1", "question": "`PRIMARY KEY` بيعمل إيه للجدول؟", "options": ["بيميّز هوية كل صف في الجدول", "بيرتّب كل الأعمدة تلقائياً", "بيحذف الصفوف المكررة", "بيخزّن سجل الاستعلامات"], "misconception_hint": "المفتاح الأساسي هو هوية الصف؛ مش أداة ترتيب أو تنظيف."},
                {"id": "s2", "question": "أي قيد بيمنع عميلين يشاركوا نفس الإيميل؟", "options": ["UNIQUE على عمود email", "NOT NULL على عمود email", "قيمة DEFAULT للإيميل", "ORDER BY email"], "misconception_hint": "التفرد بيتنفذ بقيد UNIQUE؛ NOT NULL بيشترط إن القيمة موجودة بس."},
                {"id": "s3", "question": "أي جملة عن تصميم المخطط دقيقة؟", "options": ["جملة CREATE TABLE بتوصف البنية المقصودة؛ ومش بتثبت لوحدها إن المخطط شغال على قاعدة بيانات", "كتابة DDL بتنشر المخطط على قاعدة بيانات حية فوراً", "القيود مش لها أي أثر على سلامة البيانات", "المخطط بيتحقق منه بقراية الدوكيومنتا عن حاجة عنه"], "misconception_hint": "نص DDL بيعبّر عن القصد؛ النشر والتحقق على قاعدة بيانات حقيقية خطوة وقت تشغيل منفصلة."},
            ]},
        },
    },
}


GIT_LOCAL_REPOSITORIES = {
    "status": "complete",
    "skill_aliases": ("git",),
    "competency": "Local repositories",
    "objective": "Initialise a local Git repository and use `git status` to inspect its untracked and tracked state.",
    "prerequisites": [{
        "competency": "Command line basics",
        "relationship": "required foundation",
        "why": "Git commands are issued from a terminal, so you run commands and inspect a working directory before any file is tracked.",
    }],
    "roadmap_rationale": (
        "Local repositories is the first complete Git topic on the Git roadmap because every "
        "history-based workflow starts with a repository on disk: `git init` creates the repository "
        "that later topics commit to, branch, merge, and rewrite. Committing is the next complete "
        "topic; the other Git topics remain separately scoped and are not represented as completed "
        "lessons here."
    ),
    "learn": {
        "title": "Local repositories",
        "explanation": (
            "A **local repository** is a folder that Git manages: `git init` creates the repository and its "
            "`.git` directory in the current folder, and from then on Git can record the folder's files. "
            "`git status` reports which files are untracked, which are staged, and which have changed since the "
            "last commit. A local repository records history on your machine; publishing to a remote such as "
            "GitHub is a separate, later step."
        ),
        "key_ideas": [
            "`git init` creates a new local repository in the current folder; `git init my-project` creates the folder and the repository together.",
            "Git stores the repository's history and settings inside a `.git` directory in the project root.",
            "`git status` shows the working tree state: untracked files, staged changes, and modified files.",
            "A local repository needs no remote to exist; a new repository simply has no commits yet.",
        ],
        "key_terms": {
            "repository": "A folder that Git manages, including its recorded history.",
            "working tree": "The files in your project folder that Git can see.",
            "tracked file": "A file whose changes Git is recording.",
            "untracked file": "A file Git has never been told to record.",
        },
        "job_relevance": "Developers initialise a repository once per project and read `git status` constantly to see exactly what changed before staging and committing.",
        "common_mistake": "Do not assume `git init` uploads anything, and do not expect a file to be tracked just because the repository exists; files must still be staged and committed.",
        "worked_example": "The example creates a project folder and a local repository and then inspects it with `git status`. It is a written example — the commands are not executed by SkillBridge.",
        "depth_note": "Canonical Git foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard `git init`/`git status` syntax. SkillBridge does not run these commands, install Git, or create repositories on the learner's machine.",
        "grounding_sources": [
            {"title": "Git documentation: git-init", "url": "https://git-scm.com/docs/git-init", "source": "Git official documentation"},
            {"title": "Git documentation: git-status", "url": "https://git-scm.com/docs/git-status", "source": "Git official documentation"},
            {"title": "Pro Git book: Getting a Git Repository", "url": "https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository", "source": "Git official documentation"},
        ],
    },
    "example": {
        "title": "Start a project repository",
        "type": "bash",
        "content": "cd my-project\ngit init\ngit status",
        "explanation": "This example changes into the `my-project` folder (or `git init my-project` creates it), initialises the local repository, and then inspects the repository's state. The commands are shown for study — SkillBridge does not execute them.",
    },
    "practice": {
        "type": "practical",
        "title": "Describe creating a local repository",
        "task": "Write the exact terminal commands you would use to: (1) enter a project folder named `my-project`, (2) initialise a local Git repository there, and (3) inspect the repository state with `git status`. Add one short sentence explaining what the `.git` directory is for and that this is a written answer — SkillBridge does not run these commands.",
        "response_type": "code",
        "language": "bash",
        "competency": "Local repositories",
        "starter_code": "cd my-project\ngit init\ngit status",
        "evaluation_note": "SkillBridge performs a static text review only: it checks for changing into the folder, `git init`, `git status`, and an explanation that this is a written answer rather than a run command. It does not run git or create a repository, so the review cannot prove the commands succeeded.",
    },
    "mini_check": {"questions": [
        {"id": "l1", "type": "mcq", "question": "What does `git init` do?", "options": ["Creates a local Git repository in the current folder", "Uploads the folder to GitHub immediately", "Deletes the files that are not tracked", "Installs the Git program"], "correct_answer": "Creates a local Git repository in the current folder", "competency": "Local repositories", "difficulty": "beginner", "misconception_hint": "`git init` is a local command; publishing to a remote is a separate step."},
        {"id": "l2", "type": "mcq", "question": "Where does Git store a local repository's history?", "options": ["In a hidden `.git` directory inside the project", "Only on GitHub.com", "In each source file's last line", "In the operating system's temporary folder"], "correct_answer": "In a hidden `.git` directory inside the project", "competency": "Local repositories", "difficulty": "beginner", "misconception_hint": "Git keeps version data inside the project folder, not only on a remote service."},
        {"id": "l3", "type": "mcq", "question": "Which statement about a written `git init` answer is honest?", "options": ["A static review confirms the commands are written down; it does not prove they ran or created a repository", "Writing the command proves the repository was created", "A written answer can include real files from any project", "Git never stores anything on disk"], "correct_answer": "A static review confirms the commands are written down; it does not prove they ran or created a repository", "competency": "Local repositories", "difficulty": "beginner", "misconception_hint": "Reviewing text is not the same as running git; describe commands without claiming they were executed."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "المستودعات المحلية",
                "explanation": "المستودع المحلي هو مجلد بيشرف عليه Git: `git init` بيعمل المستودع ودليل `.git` في المجلد الحالي، وبعدها Git يقدر يسجل ملفات المجلد. `git status` بيعرض الملفات اللي لسه غير مُتتبعة، واللي اتعمل stage-لها، واللي اتعّدلت. المستودع المحلي بيسجل التاريخ على جهازك؛ النشر على خدمة بعيدة زي GitHub خطوة منفصلة ولاحقة.",
                "key_ideas": ["`git init` بيعمل مستودعاً محلياً جديداً في المجلد الحالي؛ و`git init my-project` بيعمل المجلد والمستودع معاً.", "Git بيخزّن تاريخ المستودع وإعداداته جوه دليل `.git` في جذر المشروع.", "`git status` بيعرض حالة شجرة العمل: ملفات غير مُتتبعة، وتغييرات staged، وملفات معدّلة.", "المستودع المحلي لا يحتاج خدمة بعيدة لوجودها؛ المستودع الجديد ببساطة لسه من غير أي commit."],
                "key_terms": {"مستودع": "مجلد بيشرف عليه Git مع التاريخ المسجل جواه.", "شجرة العمل": "الملفات الموجودة في مجلد مشروعك اللي Git يقدر يشوفها.", "ملف مُتتبَع": "ملف Git بيقوم بالتسجيل التغييرات الخاصة به.", "ملف غير مُتتبَع": "ملف Git لسه عمره ما طُلب منه تسجيله."},
                "job_relevance": "المطورون بيعملوا مستودع مرة واحدة لكل مشروع، وبيستخدموا `git status` طول الوقت عشان يعرفوا إيه اللي اتغيّر قبل ما يعملوا stage وcommit.",
                "common_mistake": "ما تفترضش إن `git init` بيرفع حاجة، وما تتوقعش إن الملف يدخل ضمن التتبع بمجرد وجود المستودع؛ الملفات لازم تت stage وتت commit.",
                "worked_example": "المثال بيعمل مجلد مشروع ومستودع محلي وبعدين يتفحصه بـ `git status`. ده مثال مكتوب — SkillBridge لا ينفذ هذه الأوامر.",
                "depth_note": "محتوى تأسيسي ثابت لـ Git من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة `git init`/`git status` القياسية. SkillBridge لا ينفذ هذه الأوامر ولا يثبّت Git ولا ينشئ مستودعات على جهاز المتعلم.",
            },
            "example": {"title": "ابدأ مستودع مشروع", "type": "bash", "content": "cd my-project\ngit init\ngit status", "explanation": "المثال بينتقل لمجلد `my-project` (أو `git init my-project` بيعمله)، وبعدها بينشئ المستودع المحلي ويفحص حالته. الأوامر معروضة للشرح — SkillBridge لا ينفذها."},
            "practice": {"title": "اشرح إنشاء مستودع محلي", "task": "اكتب بالظبط أوامر الطرفية اللي هتستخدمها لـ: (1) الدخول إلى مجلد المشروع `my-project`، و(2) عمل مستودع Git محلي جواه، و(3) فحص حالة المستودع بـ `git status`. أضف جملة قصيرة تشرح دليل `.git` بيخدم إيه وإن ده إجابة مكتوبة — SkillBridge لا ينفذ هذه الأوامر.", "response_type": "code", "language": "bash", "competency": "Local repositories", "starter_code": "cd my-project\ngit init\ngit status", "evaluation_note": "SkillBridge بيعمل مراجعة ثابتة للنص فقط: بيتأكد من الدخول للمجلد و`git init` و`git status` ومن إن الإجابة مكتوبة مش منفّذة. لا ينفذ git ولا ينشئ مستودعاً، لذلك المراجعة لا تثبت نجاح الأوامر."},
            "mini_check": {"questions": [
                {"id": "l1", "question": "`git init` بيعمل إيه؟", "options": ["بيعمل مستودع Git محلي في المجلد الحالي", "بيرفع المجلد على GitHub فوراً", "بيحذف الملفات الغير مُتتبعة", "بيعمل install لأداة Git"], "misconception_hint": "`git init` أمر محلي؛ النشر على خدمة بعيدة خطوة منفصلة."},
                {"id": "l2", "question": "Git بيخزّن تاريخ المستودع المحلي فين؟", "options": ["في دليل `.git` مخفي جوه المشروع", "على GitHub.com بس", "في آخر سطر من كل ملف مصدر", "في المجلد المؤقت لنظام التشغيل"], "misconception_hint": "Git بيحفظ بيانات النسخ جوه مجلد المشروع، مش بس على خدمة بعيدة."},
                {"id": "l3", "question": "أي جملة عن إجابة مكتوبة فيها `git init` صادقة؟", "options": ["المراجعة الثابتة بتأكد إن الأوامر متكتوبة؛ ولا تثبت إنها اتنفذت أو عملت مستودع", "كتابة الأمر بتثبت إن المستودع اتعمل", "الإجابة المكتوبة ممكن تحط ملفات حقيقية من أي مشروع", "Git عمره ما بيخزّن أي حاجة على القرص"], "misconception_hint": "مراجعة النص مش زي تنفيذ git؛ صِف الأوامر من غير ما تدّعي إنها اتنفذت."},
            ]},
        },
    },
}


GIT_COMMITTING = {
    "status": "complete",
    "skill_aliases": ("git",),
    "competency": "Committing",
    "objective": "Stage changed files with `git add` and create a `git commit` that records a snapshot and a message.",
    "prerequisites": [{
        "competency": "Local repositories",
        "relationship": "required foundation",
        "why": "A commit records a snapshot inside a repository, so the repository must exist first (for example after `git init`).",
    }, {
        "competency": "git_local_repositories",
        "relationship": "required foundation",
        "why": "A commit records a snapshot inside a repository, so the repository must exist first (for example after `git init`).",
    }],
    "roadmap_rationale": (
        "Committing is the second complete Git topic on the Git roadmap because commits are the unit "
        "of local history: every later Git topic (branching, merging, rebasing, rewriting) operates "
        "on commits, and a commit is the first action that actually records a project change. Local "
        "repositories is its declared prerequisite; the other Git topics remain separately scoped "
        "and are not represented as completed lessons here."
    ),
    "learn": {
        "title": "Committing",
        "explanation": (
            "A **commit** is a snapshot of your staged files, saved with a message that explains the change. "
            "`git add <file>` stages a change (copies it into the staging area), and `git commit -m \"message\"` "
            "records the staged snapshot in the repository's history. `git log` shows the commits made so far. "
            "A commit is local: it needs no remote to exist."
        ),
        "key_ideas": [
            "`git add README.md` stages the README change so it is ready to be committed.",
            "`git commit -m \"Add the project README\"` creates a commit snapshot from the staged files with that message.",
            "`git log` lists the repository's commits, newest first.",
            "A commit is local; pushing it to a remote service is a separate, later step.",
        ],
        "key_terms": {
            "staging area": "A temporary area where changes wait before they are committed.",
            "stage": "To add a change with `git add` so it is ready to be committed.",
            "commit": "A saved snapshot of the staged files, with a message.",
            "commit message": "The short text that says what the change does.",
        },
        "job_relevance": "Developers commit small, focused changes with clear messages so a project's history stays understandable and reviewable.",
        "common_mistake": "Do not skip `git add` and expect `git commit` to include a brand-new file; only staged changes enter the commit.",
        "worked_example": "The example stages the README and commits it with a message, then verifies the commit with `git log`. It is a written example — the commands are not executed by SkillBridge.",
        "depth_note": "Canonical Git foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard `git add`/`git commit`/`git log` syntax. SkillBridge does not run these commands, so it cannot create or verify commits.",
        "grounding_sources": [
            {"title": "Git documentation: git-commit", "url": "https://git-scm.com/docs/git-commit", "source": "Git official documentation"},
            {"title": "Git documentation: git-add", "url": "https://git-scm.com/docs/git-add", "source": "Git official documentation"},
            {"title": "Pro Git book: Recording Changes to the Repository", "url": "https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository", "source": "Git official documentation"},
        ],
    },
    "example": {
        "title": "Commit the project README",
        "type": "bash",
        "content": "git add README.md\ngit commit -m \"Add the project README\"\ngit log",
        "explanation": "This example stages `README.md`, creates a commit that records the staged snapshot with the message `Add the project README`, and then lists history with `git log`. The commands are shown for study — SkillBridge does not execute them or touch any repository.",
    },
    "practice": {
        "type": "practical",
        "title": "Describe making a commit",
        "task": "Write the exact terminal commands you would use to: (1) stage `README.md` so it is ready to be committed, (2) create a commit that records the staged change with the message `Add the project README`, and (3) view the new commit in history with `git log`. Add one short sentence explaining that a commit is a snapshot of the staged files and that this is a written answer — SkillBridge does not run these commands.",
        "response_type": "code",
        "language": "bash",
        "competency": "Committing",
        "starter_code": "git add README.md\ngit commit -m \"Add the project README\"\ngit log",
        "evaluation_note": "SkillBridge performs a static text review only: it checks for a staging command, a `-m` commit with the expected message, `git log`, and an explanation that this is a written answer rather than a run command. It does not run git or create a commit, so the review cannot prove a commit exists.",
    },
    "mini_check": {"questions": [
        {"id": "c1", "type": "mcq", "question": "Which command makes `README.md` ready to be committed?", "options": ["git add README.md", "git commit -m \"done\"", "git log", "git init"], "correct_answer": "git add README.md", "competency": "Committing", "difficulty": "beginner", "misconception_hint": "Before a commit, a change must first be staged with `git add`."},
        {"id": "c2", "type": "mcq", "question": "What does `git commit -m \"Add the project README\"` create?", "options": ["A commit: a snapshot of the staged files with that message", "A copy of the folder on GitHub", "A new branch", "A list of every file in the folder"], "correct_answer": "A commit: a snapshot of the staged files with that message", "competency": "Committing", "difficulty": "beginner", "misconception_hint": "A commit records the staged snapshot and its message into the local history."},
        {"id": "c3", "type": "mcq", "question": "Which statement about a written `git commit` answer is honest?", "options": ["A static review shows the commands are written down; it does not prove a commit was created in a repository", "Writing the command creates the commit automatically", "SkillBridge runs the commit when the answer is submitted", "A commit needs no message"], "correct_answer": "A static review shows the commands are written down; it does not prove a commit was created in a repository", "competency": "Committing", "difficulty": "beginner", "misconception_hint": "SkillBridge reviews text only; it does not run git or create commits."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "عمل الـ Commits",
                "explanation": "الـ commit هو لقطة من ملفاتك اللي اتعمل لها stage، متحفظة برسالة بتشرح التغيير. `git add <file>` بيعمل stage للتغيير (بينسخه لمنطقة staging)، و`git commit -m \"رسالة\"` بيسجل اللقطة الجاهزة في تاريخ المستودع. `git log` بيعرض الـ commits اللي اتعملت لحد دلوقتي. الـ commit محلي: مش محتاج خدمة بعيدة عشان يبقى موجوداً.",
                "key_ideas": ["`git add README.md` بيعمل stage لتغيير الـ README عشان يبقى جاهز للـ commit.", "`git commit -m \"Add the project README\"` بيعمل لقطة commit من الملفات اللي اتعمل لها stage وبرسالة زي دي.", "`git log` بيعرض commits المستودع، الأحدث الأول.", "الـ commit محلي؛ رفعه على خدمة بعيدة خطوة منفصلة ولاحقة."],
                "key_terms": {"منطقة staging": "منطقة مؤقتة بيستنى فيها التغييرات قبل ما تتعمل commit.", "stage": "إضافة تغيير بـ `git add` عشان يبقى جاهز للـ commit.", "commit": "لقطة محفوظة للملفات المرحّلة مع رسالة.", "رسالة commit": "النص القصير اللي بيوضح التغيير بيعمل إيه."},
                "job_relevance": "المطورون بيعملوا commits صغيرة ومركّزة برسائل واضحة عشان تاريخ المشروع يفضل مفهوم وسهل للمراجعة.",
                "common_mistake": "ما تتخطاش خطوة `git add` وتتوقع إن `git commit` يضيف ملف جديد؛ الملفات المرحّلة بس هي اللي بتدخل في الـ commit.",
                "worked_example": "المثال بيعمل stage للـ README وcommit برسالة وبعدين بيتحقق بـ `git log`. ده مثال مكتوب — SkillBridge لا ينفذ هذه الأوامر.",
                "depth_note": "محتوى تأسيسي ثابت لـ Git من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة `git add`/`git commit`/`git log` القياسية. SkillBridge لا ينفذ هذه الأوامر فلا يقدر يعمل أو يتحقق من commits.",
            },
            "example": {"title": "اعمل commit للـ README", "type": "bash", "content": "git add README.md\ngit commit -m \"Add the project README\"\ngit log", "explanation": "المثال بيعمل stage للملف `README.md`، وبعدين بيعمل commit يسجل اللقطة برسالة `Add the project README`، وبعدين بيعرض التاريخ بـ `git log`. الأوامر معروضة للشرح — SkillBridge لا ينفذها ولا يلمس أي مستودع."},
            "practice": {"title": "اشرح عمل commit", "task": "اكتب بالظبط أوامر الطرفية اللي هتستخدمها لـ: (1) عمل stage للملف `README.md` عشان يبقى جاهز للـ commit، و(2) عمل commit يسجل التغيير المرحّل برسالة `Add the project README`، و(3) عرض الـ commit الجديد في التاريخ بـ `git log`. أضف جملة قصيرة تشرح إن الـ commit لقطة من الملفات المرحّلة وإن ده إجابة مكتوبة — SkillBridge لا ينفذ هذه الأوامر.", "response_type": "code", "language": "bash", "competency": "Committing", "starter_code": "git add README.md\ngit commit -m \"Add the project README\"\ngit log", "evaluation_note": "SkillBridge بيعمل مراجعة ثابتة للنص فقط: بيتأكد من أمر staging وأمر commit بـ `-m` بالرسالة المتوقعة وأمر `git log` ومن إن الإجابة مكتوبة مش منفّذة. لا ينفذ git ولا يعمل commit، لذلك المراجعة لا تثبت وجود commit."},
            "mini_check": {"questions": [
                {"id": "c1", "question": "أي أمر بيخلي `README.md` جاهز للـ commit؟", "options": ["git add README.md", "git commit -m \"done\"", "git log", "git init"], "misconception_hint": "قبل أي commit، التغيير لازم لأول مرة يتعمل له stage بـ `git add`."},
                {"id": "c2", "question": "`git commit -m \"Add the project README\"` بيعمل إيه؟", "options": ["Commit: لقطة من الملفات المرحّلة بالرسالة دي", "نسخة من المجلد على GitHub", "فرع جديد", "قائمة بكل ملف في المجلد"], "misconception_hint": "الـ commit بيسجل اللقطة المرحّلة ورسالتها في التاريخ المحلي."},
                {"id": "c3", "question": "أي جملة عن إجابة مكتوبة فيها `git commit` صادقة؟", "options": ["المراجعة الثابتة بتوريك إن الأوامر متكتوبة؛ وهي مش بتثبت إن commit اتعمل داخل مستودع", "كتابة الأمر بتعمل commit تلقائياً", "SkillBridge بينفذ الـ commit لما تتبعت الإجابة", "الـ commit مش محتاج رسالة"], "misconception_hint": "SkillBridge بيراجع النص بس؛ ولا بينفذ git ولا بيعمل commits."},
            ]},
        },
    },
}


GIT_BRANCHING = {
    "status": "complete",
    "skill_aliases": ("git",),
    "competency": "Branching",
    "objective": "Create local branches with `git branch`, switch to them with `git switch`, and inspect the branch state with `git status` and `git branch --list`.",
    "prerequisites": [{
        "competency": "Committing",
        "relationship": "required foundation",
        "why": "A branch is a named line of commits, so the repository must already have commits made on a branch before a new branch is meaningful.",
    }, {
        "competency": "git_committing",
        "relationship": "required foundation",
        "why": "A branch is a named line of commits, so the repository must already have commits made on a branch before a new branch is meaningful.",
    }],
    "roadmap_rationale": (
        "Branching is the third complete Git topic on the Git roadmap because a single "
        "chronological line of commits becomes too rigid once work happens in parallel: "
        "branches let each feature develop separately, and they are the direct prerequisite "
        "for Merging, the next complete topic. Local repositories and Committing are its "
        "foundations; the remaining Git topics stay separately scoped and are not represented "
        "as completed lessons here."
    ),
    "learn": {
        "title": "Branching",
        "explanation": (
            "A **branch** is a separate line of work in your repository. `git branch feature-payment` "
            "creates a branch named `feature-payment` but stays where you are; `git switch feature-payment` "
            "makes that branch the current branch and updates the working tree to its files. `git status` "
            "shows the branch you are on, and `git branch --list` lists every local branch with a `*` before "
            "the current one. Creating a branch is a local, lightweight action: nothing is shared with a "
            "remote yet."
        ),
        "key_ideas": [
            "`git branch feature-payment` creates a local branch named `feature-payment`; HEAD still points to the current branch until you switch.",
            "`git switch feature-payment` makes that branch the current branch and updates the working tree to its files.",
            "`git status` reports the current branch on its first line.",
            "`git branch --list` (or `git branch`) lists local branches and marks the current one with `*`.",
        ],
        "key_terms": {
            "branch": "A named line of work that points to a commit and moves as new commits land on it.",
            "current branch": "The branch Git uses for `git commit`; the one checked out in the working tree.",
            "HEAD": "A reference that names the current branch or commit.",
            "switch": "To select a branch with `git switch` so your work happens there.",
        },
        "job_relevance": "Developers create a short-lived branch per feature or fix so work stays isolated, then switch between branches to review and integrate them.",
        "common_mistake": "Do not expect `git branch X` to move you onto the new branch; creation and switching are separate steps (`git branch`, then `git switch`).",
        "worked_example": "The example creates a feature branch, switches to it, and then inspects the branch state with `git status` and `git branch --list`. It is a written example — the commands are not executed by SkillBridge.",
        "depth_note": "Canonical Git foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard `git branch`/`git switch`/`git status` syntax. SkillBridge does not run these commands, install Git, or create branches on the learner's machine.",
        "grounding_sources": [
            {"title": "Git documentation: git-branch", "url": "https://git-scm.com/docs/git-branch", "source": "Git official documentation"},
            {"title": "Git documentation: git-switch", "url": "https://git-scm.com/docs/git-switch", "source": "Git official documentation"},
            {"title": "Pro Git book: Branches in a Nutshell", "url": "https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell", "source": "Git official documentation"},
        ],
    },
    "example": {
        "title": "Create and switch to a feature branch",
        "type": "bash",
        "content": "git branch feature-payment\ngit switch feature-payment\ngit status\ngit branch --list",
        "explanation": "This example creates the local branch `feature-payment` (without switching), then switches onto it and inspects the branch state with `git status` and `git branch --list`. The commands are shown for study — SkillBridge does not execute them.",
    },
    "practice": {
        "type": "practical",
        "title": "Describe branching work started locally",
        "task": "Write the exact terminal commands you would use to: (1) create a new local branch named `feature-payment`, (2) switch to that branch, (3) inspect the current branch state with `git status`, and (4) list the repository's local branches with `git branch --list`. Add one short sentence explaining that `git branch` creates a branch without switching to it and that this is a written answer — SkillBridge does not run these commands.",
        "response_type": "code",
        "language": "bash",
        "competency": "Branching",
        "starter_code": "git branch feature-payment\ngit switch feature-payment\ngit status\ngit branch --list",
        "evaluation_note": "SkillBridge performs a static text review only: it checks for branch creation, switching onto the branch, branch-state inspection, and an explanation that this is a written answer rather than a run command. It does not run git or create a branch, so the review cannot prove a branch exists.",
    },
    "mini_check": {"questions": [
        {"id": "b1", "type": "mcq", "question": "Which command creates a new local branch named `feature-payment`?", "options": ["git branch feature-payment", "git switch feature-payment", "git commit -m \"feature-payment\"", "git status"], "correct_answer": "git branch feature-payment", "competency": "Branching", "difficulty": "beginner", "misconception_hint": "`git branch <name>` creates the branch; it does not switch onto it."},
        {"id": "b2", "type": "mcq", "question": "Which command makes `feature-payment` the current branch?", "options": ["git switch feature-payment", "git branch feature-payment", "git status", "git log"], "correct_answer": "git switch feature-payment", "competency": "Branching", "difficulty": "beginner", "misconception_hint": "You switch onto a branch with `git switch`, which also updates the working tree to its files."},
        {"id": "b3", "type": "mcq", "question": "Which statement about a written `git branch` answer is honest?", "options": ["A static review shows the commands are written down; it does not prove a branch was created", "Writing the command creates the branch on the learner's machine", "SkillBridge runs the command when the answer is submitted", "Branches only exist on GitHub"], "correct_answer": "A static review shows the commands are written down; it does not prove a branch was created", "competency": "Branching", "difficulty": "beginner", "misconception_hint": "SkillBridge reviews text only; it does not run git or create branches."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "الفروع (Branching)",
                "explanation": "الـ **فرع (branch)** هو خط عمل منفصل جوه مستودعك. `git branch feature-payment` بيعمل فرع اسمه `feature-payment` بس بيفضل مكانك؛ و`git switch feature-payment` بيخلي الفرع ده هو الفرع الحالي ويحدّث شجرة العمل بملفاته. `git status` بيعرض الفرع اللي إنت عليه، و`git branch --list` بيلست كل الفروع المحلية مع `*` قدام الفرع الحالي. عمل الفرع حاجة محلية وخفيفة: لا حاجة بتتشارك مع خدمة بعيدة لسه.",
                "key_ideas": ["`git branch feature-payment` بيعمل فرع محلي اسمه `feature-payment`؛ وHEAD لسه ماسك الفرع الحالي لحد ما تعمل switch.", "`git switch feature-payment` بيخلي الفرع ده هو الفرع الحالي ويحدّث شجرة العمل بملفاته.", "`git status` بيعرض الفرع الحالي في أول سطر.", "`git branch --list` (أو `git branch`) بيلست الفروع المحلية ويعلّم الفرع الحالي بـ `*`."],
                "key_terms": {"فرع": "خط عمل مسّمي بيشاور على commit ويتحرك مع الـ commits الجديدة اللي بتتنزل عليه.", "الفرع الحالي": "الفرع اللي Git بيستخدمو في `git commit`؛ واللي متشيك أوت في شجرة العمل.", "HEAD": "مرجع بيسمّي الفرع أو الـ commit الحالي.", "switch": "اختيار فرع بـ `git switch` عشان شغلك يحصل هناك."},
                "job_relevance": "المطورون بيعملوا فرع قصير العمر لكل feature أو fix عشان الشغل يفضل معزول، وبعدين بيعملوا switch بين الفروع للمراجعة والدمج.",
                "common_mistake": "ما تتوقعش إن `git branch X` بينقلك على الفرع الجديد؛ إنشاء الفرع والتحويل ليه خطوتان منفصلتان (`git branch` وبعدين `git switch`).",
                "worked_example": "المثال بيعمل فرع feature، وبيعمل switch ليه، وبعدين بيفحص حالة الفرع بـ `git status` و`git branch --list`. ده مثال مكتوب — SkillBridge لا ينفذ هذه الأوامر.",
                "depth_note": "محتوى تأسيسي ثابت لـ Git من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة `git branch`/`git switch`/`git status` القياسية. SkillBridge لا ينفذ هذه الأوامر ولا يثبّت Git ولا يعمل فروعاً على جهاز المتعلم.",
            },
            "example": {"title": "اعمل فرع feature وحوّل ليه", "type": "bash", "content": "git branch feature-payment\ngit switch feature-payment\ngit status\ngit branch --list", "explanation": "المثال بيعمل الفرع المحلي `feature-payment` (من غير ما يحوّل ليه)، وبعدين بيعمل switch عليه ويفحص حالة الفرع بـ `git status` و`git branch --list`. الأوامر معروضة للشرح — SkillBridge لا ينفذها."},
            "practice": {"title": "اشرح بدء شغل محلي على فرع", "task": "اكتب بالظبط أوامر الطرفية اللي هتستخدمها لـ: (1) عمل فرع محلي جديد اسمه `feature-payment`، و(2) التحويل للفرع ده، و(3) فحص حالة الفرع الحالي بـ `git status`، و(4) عرض فروع المستودع المحلية بـ `git branch --list`. أضف جملة قصيرة تشرح إن `git branch` بيعمل فرع من غير ما يحوّل ليه وإن ده إجابة مكتوبة — SkillBridge لا ينفذ هذه الأوامر.", "response_type": "code", "language": "bash", "competency": "Branching", "starter_code": "git branch feature-payment\ngit switch feature-payment\ngit status\ngit branch --list", "evaluation_note": "SkillBridge بيعمل مراجعة ثابتة للنص فقط: بيتأكد من إنشاء الفرع والتحويل ليه وفحص حالة الفرع ومن إن الإجابة مكتوبة مش منفّذة. لا ينفذ git ولا يعمل فرعاً، لذلك المراجعة لا تثبت وجود فرع."},
            "mini_check": {"questions": [
                {"id": "b1", "question": "أي أمر بيعمل فرع محلي جديد اسمه `feature-payment`؟", "options": ["git branch feature-payment", "git switch feature-payment", "git commit -m \"feature-payment\"", "git status"], "misconception_hint": "`git branch <الاسم>` بيعمل الفرع؛ وهو مش بيحوّل ليه."},
                {"id": "b2", "question": "أي أمر بيخلي `feature-payment` هو الفرع الحالي؟", "options": ["git switch feature-payment", "git branch feature-payment", "git status", "git log"], "misconception_hint": "بتتحول لفرع بـ `git switch`، واللي بيحدّث شجرة العمل بملفات الفرع كمان."},
                {"id": "b3", "question": "أي جملة عن إجابة مكتوبة فيها `git branch` صادقة؟", "options": ["المراجعة الثابتة بتوريك إن الأوامر متكتوبة؛ وهي مش بتثبت إن فرع اتعمل", "كتابة الأمر بتعمل فرع على جهاز المتعلم", "SkillBridge بينفذ الأمر لما تتبعت الإجابة", "الفروع بتبقى موجوده على GitHub بس"], "misconception_hint": "SkillBridge بيراجع النص بس؛ ولا بينفذ git ولا بيعمل فروعاً."},
            ]},
        },
    },
}


GIT_MERGING = {
    "status": "complete",
    "skill_aliases": ("git",),
    "competency": "Merging",
    "objective": "Describe integrating a branch with `git merge`, recognize merge conflicts from their markers, and explain safe conflict resolution without ever running a merge.",
    "prerequisites": [{
        "competency": "Branching",
        "relationship": "required foundation",
        "why": "A merge joins branches, so the learner must first know how branches are created and switched between.",
    }, {
        "competency": "git_branching",
        "relationship": "required foundation",
        "why": "A merge joins branches, so the learner must first know how branches are created and switched between.",
    }],
    "roadmap_rationale": (
        "Merging is the fourth complete Git topic on the Git roadmap and the first Intermediate "
        "topic: it joins parallel branches back together and introduces conflicts — the first place "
        "Git asks the developer to make an explicit judgement call. Branching is its declared "
        "prerequisite; the remaining Git topics (Rebasing and beyond) stay separately scoped and are "
        "not represented as completed lessons here."
    ),
    "learn": {
        "title": "Merging",
        "explanation": (
            "A **merge** integrates the commits of one branch into the branch you are currently on. "
            "After work happens on both `main` and `feature-payment`, `git switch main` then "
            "`git merge feature-payment` brings the feature commits into `main`. If the branches "
            "changed different lines, Git integrates them automatically (a fast-forward just moves "
            "the current branch forward when there are no diverging commits). If both branches changed "
            "the same lines, Git pauses and reports a **merge conflict**, marking the file with "
            "`<<<<<<<`, `=======` and `>>>>>>>` sections. Resolve a conflict by reading both sides, "
            "editing the file to keep the correct lines, then `git add <file>` and finish the commit "
            "(or `git merge --continue`). A static review never runs a real merge and can never "
            "overwrite files or modify a repository."
        ),
        "key_ideas": [
            "`git merge feature-payment` integrates the feature branch's commits into the current branch.",
            "A fast-forward merge moves the current branch forward with no extra commit when the histories have not diverged.",
            "A conflict appears when both branches changed the same lines; Git pauses the merge and marks the file with `<<<<<<<`/`=======`/`>>>>>>>`.",
            "Safe resolution: read both sides, keep the correct lines, stage with `git add`, then finish the commit — never overwrite the file or keep one side blindly.",
        ],
        "key_terms": {
            "merge": "The action of joining another branch's commits into the current branch.",
            "fast-forward": "A merge that moves the current branch pointer forward with no extra commit because history has not diverged.",
            "conflict": "A stop state where both branches edited the same lines and Git asks the developer to choose.",
            "conflict markers": "The `<<<<<<<`, `=======` and `>>>>>>>` lines Git adds around the clashing regions of a file.",
        },
        "job_relevance": "Developers merge reviewed feature branches back to `main` routinely; handling a conflict safely — and never force-overwriting a file — is a core team skill.",
        "common_mistake": "Do not resolve a conflict by deleting everything or overwriting the file without reading both sides; instead `git status` shows the conflicted files so each one can be edited deliberately.",
        "worked_example": "The example switches to `main`, merges `feature-payment`, and then shows the combined history with `git log`. It is a written example — the commands are not executed by SkillBridge.",
        "depth_note": "Canonical Git foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard `git switch`/`git merge`/`git log` syntax. SkillBridge does not run these commands, so it never performs a merge, overwrites files, or changes any repository.",
        "grounding_sources": [
            {"title": "Git documentation: git-merge", "url": "https://git-scm.com/docs/git-merge", "source": "Git official documentation"},
            {"title": "Pro Git book: Basic Branching and Merging", "url": "https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging", "source": "Git official documentation"},
            {"title": "Pro Git book: Advanced Merging", "url": "https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging", "source": "Git official documentation"},
        ],
    },
    "example": {
        "title": "Merge a feature branch back into main",
        "type": "bash",
        "content": "git switch main\ngit merge feature-payment\ngit log",
        "explanation": "This example switches onto `main`, merges `feature-payment` into it (if the branches diverged, Git either integrates automatically or reports a conflict for the learner to resolve), and then shows the combined history with `git log`. The commands are shown for study — SkillBridge does not execute them or modify any repository.",
    },
    "practice": {
        "type": "practical",
        "title": "Describe merging a feature branch into main",
        "task": "Write the exact terminal commands you would use to: (1) switch to `main`, (2) merge the `feature-payment` branch into `main`, and (3) view the combined history with `git log`. Add one short sentence describing what happens when both branches changed the same lines (Git reports a conflict with `<<<<<<<`/`=======`/`>>>>>>>` markers; you edit the lines, stage them with `git add`, then finish the commit) and note that this is a written answer — SkillBridge does not run the merge or change any repository.",
        "response_type": "code",
        "language": "bash",
        "competency": "Merging",
        "starter_code": "git switch main\ngit merge feature-payment\ngit log",
        "evaluation_note": "SkillBridge performs a static text review only: it checks for switching to `main`, the merge command, `git log`, a safe conflict-resolution note, and an explanation that this is a written answer. It does not run a merge, overwrite files, or modify any repository, so the review cannot prove the merge happened.",
    },
    "mini_check": {"questions": [
        {"id": "m1", "type": "mcq", "question": "Which command integrates the commits of `feature-payment` into the current branch?", "options": ["git merge feature-payment", "git branch feature-payment", "git switch feature-payment", "git status"], "correct_answer": "git merge feature-payment", "competency": "Merging", "difficulty": "intermediate", "misconception_hint": "`git merge <branch>` joins that branch into the branch you are currently on."},
        {"id": "m2", "type": "mcq", "question": "What do the `<<<<<<<`, `=======`, and `>>>>>>>` markers indicate?", "options": ["A merge conflict in the file", "That a new branch was created", "That a fast-forward completed", "That the repository has no commits"], "correct_answer": "A merge conflict in the file", "competency": "Merging", "difficulty": "intermediate", "misconception_hint": "The markers bracket the two conflicting sides; Git pauses the merge so you can choose the correct lines."},
        {"id": "m3", "type": "mcq", "question": "What is the honest capability of a static review of a merge command?", "options": ["It reviews the written commands and does not prove a real merge ran or a repository changed", "It performs the merge on the learner's computer", "It overwrites files automatically", "It resolves conflicts without reading the code"], "correct_answer": "It reviews the written commands and does not prove a real merge ran or a repository changed", "competency": "Merging", "difficulty": "intermediate", "misconception_hint": "SkillBridge reviews text only; it never runs a merge, overwrites files, or modifies a repository."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "الدمج (Merging)",
                "explanation": "الـ **دمج (merge)** بيوحّد commits فرع معين مع الفرع اللي إنت عليه حالياً. بعد ما الشغل يحصل على `main` و`feature-payment`، إنك تعمل `git switch main` وبعدين `git merge feature-payment` بيجيب commits الفيجر داخل `main`. لو الفروع عدّلت أسطر مختلفة، Git بيدمجهم تلقائياً (الـ fast-forward ببساطة بيحرّك الفرع الحالي قدام من غير commit إضافي لما ميكونش في تفرع). لو الفرعين عدّلوا نفس الأسطر، Git بيوقف ويعلن عن **تضارب دمج (merge conflict)**، ويعلم الملف بأجزاء `<<<<<<<` و`=======` و`>>>>>>>`. حل التضارب: اقرأ الطرفين، عدّل الملف عشان تفضل الأسطر الصح، وبعدين `git add <file>` وكمل الـ commit (أو `git merge --continue`). المراجعة الثابتة لا تنفذ أبداً دمجاً حقيقياً ولا تقدر تكتب على ملفات أو تعدّل أي مستودع.",
                "key_ideas": ["`git merge feature-payment` بيوحّد commits فرع الفيجر مع الفرع الحالي.", "الـ merge اللي من نوع fast-forward بيمشي الفرع الحالي قدام من غير commit إضافي لما ميكونش التاريخ اتفرع.", "التضارب بيظهر لما الفرعين يعدّلوا نفس الأسطر؛ Git بيوقف الدمج ويعلّم الملف بأجزاء `<<<<<<<`/`=======`/`>>>>>>>`.", "الحل الآمن: اقرأ الطرفين، سيب الأسطر الصح، اعمل stage بـ `git add`، وبعدين كمل الـ commit — عمرك ما تكتب على الملف أو تختار طرف واحد من غير تفكير."],
                "key_terms": {"دمج": "إجراء ضم commits فرع آخر للفرع الحالي.", "fast-forward": "دمج بيحرّك مؤشر الفرع الحالي قدام من غير commit إضافي لأن التاريخ مش متفرع.", "تضارب": "حالة توقف فيها الفرعين يعدّلوا نفس الأسطر وGit بيتطلب من المطوّر يختار.", "علامات التضارب": "الأسطر `<<<<<<<` و`=======` و`>>>>>>>` اللي Git بيعملها حوالين مناطق التعارض في الملف."},
                "job_relevance": "المطورون بيدمجوا فروع الفيجرز اللي اتراجع عليها في `main` بشكل روتيني؛ والتعامل مع التضارب بأمان — من غير ما يفرض الكتابة على ملف — مهارة فريق أساسية.",
                "common_mistake": "ما تحلش التضارب بحذف كل حاجة أو بالكتابة على الملف من غير ما تقرأ الطرفين؛ بدلاً من كده `git status` بيعرض الملفات المتنازع عليها عشان تتحرر كل واحد بتأني.",
                "worked_example": "المثال بيعمل switch لـ `main`، وبعدين دمج `feature-payment`، وبعدين بيعرض التاريخ المدمج بـ `git log`. ده مثال مكتوب — SkillBridge لا ينفذ هذه الأوامر.",
                "depth_note": "محتوى تأسيسي ثابت لـ Git من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة `git switch`/`git merge`/`git log` القياسية. SkillBridge لا ينفذ هذه الأوامر، لذلك لا ينفذ أبداً دمجاً ولا يكتب على ملفات ولا يعدّل أي مستودع.",
            },
            "example": {"title": "ادمج فرع الفيجر راجع في main", "type": "bash", "content": "git switch main\ngit merge feature-payment\ngit log", "explanation": "المثال بيعمل switch على `main`، وبعدين بيدمج `feature-payment` جواه (لو الفرعين اتفرقوا، Git بيندمج تلقائياً أو بيعلن عن تضارب للمتعلم يحله)، وبعدين بيعرض التاريخ المدمج بـ `git log`. الأوامر معروضة للشرح — SkillBridge لا ينفذها ولا يعدّل أي مستودع."},
            "practice": {"title": "اشرح دمج فرع في main", "task": "اكتب بالظبط أوامر الطرفية اللي هتستخدمها لـ: (1) التحويل لـ `main`، و(2) دمج فرع `feature-payment` جوه `main`، و(3) عرض التاريخ المدمج بـ `git log`. أضف جملة قصيرة بتوصف اللي بيحصل لما الفرعين يعدّلوا نفس الأسطر (Git بيعلن عن تضارب بعلامات `<<<<<<<`/`=======`/`>>>>>>>`؛ وإنت بتعدّل الأسطر، تعمل لها stage بـ `git add`، وبعدين تكمل الـ commit) ولاحظ إن دي إجابة مكتوبة — SkillBridge لا ينفذ الدمج ولا يعدّل أي مستودع.", "response_type": "code", "language": "bash", "competency": "Merging", "starter_code": "git switch main\ngit merge feature-payment\ngit log", "evaluation_note": "SkillBridge بيعمل مراجعة ثابتة للنص فقط: بيتأكد من التحويل لـ `main` وأمر الدمج وأمر `git log` وملاحظة حل التضارب الآمن ومن إن الإجابة مكتوبة. لا ينفذ دمجاً ولا يكتب على ملفات ولا يعدّل أي مستودع، لذلك المراجعة لا تثبت إن الدمج حصل."},
            "mini_check": {"questions": [
                {"id": "m1", "question": "أي أمر بيوحّد commits فرع `feature-payment` مع الفرع الحالي؟", "options": ["git merge feature-payment", "git branch feature-payment", "git switch feature-payment", "git status"], "misconception_hint": "`git merge <الفرع>` بيضم الفرع ده للفرع اللي إنت عليه حالياً."},
                {"id": "m2", "question": "العلامات `<<<<<<<` و`=======` و`>>>>>>>` بتدل على إيه؟", "options": ["تضارب دمج جوه الملف", "إن فرع جديد اتعمل", "إن fast-forward خلص", "إن المستودع من غير commits"], "misconception_hint": "العلامات بيحصرون الطرفين المتنازعين؛ Git بيوقف الدمج عشان تختار الأسطر الصح."},
                {"id": "m3", "question": "أيه هي قدرة المراجعة الثابتة الصادقة لأمر دمج؟", "options": ["بيراجع الأوامر المكتوبة ومش بيثبت إن دمج حقيقي حصل أو مستودع اتغيّر", "بينفذ الدمج على جهاز المتعلم", "بيكتب على الملفات تلقائياً", "بيحل التضاربات من غير ما يقرأ الكود"], "misconception_hint": "SkillBridge بيراجع النص بس؛ عمره ما بينفذ دمج أو يكتب على ملفات أو يعدّل مستودع."},
            ]},
        },
    },
}


GIT_REBASING = {
    "status": "complete",
    "skill_aliases": ("git",),
    "competency": "Rebasing",
    "objective": "Describe how `git rebase` replays commits onto a new base, how it differs from merging, and when rewriting shared history is unsafe.",
    "prerequisites": [{
        "competency": "Merging",
        "relationship": "required foundation",
        "why": "Rebasing is an alternative to merging that replays commits, so the learner must first understand how merges integrate branches and where conflicts come from.",
    }, {
        "competency": "git_merging",
        "relationship": "required foundation",
        "why": "Rebasing is an alternative to merging that replays commits, so the learner must first understand how merges integrate branches and where conflicts come from.",
    }],
    "roadmap_rationale": (
        "Rebasing is the fifth complete Git topic on the Git roadmap because it is the standard "
        "way to keep a feature branch current with `main` before merging: it replays commits for a "
        "linear history instead of joining histories with a merge commit. Merging is its declared "
        "prerequisite; Remotes & collaboration is the next complete topic, and the remaining Git "
        "topics stay separately scoped and are not represented as completed lessons here."
    ),
    "learn": {
        "title": "Rebasing",
        "explanation": (
            "A **rebase** moves your branch's commits so they sit on top of another branch's latest "
            "commit, producing a straight, linear history. `git switch feature-payment` then "
            "`git rebase main` replays each feature commit onto the tip of `main`, one by one. Unlike "
            "`git merge`, which joins two histories with a merge commit, `git rebase` **rewrites** the "
            "feature branch's commits as new commits. If a replayed commit conflicts with the base, Git "
            "pauses; you resolve it like a merge conflict (edit the file, `git add`, then "
            "`git rebase --continue`). Because rebase rewrites commits, it is unsafe on commits already "
            "shared with others — never rebase history that teammates have pulled."
        ),
        "key_ideas": [
            "`git rebase main` replays the current branch's commits onto the tip of `main`, one at a time.",
            "Merge joins histories with a merge commit; rebase rewrites the branch's commits for a linear history.",
            "A rebase can pause on conflicts; resolve the file, `git add`, then `git rebase --continue`.",
            "Never rebase commits that have been pushed and shared — rewriting shared history breaks collaborators' repositories.",
        ],
        "key_terms": {
            "rebase": "Replaying a branch's commits onto a new base commit, rewriting them as new commits.",
            "linear history": "A straight line of commits with no merge commits joining branches.",
            "replay": "Re-applying commits one by one on top of a new base.",
            "shared history": "Commits that have been pushed and that other people may have based work on.",
        },
        "job_relevance": "Developers rebase a feature branch onto `main` before merging so reviews read as a clean, linear story — but only on commits that have not been shared.",
        "common_mistake": "Do not rebase a branch that has already been pushed to a shared remote; rewriting shared history forces every collaborator to reconcile the rewritten commits.",
        "worked_example": "The example switches to the feature branch, rebases it onto `main`, and then shows the resulting linear history with `git log`. It is a written example — the commands are not executed by SkillBridge.",
        "depth_note": "Canonical Git foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard `git switch`/`git rebase`/`git log` syntax. SkillBridge does not run these commands, so it never performs a rebase or rewrites any repository's history.",
        "grounding_sources": [
            {"title": "Git documentation: git-rebase", "url": "https://git-scm.com/docs/git-rebase", "source": "Git official documentation"},
            {"title": "Pro Git book: Rebasing", "url": "https://git-scm.com/book/en/v2/Git-Branching-Rebasing", "source": "Git official documentation"},
            {"title": "Pro Git book: Basic Branching and Merging", "url": "https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging", "source": "Git official documentation"},
        ],
    },
    "example": {
        "title": "Rebase a feature branch onto main",
        "type": "bash",
        "content": "git switch feature-payment\ngit rebase main\ngit log",
        "explanation": "This example switches onto `feature-payment`, rebases its commits onto the tip of `main` (pausing for conflicts if any replayed commit clashes), and then shows the resulting linear history with `git log`. The commands are shown for study — SkillBridge does not execute them or rewrite any repository's history.",
    },
    "practice": {
        "type": "practical",
        "title": "Describe rebasing a feature branch onto main",
        "task": "Write the exact terminal commands you would use to: (1) switch to `feature-payment`, (2) rebase the branch onto `main`, and (3) view the resulting linear history with `git log`. Add one short sentence explaining how rebase differs from merge and why you must never rebase commits that have already been shared, and note that this is a written answer — SkillBridge does not run the rebase or rewrite any repository's history.",
        "response_type": "code",
        "language": "bash",
        "competency": "Rebasing",
        "starter_code": "git switch feature-payment\ngit rebase main\ngit log",
        "evaluation_note": "SkillBridge performs a static text review only: it checks for switching to the feature branch, the rebase command, `git log`, a rebase-vs-merge / shared-history safety note, and an explanation that this is a written answer. It does not run a rebase or rewrite any repository's history, so the review cannot prove a rebase happened.",
    },
    "mini_check": {"questions": [
        {"id": "r1", "type": "mcq", "question": "What does `git rebase main` do?", "options": ["Replays the current branch's commits onto the tip of main", "Joins two histories with a merge commit", "Deletes the current branch", "Pushes the branch to the remote"], "correct_answer": "Replays the current branch's commits onto the tip of main", "competency": "Rebasing", "difficulty": "intermediate", "misconception_hint": "Rebase re-applies commits one by one on top of a new base instead of joining histories."},
        {"id": "r2", "type": "mcq", "question": "How does rebase differ from merge?", "options": ["Rebase rewrites the branch's commits for a linear history; merge joins histories with a merge commit", "Rebase only works on remotes; merge only works locally", "Merge rewrites commits; rebase never changes commits", "They are two names for the same operation"], "correct_answer": "Rebase rewrites the branch's commits for a linear history; merge joins histories with a merge commit", "competency": "Rebasing", "difficulty": "intermediate", "misconception_hint": "Both integrate branches, but one creates a merge commit and the other rewrites commits."},
        {"id": "r3", "type": "mcq", "question": "When is rebasing unsafe?", "options": ["On commits that have already been pushed and shared with others", "On a local branch with a single commit", "Before the first commit of a repository", "When the working tree is clean"], "correct_answer": "On commits that have already been pushed and shared with others", "competency": "Rebasing", "difficulty": "intermediate", "misconception_hint": "Rewriting history is only safe for commits nobody else has based work on."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "إعادة التأسيس (Rebasing)",
                "explanation": "الـ **rebase** بينقل commits الفرع بتاعك عشان تيجي فوق آخر commit في فرع تاني، وده بيديك تاريخ خطي مستقيم. `git switch feature-payment` وبعدين `git rebase main` بيعيد تشغيل كل commit في الفيجر فوق رأس `main` واحد واحد. على عكس `git merge` اللي بيدمج تاريخين بـ merge commit، الـ `git rebase` **بيعيد كتابة** commits الفرع كـ commits جديدة. لو commit معاد تشغيله بيتضارب مع القاعدة، Git بيوقف؛ وإنت بتحلها زي تضارب الدمج (تعدّل الملف، `git add`، وبعدين `git rebase --continue`). ولأن الـ rebase بيعيد كتابة الـ commits، فهو غير آمن على commits اتشاركت مع غيرك — عمرك ما تعمل rebase لتاريخ زمايلك سحبوه.",
                "key_ideas": ["`git rebase main` بيعيد تشغيل commits الفرع الحالي فوق رأس `main` واحد واحد.", "الـ merge بيدمج التاريخين بـ merge commit؛ الـ rebase بيعيد كتابة commits الفرع عشان تاريخ خطي.", "الـ rebase ممكن يوقف على تضاربات؛ حل الملف، `git add`، وبعدين `git rebase --continue`.", "عمرك ما تعمل rebase لـ commits اتدفعت واتشاركت — إعادة كتابة التاريخ المشترك بتكسر مستودعات المتعاونين."],
                "key_terms": {"rebase": "إعادة تشغيل commits فرع على قاعدة commit جديدة، وإعادة كتابتها كـ commits جديدة.", "تاريخ خطي": "خط مستقيم من الـ commits من غير merge commits بتدمج الفروع.", "إعادة تشغيل": "إعادة تطبيق الـ commits واحد واحد فوق قاعدة جديدة.", "تاريخ مشترك": "Commits اتدفعت وناس تانية ممكن تكون بنت شغلها عليها."},
                "job_relevance": "المطورون بيعملوا rebase لفرع الفيجر على `main` قبل الدمج عشان المراجعة تقرأ كقصة نظيفة وخطية — بس على commits لسه ما اتشاركتش.",
                "common_mistake": "ما تعملش rebase لفرع اتدفع بالفعل على remote مشترك؛ إعادة كتابة التاريخ المشترك بتجبر كل متعاون يوفّق الـ commits المعاد كتابتها.",
                "worked_example": "المثال بيعمل switch لفرع الفيجر، وبعدين rebase على `main`، وبعدين بيعرض التاريخ الخطي الناتج بـ `git log`. ده مثال مكتوب — SkillBridge لا ينفذ هذه الأوامر.",
                "depth_note": "محتوى تأسيسي ثابت لـ Git من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة `git switch`/`git rebase`/`git log` القياسية. SkillBridge لا ينفذ هذه الأوامر، لذلك لا ينفذ أبداً rebase ولا يعيد كتابة تاريخ أي مستودع.",
            },
            "example": {"title": "اعمل rebase لفرع الفيجر على main", "type": "bash", "content": "git switch feature-payment\ngit rebase main\ngit log", "explanation": "المثال بيعمل switch على `feature-payment`، وبعدين rebase لـ commits بتاعته فوق رأس `main` (ويوقف للتضاربات لو أي commit معاد تشغيله بيتعارض)، وبعدين بيعرض التاريخ الخطي الناتج بـ `git log`. الأوامر معروضة للشرح — SkillBridge لا ينفذها ولا يعيد كتابة تاريخ أي مستودع."},
            "practice": {"title": "اشرح عمل rebase لفرع على main", "task": "اكتب بالظبط أوامر الطرفية اللي هتستخدمها لـ: (1) التحويل لـ `feature-payment`، و(2) عمل rebase للفرع على `main`، و(3) عرض التاريخ الخطي الناتج بـ `git log`. أضف جملة قصيرة تشرح الفرق بين rebase وmerge وليه ممنوع تعمل rebase لـ commits اتشاركت بالفعل، ولاحظ إن دي إجابة مكتوبة — SkillBridge لا ينفذ الـ rebase ولا يعيد كتابة تاريخ أي مستودع.", "response_type": "code", "language": "bash", "competency": "Rebasing", "starter_code": "git switch feature-payment\ngit rebase main\ngit log", "evaluation_note": "SkillBridge بيعمل مراجعة ثابتة للنص فقط: بيتأكد من التحويل لفرع الفيجر وأمر الـ rebase وأمر `git log` وملاحظة الفرق بين rebase وmerge / أمان التاريخ المشترك ومن إن الإجابة مكتوبة. لا ينفذ rebase ولا يعيد كتابة تاريخ أي مستودع، لذلك المراجعة لا تثبت إن rebase حصل."},
            "mini_check": {"questions": [
                {"id": "r1", "question": "`git rebase main` بيعمل إيه؟", "options": ["بيعيد تشغيل commits الفرع الحالي فوق رأس main", "بيدمج تاريخين بـ merge commit", "بيحذف الفرع الحالي", "بيدفع الفرع للـ remote"], "misconception_hint": "الـ rebase بيعيد تطبيق الـ commits واحد واحد فوق قاعدة جديدة بدل دمج التاريخين."},
                {"id": "r2", "question": "إيه الفرق بين rebase وmerge؟", "options": ["الـ rebase بيعيد كتابة commits الفرع لتاريخ خطي؛ الـ merge بيدمج التاريخين بـ merge commit", "الـ rebase بيشتغل على remotes بس؛ الـ merge محلي بس", "الـ merge بيعيد كتابة الـ commits؛ الـ rebase عمره ما بيغيّر commits", "هما اسمين لنفس العملية"], "misconception_hint": "الاتنين بيدمجوا فروع، بس واحد بيعمل merge commit والتاني بيعيد كتابة الـ commits."},
                {"id": "r3", "question": "إمتى الـ rebase يبقى غير آمن؟", "options": ["على commits اتدفعت بالفعل واتشاركت مع غيرك", "على فرع محلي فيه commit واحد", "قبل أول commit في المستودع", "لما شجرة العمل تكون نضيفة"], "misconception_hint": "إعادة كتابة التاريخ آمنة بس لـ commits محدش بنى شغله عليها."},
            ]},
        },
    },
}


GIT_REMOTES_COLLABORATION = {
    "status": "complete",
    "skill_aliases": ("git",),
    "competency": "Remotes & collaboration",
    "objective": "Describe remotes, `git fetch`, `git pull`, `git push`, tracking branches, and Pull Requests for safe team collaboration.",
    "prerequisites": [{
        "competency": "Committing",
        "relationship": "required foundation",
        "why": "Remote work shares commits, so the learner must first know how to record commits locally before fetching or pushing them.",
    }, {
        "competency": "git_committing",
        "relationship": "required foundation",
        "why": "Remote work shares commits, so the learner must first know how to record commits locally before fetching or pushing them.",
    }],
    "roadmap_rationale": (
        "Remotes & collaboration is the sixth complete Git topic on the Git roadmap because local "
        "history only becomes teamwork once it is shared: fetching, pulling, pushing, tracking "
        "branches, and Pull Requests are how local commits reach a team safely. Committing is its "
        "declared prerequisite; the remaining Git topics (History rewriting and beyond) stay "
        "separately scoped and are not represented as completed lessons here."
    ),
    "learn": {
        "title": "Remotes & collaboration",
        "explanation": (
            "A **remote** is a shared copy of your repository hosted on a service such as GitHub; "
            "`origin` is the conventional name for your repository's remote. `git fetch origin` "
            "downloads new commits from the remote without changing your working tree. `git pull` "
            "fetches and then integrates those commits into your current branch. `git push origin "
            "feature-payment` sends your local commits to the remote so teammates can see them. A "
            "**tracking branch** is a local branch linked to a remote branch, so `git status` can "
            "tell you how far ahead or behind you are. A **Pull Request** is a review step on the "
            "hosting service where teammates discuss and approve your branch before it is merged."
        ),
        "key_ideas": [
            "`git fetch origin` downloads remote commits without touching your working tree.",
            "`git pull` fetches and then integrates the remote commits into the current branch.",
            "`git push origin feature-payment` uploads your branch's commits to the remote.",
            "A tracking branch links a local branch to its remote counterpart; a Pull Request is the review step before merging on the host.",
        ],
        "key_terms": {
            "remote": "A shared copy of the repository hosted on a service such as GitHub.",
            "fetch": "Downloading new commits from a remote without changing your working tree.",
            "pull": "Fetching from a remote and integrating the commits into the current branch.",
            "push": "Uploading your local commits to a remote.",
            "tracking branch": "A local branch linked to a remote branch so Git can compare them.",
            "Pull Request": "A review step on the hosting service where a branch is discussed and approved before merging.",
        },
        "job_relevance": "Every team workflow runs on remotes: developers fetch and pull to stay current, push branches for review, and merge through Pull Requests instead of pushing straight to `main`.",
        "common_mistake": "Do not assume `git fetch` changes your files; it only downloads information — use `git pull` when you want the changes integrated into your branch.",
        "worked_example": "The example fetches from `origin`, pulls to integrate the downloaded commits, and then pushes the feature branch for review. It is a written example — the commands are not executed by SkillBridge.",
        "depth_note": "Canonical Git foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard `git fetch`/`git pull`/`git push` syntax. SkillBridge does not run these commands, so it never contacts a remote or performs network Git operations.",
        "grounding_sources": [
            {"title": "Git documentation: git-fetch", "url": "https://git-scm.com/docs/git-fetch", "source": "Git official documentation"},
            {"title": "Git documentation: git-push", "url": "https://git-scm.com/docs/git-push", "source": "Git official documentation"},
            {"title": "Pro Git book: Working with Remotes", "url": "https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes", "source": "Git official documentation"},
        ],
    },
    "example": {
        "title": "Sync with a remote and push a branch for review",
        "type": "bash",
        "content": "git fetch origin\ngit pull\ngit push origin feature-payment",
        "explanation": "This example downloads the latest remote state with `git fetch origin`, integrates it into the current branch with `git pull`, and then uploads the `feature-payment` branch with `git push origin feature-payment` so it can be reviewed in a Pull Request. The commands are shown for study — SkillBridge does not execute them or contact any remote.",
    },
    "practice": {
        "type": "practical",
        "title": "Describe syncing with a remote and pushing for review",
        "task": "Write the exact terminal commands you would use to: (1) download the latest state from the remote `origin` with `git fetch`, (2) integrate it into your current branch with `git pull`, and (3) upload your `feature-payment` branch with `git push`. Add one short sentence explaining the difference between fetch and pull and that a Pull Request is a review step on the hosting service, and note that this is a written answer — SkillBridge does not run these commands or contact any remote.",
        "response_type": "code",
        "language": "bash",
        "competency": "Remotes & collaboration",
        "starter_code": "git fetch origin\ngit pull\ngit push origin feature-payment",
        "evaluation_note": "SkillBridge performs a static text review only: it checks for `git fetch`, `git pull`, `git push`, a fetch-vs-pull / Pull Request note, and an explanation that this is a written answer. It does not run these commands or contact any remote, so the review cannot prove any network Git operation happened.",
    },
    "mini_check": {"questions": [
        {"id": "rc1", "type": "mcq", "question": "What does `git fetch origin` do?", "options": ["Downloads new commits from the remote without changing your working tree", "Uploads your commits to the remote", "Merges your branch into main", "Creates a Pull Request"], "correct_answer": "Downloads new commits from the remote without changing your working tree", "competency": "Remotes & collaboration", "difficulty": "intermediate", "misconception_hint": "Fetch only downloads information; integrating it into your branch is a separate step."},
        {"id": "rc2", "type": "mcq", "question": "Which command uploads your local `feature-payment` commits to the remote?", "options": ["git push origin feature-payment", "git fetch origin", "git pull", "git rebase main"], "correct_answer": "git push origin feature-payment", "competency": "Remotes & collaboration", "difficulty": "intermediate", "misconception_hint": "Pushing sends local commits to the remote; fetching and pulling move data the other way."},
        {"id": "rc3", "type": "mcq", "question": "What does a static review of fetch/pull/push commands NOT prove?", "options": ["That any network operation contacted a remote", "That `git fetch origin` appears in the answer", "That `git pull` is listed", "That `git push` is listed"], "correct_answer": "That any network operation contacted a remote", "competency": "Remotes & collaboration", "difficulty": "intermediate", "misconception_hint": "SkillBridge reviews text only; it never contacts a remote or performs network Git operations."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "الـ Remotes والتعاون",
                "explanation": "الـ **remote** هو نسخة مشتركة من مستودعك مستضافة على خدمة زي GitHub؛ و`origin` هو الاسم المتعارف عليه للـ remote بتاع مستودعك. `git fetch origin` بينزّل commits جديدة من الـ remote من غير ما يغيّر شجرة العمل بتاعتك. `git pull` بينزّل وبعدين بيدمج الـ commits دي في الفرع الحالي. `git push origin feature-payment` بيبعت commits المحلية بتاعتك للـ remote عشان زمايلك يشوفوها. الـ **tracking branch** هو فرع محلي مربوط بفرع على الـ remote، عشان `git status` يقدر يقولك إنت متقدم أو متأخر قد إيه. الـ **Pull Request** هو خطوة مراجعة على خدمة الاستضافة حيث زمايلك يناقشوا ويوافقوا على فرعك قبل ما يتدمج.",
                "key_ideas": ["`git fetch origin` بينزّل commits من الـ remote من غير ما يلمس شجرة العمل.", "`git pull` بينزّل وبعدين بيدمج commits الـ remote في الفرع الحالي.", "`git push origin feature-payment` بيرفع commits الفرع بتاعك على الـ remote.", "الـ tracking branch بيربط فرع محلي بنظيره على الـ remote؛ والـ Pull Request هو خطوة المراجعة قبل الدمج على المستضيف."],
                "key_terms": {"remote": "نسخة مشتركة من المستودع مستضافة على خدمة زي GitHub.", "fetch": "تنزيل commits جديدة من remote من غير تغيير شجرة العمل.", "pull": "تنزيل من remote ودمج الـ commits في الفرع الحالي.", "push": "رفع commits المحلية على remote.", "tracking branch": "فرع محلي مربوط بفرع على remote عشان Git يقارن بينهم.", "Pull Request": "خطوة مراجعة على خدمة الاستضافة حيث الفرع يتناقش ويتوافق عليه قبل الدمج."},
                "job_relevance": "كل شغل الفرق بيدور على remotes: المطورون بيعملوا fetch وpull عشان يفضلوا محدثين، وبيعملوا push للفروع للمراجعة، وبيدمجوا من خلال Pull Requests بدل الدفع مباشرة على `main`.",
                "common_mistake": "ما تفترضش إن `git fetch` بيغيّر ملفاتك؛ هو بينزّل معلومات بس — استخدم `git pull` لما تكون عايز التغييرات تتدمج في فرعك.",
                "worked_example": "المثال بيعمل fetch من `origin`، وبعدين pull عشان يدمج الـ commits المنزّلة، وبعدين بيعمل push لفرع الفيجر للمراجعة. ده مثال مكتوب — SkillBridge لا ينفذ هذه الأوامر.",
                "depth_note": "محتوى تأسيسي ثابت لـ Git من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة `git fetch`/`git pull`/`git push` القياسية. SkillBridge لا ينفذ هذه الأوامر، لذلك لا يتصل أبداً بأي remote ولا ينفذ عمليات Git شبكية.",
            },
            "example": {"title": "زامن مع remote واعمل push لفرع للمراجعة", "type": "bash", "content": "git fetch origin\ngit pull\ngit push origin feature-payment", "explanation": "المثال بينزّل أحدث حالة من الـ remote بـ `git fetch origin`، وبعدين بيدمجها في الفرع الحالي بـ `git pull`، وبعدين بيرفع فرع `feature-payment` بـ `git push origin feature-payment` عشان يتراجع في Pull Request. الأوامر معروضة للشرح — SkillBridge لا ينفذها ولا يتصل بأي remote."},
            "practice": {"title": "اشرح المزامنة مع remote والدفع للمراجعة", "task": "اكتب بالظبط أوامر الطرفية اللي هتستخدمها لـ: (1) تنزيل أحدث حالة من الـ remote `origin` بـ `git fetch`، و(2) دمجها في فرعك الحالي بـ `git pull`، و(3) رفع فرع `feature-payment` بتاعك بـ `git push`. أضف جملة قصيرة تشرح الفرق بين fetch وpull وإن الـ Pull Request خطوة مراجعة على خدمة الاستضافة، ولاحظ إن دي إجابة مكتوبة — SkillBridge لا ينفذ هذه الأوامر ولا يتصل بأي remote.", "response_type": "code", "language": "bash", "competency": "Remotes & collaboration", "starter_code": "git fetch origin\ngit pull\ngit push origin feature-payment", "evaluation_note": "SkillBridge بيعمل مراجعة ثابتة للنص فقط: بيتأكد من `git fetch` و`git pull` و`git push` وملاحظة الفرق بين fetch وpull / الـ Pull Request ومن إن الإجابة مكتوبة. لا ينفذ هذه الأوامر ولا يتصل بأي remote، لذلك المراجعة لا تثبت حدوث أي عملية Git شبكية."},
            "mini_check": {"questions": [
                {"id": "rc1", "question": "`git fetch origin` بيعمل إيه؟", "options": ["بينزّل commits جديدة من الـ remote من غير ما يغيّر شجرة العمل", "بيرفع commits بتاعتك على الـ remote", "بيدمج فرعك في main", "بيعمل Pull Request"], "misconception_hint": "الـ fetch بينزّل معلومات بس؛ دمجها في فرعك خطوة منفصلة."},
                {"id": "rc2", "question": "أي أمر بيرفع commits المحلية بتاع `feature-payment` على الـ remote؟", "options": ["git push origin feature-payment", "git fetch origin", "git pull", "git rebase main"], "misconception_hint": "الـ push بيبعت الـ commits المحلية للـ remote؛ الـ fetch والـ pull بينقلوا البيانات في الاتجاه التاني."},
                {"id": "rc3", "question": "المراجعة الثابتة لأوامر fetch/pull/push مش بتثبت إيه؟", "options": ["إن أي عملية شبكية اتصلت بـ remote", "إن `git fetch origin` ظاهر في الإجابة", "إن `git pull` متلست", "إن `git push` متلست"], "misconception_hint": "SkillBridge بيراجع النص بس؛ عمره ما بيتصل بـ remote ولا بينفذ عمليات Git شبكية."},
            ]},
        },
    },
}


GIT_HISTORY_REWRITING = {
    "status": "complete",
    "skill_aliases": ("git",),
    "competency": "History rewriting",
    "objective": "Describe `git commit --amend` and interactive rebase for rewriting local history, and explain why published commits must never be rewritten.",
    "prerequisites": [{
        "competency": "Rebasing",
        "relationship": "required foundation",
        "why": "Interactive rebase builds on rebasing, so the learner must first understand how rebase replays and rewrites commits.",
    }, {
        "competency": "git_rebasing",
        "relationship": "required foundation",
        "why": "Interactive rebase builds on rebasing, so the learner must first understand how rebase replays and rewrites commits.",
    }],
    "roadmap_rationale": (
        "History rewriting is the seventh complete Git topic on the Git roadmap because amend and "
        "interactive rebase are how developers polish a branch before it is shared — and the first "
        "place the local-vs-published boundary must be understood precisely. Rebasing is its declared "
        "prerequisite; Bisect & debugging is the next complete topic, and the remaining Git topics "
        "stay separately scoped and are not represented as completed lessons here."
    ),
    "learn": {
        "title": "History rewriting",
        "explanation": (
            "**History rewriting** changes existing commits instead of adding new ones. "
            "`git commit --amend` rewrites the most recent commit — for example to fix its message or "
            "add a forgotten file. **Interactive rebase** (`git rebase -i main`) opens a list of the "
            "branch's commits and lets you reorder, squash, reword, edit, or drop them before the branch "
            "is merged. Both are safe only for **local** commits that nobody else has pulled: rewriting "
            "**published** commits changes their hashes, so collaborators' copies no longer match and "
            "every pull becomes a conflict. The rule is simple: rewrite local history freely before you "
            "push; once commits are published, add new commits instead of rewriting old ones."
        ),
        "key_ideas": [
            "`git commit --amend` rewrites only the most recent commit (its message or staged content).",
            "`git rebase -i main` lets you reorder, squash, reword, edit, or drop the branch's commits.",
            "Rewriting changes commit hashes; published commits must never be rewritten.",
            "Local commits (not yet pushed) may be cleaned up safely; shared history is extended with new commits instead.",
        ],
        "key_terms": {
            "amend": "Rewriting the most recent commit, for example to fix its message or add a forgotten file.",
            "interactive rebase": "A rebase that opens the branch's commits for reordering, squashing, rewording, editing, or dropping.",
            "squash": "Combining several commits into one during an interactive rebase.",
            "published commits": "Commits that have been pushed and that other people may have based work on.",
        },
        "job_relevance": "Developers clean up a feature branch with amend and interactive rebase before opening a Pull Request, so reviewers read a tidy history — but only on commits that were never pushed.",
        "common_mistake": "Do not amend or interactively rebase commits that have already been pushed; rewrite only local commits that nobody else has.",
        "worked_example": "The example amends the last commit's message, opens an interactive rebase to clean up the branch's commits, and then shows the rewritten history with `git log`. It is a written example — the commands are not executed by SkillBridge.",
        "depth_note": "Canonical Git foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard `git commit --amend`/`git rebase -i`/`git log` syntax. SkillBridge does not run these commands, so it never amends, rebases, or rewrites any repository's history.",
        "grounding_sources": [
            {"title": "Git documentation: git-commit (--amend)", "url": "https://git-scm.com/docs/git-commit", "source": "Git official documentation"},
            {"title": "Pro Git book: Rewriting History", "url": "https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History", "source": "Git official documentation"},
            {"title": "Git documentation: git-rebase", "url": "https://git-scm.com/docs/git-rebase", "source": "Git official documentation"},
        ],
    },
    "example": {
        "title": "Polish a branch before sharing it",
        "type": "bash",
        "content": "git commit --amend -m \"Add the project README\"\ngit rebase -i main\ngit log",
        "explanation": "This example amends the most recent commit's message, opens an interactive rebase over the branch's commits (to reorder, squash, or reword them), and then shows the rewritten history with `git log`. The commands are shown for study — SkillBridge does not execute them or rewrite any repository's history.",
    },
    "practice": {
        "type": "practical",
        "title": "Describe rewriting local history before sharing",
        "task": "Write the exact terminal commands you would use to: (1) amend the most recent commit's message, (2) open an interactive rebase over the branch's commits with `git rebase -i main`, and (3) view the rewritten history with `git log`. Add one short sentence explaining the difference between local and published commits and why only local history may be rewritten, and note that this is a written answer — SkillBridge does not run these commands or rewrite any repository's history.",
        "response_type": "code",
        "language": "bash",
        "competency": "History rewriting",
        "starter_code": "git commit --amend -m \"Add the project README\"\ngit rebase -i main\ngit log",
        "evaluation_note": "SkillBridge performs a static text review only: it checks for the amend command, the interactive rebase, `git log`, a local-vs-published safety note, and an explanation that this is a written answer. It does not run these commands or rewrite any repository's history, so the review cannot prove any history was rewritten.",
    },
    "mini_check": {"questions": [
        {"id": "h1", "type": "mcq", "question": "What does `git commit --amend` do?", "options": ["Rewrites the most recent commit", "Deletes the most recent commit", "Pushes the most recent commit", "Creates a new branch"], "correct_answer": "Rewrites the most recent commit", "competency": "History rewriting", "difficulty": "intermediate", "misconception_hint": "Amend replaces only the latest commit — its message or staged content."},
        {"id": "h2", "type": "mcq", "question": "Which command opens the branch's commits for reordering, squashing, or rewording?", "options": ["git rebase -i main", "git commit --amend", "git bisect start", "git push origin main"], "correct_answer": "git rebase -i main", "competency": "History rewriting", "difficulty": "intermediate", "misconception_hint": "The interactive form of rebase lists the commits so you can choose what to do with each one."},
        {"id": "h3", "type": "mcq", "question": "When is rewriting history safe?", "options": ["Only for local commits that have not been published or shared", "For any commit, even after pushing", "Only on someone else's branch", "Never, under any circumstances"], "correct_answer": "Only for local commits that have not been published or shared", "competency": "History rewriting", "difficulty": "intermediate", "misconception_hint": "Rewriting changes commit hashes, so it is only safe for commits nobody else has."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "إعادة كتابة التاريخ",
                "explanation": "**إعادة كتابة التاريخ** بتغيّر commits موجودة بدل ما تضيف جديدة. `git commit --amend` بيعيد كتابة آخر commit — مثلاً عشان يصلّح رسالتها أو يضيف ملف منسى. الـ **interactive rebase** (`git rebase -i main`) بيفتح قائمة بـ commits الفرع ويخليك تعيد ترتيبها أو تدمجها (squash) أو تعيد تسميتها أو تعدّلها أو تحذفها قبل ما الفرع يتدمج. الاتنين آمنين بس للـ commits **المحلية** اللي محدش سحبها: إعادة كتابة commits **منشورة** بتغيّر الـ hashes بتاعتها، فنسخ المتعاونين مبقتش متطابقة وكل pull يبقى تضارب. القاعدة بسيطة: أعد كتابة التاريخ المحلي بحرية قبل ما تدفع؛ وبمجرد ما الـ commits اتنشرت، ضيف commits جديدة بدل إعادة كتابة القديمة.",
                "key_ideas": ["`git commit --amend` بيعيد كتابة آخر commit بس (رسالتها أو محتواها المرحّل).", "`git rebase -i main` بيخليك تعيد ترتيب أو تدمج أو تعيد تسمية أو تعدّل أو تحذف commits الفرع.", "إعادة الكتابة بتغيّر hashes الـ commits؛ الـ commits المنشورة ممنوع تتعاد كتابتها.", "الـ commits المحلية (لسه ما اتدفعتش) ممكن تتنضف بأمان؛ التاريخ المشترك بيتمدد بـ commits جديدة بدل الكتابة عليه."],
                "key_terms": {"amend": "إعادة كتابة آخر commit، مثلاً لتصليح رسالتها أو إضافة ملف منسى.", "interactive rebase": "rebase بيفتح commits الفرع لإعادة الترتيب أو الدمج أو إعادة التسمية أو التعديل أو الحذف.", "squash": "دمج عدة commits في واحدة أثناء الـ interactive rebase.", "commits منشورة": "Commits اتدفعت وناس تانية ممكن تكون بنت شغلها عليها."},
                "job_relevance": "المطورون بينضفوا فرع الفيجر بـ amend وinteractive rebase قبل فتح Pull Request، عشان المراجعين يقرأوا تاريخ مرتب — بس على commits عمرها ما اتدفعت.",
                "common_mistake": "ما تعملش amend أو interactive rebase لـ commits اتدفعت بالفعل؛ أعد كتابة الـ commits المحلية بس اللي محدش عنده.",
                "worked_example": "المثال بيعمل amend لرسالة آخر commit، وبعدين بيفتح interactive rebase عشان ينضف commits الفرع، وبعدين بيعرض التاريخ المعاد كتابته بـ `git log`. ده مثال مكتوب — SkillBridge لا ينفذ هذه الأوامر.",
                "depth_note": "محتوى تأسيسي ثابت لـ Git من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة `git commit --amend`/`git rebase -i`/`git log` القياسية. SkillBridge لا ينفذ هذه الأوامر، لذلك لا يعمل amend أو rebase ولا يعيد كتابة تاريخ أي مستودع.",
            },
            "example": {"title": "نضّف فرع قبل مشاركته", "type": "bash", "content": "git commit --amend -m \"Add the project README\"\ngit rebase -i main\ngit log", "explanation": "المثال بيعمل amend لرسالة آخر commit، وبعدين بيفتح interactive rebase على commits الفرع (لإعادة ترتيبها أو دمجها أو إعادة تسميتها)، وبعدين بيعرض التاريخ المعاد كتابته بـ `git log`. الأوامر معروضة للشرح — SkillBridge لا ينفذها ولا يعيد كتابة تاريخ أي مستودع."},
            "practice": {"title": "اشرح إعادة كتابة التاريخ المحلي قبل المشاركة", "task": "اكتب بالظبط أوامر الطرفية اللي هتستخدمها لـ: (1) عمل amend لرسالة آخر commit، و(2) فتح interactive rebase على commits الفرع بـ `git rebase -i main`، و(3) عرض التاريخ المعاد كتابته بـ `git log`. أضف جملة قصيرة تشرح الفرق بين الـ commits المحلية والمنشورة وليه التاريخ المحلي بس هو اللي ممكن يتعاد كتابته، ولاحظ إن دي إجابة مكتوبة — SkillBridge لا ينفذ هذه الأوامر ولا يعيد كتابة تاريخ أي مستودع.", "response_type": "code", "language": "bash", "competency": "History rewriting", "starter_code": "git commit --amend -m \"Add the project README\"\ngit rebase -i main\ngit log", "evaluation_note": "SkillBridge بيعمل مراجعة ثابتة للنص فقط: بيتأكد من أمر الـ amend والـ interactive rebase وأمر `git log` وملاحظة الفرق بين المحلي والمنشور ومن إن الإجابة مكتوبة. لا ينفذ هذه الأوامر ولا يعيد كتابة تاريخ أي مستودع، لذلك المراجعة لا تثبت إعادة كتابة أي تاريخ."},
            "mini_check": {"questions": [
                {"id": "h1", "question": "`git commit --amend` بيعمل إيه؟", "options": ["بيعيد كتابة آخر commit", "بيحذف آخر commit", "بيدفع آخر commit", "بيعمل فرع جديد"], "misconception_hint": "الـ amend بيستبدل آخر commit بس — رسالتها أو محتواها المرحّل."},
                {"id": "h2", "question": "أي أمر بيفتح commits الفرع لإعادة الترتيب أو الدمج أو إعادة التسمية؟", "options": ["git rebase -i main", "git commit --amend", "git bisect start", "git push origin main"], "misconception_hint": "الشكل التفاعلي من الـ rebase بيلست الـ commits عشان تختار تعمل إيه في كل واحدة."},
                {"id": "h3", "question": "إمتى إعادة كتابة التاريخ تبقى آمنة؟", "options": ["للـ commits المحلية بس اللي لسه ما اتنشرتش أو اتشاركتش", "لأي commit، حتى بعد الدفع", "على فرع حد تاني بس", "أبداً، تحت أي ظرف"], "misconception_hint": "إعادة الكتابة بتغيّر hashes الـ commits، فهي آمنة بس لـ commits محدش عنده."},
            ]},
        },
    },
}


GIT_BISECT_DEBUGGING = {
    "status": "complete",
    "skill_aliases": ("git",),
    "competency": "Bisect & debugging",
    "objective": "Describe how `git bisect` finds a regression by binary-searching good and bad commits, how to read the result, and how to end a session safely.",
    "prerequisites": [{
        "competency": "Committing",
        "relationship": "required foundation",
        "why": "Bisect walks the commit history, so the learner must first understand commits and how to read them.",
    }, {
        "competency": "git_committing",
        "relationship": "required foundation",
        "why": "Bisect walks the commit history, so the learner must first understand commits and how to read them.",
    }],
    "roadmap_rationale": (
        "Bisect & debugging is the eighth complete Git topic on the Git roadmap and the first "
        "Advanced topic: once a project has real history, `git bisect` is the canonical way to find "
        "the exact commit that introduced a regression. Committing is its declared prerequisite; the "
        "remaining Git topics (Submodules and beyond) stay separately scoped and are not represented "
        "as completed lessons here."
    ),
    "learn": {
        "title": "Bisect & debugging",
        "explanation": (
            "**`git bisect`** finds the commit that introduced a regression by binary-searching the "
            "history. You start with `git bisect start`, mark the current broken state with "
            "`git bisect bad`, and mark an older commit that worked with `git bisect good <commit>`. "
            "Git then checks out a commit halfway between them; you test it and answer "
            "`git bisect good` or `git bisect bad`, and Git repeats until it identifies the first bad "
            "commit. When it finishes, Git names the culprit commit so you can read it with "
            "`git show`. Always end the session with `git bisect reset`, which returns you to your "
            "original branch — during a bisect you are on a detached HEAD, so reset is the safe way "
            "back."
        ),
        "key_ideas": [
            "`git bisect start` begins the session; `git bisect bad` marks the broken state and `git bisect good <commit>` marks a working one.",
            "Git checks out the midpoint commit each round; your good/bad answer halves the search space.",
            "The result names the first bad commit; inspect it with `git show`.",
            "`git bisect reset` ends the session and returns you to your original branch — never leave a bisect half-finished.",
        ],
        "key_terms": {
            "bisect": "Binary-searching the commit history to find the commit that introduced a regression.",
            "regression": "A bug that appeared in code that used to work.",
            "first bad commit": "The earliest commit where the regression exists, as identified by the bisect.",
            "detached HEAD": "The state of being checked out on a commit rather than a branch, as happens during a bisect.",
        },
        "job_relevance": "When a regression appears in a long history, bisect turns days of guessing into a handful of tests, and ending with `git bisect reset` keeps the repository clean.",
        "common_mistake": "Do not forget `git bisect reset` at the end; a bisect session leaves you on a detached HEAD until you reset.",
        "worked_example": "The example starts a bisect, marks the broken state bad and a known-good tag good, and then resets the session. It is a written example — the commands are not executed by SkillBridge.",
        "depth_note": "Canonical Git foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard `git bisect` syntax. SkillBridge does not run these commands, so it never starts a bisect or checks out commits in any repository.",
        "grounding_sources": [
            {"title": "Git documentation: git-bisect", "url": "https://git-scm.com/docs/git-bisect", "source": "Git official documentation"},
            {"title": "Pro Git book: Debugging with Git", "url": "https://git-scm.com/book/en/v2/Git-Tools-Debugging-with-Git", "source": "Git official documentation"},
            {"title": "Git documentation: git-show", "url": "https://git-scm.com/docs/git-show", "source": "Git official documentation"},
        ],
    },
    "example": {
        "title": "Bisect a regression and end the session safely",
        "type": "bash",
        "content": "git bisect start\ngit bisect bad\ngit bisect good v1.2\ngit bisect reset",
        "explanation": "This example starts a bisect session, marks the current broken state bad, marks the known-good tag `v1.2` good (Git then checks out midpoint commits for the learner to test), and finally ends the session safely with `git bisect reset`. The commands are shown for study — SkillBridge does not execute them or run a bisect in any repository.",
    },
    "practice": {
        "type": "practical",
        "title": "Describe bisecting a regression",
        "task": "Write the exact terminal commands you would use to: (1) start a bisect session, (2) mark the current broken state bad, (3) mark the known-good tag `v1.2` good, and (4) end the session safely with `git bisect reset`. Add one short sentence explaining that Git checks out midpoint commits for you to test and that the finished bisect names the first bad commit, and note that this is a written answer — SkillBridge does not run these commands or start a bisect in any repository.",
        "response_type": "code",
        "language": "bash",
        "competency": "Bisect & debugging",
        "starter_code": "git bisect start\ngit bisect bad\ngit bisect good v1.2\ngit bisect reset",
        "evaluation_note": "SkillBridge performs a static text review only: it checks for `git bisect start`, the bad and good markers, `git bisect reset`, a midpoint / first-bad-commit note, and an explanation that this is a written answer. It does not run these commands or start a bisect in any repository, so the review cannot prove a bisect happened.",
    },
    "mini_check": {"questions": [
        {"id": "d1", "type": "mcq", "question": "After `git bisect start`, which commands mark the broken and working states?", "options": ["git bisect bad and git bisect good <commit>", "git bisect start and git bisect stop", "git commit and git push", "git merge and git rebase"], "correct_answer": "git bisect bad and git bisect good <commit>", "competency": "Bisect & debugging", "difficulty": "advanced", "misconception_hint": "You tell Git which end is broken and which end works so it can search between them."},
        {"id": "d2", "type": "mcq", "question": "What does a finished bisect report?", "options": ["The first bad commit that introduced the regression", "A list of every commit in the repository", "The author with the most commits", "The files with the most lines"], "correct_answer": "The first bad commit that introduced the regression", "competency": "Bisect & debugging", "difficulty": "advanced", "misconception_hint": "Each good/bad answer halves the range until one commit remains."},
        {"id": "d3", "type": "mcq", "question": "How do you safely end a bisect session?", "options": ["git bisect reset, which returns you to your original branch", "git push origin main", "git rebase -i main", "Closing the terminal without any command"], "correct_answer": "git bisect reset, which returns you to your original branch", "competency": "Bisect & debugging", "difficulty": "advanced", "misconception_hint": "During a bisect you are on a detached HEAD; the reset command is the safe way back."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "الـ Bisect والتصحيح",
                "explanation": "**`git bisect`** بيلاقي الـ commit اللي قدّمت الـ regression عن طريق بحث ثنائي في التاريخ. بتبدأ بـ `git bisect start`، وبتعلّم الحالة المكسورة الحالية بـ `git bisect bad`، وبتعلّم commit أقدم كانت شغالة بـ `git bisect good <commit>`. Git بعدها بيعمل checkout لـ commit في نص المسافة بينهم؛ وإنت بتختبرها وبترد `git bisect good` أو `git bisect bad`، وGit بيكرر لحد ما يحدد أول commit مكسورة. لما يخلص، Git بيسمّي الـ commit المذنبة عشان تقراها بـ `git show`. دايماً اختم الجلسة بـ `git bisect reset`، اللي بيرجعك لفرعك الأصلي — أثناء الـ bisect إنت على detached HEAD، فالـ reset هو الطريق الآمن للرجوع.",
                "key_ideas": ["`git bisect start` بيبدأ الجلسة؛ `git bisect bad` بيعلّم الحالة المكسورة و`git bisect good <commit>` بيعلّم الشغالة.", "Git بيعمل checkout للـ commit اللي في النص كل جولة؛ وردك good/bad بيقلّص مساحة البحث للنص.", "النتيجة بتسمّي أول commit مكسورة؛ افحصها بـ `git show`.", "`git bisect reset` بيختم الجلسة ويرجعك لفرعك الأصلي — عمرك ما تسيب bisect نص مكمّل."],
                "key_terms": {"bisect": "بحث ثنائي في تاريخ الـ commits عشان يلاقي الـ commit اللي قدّمت الـ regression.", "regression": "عطل ظهر في كود كان شغال قبل كده.", "أول commit مكسورة": "أقدم commit موجود فيها الـ regression، زي ما حددها الـ bisect.", "detached HEAD": "حالة إنك تكون متشيك أوت على commit مش على فرع، زي ما بيحصل أثناء الـ bisect."},
                "job_relevance": "لما regression يظهر في تاريخ طويل، الـ bisect بيحوّل أيام من التخمين لعدد قليل من الاختبارات، والختام بـ `git bisect reset` بيخلي المستودع نضيف.",
                "common_mistake": "ما تنساش `git bisect reset` في الآخر؛ جلسة الـ bisect بتسيبك على detached HEAD لحد ما تعمل reset.",
                "worked_example": "المثال بيبدأ bisect، وبيعلّم الحالة المكسورة bad وtag المعروف إنه شغال good، وبعدين بيعمل reset للجلسة. ده مثال مكتوب — SkillBridge لا ينفذ هذه الأوامر.",
                "depth_note": "محتوى تأسيسي ثابت لـ Git من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة `git bisect` القياسية. SkillBridge لا ينفذ هذه الأوامر، لذلك لا يبدأ أبداً bisect ولا يعمل checkout لـ commits في أي مستودع.",
            },
            "example": {"title": "اعمل bisect لـ regression واختم الجلسة بأمان", "type": "bash", "content": "git bisect start\ngit bisect bad\ngit bisect good v1.2\ngit bisect reset", "explanation": "المثال بيبدأ جلسة bisect، وبيعلّم الحالة المكسورة الحالية bad، وبيعلّم الـ tag المعروف إنه شغال `v1.2` good (وبعدين Git بيعمل checkout لـ commits في النص عشان المتعلم يختبرها)، وفي الآخر بيختم الجلسة بأمان بـ `git bisect reset`. الأوامر معروضة للشرح — SkillBridge لا ينفذها ولا يشغّل bisect في أي مستودع."},
            "practice": {"title": "اشرح عمل bisect لـ regression", "task": "اكتب بالظبط أوامر الطرفية اللي هتستخدمها لـ: (1) بدء جلسة bisect، و(2) تعليم الحالة المكسورة الحالية bad، و(3) تعليم الـ tag المعروف إنه شغال `v1.2` good، و(4) ختم الجلسة بأمان بـ `git bisect reset`. أضف جملة قصيرة تشرح إن Git بيعمل checkout لـ commits في النص عشان تختبرها وإن الـ bisect المكتمل بيسمّي أول commit مكسورة، ولاحظ إن دي إجابة مكتوبة — SkillBridge لا ينفذ هذه الأوامر ولا يبدأ bisect في أي مستودع.", "response_type": "code", "language": "bash", "competency": "Bisect & debugging", "starter_code": "git bisect start\ngit bisect bad\ngit bisect good v1.2\ngit bisect reset", "evaluation_note": "SkillBridge بيعمل مراجعة ثابتة للنص فقط: بيتأكد من `git bisect start` وعلامات bad وgood وأمر `git bisect reset` وملاحظة نقطة المنتصف / أول commit مكسورة ومن إن الإجابة مكتوبة. لا ينفذ هذه الأوامر ولا يبدأ bisect في أي مستودع، لذلك المراجعة لا تثبت حدوث bisect."},
            "mini_check": {"questions": [
                {"id": "d1", "question": "بعد `git bisect start`، أي أوامر بتعلّم الحالات المكسورة والشغالة؟", "options": ["git bisect bad و git bisect good <commit>", "git bisect start و git bisect stop", "git commit و git push", "git merge و git rebase"], "misconception_hint": "بتقول لـ Git أنهي طرف مكسور وأنهي طرف شغال عشان يبحث بينهم."},
                {"id": "d2", "question": "الـ bisect المكتمل بيبلّغ عن إيه؟", "options": ["أول commit مكسورة قدّمت الـ regression", "قائمة بكل commit في المستودع", "المؤلف صاحب أكبر عدد commits", "الملفات صاحبة أكبر عدد أسطر"], "misconception_hint": "كل رد good/bad بيقلّص النطاق للنص لحد ما تفضل commit واحدة."},
                {"id": "d3", "question": "إزاي تختم جلسة bisect بأمان؟", "options": ["git bisect reset، اللي بيرجعك لفرعك الأصلي", "git push origin main", "git rebase -i main", "قفل الطرفية من غير أي أمر"], "misconception_hint": "أثناء الـ bisect إنت على detached HEAD؛ أمر الـ reset هو الطريق الآمن للرجوع."},
            ]},
        },
    },
}


GIT_SUBMODULES = {
    "status": "complete",
    "skill_aliases": ("git",),
    "competency": "Submodules",
    "objective": "Describe how to add, clone, initialize, update, and pin submodules, and why a submodule references a pinned commit instead of a moving branch.",
    "prerequisites": [{
        "competency": "Branching",
        "relationship": "required foundation",
        "why": "Submodules embed one branch-based repository in another, so the learner must first understand branches and how a working tree is checked out.",
    }, {
        "competency": "git_branching",
        "relationship": "required foundation",
        "why": "Submodules embed one branch-based repository in another, so the learner must first understand branches and how a working tree is checked out.",
    }],
    "roadmap_rationale": (
        "Submodules is the ninth complete Git topic on the Git roadmap: once projects "
        "share code across repositories, submodules are how a repository pins another "
        "repository at a specific commit instead of copying its files. Branching is its "
        "declared prerequisite; Workflows & policy and Large-repo strategies are the next "
        "complete topics, and nothing Git stays planned beyond them."
    ),
    "learn": {
        "title": "Submodules",
        "explanation": (
            "A **submodule** is a Git repository embedded inside another Git repository. "
            "The parent records, in a file named `.gitmodules`, which remote the submodule "
            "comes from and — inside the index — the **pinned commit** it currently points to. "
            "Because the parent stores a specific commit, not a moving branch, every clone or "
            "checkout gets the exact same revision of the embedded repository. Adding a "
            "submodule with `git submodule add <url> <path>` stages it; cloning a project that "
            "uses submodules with `git clone --recurse-submodules <url>` brings the embedded "
            "repositories along in one step. If you clone without that flag, `git submodule "
            "init` records the remote paths in `.git/config` and `git submodule update` "
            "checks out the pinned commits listed in the index."
        ),
        "key_ideas": [
            "A submodule is a repository embedded at a pinned commit, recorded in `.gitmodules`.",
            "`git clone --recurse-submodules <url>` clones the project AND its submodules.",
            "After a plain clone, `git submodule init` + `git submodule update` fetch the pinned commits.",
            "The parent tracks a specific commit, so a submodule does not \"float\" on a branch.",
        ],
        "key_terms": {
            ".gitmodules": "The file that records which remotes the submodules come from.",
            "pinned commit": "The exact commit of the embedded repository that the parent records and checks out.",
            "recurse-submodules": "A `git clone` flag that initializes and updates submodules during the clone.",
            "submodule update": "The command that checks out the pinned commits recorded in the index.",
        },
        "job_relevance": "Teams reuse shared libraries across projects with submodules, and developers must know how a pinned commit is shared — and that a plain clone does not fetch the embedded code by itself.",
        "common_mistake": "Do not expect `git clone` to fetch submodules by default; use `--recurse-submodules`, or run `git submodule init` and `git submodule update` after the clone.",
        "worked_example": "The example clones a project, initializes its submodule remotes, and checks out the pinned submodule commits. It is a written example — the commands are not executed by SkillBridge and no repository or submodule is modified.",
        "depth_note": "Canonical Git foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard `git clone`/`git submodule` syntax. SkillBridge does not run these commands, so it never clones, initializes, updates, or modifies any repository's submodules.",
        "grounding_sources": [
            {"title": "Git documentation: git-submodule", "url": "https://git-scm.com/docs/git-submodule", "source": "Git official documentation"},
            {"title": "Pro Git book: Submodules", "url": "https://git-scm.com/book/en/v2/Git-Tools-Submodules", "source": "Git official documentation"},
            {"title": "Git documentation: git-clone", "url": "https://git-scm.com/docs/git-clone", "source": "Git official documentation"},
        ],
    },
    "example": {
        "title": "Clone a project with submodules and bring them in",
        "type": "bash",
        "content": "git clone https://example.com/team/library\ncd library\ngit submodule init\ngit submodule update",
        "explanation": "This example first clones the `library` project, then initializes its submodule remotes from `.gitmodules`, then checks out the pinned submodule commits recorded in the index. The commands are shown for study — SkillBridge does not execute them and never clones or modifies any real repository or submodule.",
    },
    "practice": {
        "type": "practical",
        "title": "Describe cloning and initializing submodules",
        "task": "Write the exact terminal commands you would use to: (1) clone a project, (2) initialize its submodule remotes with `git submodule init`, and (3) check out the recorded submodule commits with `git submodule update`. Add one short sentence explaining that the parent records a pinned commit (not a moving branch), and note that this is a written answer — SkillBridge does not run these commands and never modifies any repository's submodules.",
        "response_type": "code",
        "language": "bash",
        "competency": "Submodules",
        "starter_code": "git clone https://example.com/team/library\ngit submodule init\ngit submodule update",
        "evaluation_note": "SkillBridge performs a static text review only: it checks for the clone command, `git submodule init`, `git submodule update`, a pinned-commit note, and an explanation that this is a written answer. It does not run these commands or modify any repository's submodules, so the review cannot prove any submodule was added or updated.",
    },
    "mini_check": {"questions": [
        {"id": "m1", "type": "mcq", "question": "What is a submodule?", "options": ["A Git repository embedded in another repository at a pinned commit", "A copy of a single folder", "A remote branch", "An uncommitted change"], "correct_answer": "A Git repository embedded in another repository at a pinned commit", "competency": "Submodules", "difficulty": "advanced", "misconception_hint": "The parent stores a specific commit of the embedded repository, not loose copies of its files."},
        {"id": "m2", "type": "mcq", "question": "Which command clones a project AND its submodules in one step?", "options": ["git clone --recurse-submodules <url>", "git clone --depth 1 <url>", "git submodule deinit --all", "git reset --hard"], "correct_answer": "git clone --recurse-submodules <url>", "competency": "Submodules", "difficulty": "advanced", "misconception_hint": "A plain clone does not bring the embedded repositories along; the `--recurse-submodules` flag does."},
        {"id": "m3", "type": "mcq", "question": "What does the parent repository record for each submodule?", "options": ["A pinned commit (a specific SHA)", "The full history of the embedded repository", "A moving branch name", "A compressed archive of the files"], "correct_answer": "A pinned commit (a specific SHA)", "competency": "Submodules", "difficulty": "advanced", "misconception_hint": "The submodule points at one exact commit so every checkout gets the same revision."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "الـ Submodules",
                "explanation": "الـ **Submodule** عبارة عن مستودع Git مدمج جوه مستودع Git تاني. المستودع الأب بيحفظ في ملف اسمه `.gitmodules` الـ remote اللي جاي منه الـ submodule، وفي الـ index بيحفظ الـ commit المثبّت (pinned commit) اللي واقف عنده الساعة دي. لأن الأب بيخزن commit محدد مش فرع متحرك، أي clone أو checkout بياخد نفس النسخة بالظبط من المستودع المدمج. إضافة submodule بتتحط بـ `git submodule add <url> <path>`؛ وكلونينج مشروع بيستخدم submodules بـ `git clone --recurse-submodules <url>` بتيجي بالمستودعات المدمجة معاه في خطوة واحدة. لو عملت clone من غير العلم ده، `git submodule init` بيسجّل الـ remote paths في `.git/config` و`git submodule update` بيعمل checkout للـ commits المثبّتة اللي في الـ index.",
                "key_ideas": ["الـ submodule مستودع مدمج عند commit مثبّت، ومتسجل في `.gitmodules`.", "`git clone --recurse-submodules <url>` بيعمل clone للمشروع و submodules مع بعض.", "بعد clone عادي، `git submodule init` + `git submodule update` بيجيبوا الـ commits المثبّتة.", "الأب بيتابع commit محدد، فالـ submodule مش \"بيطفّي\" على فرع متحرك."],
                "key_terms": {".gitmodules": "الملف اللي بيسجّل الـ remotes اللي جايين منها الـ submodules.", "pinned commit": "الـ commit المحدد للمستودع المدمج اللي الأب بيسجّله وبيعمل له checkout.", "recurse-submodules": "علم لـ `git clone` بيعمل initialize وupdate للـ submodules أثناء الـ clone.", "submodule update": "الأمر اللي بيعمل checkout للـ commits المثبّتة المتسجلة في الـ index."},
                "job_relevance": "الفرق بتعيد استخدام مكتبات مشتركة بين المشاريع بالـ submodules، والمطور لازم يعرف إزاي الـ pinned commit بيتشارك — وإن الـ clone العادي مش بيجيب الكود المدمج لوحده.",
                "common_mistake": "متتوقعش إن `git clone` بيجيب الـ submodules افتراضياً؛ استخدم `--recurse-submodules`، أو نفّذ `git submodule init` و`git submodule update` بعد الـ clone.",
                "worked_example": "المثال بيعمل clone للمشروع، وبعدين بيعمل initialize لـ remotes الـ submodules، وبعدين بيعمل checkout للـ commits المثبّتة. ده مثال مكتوب — SkillBridge لا ينفذ هذه الأوامر ولا يعدّل أي مستودع أو submodule.",
                "depth_note": "محتوى تأسيسي ثابت لـ Git من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة `git clone`/`git submodule` القياسية. SkillBridge لا ينفذ هذه الأوامر، لذلك لا يعمل clone أو initialize أو update ولا يعدّل أي submodules في مستودع.",
            },
            "example": {"title": "اعمل clone لمشروع فيه submodules وجيبهم", "type": "bash", "content": "git clone https://example.com/team/library\ncd library\ngit submodule init\ngit submodule update", "explanation": "المثال بيعمل clone لمشروع `library` الأول، وبعدين بيعمل initialize لـ remotes الـ submodules من `.gitmodules`، وبعدين بيعمل checkout للـ commits المثبّتة في الـ index. الأوامر معروضة للشرح — SkillBridge لا ينفذها ولا يعمل clone أو تعديل لأي مستودع حقيقي أو submodule."},
            "practice": {"title": "اشرح عمل clone و initialize للـ submodules", "task": "اكتب بالظبط أوامر الطرفية اللي هتستخدمها: (1) لعمل clone لمشروع، و(2) لتسجيل remotes الـ submodules بـ `git submodule init`، و(3) لعمل checkout للـ commits المسجّلة بـ `git submodule update`. أضف جملة قصيرة تشرح إن الأب بيسجّل commit مثبّت (مش فرع متحرك)، ولاحظ إن دي إجابة مكتوبة — SkillBridge لا ينفذ هذه الأوامر ولا يعدّل أي submodules في أي مستودع.", "response_type": "code", "language": "bash", "competency": "Submodules", "starter_code": "git clone https://example.com/team/library\ngit submodule init\ngit submodule update", "evaluation_note": "SkillBridge بيعمل مراجعة ثابتة للنص فقط: بيتأكد من أمر الـ clone ومن `git submodule init` و`git submodule update` ومن ملاحظة الـ pinned commit ومن إن الإجابة مكتوبة. لا ينفذ هذه الأوامر ولا يعدّل أي submodules في مستودع، لذلك المراجعة لا تثبت إضافة أو تحديث أي submodule."},
            "mini_check": {"questions": [
                {"id": "m1", "question": "إيه هو الـ submodule؟", "options": ["مستودع Git مدمج جوه مستودع تاني عند commit مثبّت", "نسخة من فولدر واحد", "فرع على الـ remote", "تغيير مش متعمّد"], "misconception_hint": "الأب بيخزن commit محدد من المستودع المدمج، مش نسخ متفرقة من الملفات."},
                {"id": "m2", "question": "أي أمر بيعمل clone للمشروع و submodules مع بعض في خطوة واحدة؟", "options": ["git clone --recurse-submodules <url>", "git clone --depth 1 <url>", "git submodule deinit --all", "git reset --hard"], "misconception_hint": "الـ clone العادي مش بيجيب المستودعات المدمجة؛ علم الـ `--recurse-submodules` هو اللي بيجيبها."},
                {"id": "m3", "question": "الأب بيسجّل إيه لكل submodule؟", "options": ["commit مثبّت (SHA محدد)", "التاريخ الكامل للمستودع المدمج", "اسم فرع متحرك", "ملف مضغوط من الملفات"], "misconception_hint": "الـ submodule بيشاور على commit واحد محدد عشان أي checkout ياخد نفس النسخة."},
            ]},
        },
    },
}


GIT_WORKFLOWS_POLICY = {
    "status": "complete",
    "skill_aliases": ("git",),
    "competency": "Workflows & policy",
    "objective": "Describe feature-branch workflows, Pull Requests, code review, protected branches, and CI as team policy — without claiming any real branch protection or CI was configured.",
    "prerequisites": [{
        "competency": "Rebasing",
        "relationship": "required foundation",
        "why": "Team workflows are built on branches that keep history clean, so the learner must first understand branches and how rebase keeps a linear history.",
    }, {
        "competency": "git_rebasing",
        "relationship": "required foundation",
        "why": "Team workflows are built on branches that keep history clean, so the learner must first understand branches and how rebase keeps a linear history.",
    }],
    "roadmap_rationale": (
        "Workflows & policy is the tenth complete Git topic on the Git roadmap: feature "
        "branching, Pull Requests, code review, protected branches, and continuous "
        "integration turn single-developer Git into a team process. Rebasing is its declared "
        "prerequisite; Large-repo strategies is the final complete topic, and nothing Git "
        "stays planned after it."
    ),
    "learn": {
        "title": "Workflows & policy",
        "explanation": (
            "A **feature-branch workflow** keeps `main` protected and asks every developer "
            "to do work on a short-lived branch. You create one with `git switch -c "
            "feature-<name>`, commit on it, and push it to the remote. A **Pull Request** is "
            "not a native Git command — it is a **review step on the hosting service** that "
            "proposes merging your branch into another one, so teammates can read the diff "
            "and comment before anything lands. A **protected branch** is hosting-side policy "
            "that stops direct pushes to branches like `main` and requires reviews (and "
            "passing **CI** checks) before a merge is allowed. CI (continuous integration) "
            "runs automated builds and tests on every proposed change, so a red build blocks "
            "the merge instead of breaking `main`."
        ),
        "key_ideas": [
            "Feature branches isolate work; `git switch -c feature-<name>` starts one.",
            "A Pull Request is a review step on the hosting service, not a Git command.",
            "Protected branches block direct pushes and require reviews and green CI.",
            "CI runs builds and tests automatically on proposed changes before merge.",
        ],
        "key_terms": {
            "feature branch": "A short-lived branch created for one piece of work, then merged and deleted.",
            "Pull Request": "A hosting-service review step that proposes merging one branch into another.",
            "protected branch": "Hosting-side policy that prevents direct pushes and requires checks before merging.",
            "CI": "Continuous integration: automated builds and tests run on every proposed change.",
        },
        "job_relevance": "Companies ship through branches, Pull Requests, code review, protected branches, and CI; understanding the flow (and that policies live on the hosting service) is how a junior joins a team without breaking main.",
        "common_mistake": "Do not claim Git itself enforces protection or runs CI; protected branches and CI are hosting-service policy that must be configured there, and this lesson never claims any policy was actually configured.",
        "worked_example": "The example shows the branch, push, and merge commands a developer types, and explains that the Pull Request and branch protection live on the hosting service. It is a written example — the commands are not executed by SkillBridge and no policy is configured in any repository.",
        "depth_note": "Canonical Git foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard `git switch`/`git push`/`git merge` syntax and describe hosting-side Pull Requests and protection. SkillBridge does not run these commands, so it never pushes, creates a Pull Request, or configures any repository policy.",
        "grounding_sources": [
            {"title": "Pro Git book: Distributed Git — Contributing to a Project", "url": "https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project", "source": "Git official documentation"},
            {"title": "Git documentation: git-push", "url": "https://git-scm.com/docs/git-push", "source": "Git official documentation"},
            {"title": "Git documentation: git-switch", "url": "https://git-scm.com/docs/git-switch", "source": "Git official documentation"},
        ],
    },
    "example": {
        "title": "Take a feature branch through review",
        "type": "bash",
        "content": "git switch -c feature-login\ngit push origin feature-login\ngit merge feature-login",
        "explanation": "This example creates the feature branch, pushes it to the remote, and — after teammates review and approve the Pull Request on the hosting service and CI passes — merges it. The Pull Request and protection live on the hosting service, not in Git itself. The commands are shown for study — SkillBridge does not execute them and never configures any repository policy.",
    },
    "practice": {
        "type": "practical",
        "title": "Describe a feature-branch workflow under review policy",
        "task": "Write the exact terminal commands you would use to: (1) create a feature branch with `git switch -c feature-login`, (2) push it to the remote, and (3) merge it after review. Add one short sentence explaining that feature branches isolate work and that Pull Requests, protected branches, and CI are hosting-service policy, and note that this is a written answer — SkillBridge does not run these commands and no GitHub repository policy was configured.",
        "response_type": "code",
        "language": "bash",
        "competency": "Workflows & policy",
        "starter_code": "git switch -c feature-login\ngit push origin feature-login\ngit merge feature-login",
        "evaluation_note": "SkillBridge performs a static text review only: it checks for the branch creation, a push, a merge or Pull Request reference, a policy/protection/review note, and an explanation that this is a written answer. It does not run these commands or configure any repository policy, so the review cannot prove any branch was pushed or any policy was configured.",
    },
    "mini_check": {"questions": [
        {"id": "w1", "type": "mcq", "question": "Which command creates a feature branch and switches onto it?", "options": ["git switch -c feature-login", "git checkout main", "git push origin main", "git log --oneline"], "correct_answer": "git switch -c feature-login", "competency": "Workflows & policy", "difficulty": "advanced", "misconception_hint": "The `-c` flag creates the branch and the command switches onto it in one step."},
        {"id": "w2", "type": "mcq", "question": "What is a Pull Request?", "options": ["A review step on the hosting service that proposes merging a branch", "A native Git command that merges branches locally", "A backup of the repository", "A command that rewrites history"], "correct_answer": "A review step on the hosting service that proposes merging a branch", "competency": "Workflows & policy", "difficulty": "advanced", "misconception_hint": "Pull Requests exist on the hosting service, not as a built-in Git command."},
        {"id": "w3", "type": "mcq", "question": "What do protected branches and CI enforce?", "options": ["That changes are reviewed and tests pass before merging", "That every commit is rewritten", "That the repository is never pushed", "That only one developer can use Git"], "correct_answer": "That changes are reviewed and tests pass before merging", "competency": "Workflows & policy", "difficulty": "advanced", "misconception_hint": "Protection and CI are hosting-side policy that gates merges on review and green builds."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "الـ Workflows والسياسات",
                "explanation": "الـ **feature-branch workflow** بيحافظ على `main` محمي وبيطلب من كل مطور يشتغل على فرع قصير العمر. بتعمل فرع بـ `git switch -c feature-<name>`، وتعمل عليه commits، وبعدين بتدفعه للـ remote. الـ **Pull Request** مش أمر Git — هو **خطوة مراجعة على الـ hosting service** بتقترح دمج فرعك في فرع تاني، عشان زملائك يقرأوا الـ diff ويعلّقوا قبل ما أي حاجة تندمج. الـ **protected branch** سياسة على الـ hosting بتمنع الـ pushes المباشرة لـ branches زي `main` وبتطلب مراجعات (و **CI** ناجحة) قبل ما الدمج يتسمح به. الـ **CI** (التكامل المستمر) بيعمل builds و tests تلقائية على كل تغيير مقترح، فالـ build الأحمر بيحجب الدمج بدل ما يكسر `main`.",
                "key_ideas": ["الـ feature branches بتعزل الشغل؛ `git switch -c feature-<name>` بتبدأ واحدة.", "الـ Pull Request خطوة مراجعة على الـ hosting service، مش أمر Git.", "الـ protected branches بتمنع الـ pushes المباشرة وبتطلب مراجعات و CI ناجح.", "الـ CI بيشغّل builds و tests تلقائياً على التغييرات المقترحة قبل الدمج."],
                "key_terms": {"feature branch": "فرع قصير العمر متعمل لقطعة شغل واحدة، وبعدين بيتدمج ويتشال.", "Pull Request": "خطوة مراجعة على الـ hosting service بتقترح دمج فرع في فرع تاني.", "protected branch": "سياسة على الـ hosting بتمنع الـ pushes المباشرة وبتطلب فحوصات قبل الدمج.", "CI": "التكامل المستمر: builds و tests أوتوماتيك على كل تغيير مقترح."},
                "job_relevance": "الشركات بتشحن عن طريق branches وPull Requests و code review و protected branches و CI؛ فهَم العملية (وإن السياسات عايشة على الـ hosting service) هو اللي بيخلي مبتدئ يلتحق بفريق من غير ما يكسر main.",
                "common_mistake": "ما تدّعيش إن Git نفسه بينفّذ الحماية أو بيعمل CI؛ الـ protected branches والـ CI سياسات على الـ hosting لازم تتظبط هناك، والدرس ده عمره ما بيدّعي إن أي سياسة اتعملت بالفعل.",
                "worked_example": "المثال بيعرض أوامر الـ branch والـ push والـ merge اللي المطور بيكتبها، وبيشرح إن الـ Pull Request وحماية الفروع عايشين على الـ hosting service. ده مثال مكتوب — SkillBridge لا ينفذ هذه الأوامر ولا بيعمل أي سياسة في أي مستودع.",
                "depth_note": "محتوى تأسيسي ثابت لـ Git من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة `git switch`/`git push`/`git merge` القياسية وبتشرح الـ Pull Requests والحماية على الـ hosting. SkillBridge لا ينفذ هذه الأوامر، لذلك لا يدفع ولا يعمل Pull Request ولا يعمل أي سياسة في أي مستودع.",
            },
            "example": {"title": "خد فرع فيجر على مراجعة", "type": "bash", "content": "git switch -c feature-login\ngit push origin feature-login\ngit merge feature-login", "explanation": "المثال بيعمل فرع الفيجر، وبيدفعه للـ remote، وبعد ما الزملاء يراجعوا القيد في الـ Pull Request على الـ hosting service ويعدّي الـ CI — بيدمجه. الـ Pull Request والحماية عايشين على الـ hosting service، مش جوه Git نفسه. الأوامر معروضة للشرح — SkillBridge لا ينفذها ولا يعمل أي سياسة في أي مستودع."},
            "practice": {"title": "اشرح feature-branch workflow تحت سياسة مراجعة", "task": "اكتب بالظبط أوامر الطرفية اللي هتستخدمها: (1) لعمل feature branch بـ `git switch -c feature-login`، و(2) لدفعه للـ remote، و(3) لدمجه بعد المراجعة. أضف جملة قصيرة تشرح إن الـ feature branches بتعزل الشغل وإن الـ Pull Requests والـ protected branches والـ CI سياسات على الـ hosting service، ولاحظ إن دي إجابة مكتوبة — SkillBridge لا ينفذ هذه الأوامر ولا اتعملت أي سياسة على أي GitHub repository.", "response_type": "code", "language": "bash", "competency": "Workflows & policy", "starter_code": "git switch -c feature-login\ngit push origin feature-login\ngit merge feature-login", "evaluation_note": "SkillBridge بيعمل مراجعة ثابتة للنص فقط: بيتأكد من عمل الفرع ومن push ومن ذكر merge أو Pull Request ومن ملاحظة السياسة والحماية/المراجعة ومن إن الإجابة مكتوبة. لا ينفذ هذه الأوامر ولا يعمل أي سياسة في أي مستودع، لذلك المراجعة لا تثبت إن أي فرع اتدفع أو أي سياسة اتعملت."},
            "mini_check": {"questions": [
                {"id": "w1", "question": "أي أمر بيعمل feature branch وبيحوّل عليه؟", "options": ["git switch -c feature-login", "git checkout main", "git push origin main", "git log --oneline"], "misconception_hint": "علم الـ `-c` بيعمل الفرع والأمر بيحوّل عليه في خطوة واحدة."},
                {"id": "w2", "question": "إيه هو الـ Pull Request؟", "options": ["خطوة مراجعة على الـ hosting service بتقترح دمج فرع", "أمر Git أصلي بيدمج فروع محلياً", "نسخة احتياطية من المستودع", "أمر بيعيد كتابة التاريخ"], "misconception_hint": "الـ Pull Requests عايشين على الـ hosting service، مش أمر Git مدمج."},
                {"id": "w3", "question": "الـ protected branches والـ CI بينفّذوا إيه؟", "options": ["إن التغييرات تتُراجع والاختبارات تعدي قبل الدمج", "إن كل commit يتعاد كتابته", "إن المستودع عمره ما يتدفع", "إن مطور واحد بس يقدر يستخدم Git"], "misconception_hint": "الحماية والـ CI سياسات على الـ hosting بتحجب الدمج غير المراجع أو الفاشل."},
            ]},
        },
    },
}


GIT_LARGE_REPO_STRATEGIES = {
    "status": "complete",
    "skill_aliases": ("git",),
    "competency": "Large-repo strategies",
    "objective": "Describe shallow clones, partial clones, sparse checkout, and Git LFS as ways to handle very large repositories, including their limitations and trade-offs — without claiming any performance gain was measured.",
    "prerequisites": [{
        "competency": "History rewriting",
        "relationship": "required foundation",
        "why": "Choosing a clone strategy is easier once the learner understands history, so rewriting and inspecting history must come first.",
    }, {
        "competency": "git_history_rewriting",
        "relationship": "required foundation",
        "why": "Choosing a clone strategy is easier once the learner understands history, so rewriting and inspecting history must come first.",
    }, {
        "competency": "Bisect & debugging",
        "relationship": "required foundation",
        "why": "Debugging a huge repository depends on navigating history with bisect, so the learner must already be comfortable with advanced Git history tools.",
    }, {
        "competency": "git_bisect_debugging",
        "relationship": "required foundation",
        "why": "Debugging a huge repository depends on navigating history with bisect, so the learner must already be comfortable with advanced Git history tools.",
    }],
    "roadmap_rationale": (
        "Large-repo strategies is the eleventh and final complete Git topic on the Git "
        "roadmap: after history rewriting and bisect, the learner has the advanced skills a "
        "huge repository demands, and this topic explains how to fetch and work with it "
        "efficiently. It declares History rewriting AND Bisect & debugging as prerequisites; "
        "with it, all eleven Git blueprint topics are complete canonical content."
    ),
    "learn": {
        "title": "Large-repo strategies",
        "explanation": (
            "Very large repositories can be fetched and worked on in several ways. A "
            "**shallow clone** (`git clone --depth 1`) copies only the latest commit instead "
            "of the whole history — fast, but you lose history, so commands like `git log` "
            "and `git blame` are limited. A **partial clone** (`git clone "
            "--filter=blob:none`) fetches tree and commit objects eagerly but downloads blobs "
            "on demand — lighter until you touch many files. A **sparse checkout** "
            "(`git sparse-checkout set src tests`) restricts the working tree to the "
            "directories you need, which helps in monorepos with millions of files. **Git "
            "LFS** (`git lfs install` then `git lfs track \"*.psd\"`) stores large binaries "
            "on a separate server and keeps lightweight pointers in the repository. Every "
            "strategy has a limitation: shallow clones cannot rebase onto older history, "
            "partial clones need network for missing blobs, sparse checkout only narrows the "
            "working tree, and LFS moves the burden to a separate server."
        ),
        "key_ideas": [
            "Shallow clones (`--depth 1`) skip history for a smaller, faster clone.",
            "Partial clones (`--filter=blob:none`) fetch blobs on demand.",
            "Sparse checkout limits the working tree to chosen directories.",
            "Git LFS keeps large binaries on a server and lightweight pointers in the repo.",
            "Each strategy trades something away: history, network, or server-side storage.",
        ],
        "key_terms": {
            "shallow clone": "A clone with only the most recent commits (`git clone --depth 1`).",
            "partial clone": "A clone that lazily downloads blobs on demand (`--filter=blob:none`).",
            "sparse checkout": "Limiting the working tree to specific directories.",
            "Git LFS": "Git Large File Storage, which stores large files on a server and pointers in the repo.",
        },
        "job_relevance": "Monorepos and asset-heavy projects do not fit a plain clone; choosing shallow, partial, sparse, and LFS with their trade-offs is how developers stay productive in very large repositories.",
        "common_mistake": "Do not expect one strategy to solve everything; each trades something off (history, on-demand network, working-tree scope, or server storage), and no performance improvement is claimed or measured here.",
        "worked_example": "The example shows the exact commands for a shallow clone, a partial clone, a sparse checkout, and Git LFS setup. It is a written example — the commands are not executed by SkillBridge and no clone, sparse checkout, or LFS configuration is made to any real repository.",
        "depth_note": "Canonical Git foundation content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": "Examples use standard `git clone --depth`, `git clone --filter`, `git sparse-checkout`, and `git lfs` syntax. SkillBridge does not run these commands and never measures any performance improvement.",
        "grounding_sources": [
            {"title": "Git documentation: git-clone", "url": "https://git-scm.com/docs/git-clone", "source": "Git official documentation"},
            {"title": "Pro Git book: Git Tools — Submodules (large repositories)", "url": "https://git-scm.com/book/en/v2/Git-Tools-Submodules", "source": "Git official documentation"},
            {"title": "Git LFS official site", "url": "https://git-lfs.com/", "source": "Git LFS official documentation"},
        ],
    },
    "example": {
        "title": "Fetch and work on a very large repository safely",
        "type": "bash",
        "content": "git clone --depth 1 https://example.com/big-project\ngit clone --filter=blob:none https://example.com/big-project\ngit sparse-checkout set src tests\ngit lfs install\ngit lfs track \"*.psd\"",
        "explanation": "This example shows a shallow clone that skips history, a partial clone that avoids downloading blobs eagerly, a sparse checkout that narrows the working tree to chosen directories, and Git LFS setup that keeps large binaries on a separate server. The commands are shown for study — SkillBridge does not execute them and never clones, filters, or configures LFS in any real repository or measures performance.",
    },
    "practice": {
        "type": "practical",
        "title": "Describe strategies for very large repositories",
        "task": "Write the exact terminal commands you would use to: (1) make a shallow clone with `git clone --depth 1`, (2) start a partial clone with `git clone --filter=blob:none`, (3) set a sparse checkout to `src` and `tests` with `git sparse-checkout set src tests`, and (4) enable Git LFS with `git lfs install`. Add one short sentence naming the limitations or trade-offs (history, on-demand network, working-tree scope, server storage), and note that this is a written answer — SkillBridge does not run these commands and no performance improvement was measured.",
        "response_type": "code",
        "language": "bash",
        "competency": "Large-repo strategies",
        "starter_code": "git clone --depth 1 https://example.com/big-project\ngit clone --filter=blob:none https://example.com/big-project\ngit sparse-checkout set src tests\ngit lfs install",
        "evaluation_note": "SkillBridge performs a static text review only: it checks for a shallow clone, a partial clone (`--filter`), a sparse checkout, a Git LFS command, a limitations/trade-offs note, and an explanation that this is a written answer. It does not run these commands or measure performance, so the review cannot prove any performance improvement.",
    },
    "mini_check": {"questions": [
        {"id": "l1", "type": "mcq", "question": "What does a shallow clone (`git clone --depth 1`) do?", "options": ["Copies only the latest commit history instead of the full history", "Copies every commit in full", "Deletes files over a size limit", "Converts the repository to a single file"], "correct_answer": "Copies only the latest commit history instead of the full history", "competency": "Large-repo strategies", "difficulty": "advanced", "misconception_hint": "The `--depth` flag trims history, which is why it is called shallow."},
        {"id": "l2", "type": "mcq", "question": "Which tool keeps very large binary files out of the repository?", "options": ["Git LFS (`git lfs track \"*.psd\"`)", "git commit --amend", "git rebase -i main", "git bisect reset"], "correct_answer": "Git LFS (`git lfs track \"*.psd\"`)", "competency": "Large-repo strategies", "difficulty": "advanced", "misconception_hint": "LFS stores the large file on a server and keeps only a lightweight pointer in Git."},
        {"id": "l3", "type": "mcq", "question": "Which strategy limits the working tree to chosen directories?", "options": ["Sparse checkout (`git sparse-checkout set src tests`)", "Shallow clone", "Partial clone", "Git LFS"], "correct_answer": "Sparse checkout (`git sparse-checkout set src tests`)", "competency": "Large-repo strategies", "difficulty": "advanced", "misconception_hint": "Sparse checkout narrows what is checked out, not what is stored."},
    ]},
    "locales": {
        "ar": {
            "learn": {
                "title": "استراتيجيات المستودعات الضخمة",
                "explanation": "المستودعات الضخمة جداً ممكن تتسحب وتتشغل عليها بطرق كتير. **Shallow clone** (`git clone --depth 1`) بينسخ آخر commit بس بدل التاريخ الكامل — سريع، بس بتخسر التاريخ، فأوامر زي `git log` و`git blame` بتبقى محدودة. **Partial clone** (`git clone --filter=blob:none`) بيجيب الـ commits والـ trees بحماس بس بيحمّل الـ blobs عند الحاجة — أخف لحد ما تلمس ملفات كتير. **Sparse checkout** (`git sparse-checkout set src tests`) بيحصر شجرة الشغل في الفولدرات اللي محتاجها، وبيوفّر في الـ monorepos اللي فيها ملايين الملفات. **Git LFS** (`git lfs install` وبعدين `git lfs track \"*.psd\"`) بيخزن الملفات الكبيرة على سيرفر منفصل وبيحتفظ بمؤشرات خفيفة جوه المستودع. كل استراتيجية ليها حد: الـ shallow clones مبتقدرش تعمل rebase على تاريخ أقدم، والـ partial clones محتاجة نت للـ blobs الناقصة، والـ sparse checkout بيحصّر شجرة الشغل بس، والـ LFS بينقل العبء لسيرفر منفصل.",
                "key_ideas": ["الـ shallow clones (`--depth 1`) بتتخطى التاريخ عشان clone أصغر وأسرع.", "الـ partial clones (`--filter=blob:none`) بتنزّل الـ blobs وقت الحاجة.", "الـ sparse checkout بيحصر شجرة الشغل في فولدرات محددة.", "الـ Git LFS بيخزّن الملفات الكبيرة على سيرفر وبيركّب مؤشرات خفيفة في المستودع.", "كل استراتيجية بتستغني عن حاجة: تاريخ، أو نت، أو مساحة على السيرفر."],
                "key_terms": {"shallow clone": "Clone فيه أحدث الـ commits بس (`git clone --depth 1`).", "partial clone": "Clone بينزّل الـ blobs كسول عند الحاجة (`--filter=blob:none`).", "sparse checkout": "تحديد شجرة الشغل لفولدرات معينة بس.", "Git LFS": "Git Large File Storage، بيخزن الملفات الكبيرة على سيرفر ومؤشراتها في المستودع."},
                "job_relevance": "الـ monorepos والمشاريع الغنية بالملفات الكبيرة مش بتنفع مع clone عادي؛ اختيار shallow وpartial وsparse وLFS بمقايضاتهم هو اللي بيخلي المطور منتج في المستودعات الضخمة.",
                "common_mistake": "متتوقعش إن استراتيجية واحدة تحل كل حاجة؛ كل واحدة بتستغني عن حاجة (تاريخ، أو نت عند الطلب، أو نطاق شجرة الشغل، أو تخزين على السيرفر)، ولا بيدّعي ولا بيقيس أي تحسين في الأداء هنا.",
                "worked_example": "المثال بيعرض الأوامر بالظبط لـ shallow clone و partial clone و sparse checkout وإعداد Git LFS. ده مثال مكتوب — SkillBridge لا ينفذ هذه الأوامر ولا بيعمل clone أو sparse checkout أو إعداد LFS لأي مستودع حقيقي.",
                "depth_note": "محتوى تأسيسي ثابت لـ Git من قاعدة المعرفة المراجَعة، وليس محتوى مولداً حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صياغة `git clone --depth` و`git clone --filter` و`git sparse-checkout` و`git lfs` القياسية. SkillBridge لا ينفذ هذه الأوامر ولا يقيس أي تحسين في الأداء.",
            },
            "example": {"title": "اسحب واشتغل على مستودع ضخم بأمان", "type": "bash", "content": "git clone --depth 1 https://example.com/big-project\ngit clone --filter=blob:none https://example.com/big-project\ngit sparse-checkout set src tests\ngit lfs install\ngit lfs track \"*.psd\"", "explanation": "المثال بيعرض shallow clone بيتخطى التاريخ، وpartial clone مش بينزّل الـ blobs بحماس، وsparse checkout بيحصر شجرة الشغل في فولدرات، وإعداد Git LFS اللي بيخزن الملفات الكبيرة على سيرفر منفصل. الأوامر معروضة للشرح — SkillBridge لا ينفذها ولا يعمل clone أو filter أو إعداد LFS في أي مستودع حقيقي ولا يقيس أداء."},
            "practice": {"title": "اشرح استراتيجيات المستودعات الضخمة", "task": "اكتب بالظبط أوامر الطرفية اللي هتستخدمها: (1) لعمل shallow clone بـ `git clone --depth 1`، و(2) لبدء partial clone بـ `git clone --filter=blob:none`، و(3) لتحديد sparse checkout لـ `src` و`tests` بـ `git sparse-checkout set src tests`، و(4) لتفعيل Git LFS بـ `git lfs install`. أضف جملة قصيرة تسمّي القيود أو المقايضات (التاريخ، أو النت عند الطلب، أو نطاق شجرة الشغل، أو تخزين السيرفر)، ولاحظ إن دي إجابة مكتوبة — SkillBridge لا ينفذ هذه الأوامر ولا اتقاس أي تحسين في الأداء.", "response_type": "code", "language": "bash", "competency": "Large-repo strategies", "starter_code": "git clone --depth 1 https://example.com/big-project\ngit clone --filter=blob:none https://example.com/big-project\ngit sparse-checkout set src tests\ngit lfs install", "evaluation_note": "SkillBridge بيعمل مراجعة ثابتة للنص فقط: بيتأكد من shallow clone ومن partial clone (`--filter`) ومن sparse checkout ومن أمر Git LFS ومن ملاحظة القيود/المقايضات ومن إن الإجابة مكتوبة. لا ينفذ هذه الأوامر ولا يقيس الأداء، لذلك المراجعة لا تثبت أي تحسين في الأداء."},
            "mini_check": {"questions": [
                {"id": "l1", "question": "الـ shallow clone (`git clone --depth 1`) بيعمل إيه؟", "options": ["بينسخ آخر commit بس بدل التاريخ الكامل", "بينسخ كل commit كامل", "بيحذف الملفات اللي أكبر من حجم", "بيحوّل المستودع لملف واحد"], "misconception_hint": "علم الـ `--depth` بيقصّ التاريخ، وعلشان كده اسمه shallow."},
                {"id": "l2", "question": "أي أداة بتبعد الملفات الضخمة عن المستودع نفسه؟", "options": ["Git LFS (`git lfs track \"*.psd\"`)", "git commit --amend", "git rebase -i main", "git bisect reset"], "misconception_hint": "LFS بيخزّن الملف الكبير على سيرفر وبيحتفظ بمؤشر خفيف بس في Git."},
                {"id": "l3", "question": "أي استراتيجية بتحدّ شجرة الشغل لفولدرات معينة؟", "options": ["Sparse checkout (`git sparse-checkout set src tests`)", "Shallow clone", "Partial clone", "Git LFS"], "misconception_hint": "الـ sparse checkout بيحصّر اللي بيتعمل له checkout، مش اللي بيتخزن."},
            ]},
        },
    },
}


DOCKER_CONTAINERS = {
    "status": "complete",
    "skill_aliases": ("docker", "docker & containers"),
    "competency": "Containers",
    "objective": "Run, inspect, stop, and remove a named container with the modern Docker CLI.",
    "objectives": [
        "Explain what a container is: an isolated running instance of an image.",
        "Start a named background container with `docker run -d --name`.",
        "Check running and stopped containers with `docker ps` and `docker ps -a`, and read output with `docker logs`.",
        "Stop a container with `docker stop`, restart it with `docker start`, and remove it with `docker rm`.",
    ],
    "prerequisites": [],
    "roadmap_rationale": (
        "Containers is the first complete Docker topic because every later Docker topic — images, Dockerfiles, "
        "ports, volumes, networking, Compose — operates on a running container. Starting here means the "
        "learner can always answer 'what is running, and why did it stop?' before building anything."
    ),
    "learn": {
        "title": "Containers",
        "explanation": (
            "A **container** is a running instance of an **image**: an isolated process with its own filesystem, "
            "started by the Docker Engine. `docker run` creates and starts one, `-d` runs it in the background "
            "(detached), and `--name` gives it a stable name every later command can use."
        ),
        "key_ideas": [
            "`docker run -d --name web -p 8080:80 nginx:1.27` starts a background container named `web` from the `nginx:1.27` image and maps host port 8080 to container port 80.",
            "`docker ps` lists running containers; `docker ps -a` also includes stopped ones.",
            "`docker logs web` shows a container's output; `docker inspect web` shows its full configuration.",
            "`docker stop web` stops the container but keeps it (restart with `docker start web`); `docker rm web` removes it and only works once it is stopped (or with `-f`).",
        ],
        "key_terms": {
            "container": "A running, isolated instance of an image managed by the Docker Engine.",
            "image": "The read-only template a container is started from.",
            "detached mode": "Running a container in the background with `-d` instead of tying up your terminal.",
            "container name": "The stable label passed with `--name`, used by logs, stop, start, and rm.",
        },
        "job_relevance": (
            "Deploying, checking, and restarting services in containers is day-to-day work for backend, DevOps, "
            "and data engineers. 'Is it running, and what did it log?' is the first question in almost every "
            "container incident."
        ),
        "real_world_example": (
            "A teammate pings you: 'the staging API stopped responding.' You run `docker ps` — the API container "
            "is not listed, but `docker ps -a` shows it exited 20 minutes ago. You read `docker logs` to find the "
            "crash reason, fix the cause, then `docker start` the same container (or `docker rm` it and run a "
            "fresh one). The container lifecycle is how you answer 'what is running and why did it stop?' in minutes."
        ),
        "common_mistake": "Do not confuse a container with an image: the image is the template, the container is the running instance. Removing the container does not remove the image, and a stopped container still exists until you run `docker rm`.",
        "worked_example": "The example starts one background nginx container, checks it, reads its logs, then stops and removes it.",
        "depth_note": "Canonical beginner content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": (
            "Examples use the modern unified Docker CLI (Docker Engine 23 and later; `docker run` is the shorthand "
            "for `docker container run`). SkillBridge does not execute Docker commands; the outputs described are "
            "what Docker prints when a command succeeds."
        ),
        "grounding_sources": [
            {"title": "Docker docs: What is a container?", "url": "https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/", "source": "Docker documentation"},
            {"title": "docker container run reference", "url": "https://docs.docker.com/reference/cli/docker/container/run/", "source": "Docker documentation"},
        ],
    },
    "example": {
        "title": "Run, check, and stop a container",
        "type": "bash",
        "content": (
            "# 1) start a background container from a pinned image\n"
            "docker run -d --name web -p 8080:80 nginx:1.27\n"
            "\n"
            "# 2) confirm it is running\n"
            "docker ps\n"
            "\n"
            "# 3) read its output\n"
            "docker logs web\n"
            "\n"
            "# 4) stop it (it still exists, stopped)\n"
            "docker stop web\n"
            "\n"
            "# 5) remove it for good\n"
            "docker rm web"
        ),
        "explanation": (
            "Each step is one stage of the container lifecycle: `docker run` creates and starts, `docker ps` "
            "confirms, `docker logs` reads output, `docker stop` stops without deleting, and `docker rm` removes. "
            "This is a worked example for reading — SkillBridge does not run these commands."
        ),
    },
    "practice": {
        "type": "practical",
        "title": "Bring a service container back to life",
        "task": (
            "Your team's staging web service runs in a Docker container, and a teammate reports it is down. "
            "Write the concrete Docker commands you would run to: (1) check whether the container is running "
            "or stopped, (2) read its recent logs to find why it stopped, (3) start it again if it is stopped, "
            "and (4) remove it cleanly if you instead need to re-run it fresh from the same image. For each "
            "command, add one line saying what success looks like (what Docker prints, or how you verify the "
            "container is healthy again). Finally, explain in one or two sentences how you would debug the "
            "case where `docker logs` shows the container exits immediately after starting. SkillBridge reviews "
            "your commands as text only — it never executes them."
        ),
        "response_type": "command",
        "competency": "Containers",
        "evaluation_note": (
            "Static text review only: SkillBridge checks for concrete `docker ps` / `docker ps -a`, "
            "`docker logs`, `docker start`, and `docker rm` usage against a named container, plus a stated "
            "verification step for each. It does not run Docker, so the review cannot prove runtime results. "
            "A strong answer names the container, uses the right lifecycle command for each step, states how "
            "each step is verified, and gives a concrete debugging idea for the immediate-exit case (for "
            "example: read the logs' error line, check the container's command, or run it once in the "
            "foreground to see the failure). A weak answer says 'restart Docker' or 'delete and retry' with "
            "no logs check, no container name, and no verification."
        ),
    },
    "mini_check": {
        "questions": [
            {"id": "c1", "type": "mcq", "question": "Which command lists containers that have already stopped?", "options": ["docker ps", "docker ps -a", "docker logs", "docker images"], "correct_answer": "docker ps -a", "competency": "Containers", "difficulty": "beginner", "misconception_hint": "One flag widens the default listing to include exited containers."},
            {"id": "c2", "type": "mcq", "question": "What is true right after `docker stop web` finishes?", "options": ["It is deleted from disk immediately", "It still exists and can be started again with `docker start web`", "Its image is removed too", "It restarts automatically"], "correct_answer": "It still exists and can be started again with `docker start web`", "competency": "Containers", "difficulty": "beginner", "misconception_hint": "Stopping and removing are separate steps in the container lifecycle."},
            {"id": "c3", "type": "mcq", "question": "In `docker run -d --name web -p 8080:80 nginx:1.27`, what does `-d` do?", "options": ["Runs the container in the background (detached)", "Deletes the container when it exits", "Publishes port 8080", "Pins the image by digest"], "correct_answer": "Runs the container in the background (detached)", "competency": "Containers", "difficulty": "beginner", "misconception_hint": "The flag changes how the container attaches to your terminal, not its networking."},
        ]
    },
    # Display translations deliberately retain canonical English answer values;
    # the persisted Mini Check continues to grade the immutable canonical set.
    "locales": {
        "ar": {
            "learn": {
                "title": "حاويات Docker",
                "explanation": "**الحاوية** هي نسخة شغالة من **صورة (image)**: عملية معزولة ليها نظام ملفات خاص بيها، بيشغّلها Docker Engine. الأمر `docker run` بيعمل الحاوية ويشغّلها، و`-d` بيخلّيها تشتغل في الخلفية (detached)، و`--name` بيديها اسم ثابت تقدر تستخدمه في كل الأوامر اللي بعد كده.",
                "key_ideas": [
                    "`docker run -d --name web -p 8080:80 nginx:1.27` يشغّل حاوية في الخلفية اسمها `web` من صورة `nginx:1.27` وبيوصّل بورت 8080 على جهازك ببورت 80 جوه الحاوية.",
                    "`docker ps` بيوريك الحاويات اللي شغالة؛ `docker ps -a` بيشمل كمان اللي واقفة.",
                    "`docker logs web` بيوريك اللي الحاوية طبعت؛ `docker inspect web` بيعرض كل إعداداتها.",
                    "`docker stop web` بيوقفها بس مش بيحذفها (ترجع تشتغل بـ `docker start web`)؛ `docker rm web` بيحذفها وبيشتغل بس لما تكون واقفة (أو بـ `-f`).",
                ],
                "key_terms": {"حاوية": "نسخة شغالة معزولة من صورة، بيتحكم فيها Docker Engine.", "صورة": "القالب اللي الحاوية بتبدأ منه.", "detached": "تشغيل الحاوية في الخلفية بـ `-d` بدل ما تفضل ماسكة الترمينال.", "اسم الحاوية": "الاسم الثابت اللي بتحدده بـ `--name`، بتستخدمه مع logs وstop وstart وrm."},
                "job_relevance": "تشغيل الخدمات وفحصها وإعادة تشغيلها في حاويات شغل يومي لمهندسي الـ backend والـ DevOps والداتا — «الحاوية شغالة ولا لأ، وطبعت إيه؟» أول سؤال في أغلب مشاكل الحاويات.",
                "real_world_example": "زميلك بيكتب لك: «الـ API بتاع الـ staging مش بيرد.» تجري `docker ps` — الحاوية مش موجودة في القايمة، بس `docker ps -a` بيقولك انتهت من ٢٠ دقيقة. بتقرا `docker logs` تعرف سبب الوقوف، تصلّح المشكلة، وبعدين يا إما `docker start` لنفس الحاوية يا إما `docker rm` وتشغّل واحدة جديدة. دورة حياة الحاوية هي اللي بتخلّيك تجاوب على «إيه اللي شغال وليه وقف؟» في دقايق.",
                "common_mistake": "ما تخلطش بين الحاوية والصورة: الصورة هي القالب، والحاوية هي النسخة اللي شغالة. حذف الحاوية مش بيحذف الصورة، والحاوية اللي واقفة لسه موجودة لحد ما تعمل `docker rm`.",
                "worked_example": "المثال يشغّل حاوية nginx في الخلفية، بيتأكد منها، بيقرا الـ logs، وبعدين بيوقفها ويحذفها.",
                "depth_note": "محتوى تأسيسي ثابت من قاعدة المعرفة المراجَعة، مش محتوى مولّد حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم الـ Docker CLI الحديث (Docker Engine 23 وما بعده؛ `docker run` اختصار لـ `docker container run`). SkillBridge ما بينفّذش أوامر Docker؛ المخرجات الموصوفة هي اللي Docker بيطبعها لما الأمر ينجح.",
            },
            "example": {
                "title": "شغّل وافحص ووقّف حاوية",
                "type": "bash",
                "content": "# 1) start a background container from a pinned image\ndocker run -d --name web -p 8080:80 nginx:1.27\n\n# 2) confirm it is running\ndocker ps\n\n# 3) read its output\ndocker logs web\n\n# 4) stop it (it still exists, stopped)\ndocker stop web\n\n# 5) remove it for good\ndocker rm web",
                "explanation": "كل خطوة بتمثل مرحلة في دورة حياة الحاوية: `docker run` ينشئ ويشغّل، `docker ps` يتأكد، `docker logs` يقرا المخرجات، `docker stop` يوقف من غير حذف، و`docker rm` يحذف نهائي. ده مثال للقراية — SkillBridge ما بينفّذش الأوامر دي.",
            },
            "practice": {
                "title": "رجّع حاوية الخدمة للشغل",
                "task": "خدمة الويب بتاعة فريقكم شغالة في حاوية Docker، وزميلك بلّغ إنها واقفة. اكتب أوامر Docker اللي هتشغّلها عشان: (١) تعرف الحاوية شغالة ولا واقفة، (٢) تقرا الـ logs الأخيرة عشان تعرف ليه وقفت، (٣) تشغّلها تاني لو واقفة، و(٤) تحذفها بنضافة لو قررت تشغّل واحدة جديدة من نفس الصورة. مع كل أمر اكتب سطر يقول النجاح شكله إيه (Docker هيطبع إيه، أو هتتأكد إزاي إن الحاوية رجعت سليمة). وفي الآخر اشرح في سطر أو اتنين هتصلّح إزاي الحالة اللي `docker logs` بيظهر فيها إن الحاوية بتنتهي فورًا بعد ما تشتغل. SkillBridge بيراجع أوامرك كنص بس — مش بينفّذها.",
                "response_type": "command",
                "competency": "Containers",
                "evaluation_note": "مراجعة نصية ثابتة فقط: SkillBridge بيتأكد من استخدام `docker ps` / `docker ps -a` و`docker logs` و`docker start` و`docker rm` مع حاوية باسمها، ومن وجود خطوة تحقق لكل أمر. مش بيشغّل Docker، فالمراجعة ما بتثبتش نتيجة تشغيل. الإجابة القوية بتسمّي الحاوية، وتستخدم أمر دورة الحياة الصح لكل خطوة، وتقول إزاي بتتأكد من كل خطوة، وبتفكرة حقيقية لحالة الخروج الفوري (مثلًا: قرا سطر الخطأ في الـ logs، أو شغّلها مرة في الـ foreground تشوف الفشل بعينك). الإجابة الضعيفة بتقول «أعمل ريستارت لـ Docker» أو «امسحها وحاول تاني» من غير قراية logs ولا اسم حاوية ولا أي تحقق.",
            },
            "mini_check": {"questions": [
                {"id": "c1", "question": "أي أمر بيوريك الحاويات اللي وقفت خلاص؟", "options": ["docker ps", "docker ps -a", "docker logs", "docker images"], "misconception_hint": "فيه فلاغ واحد بيوسّع القايمة الافتراضية عشان تشمل الحاويات اللي انتهت."},
                {"id": "c2", "question": "إيه اللي بيحصل بعد ما `docker stop web` يخلص؟", "options": ["بتتحذف من على الديسك فورًا", "لسه موجودة وممكن ترجع تشتغل بـ `docker start web`", "صورتها بتتحذف معاها", "بتشتغل تاني لوحدها"], "misconception_hint": "الإيقاف والحذف خطوتين منفصلتين في دورة حياة الحاوية."},
                {"id": "c3", "question": "في `docker run -d --name web -p 8080:80 nginx:1.27`، `-d` بيعمل إيه؟", "options": ["بيشغّل الحاوية في الخلفية (detached)", "بيحذف الحاوية لما تخلص", "بينشر بورت 8080", "بتثبيت الصورة بالـ digest"], "misconception_hint": "الفلاغ ده بيغيّر إزاي الحاوية بتتوصّل بالترمينال بتاعك، مش الشبكة."},
            ]},
        },
    },
}


DOCKER_IMAGES = {
    "status": "complete",
    "skill_aliases": ("docker", "docker & containers"),
    "competency": "Images",
    "objective": "Pull a version-pinned image, inspect and list local images, retag one, and remove an unused image.",
    "objectives": [
        "Explain what an image is: a read-only, layered template identified by a tag or digest.",
        "Pull an exact version with `docker pull nginx:1.27` instead of an unpinned `:latest`.",
        "List local images with `docker images` and inspect one with `docker image inspect`.",
        "Retag an image with `docker tag` and remove an unused one with `docker rmi`.",
    ],
    "prerequisites": [
        {
            "competency": "Containers",
            "relationship": "required foundation",
            "why": "An image only matters once you can run it: the run/stop lifecycle from Containers is the context for pulling, pinning, and cleaning up images.",
        },
    ],
    "roadmap_rationale": (
        "Images follows Containers because every container is started from an image: you learn to run one "
        "before you learn where it comes from, how it is versioned, and how to keep the local store clean. "
        "Dockerfile, Ports, and Volumes later build on both."
    ),
    "learn": {
        "title": "Images",
        "explanation": (
            "An **image** is the read-only template a container starts from: stacked **layers** identified by a "
            "**tag** such as `nginx:1.27` (or an immutable **digest**). `docker pull` downloads it to your machine "
            "once; containers then start from that local copy."
        ),
        "key_ideas": [
            "`docker pull nginx:1.27` downloads that exact version; a plain `docker pull nginx` means `:latest`, a moving pointer that can change underneath you.",
            "`docker images` lists what is stored locally: repository, tag, image ID, and size.",
            "Layers are shared: pulling `nginx:1.27-bookworm` after `nginx:1.27` reuses the identical layers instead of downloading them again.",
            "`docker tag` adds another name to an image; `docker rmi` removes an image only when no container (running or stopped) still uses it.",
        ],
        "key_terms": {
            "image": "The read-only, layered template containers are started from.",
            "tag": "A mutable label such as `1.27` or `latest` pointing at one image version.",
            "digest": "The immutable `sha256:...` identifier that pins exactly one image.",
            "layer": "A reusable filesystem step shared between images.",
        },
        "job_relevance": (
            "Every deployment review asks 'which exact image version is running?'. Pinning tags (or digests) and "
            "knowing what is stored on a server is daily work for anyone who ships services."
        ),
        "real_world_example": (
            "A security audit flags `nginx:latest` on your server — nobody can say which version that pulled. "
            "You pin instead: `docker pull nginx:1.27`, retag your copy for the company registry with "
            "`docker tag nginx:1.27 myregistry.local:5000/web:1.27`, remove the stale entry with `docker rmi`, "
            "and record the image ID in the deployment ticket. At the next audit you answer with one command: "
            "`docker images`."
        ),
        "common_mistake": "Do not rely on `:latest` in anything that must be reproducible: it is a moving pointer, so the same command can pull a different image next month. Pin a version tag (or a digest) instead.",
        "worked_example": "The example pins a version, verifies what is stored locally, retags it for an internal registry, and removes an old image.",
        "depth_note": "Canonical beginner content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": (
            "Examples use the modern unified Docker CLI (Docker Engine 23 and later; `docker pull` is the shorthand "
            "for `docker image pull`, and image IDs are content-addressed SHA-256 digests). SkillBridge does not "
            "execute Docker commands or pull anything."
        ),
        "grounding_sources": [
            {"title": "Docker docs: What is an image?", "url": "https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/", "source": "Docker documentation"},
            {"title": "docker image pull reference", "url": "https://docs.docker.com/reference/cli/docker/image/pull/", "source": "Docker documentation"},
        ],
    },
    "example": {
        "title": "Pull, verify, retag, and clean up an image",
        "type": "bash",
        "content": (
            "# 1) pull an exact version, not :latest\n"
            "docker pull nginx:1.27\n"
            "\n"
            "# 2) confirm it is stored locally\n"
            "docker images\n"
            "\n"
            "# 3) inspect the pinned image (image ID, layers, env)\n"
            "docker image inspect nginx:1.27\n"
            "\n"
            "# 4) retag it for an internal registry\n"
            "docker tag nginx:1.27 myregistry.local:5000/web:1.27\n"
            "\n"
            "# 5) remove an old image no container uses\n"
            "docker rmi nginx:1.25"
        ),
        "explanation": (
            "`docker pull` downloads the pinned version once; `docker images` proves what is stored locally; "
            "`docker image inspect` shows the image ID and layers; `docker tag` adds a registry name without "
            "copying; `docker rmi` frees an unused image. Worked example for reading — SkillBridge does not run "
            "these commands."
        ),
    },
    "practice": {
        "type": "practical",
        "title": "Make a deployment reproducible",
        "task": (
            "Your server currently runs `nginx:latest` and nobody can say which version that is — so the next "
            "deploy is not reproducible. Write the Docker commands you would run to: (1) pull a pinned public "
            "version of the image, (2) verify exactly what is now stored locally, including its identifier, "
            "(3) retag that image for a private registry at `myregistry.local:5000`, and (4) clean up the old "
            "local image safely. For each command, add one line stating what success looks like. Then explain in "
            "one sentence why `:latest` is the wrong choice here and what you would pin instead — a version tag "
            "or a digest, and why. SkillBridge reviews your commands as text only — it never executes them."
        ),
        "response_type": "command",
        "competency": "Images",
        "evaluation_note": (
            "Static text review only: SkillBridge checks for a pinned `docker pull` (an explicit tag or digest, "
            "not `:latest`), `docker images` / `docker image inspect` to verify the local copy, a `docker tag` "
            "naming the private registry, and a `docker rmi` cleanup, plus a stated reason why `:latest` is not "
            "reproducible. It does not run Docker, so the review cannot prove runtime results. A strong answer "
            "pins an exact version, states how each step is verified, and explains the tag-versus-digest "
            "trade-off in one honest sentence. A weak answer pulls `:latest` again, skips verification, or "
            "removes an image a container still uses."
        ),
    },
    "mini_check": {
        "questions": [
            {"id": "i1", "type": "mcq", "question": "What does `docker pull nginx` (no tag) actually download?", "options": ["The `nginx:latest` tag — whichever version it points to today", "Every tag in the repository", "Only the smallest layer", "A digest-pinned snapshot"], "correct_answer": "The `nginx:latest` tag — whichever version it points to today", "competency": "Images", "difficulty": "beginner", "misconception_hint": "Ask yourself whether the name identifies one fixed version or a moving pointer."},
            {"id": "i2", "type": "mcq", "question": "Why can `docker rmi nginx:1.27` fail even when the command is typed correctly?", "options": ["A container — even a stopped one — still uses that image", "Images can never be removed", "`rmi` only works on dangling images", "Docker must be stopped first"], "correct_answer": "A container — even a stopped one — still uses that image", "competency": "Images", "difficulty": "beginner", "misconception_hint": "Removal is blocked while anything still references the image."},
            {"id": "i3", "type": "mcq", "question": "Two images stored locally share most of their layers. What does that mean for disk space?", "options": ["The shared layers are stored once, not duplicated per image", "Each image keeps a full private copy", "The layers are compressed twice", "Docker deletes the older image automatically"], "correct_answer": "The shared layers are stored once, not duplicated per image", "competency": "Images", "difficulty": "beginner", "misconception_hint": "Think about how the storage driver reuses identical content."},
        ]
    },
    # Display translations deliberately retain canonical English answer values;
    # the persisted Mini Check continues to grade the immutable canonical set.
    "locales": {
        "ar": {
            "learn": {
                "title": "صُوَر Docker",
                "explanation": "**الصورة (image)** هي القالب اللي الحاوية بتبدأ منه: طبقات (layers) للقراءة بس، ليها **تاج (tag)** زي `nginx:1.27` (أو **digest** ثابت مش بيتغير). `docker pull` بينزّلها على جهازك مرة واحدة، وبعدين الحاويات بتبدأ من النسخة المحلية دي.",
                "key_ideas": [
                    "`docker pull nginx:1.27` بينزّل النسخة دي بالظبط؛ أما `docker pull nginx` من غير تاج فمعناه `:latest` — مؤشر متحرك ممكن يتغير من تحتك.",
                    "`docker images` بيوريك المخزن محليًا: الـ repository والتاج والـ image ID والحجم.",
                    "الطبقات مشتركة: لو نزّلت `nginx:1.27-bookworm` بعد `nginx:1.27`، هتلاقي الطبقات المتطابقة بتتاستخدم تاني بدل ما تتنزّل من الأول.",
                    "`docker tag` بيضيف اسم تاني للصورة؛ `docker rmi` بيحذف الصورة بس لما مفيش حاوية (شغالة أو واقفة) لسه بتستخدمها.",
                ],
                "key_terms": {"صورة": "القالب الطبقي للقراءة بس اللي الحاويات بتبدأ منه.", "تاج (tag)": "علامة قابلة للتغيير زي `1.27` أو `latest` بتشاور على نسخة من الصورة.", "digest": "المعرّف الثابت `sha256:...` اللي بيحدد صورة واحدة بالظبط.", "طبقة (layer)": "خطوة نظام ملفات قابلة لإعادة الاستخدام بتتشاور بين الصور."},
                "job_relevance": "أي مراجعة نشر بتسأل «إيه النسخة بالظبط اللي شغالة؟». تثبيت التاجات (أو الـ digests) ومعرفتك إيه المخزّن على السيرفر شغل يومي لأي حد بيشحن خدمات.",
                "real_world_example": "تدقيق أمني علّم على `nginx:latest` عندكم على السيرفر — ومحدش يعرف يقول النسخة اللي اتنزّلت دي إيه. بتعمل التثبيت بدل كده: `docker pull nginx:1.27`، وبتعمل تاج لنسختك على ريجستري الشركة بـ `docker tag nginx:1.27 myregistry.local:5000/web:1.27`، وبتشيل القديم بـ `docker rmi`، وبتسجّل الـ image ID في تيكت النشر. في التدقيق الجاي بتجاوب بأمر واحد: `docker images`.",
                "common_mistake": "ما تعتمدش على `:latest` في أي حاجة لازم تتكرر بنفس الشكل: ده مؤشر بيتحرك، يعني نفس الأمر ممكن ينزّل صورة مختلفة الشهر الجاي. ثبّت تاج نسخة (أو digest) بدل كده.",
                "worked_example": "المثال بيثبّت نسخة، بيتأكد من المخزن المحلي، بيعمل تاج لريجستري داخلي، وبيحذف صورة قديمة.",
                "depth_note": "محتوى تأسيسي ثابت من قاعدة المعرفة المراجَعة، مش محتوى مولّد حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم الـ Docker CLI الحديث (Docker Engine 23 وما بعده؛ `docker pull` اختصار لـ `docker image pull`، والـ image IDs عبارة عن digests من نوع SHA-256). SkillBridge ما بينفّذش أوامر Docker وما بينزّلش حاجة.",
            },
            "example": {
                "title": "نزّل واتأكد واعمل تاج ونضّف صورة",
                "type": "bash",
                "content": "# 1) pull an exact version, not :latest\ndocker pull nginx:1.27\n\n# 2) confirm it is stored locally\ndocker images\n\n# 3) inspect the pinned image (image ID, layers, env)\ndocker image inspect nginx:1.27\n\n# 4) retag it for an internal registry\ndocker tag nginx:1.27 myregistry.local:5000/web:1.27\n\n# 5) remove an old image no container uses\ndocker rmi nginx:1.25",
                "explanation": "`docker pull` بينزّل النسخة المثبتة مرة واحدة؛ `docker images` بيثبت المخزن محليًا؛ `docker image inspect` بيوريك الـ image ID والطبقات؛ `docker tag` بيضيف اسم ريجستري من غير نسخ؛ و`docker rmi` بيحرر صورة مش مستخدمة. مثال للقراية — SkillBridge ما بينفّذش الأوامر دي.",
            },
            "practice": {
                "title": "خلّي النشر قابل للتكرار",
                "task": "السيرفر عندكم شغال بـ `nginx:latest` ومحدش يعرف النسخة دي إيه — يعني النشر الجاي مش قابل للتكرار. اكتب أوامر Docker اللي هتشغّلها عشان: (١) تنزّل نسخة مثبتة من الصورة، (٢) تتأكد بالظبط إيه المخزّن محليًا دلوقتي بمعرّفه، (٣) تعمل تاج للصورة دي على ريجستري خاص عند `myregistry.local:5000`، و(٤) تنضّف الصورة القديمة المحلية بأمان. مع كل أمر اكتب سطر يقول النجاح شكله إيه. وبعدين اشرح في جملة ليه `:latest` اختيار غلط هنا، وهتثبّت إيه بداله — تاج نسخة ولا digest — وليه. SkillBridge بيراجع أوامرك كنص بس — مش بينفّذها.",
                "response_type": "command",
                "competency": "Images",
                "evaluation_note": "مراجعة نصية ثابتة فقط: SkillBridge بيتأكد من `docker pull` بتاج أو digest مثبت (مش `:latest`)، ومن `docker images` / `docker image inspect` للتحقق من النسخة المحلية، ومن `docker tag` بيسمّي الريجستري الخاص، ومن تنظيف بـ `docker rmi`، ومن سبب واضح ليه `:latest` مش قابل للتكرار. مش بيشغّل Docker، فالمراجعة ما بتثبتش نتيجة تشغيل. الإجابة القوية بتثبّت نسخة بالظبط، وبتقول إزاي بتتأكد من كل خطوة، وبتشرح الفرق بين التاج والـ digest بجملة صادقة. الإجابة الضعيفة بينزّل `:latest` تاني، أو مبتتحققش من حاجة، أو بتحذف صورة لسه فيه حاوية بتستخدمها.",
            },
            "mini_check": {"questions": [
                {"id": "i1", "question": "`docker pull nginx` (من غير تاج) بينزّل إيه بالظبط؟", "options": ["تاج `nginx:latest` — أي نسخة هو مشاور عليها النهارده", "كل التاجات في المستودع", "أصغر طبقة بس", "نسخة مثبتة بالـ digest"], "misconception_hint": "اسأل نفسك: الاسم ده بيحدد نسخة واحدة ثابتة ولا مؤشر بيتحرك؟"},
                {"id": "i2", "question": "ليه `docker rmi nginx:1.27` ممكن يفشل حتى لو الأمر مكتوب صح؟", "options": ["فيه حاوية — حتى لو واقفة — لسه بتستخدم الصورة دي", "الصور عمرها ما بتتحذف", "`rmi` بيشتغل على الـ dangling بس", "لازم تقفل Docker الأول"], "misconception_hint": "الحذف بيتمنع طالما فيه حاجة لسه بتشاور على الصورة."},
                {"id": "i3", "question": "صورتين مخزنين محليًا بيتشاركوا في أغلب الطبقات. معنى ده إيه للمساحة على الديسك؟", "options": ["الطبقات المشتركة بتتخزن مرة واحدة، مش نسخة لكل صورة", "كل صورة بتحتفظ بنسخة كاملة ليها", "الطبقات بتتنضغط مرتين", "Docker بيحذف الصورة الأقدم تلقائيًا"], "misconception_hint": "فكّر إزاي الـ storage driver بيعيد استخدام المحتوى المتطابق."},
            ]},
        },
    },
}


DOCKER_BASIC_COMMANDS = {
    "status": "complete",
    "skill_aliases": ("docker", "docker & containers"),
    "competency": "Basic commands",
    "objective": "Run the most common Docker CLI commands that inspect and interact with containers and images.",
    "objectives": [
        "Verify the Docker installation with `docker --version` and `docker info`.",
        "Pull and run a one-off container with `docker run --rm`.",
        "List running and stopped containers with `docker ps` and `docker ps -a`.",
        "List local images with `docker images`.",
        "Read container output with `docker logs` and run commands inside a container with `docker exec`.",
        "Clean up stopped containers and unused images with `docker rm` and `docker rmi`.",
    ],
    "prerequisites": [],
    "roadmap_rationale": (
        "Basic commands follows Containers and Images because the learner already knows what a "
        "container and image are; this topic turns those concepts into the everyday CLI actions "
        "every Docker user performs."
    ),
    "learn": {
        "title": "Basic commands",
        "explanation": (
            "The Docker CLI is a single command-line tool. A small set of verbs handles most "
            "day-to-day work: `run`, `ps`, `images`, `logs`, `exec`, `rm`, `rmi`, and `info`. "
            "Flags like `--rm` (delete the container when it exits) and `-it` (interactive + TTY) "
            "change how a command behaves without changing what it does."
        ),
        "key_ideas": [
            "`docker --version` and `docker info` prove Docker is installed and show engine details.",
            "`docker run --rm hello-world` downloads the image if needed, runs the container once, and removes it when it exits.",
            "`docker ps` lists running containers; `docker ps -a` also shows stopped ones. `docker images` lists local images.",
            "`docker logs <container>` prints output; `docker exec -it <container> <command>` runs a command inside a running container.",
            "`docker rm <container>` removes a stopped container; `docker rmi <image>` removes an unused image.",
        ],
        "key_terms": {
            "docker cli": "The unified command-line client for Docker Engine.",
            "--rm": "Flag that automatically deletes a container after it stops.",
            "-it": "Flags that make a container interactive with a terminal (`-i` stdin, `-t` TTY).",
            "exec": "The `docker exec` command that runs a process inside an already-running container.",
        },
        "job_relevance": (
            "Checking versions, running one-off containers, reading logs, opening a shell to debug, "
            "and cleaning up are daily tasks for anyone working with Docker."
        ),
        "real_world_example": (
            "You join a new team and need to confirm the environment before running the project. "
            "`docker --version` and `docker info` confirm Docker is healthy; `docker ps` and "
            "`docker images` show what is already running and stored; `docker run --rm hello-world` "
            "proves you can pull and run. In five commands you have a working baseline."
        ),
        "common_mistake": (
            "`docker run --rm` deletes the container only after it stops — it does not delete the image. "
            "`docker exec` runs a command in a running container; it does not create a new container."
        ),
        "worked_example": (
            "The example verifies Docker, runs a one-off hello-world container, lists containers and "
            "images, reads logs, opens a shell inside a running container, and cleans up."
        ),
        "depth_note": "Canonical beginner content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": (
            "Examples use the modern unified Docker CLI (Docker Engine 23 and later). SkillBridge "
            "does not execute Docker commands; the outputs described are what Docker prints when a "
            "command succeeds."
        ),
        "grounding_sources": [
            {"title": "Docker CLI reference", "url": "https://docs.docker.com/engine/reference/commandline/docker/", "source": "Docker documentation"},
            {"title": "docker container run reference", "url": "https://docs.docker.com/reference/cli/docker/container/run/", "source": "Docker documentation"},
        ],
    },
    "example": {
        "title": "Verify, run, inspect, and clean up",
        "type": "bash",
        "content": (
            "# 1) verify Docker is installed\n"
            "docker --version\n"
            "\n"
            "# 2) run a one-off container that removes itself on exit\n"
            "docker run --rm hello-world\n"
            "\n"
            "# 3) list running and stored containers/images\n"
            "docker ps\n"
            "docker ps -a\n"
            "docker images\n"
            "\n"
            "# 4) read logs and open a shell in a running container named api\n"
            "docker logs api\n"
            "docker exec -it api /bin/sh\n"
            "\n"
            "# 5) clean up a stopped container and an unused image\n"
            "docker rm old\n"
            "docker rmi myapp:0.1"
        ),
        "explanation": (
            "These commands cover the daily lifecycle outside of building images: verify the tool, "
            "run a quick smoke test, inspect what exists, debug a running service, and remove "
            "artifacts that are no longer needed. Worked example for reading — SkillBridge does not "
            "run these commands."
        ),
    },
    "practice": {
        "type": "practical",
        "title": "Inspect and clean up a local Docker environment",
        "task": (
            "You have inherited a laptop with Docker already installed. Write the Docker commands "
            "you would run to: (1) confirm Docker is installed and show its version, (2) list all "
            "running containers and all stopped containers, (3) list all local images, (4) run a "
            "one-off `hello-world` container that removes itself when it exits, (5) read the logs "
            "of a running container named `api`, (6) open an interactive shell inside the running "
            "`api` container to inspect a file, and (7) remove a stopped container named `old` and "
            "an unused image `myapp:0.1`. For each command, add one line stating the output you "
            "expect or how you verify it worked. SkillBridge reviews your commands as text only — "
            "it never executes them."
        ),
        "response_type": "command",
        "competency": "Basic commands",
        "evaluation_note": (
            "Static text review only: SkillBridge checks for `docker --version` or `docker info`, "
            "`docker ps` / `docker ps -a`, `docker images`, `docker run --rm hello-world`, "
            "`docker logs api`, `docker exec -it api ...`, `docker rm old`, and `docker rmi myapp:0.1`, "
            "plus a stated verification step for each. It does not run Docker, so the review cannot "
            "prove runtime results. A strong answer names the target container/image and states "
            "what success looks like for every step. A weak answer skips verification, confuses "
            "`exec` with `run`, or omits the cleanup commands."
        ),
    },
    "mini_check": {
        "questions": [
            {"id": "b1", "type": "mcq", "question": "Which flag removes a container automatically after it exits?", "options": ["--rm", "-d", "-p", "--name"], "correct_answer": "--rm", "competency": "Basic commands", "difficulty": "beginner", "misconception_hint": "Think about the flag whose whole purpose is cleanup on stop."},
            {"id": "b2", "type": "mcq", "question": "What is the difference between `docker ps` and `docker ps -a`?", "options": ["`ps` lists only running containers; `ps -a` also lists stopped ones", "`ps -a` deletes stopped containers", "`ps` shows images", "There is no difference"], "correct_answer": "`ps` lists only running containers; `ps -a` also lists stopped ones", "competency": "Basic commands", "difficulty": "beginner", "misconception_hint": "The `-a` flag widens the listing to include containers that have exited."},
            {"id": "b3", "type": "mcq", "question": "Which command runs a shell inside an already-running container named `api`?", "options": ["docker exec -it api /bin/sh", "docker run api /bin/sh", "docker start api /bin/sh", "docker logs api /bin/sh"], "correct_answer": "docker exec -it api /bin/sh", "competency": "Basic commands", "difficulty": "beginner", "misconception_hint": "One command is meant for entering a running container; the others create or control containers."},
        ]
    },
    "locales": {
        "ar": {
            "learn": {
                "title": "الأوامر الأساسية في Docker",
                "explanation": "أداة سطر الأوامر Docker CLI هي أداة واحدة. مجموعة صغيرة من الأفعال بتغطي أغلب الشغل اليومي: `run`، `ps`، `images`، `logs`، `exec`، `rm`، `rmi`، و`info`. الفلاغات زي `--rm` (بيحذف الحاوية لما تخلص) و`-it` (تفاعلي + ترمينال) بتغيّر سلوك الأمر من غير ما تغيّر وظيفته.",
                "key_ideas": [
                    "`docker --version` و`docker info` بيثبتوا إن Docker مركّب وبيورو تفاصيل الـ engine.",
                    "`docker run --rm hello-world` بينزّل الصورة لو محتاجة، ويشغّل الحاوية مرة واحدة، ويحذفها لما تخلص.",
                    "`docker ps` بيوريك الحاويات الشغالة؛ `docker ps -a` بيضيف كمان اللي واقفة. `docker images` بيوريك الصور المحلية.",
                    "`docker logs <container>` بيطبع المخرجات؛ `docker exec -it <container> <command>` بيشغّل أمر جوه حاوية شغالة.",
                    "`docker rm <container>` بيحذف حاوية واقفة؛ `docker rmi <image>` بيحذف صورة مش مستخدمة.",
                ],
                "key_terms": {"docker cli": "عميل سطر الأوامر الموحّد لـ Docker Engine.", "--rm": "فلاغ بيحذف الحاوية تلقائيًا بعد ما تخلص.", "-it": "فلاغات بتخلي الحاوية تفاعلية مع ترمينال (`-i` stdin، `-t` TTY).", "exec": "الأمر `docker exec` اللي بيشغّل عملية جوه حاوية شغالة أصلاً."},
                "job_relevance": "التحقق من الإصدارات، تشغيل حاويات مؤقتة، قراية الـ logs، فتح شل للتصحيح، والتنظيف هي مهام يومية لأي حد بيشتغل بـ Docker.",
                "real_world_example": "بتنضم لفريق جديد وعايز تتأكد من البيئة قبل ما تشغّل المشروع. `docker --version` و`docker info` بيثبتوا إن Docker سليم؛ `docker ps` و`docker images` بيوروك إيه اللي شغال ومخزّن؛ `docker run --rm hello-world` بيثبت إنك تقدر تنزّل وتشغّل. في خمس أوامر عندك baseline شغّالة.",
                "common_mistake": "`docker run --rm` بيحذف الحاوية بس بعد ما تخلص — مش بيحذف الصورة. `docker exec` بيشغّل أمر جوه حاوية شغالة؛ مش بيعمل حاوية جديدة.",
                "worked_example": "المثال بيتأكد من Docker، بيشغّل حاوية hello-world مرة واحدة، بيسرد الحاويات والصور، بيقرا الـ logs، بيفتح شل جوه حاوية شغالة، وبينضّف في الآخر.",
                "depth_note": "محتوى تأسيسي ثابت من قاعدة المعرفة المراجَعة، مش محتوى مولّد حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم الـ Docker CLI الحديث (Docker Engine 23 وما بعده). SkillBridge ما بينفّذش أوامر Docker؛ المخرجات الموصوفة هي اللي Docker بيطبعها لما الأمر ينجح.",
                "grounding_sources": [
                    {"title": "مرجع Docker CLI", "url": "https://docs.docker.com/engine/reference/commandline/docker/", "source": "Docker documentation"},
                    {"title": "مرجع docker container run", "url": "https://docs.docker.com/reference/cli/docker/container/run/", "source": "Docker documentation"},
                ],
            },
            "example": {
                "title": "تحقق وشغّل وافحص ونضّف",
                "type": "bash",
                "content": "# 1) verify Docker is installed\ndocker --version\n\n# 2) run a one-off container that removes itself on exit\ndocker run --rm hello-world\n\n# 3) list running and stored containers/images\ndocker ps\ndocker ps -a\ndocker images\n\n# 4) read logs and open a shell in a running container named api\ndocker logs api\ndocker exec -it api /bin/sh\n\n# 5) clean up a stopped container and an unused image\ndocker rm old\ndocker rmi myapp:0.1",
                "explanation": "الأوامر دي بتغطي دورة الحياة اليومية برّا بناء الصور: تأكد من الأداة، شغّل اختبار سريع، افحص الموجود، صحّح حاوية شغالة، وامسح اللي مش محتاجه. مثال للقراية — SkillBridge ما بينفّذش الأوامر دي.",
            },
            "practice": {
                "title": "افحص ونضّف بيئة Docker محلية",
                "task": "عندك لابتوب فيه Docker مركّب. اكتب أوامر Docker اللي هتشغّلها عشان: (١) تتأكد إن Docker مركّب وتوري الإصدار، (٢) تسرد كل الحاويات الشغالة واللي واقفة، (٣) تسرد كل الصور المحلية، (٤) تشغّل حاوية `hello-world` مرة واحدة وتحذف نفسها لما تخلص، (٥) تقرا الـ logs بتاعة حاوية `api`، (٦) تفتح شل تفاعلي جوه حاوية `api` عشان تفحص ملف، و(٧) تحذف حاوية واقفة اسمها `old` وصورة مش مستخدمة `myapp:0.1`. مع كل أمر اكتب سطر يقول المخرج المتوقع أو إزاي هتتأكد إنه اشتغل. SkillBridge بيراجع أوامرك كنص بس — مش بينفّذها.",
                "response_type": "command",
                "competency": "Basic commands",
                "evaluation_note": "مراجعة نصية ثابتة فقط: SkillBridge بيتأكد من `docker --version` أو `docker info`، و`docker ps` / `docker ps -a`، و`docker images`، و`docker run --rm hello-world`، و`docker logs api`، و`docker exec -it api ...`، و`docker rm old`، و`docker rmi myapp:0.1`، ومن وجود خطوة تحقق لكل أمر. مش بيشغّل Docker، فالمراجعة ما بتثبتش نتيجة تشغيل. الإجابة القوية بتسمّي الحاوية/الصورة المستهدفة وتقول النجاح شكله إيه في كل خطوة. الإجابة الضعيفة بتتخطّى التحقق، أو تخلط بين `exec` و`run`، أو تنسى أوامر التنظيف.",
            },
            "mini_check": {"questions": [
                {"id": "b1", "question": "أي فلاغ بيحذف الحاوية تلقائيًا بعد ما تخلص؟", "options": ["--rm", "-d", "-p", "--name"], "misconception_hint": "فكّر في الفلاغ اللي وظيفته الأساسية التنظيف بعد التوقف."},
                {"id": "b2", "question": "إيه الفرق بين `docker ps` و`docker ps -a`؟", "options": ["`ps` بيوري الحاويات الشغالة بس؛ `ps -a` بيضيف كمان اللي واقفة", "`ps -a` بيحذف الحاويات الوقفة", "`ps` بيوري الصور", "مفيش فرق"], "misconception_hint": "الفلاغ `-a` بيوسّع القايمة عشان تشمل الحاويات اللي خلصت."},
                {"id": "b3", "question": "أي أمر بيشغّل شل جوه حاوية شغالة اسمها `api`؟", "options": ["docker exec -it api /bin/sh", "docker run api /bin/sh", "docker start api /bin/sh", "docker logs api /bin/sh"], "misconception_hint": "أمر واحد مخصوص للدخول لحاوية شغالة؛ الباقي بيعمل أو بيتحكم في حاويات."},
            ]},
        },
    },
}


DOCKER_DOCKERFILE = {
    "status": "complete",
    "skill_aliases": ("docker", "docker & containers"),
    "competency": "Dockerfile",
    "objective": "Write a Dockerfile that builds a small, reproducible image using FROM, COPY, RUN, CMD, and EXPOSE.",
    "objectives": [
        "Explain that a Dockerfile is a recipe that builds an image in ordered layers.",
        "Pin a base image version with FROM instead of using :latest.",
        "Copy source files with COPY and install dependencies with RUN.",
        "Set the default container command with CMD.",
        "Document the intended listening port with EXPOSE.",
    ],
    "prerequisites": [
        {
            "competency": "Images",
            "relationship": "required foundation",
            "why": "A Dockerfile produces an image; you need to understand tags, layers, and image storage before writing a recipe that creates one.",
        },
    ],
    "roadmap_rationale": (
        "Dockerfile follows Images because every Dockerfile builds an image. Knowing how tags, "
        "layers, and local image storage work makes the build process meaningful."
    ),
    "learn": {
        "title": "Dockerfile",
        "explanation": (
            "A Dockerfile is a text recipe that tells Docker how to build an image. Each instruction "
            "creates a layer. `FROM` chooses the starting image, `COPY` adds files from the build "
            "context, `RUN` executes commands during the build, `CMD` sets the default command for "
            "containers started from the image, and `EXPOSE` documents the port the service listens on."
        ),
        "key_ideas": [
            "A Dockerfile builds an image; `docker build -t myapp:1.0 .` tags the result.",
            "`FROM python:3.12-slim` pins a specific base image; avoid `:latest` for reproducible builds.",
            "Order matters for caching: copy dependency files first, install, then copy source code.",
            "`CMD` is the default command when a container starts; it can be overridden at runtime.",
            "`EXPOSE` documents the port but does not publish it — `-p` is still required on `docker run`.",
        ],
        "key_terms": {
            "dockerfile": "A text file containing instructions for building a Docker image.",
            "FROM": "Sets the base image for the build.",
            "COPY": "Copies files from the build context into the image.",
            "RUN": "Executes a command during image build, creating a new layer.",
            "CMD": "Sets the default command for containers started from the image.",
            "EXPOSE": "Documents the port the container service listens on.",
            "build context": "The set of files Docker can see while building, usually the directory containing the Dockerfile.",
        },
        "job_relevance": (
            "Almost every containerized project ships a Dockerfile. Writing one that is small, "
            "cache-friendly, and reproducible is a standard backend and DevOps task."
        ),
        "real_world_example": (
            "Your Python API needs a reproducible deploy image. You write a Dockerfile starting "
            "`FROM python:3.12-slim`, copy `requirements.txt` and run `pip install`, then copy the "
            "source and set `CMD [\"python\", \"app.py\"]`. Now any teammate builds the exact same image "
            "with `docker build -t api:1.0 .`."
        ),
        "common_mistake": (
            "Do not use `:latest` in FROM in production: it makes the build non-reproducible. Also, "
            "EXPOSE does not publish the port by itself; you still need `-p` when running the container."
        ),
        "worked_example": (
            "The example writes a small Python API Dockerfile, builds it with a pinned tag, and runs "
            "a container from the resulting image."
        ),
        "depth_note": "Canonical intermediate content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": (
            "Examples use Dockerfile syntax compatible with Docker Engine 23+ and BuildKit. SkillBridge "
            "does not execute Docker commands."
        ),
        "grounding_sources": [
            {"title": "Dockerfile reference", "url": "https://docs.docker.com/reference/dockerfile/", "source": "Docker documentation"},
            {"title": "Dockerfile best practices", "url": "https://docs.docker.com/build/building/best-practices/", "source": "Docker documentation"},
        ],
    },
    "example": {
        "title": "Build a tiny Python API image",
        "type": "bash",
        "content": (
            "# Dockerfile\n"
            "FROM python:3.12-slim\n"
            "WORKDIR /app\n"
            "COPY requirements.txt .\n"
            "RUN pip install --no-cache-dir -r requirements.txt\n"
            "COPY . .\n"
            "EXPOSE 8000\n"
            "CMD [\"python\", \"app.py\"]\n"
            "\n"
            "# Build and run\n"
            "docker build -t api:1.0 .\n"
            "docker run -d --name api -p 8080:8000 api:1.0"
        ),
        "explanation": (
            "The Dockerfile orders layers for caching: dependencies are installed before the source "
            "is copied, so code-only changes reuse the install layer. `EXPOSE` documents port 8000, "
            "and `-p 8080:8000` actually publishes it. Worked example for reading — SkillBridge does "
            "not run these commands."
        ),
    },
    "practice": {
        "type": "practical",
        "title": "Write a Dockerfile for a Node.js service",
        "task": (
            "Write a Dockerfile for a Node.js service and the commands to build and run it. Requirements: "
            "(1) Pin a specific Node version in FROM (not `:latest`), (2) set a working directory, "
            "(3) copy `package.json` and `package-lock.json` first and run `npm install` to leverage "
            "layer caching, (4) copy the rest of the source, (5) set the default command to "
            "`node server.js`, (6) document that the service listens on port 3000. Then write the "
            "commands to build the image tagged `myapi:1.0` and run a container named `myapi` that "
            "maps host port 8080 to container port 3000. Add one sentence explaining why you copy "
            "the package files before the source. SkillBridge reviews your Dockerfile and commands "
            "as text only — it never executes them."
        ),
        "response_type": "configuration",
        "competency": "Dockerfile",
        "evaluation_note": (
            "Static text review only: SkillBridge checks for a pinned FROM, WORKDIR, COPY of package "
            "files before source, RUN npm install, COPY of remaining source, EXPOSE 3000, CMD "
            "node server.js, `docker build -t myapi:1.0 .`, and `docker run -d --name myapi -p 8080:3000 myapi:1.0`, "
            "plus an explanation of layer caching. It does not run Docker, so the review cannot prove "
            "runtime results. A strong answer pins a version, orders COPY for caching, and distinguishes "
            "EXPOSE from `-p`. A weak answer uses `:latest`, copies everything in one step, or omits "
            "the port mapping."
        ),
    },
    "mini_check": {
        "questions": [
            {"id": "d1", "type": "mcq", "question": "Which Dockerfile instruction sets the base image?", "options": ["FROM", "COPY", "RUN", "CMD"], "correct_answer": "FROM", "competency": "Dockerfile", "difficulty": "beginner", "misconception_hint": "Every Dockerfile starts by choosing what image to build on top of."},
            {"id": "d2", "type": "mcq", "question": "Why is `COPY requirements.txt .` followed by `RUN pip install` before copying the rest of the source?", "options": ["It lets Docker reuse the installed-dependency layer when only code changes", "It makes the image larger", "It is required by the Dockerfile syntax", "It prevents the container from starting"], "correct_answer": "It lets Docker reuse the installed-dependency layer when only code changes", "competency": "Dockerfile", "difficulty": "intermediate", "misconception_hint": "Think about which layers are invalidated when source files change."},
            {"id": "d3", "type": "mcq", "question": "What does `EXPOSE 3000` do?", "options": ["Documents that the container service listens on port 3000", "Publishes port 3000 to the host automatically", "Forces the container to use port 3000", "Creates a Docker network"], "correct_answer": "Documents that the container service listens on port 3000", "competency": "Dockerfile", "difficulty": "beginner", "misconception_hint": "Publishing to the host requires a runtime flag, not just EXPOSE."},
        ]
    },
    "locales": {
        "ar": {
            "learn": {
                "title": "Dockerfile",
                "explanation": "Dockerfile هو وصفة نصية بتقول لـ Docker إزاي تبني صورة. كل تعليمة بتعمل طبقة. `FROM` بيختار الصورة الأساسية، `COPY` بيضيف ملفات من سياق البناء، `RUN` بينفّذ أوامر أثناء البناء، `CMD` بيحدد الأمر الافتراضي لما الحاوية تبدأ، و`EXPOSE` بيوثّق البورت اللي الخدمة بتسمع عليه.",
                "key_ideas": [
                    "الـ Dockerfile بيبني صورة؛ `docker build -t myapp:1.0 .` بيعمل تاج للنتيجة.",
                    "`FROM python:3.12-slim` بيثبّت صورة أساسية محددة؛ تجنّب `:latest` عشان البناء يتكرر بنفس الشكل.",
                    "الترتيب مهم للكاش: انسخ ملفات الاعتماديات الأول، ثبّتها، وبعدين انسخ الكود.",
                    "`CMD` هو الأمر الافتراضي لما الحاوية تبدأ؛ ممكن يتجاوز وقت التشغيل.",
                    "`EXPOSE` بيوثّق البورت بس مش بينشره — لسه محتاج `-p` في `docker run`.",
                ],
                "key_terms": {"dockerfile": "ملف نصي بيحتوي على تعليمات لبناء صورة Docker.", "FROM": "بيحدد الصورة الأساسية للبناء.", "COPY": "بينسخ ملفات من سياق البناء للصورة.", "RUN": "بينفّذ أمر أثناء بناء الصورة ويعمل طبقة جديدة.", "CMD": "بيحدد الأمر الافتراضي للحاويات اللي بتبدأ من الصورة.", "EXPOSE": "بيوثّق البورت اللي خدمة الحاوية بتسمع عليه.", "build context": "مجموعة الملفات اللي Docker شايفها وقت البناء، عادة المجلد اللي فيه الـ Dockerfile."},
                "job_relevance": "تقريبًا كل مشروع بيستخدم حاويات بيشحن Dockerfile. كتابة Dockerfile صغيرة، صديقة للكاش، وقابلة للتكرار هي مهمة أساسية لـ backend وDevOps.",
                "real_world_example": "الـ API بتاع Python محتاج صورة نشر قابلة للتكرار. بتكتب Dockerfile يبدأ بـ `FROM python:3.12-slim`، بتنسخ `requirements.txt` وتشغّل `pip install`، وبعدين بتنسخ المصدر وتحدد `CMD [\"python\", \"app.py\"]`. دلوقتي أي زميل يقدر يبني نفس الصورة بالظبط بـ `docker build -t api:1.0 .`.",
                "common_mistake": "ما تستخدمش `:latest` في FROM في الإنتاج: ده بيخلي البناء مش قابل للتكرار. كمان EXPOSE مش بينشر البورت لوحده؛ لسه محتاج `-p` وقت تشغيل الحاوية.",
                "worked_example": "المثال بيكتب Dockerfile صغير لـ Python API، يبنيه بتاج مثبت، ويشغّل حاوية من الصورة الناتجة.",
                "depth_note": "محتوى متوسط ثابت من قاعدة المعرفة المراجَعة، مش محتوى مولّد حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صيغة Dockerfile متوافقة مع Docker Engine 23+ وBuildKit. SkillBridge ما بينفّذش أوامر Docker.",
                "grounding_sources": [
                    {"title": "مرجع Dockerfile", "url": "https://docs.docker.com/reference/dockerfile/", "source": "Docker documentation"},
                    {"title": "أفضل ممارسات Dockerfile", "url": "https://docs.docker.com/build/building/best-practices/", "source": "Docker documentation"},
                ],
            },
            "example": {
                "title": "ابنِ صورة Python API صغيرة",
                "type": "bash",
                "content": "# Dockerfile\nFROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nEXPOSE 8000\nCMD [\"python\", \"app.py\"]\n\n# Build and run\ndocker build -t api:1.0 .\ndocker run -d --name api -p 8080:8000 api:1.0",
                "explanation": "الـ Dockerfile بيرتّب الطبقات عشان الكاش: الاعتماديات تتثبّت قبل ما يتنسخ الكود، فلو اتغيّر الكود بس بيُستخدم طبقة التثبيت القديمة. `EXPOSE` بيوثّق بورت 8000، و`-p 8080:8000` هو اللي بينشره فعليًا. مثال للقراية — SkillBridge ما بينفّذش الأوامر دي.",
            },
            "practice": {
                "title": "اكتب Dockerfile لخدمة Node.js",
                "task": "اكتب Dockerfile لخدمة Node.js والأوامر اللي هتبني وتشغّلها. المتطلبات: (١) ثبّت نسخة Node معينة في FROM (مش `:latest`)، (٢) حدّد working directory، (٣) انسخ `package.json` و`package-lock.json` الأول وشغّل `npm install` عشان تستفيد من كاش الطبقات، (٤) انسخ باقي المصدر، (٥) حدّد الأمر الافتراضي `node server.js`، (٦) وثّق إن الخدمة بتسمع على بورت 3000. وبعدين اكتب الأوامر اللي هتبني الصورة بـ تاج `myapi:1.0` وتشغّل حاوية اسمها `myapi` بتوصيل بورت 8080 على الجهاز ببورت 3000 جوه الحاوية. ضيف جملة واحدة تشرح ليه بنسخ ملفات الباكج قبل المصدر. SkillBridge بيراجع الـ Dockerfile والأوامر كنص بس — مش بينفّذهم.",
                "response_type": "configuration",
                "competency": "Dockerfile",
                "evaluation_note": "مراجعة نصية ثابتة فقط: SkillBridge بيتأكد من FROM مثبت، وWORKDIR، وCOPY لملفات الباكج قبل المصدر، وRUN npm install، وCOPY باقي المصدر، وEXPOSE 3000، وCMD node server.js، و`docker build -t myapi:1.0 .`، و`docker run -d --name myapi -p 8080:3000 myapi:1.0`، وشرح طبقات الكاش. مش بيشغّل Docker، فالمراجعة ما بتثبتش نتيجة تشغيل. الإجابة القوية بتثبّت نسخة، وترتّب COPY عشان الكاش، وتميّز بين EXPOSE و`-p`. الإجابة الضعيفة بتستخدم `:latest`، أو بتنسخ كل حاجة في خطوة واحدة، أو بتنسى ربط البورت.",
            },
            "mini_check": {"questions": [
                {"id": "d1", "question": "أي تعليمة في Dockerfile بتحدد الصورة الأساسية؟", "options": ["FROM", "COPY", "RUN", "CMD"], "misconception_hint": "كل Dockerfile بيبدأ باختيار الصورة اللي هيبني فوقها."},
                {"id": "d2", "question": "ليه بنعمل `COPY requirements.txt .` وبعدين `RUN pip install` قبل ما ننسخ باقي المصدر؟", "options": ["عشان Docker تستخدم طبقة تثبيت الاعتماديات تاني لما الكود بس هو اللي يتغير", "عشان الصورة تكبر", "ده مطلوب من صيغة Dockerfile", "عشان الحاوية متبدأش"], "misconception_hint": "فكّر أي الطبقات بتتبطل لما ملفات المصدر تتغير."},
                {"id": "d3", "question": "إيه اللي بيعمله `EXPOSE 3000`؟", "options": ["بيوثّق إن خدمة الحاوية بتسمع على بورت 3000", "بينشر بورت 3000 على الجهاز تلقائيًا", "بيلزم الحاوية تستخدم بورت 3000", "بينشئ شبكة Docker"], "misconception_hint": "النشر على الجهاز بيتطلب فلاغ وقت التشغيل، مش بس EXPOSE."},
            ]},
        },
    },
}


DOCKER_PORTS = {
    "status": "complete",
    "skill_aliases": ("docker", "docker & containers"),
    "competency": "Ports",
    "objective": "Publish a container port to the host, inspect port bindings, and understand the difference between EXPOSE and -p.",
    "objectives": [
        "Explain that container ports are isolated from the host by default.",
        "Publish a port with `docker run -p HOST_PORT:CONTAINER_PORT`.",
        "Inspect bindings with `docker port` and `docker inspect`.",
        "Distinguish `EXPOSE` in a Dockerfile from `-p` on the CLI.",
    ],
    "prerequisites": [
        {
            "competency": "Containers",
            "relationship": "required foundation",
            "why": "Port publishing only makes sense once you can run a container and name it; the run/stop lifecycle is the context for exposing services.",
        },
    ],
    "roadmap_rationale": (
        "Ports follows Containers because publishing is meaningless without a running container. "
        "It bridges the gap between a service running inside a container and a client reaching it "
        "from the host."
    ),
    "learn": {
        "title": "Ports",
        "explanation": (
            "By default, a container's network is isolated. A service listening on port 80 inside "
            "the container is not reachable from your laptop unless you publish the port with "
            "`-p HOST_PORT:CONTAINER_PORT` when running it. `EXPOSE` in a Dockerfile only documents "
            "the intended port; it does not publish it."
        ),
        "key_ideas": [
            "A container port is reachable only from inside the container unless published.",
            "`docker run -d --name web -p 8080:80 nginx:1.27` maps host port 8080 to container port 80.",
            "`docker port web` shows the current bindings; `docker inspect web` shows full network details.",
            "`EXPOSE 80` in a Dockerfile is documentation; `-p 8080:80` at runtime does the actual mapping.",
            "Use host port 0 or ephemeral ports only when you do not care which host port is assigned.",
        ],
        "key_terms": {
            "container port": "The port a process listens on inside the container.",
            "host port": "The port on the machine running Docker that is mapped to a container port.",
            "publish": "To make a container port reachable from outside the container using `-p`.",
            "EXPOSE": "A Dockerfile instruction that documents the intended listening port.",
        },
        "job_relevance": (
            "Every containerized service that receives traffic — APIs, databases, frontends — must "
            "publish its port correctly. Misunderstanding EXPOSE versus -p is one of the most common "
            "reasons a container 'is running but not responding'."
        ),
        "real_world_example": (
            "You run a web container but `curl http://localhost` fails. `docker ps` shows the "
            "container is up, but there is no `0.0.0.0:80->80/tcp` binding because you forgot `-p`. "
            "You stop and rerun with `-p 8080:80`, then `curl http://localhost:8080` returns the page."
        ),
        "common_mistake": (
            "`EXPOSE` does not publish a port. A container can `EXPOSE 80` and still be unreachable "
            "from the host unless you start it with `-p`."
        ),
        "worked_example": (
            "The example starts an nginx container with a published port, verifies the binding, "
            "and shows the difference between EXPOSE and -p."
        ),
        "depth_note": "Canonical intermediate content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": (
            "Examples use the modern unified Docker CLI (Docker Engine 23 and later). SkillBridge "
            "does not execute Docker commands."
        ),
        "grounding_sources": [
            {"title": "Publishing and exposing ports", "url": "https://docs.docker.com/get-started/docker-concepts/running-containers/publishing-ports/", "source": "Docker documentation"},
            {"title": "docker container run reference", "url": "https://docs.docker.com/reference/cli/docker/container/run/", "source": "Docker documentation"},
        ],
    },
    "example": {
        "title": "Publish and verify a web container port",
        "type": "bash",
        "content": (
            "# 1) start nginx and publish host port 8080 to container port 80\n"
            "docker run -d --name web -p 8080:80 nginx:1.27\n"
            "\n"
            "# 2) show the port binding\n"
            "docker port web\n"
            "\n"
            "# 3) inspect the network settings\n"
            "docker inspect --format='{{range $p, $conf := .NetworkSettings.Ports}}{{$p}} -> {{(index $conf 0).HostPort}}{{end}}' web\n"
            "\n"
            "# 4) test from the host\n"
            "curl http://localhost:8080"
        ),
        "explanation": (
            "`-p 8080:80` bridges the host and the container. `docker port` confirms the mapping, "
            "and `curl` verifies the service is reachable from the host. Worked example for reading — "
            "SkillBridge does not run these commands."
        ),
    },
    "practice": {
        "type": "practical",
        "title": "Expose a containerised API on the correct host port",
        "task": (
            "A container named `api` runs a service that listens on port 3000 inside the container, "
            "but you cannot reach it from your laptop. Write the exact `docker run` command you "
            "should have used to start it so the service is reachable on host port 8080, and show "
            "how to verify the binding with `docker port` and `docker inspect`. Then explain the "
            "difference between `EXPOSE 3000` in the Dockerfile and `-p 8080:3000` on the CLI. "
            "SkillBridge reviews your commands as text only — it never executes them."
        ),
        "response_type": "command",
        "competency": "Ports",
        "evaluation_note": (
            "Static text review only: SkillBridge checks for a `docker run` command that uses "
            "`-p 8080:3000` (or equivalent) with `--name api`, `docker port api`, `docker inspect` "
            "to read the binding, and an explanation that EXPOSE documents the port while `-p` "
            "publishes it to the host. It does not run Docker, so the review cannot prove runtime "
            "results. A strong answer names the image, states the exact mapping, and gives a concrete "
            "verify step. A weak answer suggests EXPOSE alone is enough, uses the ports in reverse "
            "order, or omits verification."
        ),
    },
    "mini_check": {
        "questions": [
            {"id": "p1", "type": "mcq", "question": "Which `docker run` flag publishes a container port to the host?", "options": ["-p", "-d", "--name", "--rm"], "correct_answer": "-p", "competency": "Ports", "difficulty": "beginner", "misconception_hint": "Look for the flag that creates the host-to-container port mapping."},
            {"id": "p2", "type": "mcq", "question": "What does `EXPOSE 3000` in a Dockerfile do?", "options": ["Documents that the service listens on port 3000", "Publishes port 3000 to the host", "Forwards port 3000 automatically", "Creates a network bridge"], "correct_answer": "Documents that the service listens on port 3000", "competency": "Ports", "difficulty": "beginner", "misconception_hint": "Publishing requires a runtime flag, not just a Dockerfile instruction."},
            {"id": "p3", "type": "mcq", "question": "In `docker run -p 8080:80`, which port belongs to the host?", "options": ["8080", "80", "Both", "Neither"], "correct_answer": "8080", "competency": "Ports", "difficulty": "beginner", "misconception_hint": "The host port is written first in HOST:CONTAINER notation."},
        ]
    },
    "locales": {
        "ar": {
            "learn": {
                "title": "البورتات في Docker",
                "explanation": "افتراضيًا، شبكة الحاوية معزولة. خدمة بتسمع على بورت 80 جوه الحاوية مش هتوصل من لابتوبك إلا لو نشرت البورت بـ `-p HOST_PORT:CONTAINER_PORT` وقت التشغيل. `EXPOSE` في Dockerfile بيوثّق البورت المقصود بس مش بينشره.",
                "key_ideas": [
                    "بورت الحاوية بيوصل من جوه الحاوية بس إلا لو اتنشر.",
                    "`docker run -d --name web -p 8080:80 nginx:1.27` بيوصّل بورت 8080 على الجهاز ببورت 80 جوه الحاوية.",
                    "`docker port web` بيوري الربط الحالي؛ `docker inspect web` بيوري تفاصيل الشبكة كاملة.",
                    "`EXPOSE 80` في Dockerfile مجرد توثيق؛ `-p 8080:80` وقت التشغيل هو اللي بيعمل الربط الفعلي.",
                    "استخدم بورت 0 على الـ host أو بورتات مؤقتة بس لما يبقى مش مهم أي بورت على الجهاز هيُخصص.",
                ],
                "key_terms": {"container port": "البورت اللي العملية بتسمع عليه جوه الحاوية.", "host port": "البورت على الجهاز اللي Docker شغال عليه واللي بيرتبط ببورت الحاوية.", "publish": "إتاحة بورت الحاوية من برّا باستخدام `-p`.", "EXPOSE": "تعليمة في Dockerfile بتوثّق البورت المقصود."},
                "job_relevance": "كل خدمة في حاوية بتستقبل ترافيك — APIs، قواعد بيانات، frontends — لازم تنشر بورتها صح. عدم الفهم الفرق بين EXPOSE و -p من أشهر أسباب إن الحاوية «شغالة بس مش بترد».",
                "real_world_example": "بتشغّل حاوية ويب بس `curl http://localhost` بيفشل. `docker ps` بيوريك إنها شغالة، بس مفيش ربط `0.0.0.0:80->80/tcp` عشان نسيت `-p`. بتوقفها وتشغّلها تاني بـ `-p 8080:80`، وبعدين `curl http://localhost:8080` بيرجّع الصفحة.",
                "common_mistake": "`EXPOSE` مش بينشر البورت. الحاوية ممكن تكون عاملة `EXPOSE 80` وماتبقاش قابلة للوصول من الجهاز إلا لو تشغّلت بـ `-p`.",
                "worked_example": "المثال بيشغّل حاوية nginx بنشر بورت، بيتأكد من الربط، وبيوري الفرق بين EXPOSE و -p.",
                "depth_note": "محتوى متوسط ثابت من قاعدة المعرفة المراجَعة، مش محتوى مولّد حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم الـ Docker CLI الحديث (Docker Engine 23 وما بعده). SkillBridge ما بينفّذش أوامر Docker.",
                "grounding_sources": [
                    {"title": "نشر وإتاحة البورتات", "url": "https://docs.docker.com/get-started/docker-concepts/running-containers/publishing-ports/", "source": "Docker documentation"},
                    {"title": "مرجع docker container run", "url": "https://docs.docker.com/reference/cli/docker/container/run/", "source": "Docker documentation"},
                ],
            },
            "example": {
                "title": "انشر بورت حاوية ويب وتأكد منه",
                "type": "bash",
                "content": "# 1) start nginx and publish host port 8080 to container port 80\ndocker run -d --name web -p 8080:80 nginx:1.27\n\n# 2) show the port binding\ndocker port web\n\n# 3) inspect the network settings\ndocker inspect --format='{{range $p, $conf := .NetworkSettings.Ports}}{{$p}} -> {{(index $conf 0).HostPort}}{{end}}' web\n\n# 4) test from the host\ncurl http://localhost:8080",
                "explanation": "`-p 8080:80` بيوصل الجهاز بالحاوية. `docker port` بيثبت الربط، و`curl` بيثبت إن الخدمة قابلة للوصول من الجهاز. مثال للقراية — SkillBridge ما بينفّذش الأوامر دي.",
            },
            "practice": {
                "title": "أتاح API في الحاوية على البورت الصح",
                "task": "حاوية اسمها `api` شغالة بخدمة بتسمع على بورت 3000 جوهها، بس مش قادرة توصلها من لابتوبك. اكتب أمر `docker run` المظبوط اللي كان المفروض تشغّل بيه الحاوية عشان الخدمة تكون قابلة للوصول على بورت 8080 على الجهاز، وورّي إزاي تتأكد من الربط بـ `docker port` و`docker inspect`. وبعدين اشرح الفرق بين `EXPOSE 3000` في Dockerfile و`-p 8080:3000` في سطر الأوامر. SkillBridge بيراجع أوامرك كنص بس — مش بينفّذها.",
                "response_type": "command",
                "competency": "Ports",
                "evaluation_note": "مراجعة نصية ثابتة فقط: SkillBridge بيتأكد من أمر `docker run` بيستخدم `-p 8080:3000` (أو ما يعادله) مع `--name api`، و`docker port api`، و`docker inspect` لقراية الربط، وشرح إن EXPOSE بيوثّق البورت بينما `-p` بينشره على الجهاز. مش بيشغّل Docker، فالمراجعة ما بتثبتش نتيجة تشغيل. الإجابة القوية بتسمّي الصورة، وتحدد الربط بالظبط، وتعطي خطوة تحقق عملية. الإجابة الضعيفة بتقول إن EXPOSE كفاية لوحده، أو تستخدم البورتات بترتيب عكسي، أو تتخطّى التحقق.",
            },
            "mini_check": {"questions": [
                {"id": "p1", "question": "أي فلاغ في `docker run` بينشر بورت الحاوية على الجهاز؟", "options": ["-p", "-d", "--name", "--rm"], "misconception_hint": "دور على الفلاغ اللي بيعمل ربط من بورت الجهاز لبورت الحاوية."},
                {"id": "p2", "question": "إيه اللي بيعمله `EXPOSE 3000` في Dockerfile؟", "options": ["بيوثّق إن الخدمة بتسمع على بورت 3000", "بينشر بورت 3000 على الجهاز", "بيفوّر البورت تلقائيًا", "بينشئ شبكة Docker"], "misconception_hint": "النشر على الجهاز بيتطلب فلاغ وقت التشغيل، مش بس تعليمة في Dockerfile."},
                {"id": "p3", "question": "في `docker run -p 8080:80`، أي بورت تبع الجهاز؟", "options": ["8080", "80", "الاتنين", "ولا واحد"], "misconception_hint": "بورت الجهاز هو اللي بيكتب الأول في صيغة HOST:CONTAINER."},
            ]},
        },
    },
}


DOCKER_VOLUMES = {
    "status": "complete",
    "skill_aliases": ("docker", "docker & containers"),
    "competency": "Volumes",
    "objective": "Use Docker volumes to persist data beyond the container lifecycle and share data between containers.",
    "objectives": [
        "Explain that files written inside a container's writable layer are lost when the container is removed.",
        "Create a named volume with `docker volume create`.",
        "Mount a volume into a container with `docker run -v NAME:PATH`.",
        "List and inspect volumes with `docker volume ls` and `docker volume inspect`.",
        "Choose when to use a named volume versus a bind mount.",
    ],
    "prerequisites": [],
    "roadmap_rationale": (
        "Volumes follows Containers because persistence only matters once you can create and remove "
        "containers. It prepares the learner for stateful services and multi-container Compose stacks."
    ),
    "learn": {
        "title": "Volumes",
        "explanation": (
            "By default, files written inside a container live only as long as the container. A "
            "**Docker volume** is a managed storage area outside the container filesystem. Data in a "
            "volume survives `docker rm`, can be mounted into a replacement container, and can even be "
            "shared by multiple containers at the same time."
        ),
        "key_ideas": [
            "A container's writable layer is deleted when the container is removed; a volume is not.",
            "`docker volume create mydata` creates a named volume managed by Docker.",
            "`docker run -v mydata:/app/data ...` mounts the volume at `/app/data` inside the container.",
            "`docker volume ls` lists volumes; `docker volume inspect mydata` shows where it is mounted and which driver it uses.",
            "Named volumes are easier to back up and move than bind mounts; bind mounts tie a host path directly to a container path.",
        ],
        "key_terms": {
            "volume": "Managed storage outside a container's filesystem that survives container removal.",
            "named volume": "A volume created explicitly with a name, such as `mydata`, so it can be reused.",
            "bind mount": "A mount that maps a specific host path into a container path.",
            "mount point": "The path inside the container where external storage appears.",
            "persistent storage": "Storage that keeps its data after the process or container using it stops.",
        },
        "job_relevance": (
            "Databases, caches, user uploads, and log files must outlive the container. Volumes are the "
            "standard way to keep that data safe across deploys, restarts, and container replacements."
        ),
        "real_world_example": (
            "You upgrade Postgres from 15 to 16. The old container is removed with `docker rm`, but its "
            "data directory was stored in a named volume called `pgdata`. You start the new Postgres "
            "container with the same `-v pgdata:/var/lib/postgresql/data` flag, and the database comes "
            "back online with all tables and rows intact."
        ),
        "common_mistake": (
            "Do not store important data only in the container's writable layer: it is deleted when the "
            "container is removed. Use a volume (or bind mount) for anything that must survive."
        ),
        "worked_example": (
            "The example creates a named volume, runs a container that writes a file into it, removes "
            "the container, and proves the data still exists by mounting the same volume in a new container."
        ),
        "depth_note": "Canonical intermediate content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": (
            "Examples use the modern unified Docker CLI (Docker Engine 23 and later). SkillBridge does not "
            "execute Docker commands."
        ),
        "grounding_sources": [
            {"title": "Docker volumes", "url": "https://docs.docker.com/engine/storage/volumes/", "source": "Docker documentation"},
            {"title": "Docker storage overview", "url": "https://docs.docker.com/engine/storage/", "source": "Docker documentation"},
        ],
    },
    "example": {
        "title": "Persist data with a named volume",
        "type": "bash",
        "content": (
            "# 1) create a named volume\n"
            "docker volume create mydata\n"
            "\n"
            "# 2) run a container that writes to the volume\n"
            "docker run -d --name writer -v mydata:/app/data busybox:1.36 \"\n"
            "  sh -c 'echo hello > /app/data/file.txt'\n"
            "\n"
            "# 3) remove the writer container\n"
            "docker rm writer\n"
            "\n"
            "# 4) run a new container with the same volume and read the file\n"
            "docker run --rm -v mydata:/app/data busybox:1.36 cat /app/data/file.txt"
        ),
        "explanation": (
            "The volume outlives the first container. Even after `docker rm writer`, the file written to "
            "`/app/data` remains in `mydata` and is visible to the second container. Worked example for "
            "reading — SkillBridge does not run these commands."
        ),
    },
    "practice": {
        "type": "practical",
        "title": "Keep a database alive across container restarts",
        "task": (
            "Your Postgres container must keep its data even if the container is removed. Write the "
            "Docker commands to: (1) create a named volume called `pgdata`, (2) run a Postgres 16 "
            "container named `db` with the volume mounted at `/var/lib/postgresql/data` and a password "
            "set via `-e POSTGRES_PASSWORD=secret`, (3) confirm the volume is listed and the container "
            "is running, (4) remove the `db` container, and (5) start a new Postgres 16 container named "
            "`db2` using the same volume and show that the previous data is still there. For each step, "
            "add one line stating what output proves it worked. SkillBridge reviews your commands as text "
            "only — it never executes them."
        ),
        "response_type": "command",
        "competency": "Volumes",
        "evaluation_note": (
            "Static text review only: SkillBridge checks for `docker volume create pgdata`, a `docker run` "
            "command with `-v pgdata:/var/lib/postgresql/data` and `-e POSTGRES_PASSWORD=secret`, "
            "`docker volume ls` / `docker volume inspect pgdata` or `docker ps` for verification, "
            "`docker rm db`, and a second `docker run` reusing the same volume. It does not run Docker, "
            "so the review cannot prove runtime results. A strong answer names the volume and container, "
            "states the verification output for every step, and explains why the data survives. A weak "
            "answer omits the volume, forgets the environment variable, or skips verification."
        ),
    },
    "mini_check": {
        "questions": [
            {"id": "v1", "type": "mcq", "question": "What happens to data written in a container's writable layer when the container is removed?", "options": ["It is deleted", "It is copied into the image", "It moves to a volume automatically", "It stays forever"], "correct_answer": "It is deleted", "competency": "Volumes", "difficulty": "beginner", "misconception_hint": "The writable layer is part of the container, not a separate persistent store."},
            {"id": "v2", "type": "mcq", "question": "Which command creates a named Docker volume?", "options": ["docker volume create mydata", "docker create volume mydata", "docker run -v mydata", "docker build -v mydata"], "correct_answer": "docker volume create mydata", "competency": "Volumes", "difficulty": "beginner", "misconception_hint": "The noun comes before the verb in the Docker CLI for this resource."},
            {"id": "v3", "type": "mcq", "question": "Which flag mounts a named volume `mydata` into a container at `/app/data`?", "options": ["-v mydata:/app/data", "-p mydata:/app/data", "--name mydata:/app/data", "--rm mydata:/app/data"], "correct_answer": "-v mydata:/app/data", "competency": "Volumes", "difficulty": "beginner", "misconception_hint": "The flag for mounting storage is the same one used for bind mounts."},
        ]
    },
    "locales": {
        "ar": {
            "learn": {
                "title": "الـ Volumes في Docker",
                "explanation": "افتراضيًا، الملفات اللي بتتكتب جوه الحاوية بتعيش لحد ما الحاوية تتشال. الـ **Docker volume** هي مساحة تخزين مُدارة برّا نظام ملفات الحاوية. البيانات في الـ volume بتفوق `docker rm`، وممكن تركّبها في حاوية بديلة، وممكن كمان تشاركها حاويات متعددة في نفس الوقت.",
                "key_ideas": [
                    "طبقة الكتابة في الحاوية بتمسح لما الحاوية تتشال؛ الـ volume لأ.",
                    "`docker volume create mydata` بيعمل volume مسمّى بيديره Docker.",
                    "`docker run -v mydata:/app/data ...` بيركّب الـ volume على مسار `/app/data` جوه الحاوية.",
                    "`docker volume ls` بيسرد الـ volumes؛ `docker volume inspect mydata` بيوري فين متركّب والـ driver المستخدم.",
                    "الـ named volumes أسهل في الـ backup والنقل من الـ bind mounts؛ الـ bind mounts بيربطوا مسار محدد على الـ host مباشرة بالحاوية.",
                ],
                "key_terms": {"volume": "تخزين مُدارة برّا نظام ملفات الحاوية وبيفوق إزالتها.", "named volume": "volume اتعمل باسم صريح زي `mydata` عشان يت reused.", "bind mount": "تركيب بيربط مسار محدد على الـ host بمسار جوه الحاوية.", "mount point": "المسار جوه الحاوية اللي بيظهر فيه التخزين الخارجي.", "persistent storage": "تخزين بيحتفظ بالبيانات بعد ما العملية أو الحاوية توقف."},
                "job_relevance": "قواعد البيانات والـ caches وملفات المستخدمين والـ logs لازم تفوق الحاوية. الـ Volumes هي الطريقة القياسية للحفاظ على البيانات أثناء النشر وإعادة التشغيل واستبدال الحاويات.",
                "real_world_example": "بتعمل upgrade لـ Postgres من 15 لـ 16. الحاوية القديمة اتشالت بـ `docker rm`، بس مجلد البيانات كان في volume اسمه `pgdata`. بتشغّل حاوية Postgres 16 جديدة بنفس الفلاغ `-v pgdata:/var/lib/postgresql/data`، وقاعدة البيانات ترجع شغالة بكل الجداول والصفوف زي ما هي.",
                "common_mistake": "ما تخزّنش بيانات مهمة في طبقة الكتابة بتاعة الحاوية بس: هتمسح لما الحاوية تتشال. استخدم volume (أو bind mount) لأي حاجة لازم تفوق.",
                "worked_example": "المثال بيعمل volume مسمّى، بيشغّل حاوية تكتب ملف فيه، بيمسح الحاوية، وبيثبت إن البيانات لسه موجودة بتركيب نفس الـ volume في حاوية جديدة.",
                "depth_note": "محتوى متوسط ثابت من قاعدة المعرفة المراجَعة، مش محتوى مولّد حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم الـ Docker CLI الحديث (Docker Engine 23 وما بعده). SkillBridge ما بينفّذش أوامر Docker.",
                "grounding_sources": [
                    {"title": "Docker volumes", "url": "https://docs.docker.com/engine/storage/volumes/", "source": "Docker documentation"},
                    {"title": "نظرة عامة على تخزين Docker", "url": "https://docs.docker.com/engine/storage/", "source": "Docker documentation"},
                ],
            },
            "example": {
                "title": "حافظ على البيانات بـ named volume",
                "type": "bash",
                "content": "# 1) create a named volume\ndocker volume create mydata\n\n# 2) run a container that writes to the volume\ndocker run -d --name writer -v mydata:/app/data busybox:1.36 \\\n  sh -c 'echo hello > /app/data/file.txt'\n\n# 3) remove the writer container\ndocker rm writer\n\n# 4) run a new container with the same volume and read the file\ndocker run --rm -v mydata:/app/data busybox:1.36 cat /app/data/file.txt",
                "explanation": "الـ volume بيفوق الحاوية الأولى. حتى بعد `docker rm writer`، الملف اللي اتكتب في `/app/data` لسه موجود في `mydata` وظاهر للحاوية التانية. مثال للقراية — SkillBridge ما بينفّذش الأوامر دي.",
            },
            "practice": {
                "title": "أبقِ قاعدة البيانات شغالة بعد استبدال الحاوية",
                "task": "حاوية Postgres عندك لازم تحتفظ ببياناتها حتى لو اتشالت. اكتب أوامر Docker عشان: (١) تعمل volume مسمّى `pgdata`، (٢) تشغّل حاوية Postgres 16 اسمها `db` مركّبة الـ volume على `/var/lib/postgresql/data` وكلمة سر محددة بـ `-e POSTGRES_PASSWORD=secret`، (٣) تتأكد إن الـ volume موجود والحاوية شغالة، (٤) تمسح الحاوية `db`، و(٥) تشغّل حاوية Postgres 16 جديدة اسمها `db2` بنفس الـ volume وتوري إن البيانات القديمة لسه موجودة. لكل خطوة ضيف سطر بيقول إيه المخرج اللي بيثبت نجاحها. SkillBridge بيراجع أوامرك كنص بس — مش بينفّذها.",
                "response_type": "command",
                "competency": "Volumes",
                "evaluation_note": "مراجعة نصية ثابتة فقط: SkillBridge بيتأكد من `docker volume create pgdata`، وأمر `docker run` بيستخدم `-v pgdata:/var/lib/postgresql/data` و`-e POSTGRES_PASSWORD=secret`، و`docker volume ls` / `docker volume inspect pgdata` أو `docker ps` للتحقق، و`docker rm db`، وأمر `docker run` تاني بيستخدم نفس الـ volume. مش بيشغّل Docker، فالمراجعة ما بتثبتش نتيجة تشغيل. الإجابة القوية بتسمّي الـ volume والحاوية، وبتقول مخرج التحقق في كل خطوة، وبتشرح ليه البيانات بتفوق. الإجابة الضعيفة بتنسى الـ volume، أو متسيب variable الباسورد، أو تتخطّى التحقق.",
            },
            "mini_check": {"questions": [
                {"id": "v1", "question": "إيه اللي بيحصل للبيانات اللي اتكتبت في طبقة الكتابة بتاعة الحاوية لما الحاوية تتشال؟", "options": ["بتمسح", "بتتنسخ للصورة", "بتروح لـ volume تلقائيًا", "بتفضل للأبد"], "misconception_hint": "طبقة الكتابة جزء من الحاوية، مش تخزين منفصل دائم."},
                {"id": "v2", "question": "أي أمر بيعمل Docker volume مسمّى؟", "options": ["docker volume create mydata", "docker create volume mydata", "docker run -v mydata", "docker build -v mydata"], "misconception_hint": "في الـ Docker CLI الاسم بيجي بعد الفعل بالنسبة للـ resource ده."},
                {"id": "v3", "question": "أي فلاغ بيركّب volume اسمه `mydata` جوه الحاوية على `/app/data`؟", "options": ["-v mydata:/app/data", "-p mydata:/app/data", "--name mydata:/app/data", "--rm mydata:/app/data"], "misconception_hint": "نفس الفلاغ بيستخدم للـ bind mounts كمان."},
            ]},
        },
    },
}


DOCKER_NETWORKING = {
    "status": "complete",
    "skill_aliases": ("docker", "docker & containers"),
    "competency": "Networking",
    "objective": "Connect containers with a user-defined bridge network and use container names as hostnames for service-to-service communication.",
    "objectives": [
        "Explain the difference between the default bridge and a user-defined bridge network.",
        "Create a network with `docker network create`.",
        "Run containers on the same network with `--network`.",
        "Use container names as DNS hostnames to reach another container.",
        "Inspect a network with `docker network inspect`.",
    ],
    "prerequisites": [],
    "roadmap_rationale": (
        "Networking follows Ports because once a learner can publish a single container's port, the next "
        "step is making multiple containers talk to each other reliably by name. It is a prerequisite for Compose."
    ),
    "learn": {
        "title": "Networking",
        "explanation": (
            "By default, every container gets its own network namespace. Containers on the default bridge "
            "can reach each other only by IP address, which changes. A **user-defined bridge network** gives "
            "containers DNS-based names and controlled isolation: containers on the same network can talk by "
            "name, while unrelated containers stay separated."
        ),
        "key_ideas": [
            "The default bridge network does not provide DNS; containers are reached by IP, which is fragile.",
            "`docker network create appnet` creates a user-defined bridge network.",
            "`docker run --network appnet --name web ...` joins a container to that network.",
            "Containers on the same user-defined network can resolve each other by name, e.g. `web` or `db:5432`.",
            "`docker network inspect appnet` shows which containers are attached and their IP addresses.",
        ],
        "key_terms": {
            "network namespace": "An isolated network stack (interfaces, routes, firewall rules) for a container.",
            "bridge network": "A virtual switch inside Docker that connects containers on the same host.",
            "user-defined network": "A custom bridge network created by the user, with built-in DNS and better isolation.",
            "DNS resolution": "Looking up a container by its name to find its IP address.",
            "service discovery": "Finding another service by name rather than by a changing IP address.",
        },
        "job_relevance": (
            "Multi-service applications (web + database + cache) need reliable communication. User-defined "
            "networks are the standard way to give containers stable names and isolate application stacks."
        ),
        "real_world_example": (
            "An API container needs to reach a Postgres container. If they share a user-defined network called "
            "`appnet`, the API can connect to `postgres://db:5432/mydb`. When the Postgres container restarts "
            "and gets a new IP, the name still resolves correctly."
        ),
        "common_mistake": (
            "Do not rely on the default bridge for service-to-service communication: IP addresses change and "
            "there is no DNS. Create a user-defined network and use container names as hostnames."
        ),
        "worked_example": (
            "The example creates a network, runs a database and a web container on it, and shows how the web "
            "container reaches the database by name instead of by IP."
        ),
        "depth_note": "Canonical intermediate content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": (
            "Examples use the modern unified Docker CLI (Docker Engine 23 and later). SkillBridge does not "
            "execute Docker commands."
        ),
        "grounding_sources": [
            {"title": "Docker networking overview", "url": "https://docs.docker.com/engine/network/", "source": "Docker documentation"},
            {"title": "Bridge network overview", "url": "https://docs.docker.com/engine/network/drivers/bridge/", "source": "Docker documentation"},
        ],
    },
    "example": {
        "title": "Connect a web app and a database on the same network",
        "type": "bash",
        "content": (
            "# 1) create a user-defined bridge network\n"
            "docker network create appnet\n"
            "\n"
            "# 2) run a database container on the network\n"
            "docker run -d --name db --network appnet -e POSTGRES_PASSWORD=secret postgres:16\n"
            "\n"
            "# 3) run a web container on the same network, publishing its port\n"
            "docker run -d --name web --network appnet -p 8080:80 myweb:1.0\n"
            "\n"
            "# 4) inspect the network to see attached containers\n"
            "docker network inspect appnet\n"
            "\n"
            "# Inside the web container, the database is reachable at db:5432"
        ),
        "explanation": (
            "Both containers are on `appnet`, so they can resolve each other by name. The web container does "
            "not need to know the database's IP; it uses `db:5432`. Publishing `-p 8080:80` only exposes the "
            "web service to the host. Worked example for reading — SkillBridge does not run these commands."
        ),
    },
    "practice": {
        "type": "practical",
        "title": "Wire a web container to a database by name",
        "task": (
            "You need an API container (`api`) to reach a Postgres database container (`db`) without hardcoding "
            "an IP address. Write the commands to: (1) create a user-defined bridge network called `appnet`, "
            "(2) run the `db` container on `appnet` with a password set via environment variable, (3) run the "
            "`api` container on `appnet` publishing host port 8080 to container port 3000, and (4) show how the "
            "API would connect to the database using the container name. Also write the `docker network inspect` "
            "command you would use to verify both containers are attached. SkillBridge reviews your commands as "
            "text only — it never executes them."
        ),
        "response_type": "command",
        "competency": "Networking",
        "evaluation_note": (
            "Static text review only: SkillBridge checks for `docker network create appnet`, two `docker run` "
            "commands using `--network appnet` with `--name db` and `--name api`, `-e POSTGRES_PASSWORD=...`, "
            "`-p 8080:3000`, a connection string or hostname using `db` (not an IP), and `docker network inspect appnet`. "
            "It does not run Docker, so the review cannot prove runtime results. A strong answer explains why a "
            "user-defined network is better than the default bridge for name resolution. A weak answer uses IP "
            "addresses, omits `--network`, or confuses port publishing with internal container DNS."
        ),
    },
    "mini_check": {
        "questions": [
            {"id": "n1", "type": "mcq", "question": "What is the main advantage of a user-defined bridge network over the default bridge?", "options": ["Containers can resolve each other by name (DNS)", "It makes containers run faster", "It removes the need for port publishing", "It gives containers direct host network access"], "correct_answer": "Containers can resolve each other by name (DNS)", "competency": "Networking", "difficulty": "beginner", "misconception_hint": "The default bridge lacks a feature that makes service-to-service addressing fragile."},
            {"id": "n2", "type": "mcq", "question": "Which command creates a new Docker network?", "options": ["docker network create appnet", "docker create network appnet", "docker net add appnet", "docker bridge create appnet"], "correct_answer": "docker network create appnet", "competency": "Networking", "difficulty": "beginner", "misconception_hint": "The CLI follows the same resource-verb pattern as volumes and containers."},
            {"id": "n3", "type": "mcq", "question": "In a user-defined network, how does a web container reach a database container named `db`?", "options": ["Using the hostname `db`", "Using the host's IP address", "By sharing the same writable layer", "Through `docker exec` only"], "correct_answer": "Using the hostname `db`", "competency": "Networking", "difficulty": "beginner", "misconception_hint": "User-defined networks provide DNS resolution for container names."},
        ]
    },
    "locales": {
        "ar": {
            "learn": {
                "title": "الشبكات في Docker",
                "explanation": "افتراضيًا، كل حاوية ليها namespace شبكة منفصل. الحاويات على الـ bridge الافتراضي ممكن توصل بعضها بس عن طريق IP address، واللي بيتغيّر. الـ **user-defined bridge network** بتدي الحاويات أسماء من خلال DNS وعزل محكوم: الحاويات على نفس الشبكة ممكن تتكلم باسمها، بينما الحاويات غير المرتبطة بتفضل منفصلة.",
                "key_ideas": [
                    "الـ default bridge network مفيش فيه DNS؛ الحاويات بتتوصل ببعضها عن طريق IP، وده مش ثابت.",
                    "`docker network create appnet` بيعمل user-defined bridge network.",
                    "`docker run --network appnet --name web ...` بيدخل حاوية للشبكة دي.",
                    "الحاويات على نفس الـ user-defined network ممكن تستخدم أسماء بعضها، مثلًا `web` أو `db:5432`.",
                    "`docker network inspect appnet` بيوريك الحاويات المرتبطة وعناوين IP بتاعتها.",
                ],
                "key_terms": {"network namespace": "stack شبكة معزول (interfaces, routes, firewall rules) للحاوية.", "bridge network": "switch افتراضي جوه Docker بيوصّل الحاويات على نفس الجهاز.", "user-defined network": "شبكة bridge مخصصة بتتعمل بواسطة المستخدم، فيها DNS مدمج وعزل أفضل.", "DNS resolution": "إنك تلاقي الحاوية باسمها بدل ما تدور على IP address.", "service discovery": "إنك تلاقي خدمة تانية باسمها بدل IP متغيّر."},
                "job_relevance": "التطبيقات متعددة الخدمات (web + database + cache) محتاجة تواصل ثابت. الـ user-defined networks هي الطريقة القياسية لمنح الحاويات أسماء ثابتة وعزل stack التطبيق.",
                "real_world_example": "حاوية API محتاجة توصل لـ Postgres. لو هما على نفس شبكة اسمها `appnet`، الـ API ممكن يتصل بـ `postgres://db:5432/mydb`. لما حاوية Postgres تتعمل restart وتاخد IP جديد، الاسم لسه بيتحلّل صح.",
                "common_mistake": "ما تعتمدش على الـ default bridge للتواصل بين الخدمات: عناوين IP بتتغيّر ومفيش DNS. اعمل user-defined network واستخدم أسماء الحاويات كـ hostnames.",
                "worked_example": "المثال بيعمل شبكة، بيشغّل حاوية قاعدة بيانات وحاوية ويب عليها، وبيوضّح إزاي حاوية الـ web توصل لـ db بالاسم بدل IP.",
                "depth_note": "محتوى متوسط ثابت من قاعدة المعرفة المراجَعة، مش محتوى مولّد حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم الـ Docker CLI الحديث (Docker Engine 23 وما بعده). SkillBridge ما بينفّذش أوامر Docker.",
                "grounding_sources": [
                    {"title": "نظرة عامة على شبكات Docker", "url": "https://docs.docker.com/engine/network/", "source": "Docker documentation"},
                    {"title": "نظرة عامة على bridge network", "url": "https://docs.docker.com/engine/network/drivers/bridge/", "source": "Docker documentation"},
                ],
            },
            "example": {
                "title": "وصّل تطبيق ويب بقاعدة بيانات على نفس الشبكة",
                "type": "bash",
                "content": "# 1) create a user-defined bridge network\ndocker network create appnet\n\n# 2) run a database container on the network\ndocker run -d --name db --network appnet -e POSTGRES_PASSWORD=secret postgres:16\n\n# 3) run a web container on the same network, publishing its port\ndocker run -d --name web --network appnet -p 8080:80 myweb:1.0\n\n# 4) inspect the network to see attached containers\ndocker network inspect appnet\n\n# Inside the web container, the database is reachable at db:5432",
                "explanation": "الاتنين على `appnet`، فممكن يحلّلوا بعض بالاسم. حاوية الـ web مش محتاجة تعرف IP بتاع الـ database؛ بتستخدم `db:5432`. نشر `-p 8080:80` بيكشف خدمة الويب للـ host بس. مثال للقراية — SkillBridge ما بينفّذش الأوامر دي.",
            },
            "practice": {
                "title": "وصّل حاوية API بقاعدة بيانات بالاسم",
                "task": "محتاج حاوية API (`api`) توصل لـ Postgres (`db`) من غير ما تثبت IP address. اكتب الأوامر عشان: (١) تعمل user-defined bridge network اسمها `appnet`، (٢) تشغّل حاوية `db` على `appnet` مع كلمة سر محددة بـ environment variable، (٣) تشغّل حاوية `api` على `appnet` وتنشر بورت 8080 على الجهاز لبورت 3000 جوهها، و(٤) تورّي إزاي الـ API هيتصل بـ db باستخدام اسم الحاوية. اكتب كمان أمر `docker network inspect appnet` اللي هتستخدمه للتحقق إن الاتنين مرتبطين. SkillBridge بيراجع أوامرك كنص بس — مش بينفّذها.",
                "response_type": "command",
                "competency": "Networking",
                "evaluation_note": "مراجعة نصية ثابتة فقط: SkillBridge بيتأكد من `docker network create appnet`، وأمرين `docker run` بيستخدموا `--network appnet` مع `--name db` و`--name api`، و`-e POSTGRES_PASSWORD=...`، و`-p 8080:3000`، وconnection string أو hostname بيستخدم `db` (مش IP)، و`docker network inspect appnet`. مش بيشغّل Docker، فالمراجعة ما بتثبتش نتيجة تشغيل. الإجابة القوية بتشرح ليه user-defined network أحسن من الـ default bridge للـ name resolution. الإجابة الضعيفة بتستخدم IP addresses، أو تنسى `--network`، أو تخلط بين نشر البورت والـ DNS الداخلي للحاويات.",
            },
            "mini_check": {"questions": [
                {"id": "n1", "question": "إيه أهم ميزة في user-defined bridge network مقارنة بالـ default bridge؟", "options": ["الحاويات ممكن تحلّل بعضها بالاسم (DNS)", "الحاويات بتشتغل أسرع", "بيلغي الحاجة لنشر البورتات", "بيدي الحاويات وصول مباشر لشبكة الـ host"], "misconception_hint": "الـ default bridge ناقصة ميزة بتخلي التواصل بين الخدمات غير ثابت."},
                {"id": "n2", "question": "أي أمر بيعمل شبكة Docker جديدة؟", "options": ["docker network create appnet", "docker create network appnet", "docker net add appnet", "docker bridge create appnet"], "misconception_hint": "الـ CLI بنفس نمط الـ resource-verb زي الـ volumes والحاويات."},
                {"id": "n3", "question": "في user-defined network، إزاي حاوية web توصل لحاوية database اسمها `db`؟", "options": ["باستخدام الـ hostname `db`", "باستخدام IP address بتاع الـ host", "بمشاركة نفس طبقة الكتابة", "عن طريق `docker exec` بس"], "misconception_hint": "الـ user-defined networks بتدي DNS resolution لأسماء الحاويات."},
            ]},
        },
    },
}


DOCKER_COMPOSE = {
    "status": "complete",
    "skill_aliases": ("docker", "docker & containers"),
    "competency": "Compose",
    "objective": "Define and run a multi-container application with a docker-compose.yml file using the modern docker compose plugin syntax.",
    "objectives": [
        "Explain when Docker Compose is preferable to many individual `docker run` commands.",
        "Write a `docker-compose.yml` file with services, images, ports, volumes, and environment variables.",
        "Start and stop a stack with `docker compose up -d` and `docker compose down`.",
        "View logs with `docker compose logs`.",
        "Use the modern `docker compose` plugin syntax instead of the legacy `docker-compose` command.",
    ],
    "prerequisites": [],
    "roadmap_rationale": (
        "Compose is the capstone Docker topic: it uses containers, images, ports, volumes, and networking "
        "together in one declarative file. It belongs after the individual building blocks are established."
    ),
    "learn": {
        "title": "Compose",
        "explanation": (
            "Docker Compose lets you describe a multi-container application in a single YAML file, "
            "`docker-compose.yml`. Instead of remembering many `docker run` commands, you declare services, "
            "their images, ports, volumes, environment variables, and networks, then start the whole stack "
            "with one command. Modern Docker uses the `docker compose` plugin (a space), not the older "
            "`docker-compose` binary."
        ),
        "key_ideas": [
            "A `docker-compose.yml` file describes one or more services and their relationships.",
            "`docker compose up -d` creates networks, volumes, and containers in the right order and starts them in the background.",
            "`docker compose down` stops and removes containers and networks; add `--volumes` to remove named volumes too.",
            "`docker compose logs` shows combined logs from all services, or a single service with `docker compose logs web`.",
            "Each service name becomes a DNS hostname on the Compose-created network, just like a user-defined bridge network.",
        ],
        "key_terms": {
            "compose": "A Docker tool that defines and runs multi-container applications from a YAML file.",
            "service": "One container definition inside a docker-compose.yml file.",
            "docker-compose.yml": "The declarative file that describes the application's services, networks, and volumes.",
            "docker compose": "The modern Docker CLI plugin command (space between words).",
            "stack": "The collection of containers, networks, and volumes created by a Compose file.",
        },
        "job_relevance": (
            "Most real projects run more than one container. Compose is the standard way to define local "
            "development environments and small deployments so the whole team starts the same stack with one command."
        ),
        "real_world_example": (
            "A new developer clones the repository and runs `docker compose up -d`. One command starts the "
            "web service, the API, and the database, all on the same network with the right volumes and "
            "environment variables. There is no need to copy five separate `docker run` commands from a README."
        ),
        "common_mistake": (
            "Do not use the legacy `docker-compose` command in new workflows. Modern Docker installs provide "
            "`docker compose` (two words, a CLI plugin) with better integration and consistency."
        ),
        "worked_example": (
            "The example defines a web service and a database service in docker-compose.yml, starts them in "
            "the background, checks logs, and tears the stack down."
        ),
        "depth_note": "Canonical advanced content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": (
            "Examples use Compose file format 3.8 and the modern `docker compose` CLI plugin. SkillBridge does "
            "not execute Docker commands."
        ),
        "grounding_sources": [
            {"title": "Docker Compose overview", "url": "https://docs.docker.com/compose/", "source": "Docker documentation"},
            {"title": "Compose file reference", "url": "https://docs.docker.com/reference/compose-file/", "source": "Docker documentation"},
        ],
    },
    "example": {
        "title": "Run a web service and database with Compose",
        "type": "bash",
        "content": (
            "# docker-compose.yml\n"
            "version: \"3.8\"\n"
            "services:\n"
            "  db:\n"
            "    image: postgres:16\n"
            "    environment:\n"
            "      POSTGRES_PASSWORD: secret\n"
            "    volumes:\n"
            "      - pgdata:/var/lib/postgresql/data\n"
            "  web:\n"
            "    image: myweb:1.0\n"
            "    ports:\n"
            "      - \"8080:80\"\n"
            "    depends_on:\n"
            "      - db\n"
            "volumes:\n"
            "  pgdata:\n"
            "\n"
            "# Start the stack in the background\n"
            "docker compose up -d\n"
            "\n"
            "# View logs\n"
            "docker compose logs\n"
            "\n"
            "# Stop and remove containers and networks\n"
            "docker compose down"
        ),
        "explanation": (
            "The YAML file replaces several `docker run` commands. Compose creates the network and volume, "
            "starts the database, then starts the web service, and makes `db` reachable by name from `web`. "
            "Worked example for reading — SkillBridge does not run these commands."
        ),
    },
    "practice": {
        "type": "practical",
        "title": "Write a Compose file for a Node.js app and Postgres",
        "task": (
            "Write a `docker-compose.yml` file for a small Node.js API (`api`) and a Postgres database (`db`). "
            "Requirements: (1) Use Compose file version `3.8`, (2) define a `db` service using image `postgres:16` "
            "with environment variable `POSTGRES_PASSWORD=secret` and a named volume `pgdata` mounted at "
            "`/var/lib/postgresql/data`, (3) define an `api` service using image `myapi:1.0` that publishes host "
            "port 8080 to container port 3000 and depends on `db`, (4) declare the `pgdata` volume at the top level, "
            "(5) write the commands to start the stack in the background and view logs, (6) write the command to "
            "stop and remove everything including volumes. Use modern `docker compose` syntax (not `docker-compose`). "
            "SkillBridge reviews your YAML and commands as text only — it never executes them."
        ),
        "response_type": "configuration",
        "competency": "Compose",
        "evaluation_note": (
            "Static text review only: SkillBridge checks for `version: \"3.8\"`, two services (`db`, `api`), "
            "`image`, `environment`, `volumes`, `ports`, and `depends_on`, top-level `volumes:`, `docker compose up -d`, "
            "`docker compose logs`, and `docker compose down --volumes`, all using the modern `docker compose` form. "
            "It does not run Docker, so the review cannot prove runtime results. A strong answer keeps the YAML "
            "indentation consistent and explains why `depends_on` only controls start order, not readiness. A weak "
            "answer uses the legacy `docker-compose` command, omits the volume declaration, or mixes up host and container ports."
        ),
    },
    "mini_check": {
        "questions": [
            {"id": "c1", "type": "mcq", "question": "Which command starts a Compose stack in the background using the modern plugin syntax?", "options": ["docker compose up -d", "docker-compose up -d", "docker compose start", "docker run compose up"], "correct_answer": "docker compose up -d", "competency": "Compose", "difficulty": "beginner", "misconception_hint": "Modern Docker uses a CLI plugin with a space, not the legacy hyphenated binary."},
            {"id": "c2", "type": "mcq", "question": "In a docker-compose.yml, what does `depends_on` do?", "options": ["Controls service start order only", "Waits until a service is healthy before starting", "Creates a shared volume", "Publishes ports"], "correct_answer": "Controls service start order only", "competency": "Compose", "difficulty": "beginner", "misconception_hint": "It does not guarantee the dependency is ready to accept traffic."},
            {"id": "c3", "type": "mcq", "question": "How do containers in a Compose project reach each other by name?", "options": ["Compose creates a user-defined network with DNS", "They share the host network", "They must use published host ports", "They use the default bridge with IP addresses"], "correct_answer": "Compose creates a user-defined network with DNS", "competency": "Compose", "difficulty": "beginner", "misconception_hint": "Compose automatically provides the same name-resolution feature as a user-defined bridge network."},
        ]
    },
    "locales": {
        "ar": {
            "learn": {
                "title": "Docker Compose",
                "explanation": "Docker Compose بيسمح لك توصف تطبيق متعدد الحاويات في ملف YAML واحد، `docker-compose.yml`. بدل ما تفتكر كام أمر `docker run`، بتصرّح بالـ services والصور والبورتات والـ volumes والـ environment variables، وبعدين تشغّل الـ stack كله بأمر واحد. Docker الحديث بيستخدم `docker compose` plugin (مسافة)، مش الـ `docker-compose` binary القديم.",
                "key_ideas": [
                    "ملف `docker-compose.yml` بيوصف واحد أو أكتر من services وعلاقتهم ببعض.",
                    "`docker compose up -d` بيعمل الشبكات والـ volumes والحاويات بالترتيب الصح ويشغّلها في الخلفية.",
                    "`docker compose down` بيوقف ويمسح الحاويات والشبكات؛ ضيف `--volumes` عشان تمسح الـ named volumes كمان.",
                    "`docker compose logs` بيوريك الـ logs المجمعة من كل الخدمات، أو خدمة واحدة بـ `docker compose logs web`.",
                    "كل اسم service بيتحوّل لـ DNS hostname على الشبكة اللي Compose بيعملها، زي user-defined bridge network بالظبط.",
                ],
                "key_terms": {"compose": "أداة Docker بتعرف وتشغّل تطبيقات متعددة الحاويات من ملف YAML.", "service": "تعريف حاوية واحدة جوه ملف docker-compose.yml.", "docker-compose.yml": "الملف التصريحي اللي بيوصف services وnetworks وvolumes بتاعة التطبيق.", "docker compose": "أمر الـ Docker CLI plugin الحديث (كلمتين منفصلين).", "stack": "مجموعة الحاويات والشبكات والـ volumes اللي بيعملها ملف Compose."},
                "job_relevance": "أغلب المشاريع الحقيقية بتشغّل أكتر من حاوية. Compose هو الطريقة القياسية لتعريف بيئات التطوير المحلية والنشرات الصغيرة، عشان الفريق كله يشغّل نفس الـ stack بأمر واحد.",
                "real_world_example": "مطوّر جديد بيعمل clone للريبو ويشغّل `docker compose up -d`. أمر واحد بيشغّل خدمة الويب، والـ API، وقاعدة البيانات، كلهم على نفس الشبكة مع الـ volumes ومتغيرات البيئة الصح. مفيش حاجة تنسخ خمس أوامر `docker run` من README.",
                "common_mistake": "ما تستخدمش أمر `docker-compose` القديم في الـ workflows الجديدة. Docker الحديث بيوفر `docker compose` (كلمتين، CLI plugin) بتكامل أفضل واتساق أكتر.",
                "worked_example": "المثال بيعرّف خدمة web وخدمة database في docker-compose.yml، يشغّلهم في الخلفية، يتحقق من الـ logs، ويمسح الـ stack.",
                "depth_note": "محتوى متقدم ثابت من قاعدة المعرفة المراجَعة، مش محتوى مولّد حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم Compose file format 3.8 وmodern `docker compose` CLI plugin. SkillBridge ما بينفّذش أوامر Docker.",
                "grounding_sources": [
                    {"title": "نظرة عامة على Docker Compose", "url": "https://docs.docker.com/compose/", "source": "Docker documentation"},
                    {"title": "مرجع ملف Compose", "url": "https://docs.docker.com/reference/compose-file/", "source": "Docker documentation"},
                ],
            },
            "example": {
                "title": "شغّل خدمة ويب وقاعدة بيانات بـ Compose",
                "type": "bash",
                "content": "# docker-compose.yml\nversion: \"3.8\"\nservices:\n  db:\n    image: postgres:16\n    environment:\n      POSTGRES_PASSWORD: secret\n    volumes:\n      - pgdata:/var/lib/postgresql/data\n  web:\n    image: myweb:1.0\n    ports:\n      - \"8080:80\"\n    depends_on:\n      - db\nvolumes:\n  pgdata:\n\n# Start the stack in the background\ndocker compose up -d\n\n# View logs\ndocker compose logs\n\n# Stop and remove containers and networks\ndocker compose down",
                "explanation": "ملف YAML بيحلّ محل كام أمر `docker run`. Compose بيعمل الشبكة والـ volume، يشغّل قاعدة البيانات، وبعدين يشغّل خدمة الويب، ويخلي `db` تتوصل بالاسم من `web`. مثال للقراية — SkillBridge ما بينفّذش الأوامر دي.",
            },
            "practice": {
                "title": "اكتب Compose file لتطبيق Node.js وPostgres",
                "task": "اكتب ملف `docker-compose.yml` لتطبيق Node.js API (`api`) وقاعدة بيانات Postgres (`db`). المتطلبات: (١) استخدم Compose file version `3.8`، (٢) عرّف خدمة `db` بصورة `postgres:16` ومتغير بيئة `POSTGRES_PASSWORD=secret` وnamed volume `pgdata` مركّب على `/var/lib/postgresql/data`، (٣) عرّف خدمة `api` بصورة `myapi:1.0` تنشر بورت 8080 على الجهاز لبورت 3000 جوهها وتعتمد على `db`، (٤) صرّح عن الـ volume `pgdata` على مستوى أعلى، (٥) اكتب الأوامر اللي تشغّل الـ stack في الخلفية وتوري الـ logs، (٦) اكتب الأمر اللي يوقف ويمسح كل حاجة بما فيها الـ volumes. استخدم صيغة `docker compose` الحديثة (مش `docker-compose`). SkillBridge بيراجع الـ YAML والأوامر كنص بس — مش بينفّذهم.",
                "response_type": "configuration",
                "competency": "Compose",
                "evaluation_note": "مراجعة نصية ثابتة فقط: SkillBridge بيتأكد من `version: \"3.8\"`، وخدمتين (`db` و`api`)، و`image` و`environment` و`volumes` و`ports` و`depends_on`، وإعلان `volumes:` على المستوى الأعلى، و`docker compose up -d` و`docker compose logs` و`docker compose down --volumes`، كلهم بصيغة `docker compose` الحديثة. مش بيشغّل Docker، فالمراجعة ما بتثبتش نتيجة تشغيل. الإجابة القوية بتحافظ على مسافات الـ YAML متسقة وبتشرح ليه `depends_on` بيتحكم في ترتيب التشغيل بس مش في الجاهزية. الإجابة الضعيفة بتستخدم أمر `docker-compose` القديم، أو بتنسى إعلان الـ volume، أو بتخلط بين بورت الجهاز والحاوية.",
            },
            "mini_check": {"questions": [
                {"id": "c1", "question": "أي أمر بيشغّل Compose stack في الخلفية باستخدام الـ plugin الحديث؟", "options": ["docker compose up -d", "docker-compose up -d", "docker compose start", "docker run compose up"], "misconception_hint": "Docker الحديث بيستخدم CLI plugin بمسافة، مش الـ binary القديم اللي فيه hyphen."},
                {"id": "c2", "question": "في docker-compose.yml، إيه اللي بيعمله `depends_on`؟", "options": ["بيتحكم في ترتيب تشغيل الخدمات بس", "بيستنى لحد ما الخدمة تبقى healthy قبل التشغيل", "بينشئ shared volume", "بينشر البورتات"], "misconception_hint": "مش بيضمن إن الـ dependency جاهز يستقبل ترافيك."},
                {"id": "c3", "question": "إزاي الحاويات في مشروع Compose بتوصل بعضها بالاسم؟", "options": ["Compose بيعمل user-defined network مع DNS", "بيتشاركوا شبكة الـ host", "لازم يستخدموا published host ports", "بيتخدموا default bridge مع IP addresses"], "misconception_hint": "Compose بيوفر تلقائيًا نفس ميزة name resolution اللي في user-defined bridge network."},
            ]},
        },
    },
}


DOCKER_MULTI_STAGE_BUILDS = {
    "status": "complete",
    "skill_aliases": ("docker", "docker & containers"),
    "competency": "Multi-stage builds",
    "objective": "Use multi-stage builds to keep build tools out of the final image and produce smaller, more secure production images.",
    "objectives": [
        "Explain why shipping build tools in a production image is wasteful and risky.",
        "Use multiple `FROM` instructions to create build and runtime stages.",
        "Copy artifacts between stages with `COPY --from=STAGE`.",
        "Choose a small runtime base image such as `alpine` or `distroless`.",
        "Identify the final stage as the only image that is kept.",
    ],
    "prerequisites": [],
    "roadmap_rationale": (
        "Multi-stage builds is an advanced Dockerfile technique. It belongs after Dockerfile because it "
        "builds on the same instructions, and after Images because the learner already understands layers "
        "and image size."
    ),
    "learn": {
        "title": "Multi-stage builds",
        "explanation": (
            "A Dockerfile can have more than one `FROM` instruction. Each `FROM` begins a new **stage**. "
            "You use a large build stage to compile code or install dependencies, then `COPY --from=BUILD_STAGE` "
            "only the compiled artifact into a small runtime stage. The final image contains only what is "
            "needed at runtime, so it is smaller, faster to deploy, and has fewer security risks."
        ),
        "key_ideas": [
            "Each `FROM` in a Dockerfile starts a new stage; only the last stage becomes the final image.",
            "The build stage can contain compilers, dev tools, and source code that the runtime does not need.",
            "`COPY --from=builder /src/app /app/app` copies a file from the `builder` stage into the current stage.",
            "A small runtime base image such as `alpine`, `debian:slim`, or `distroless` keeps the attack surface low.",
            "Multi-stage builds reduce image size and avoid shipping secrets that were only needed during build.",
        ],
        "key_terms": {
            "stage": "A named or numbered build phase in a Dockerfile, started by a FROM instruction.",
            "builder stage": "The stage that compiles or packages the application.",
            "runtime stage": "The final stage that becomes the published image.",
            "COPY --from": "An instruction that copies files from a previous stage into the current stage.",
            "artifact": "A compiled binary, bundle, or other file produced by the build stage.",
        },
        "job_relevance": (
            "Production images should be small and contain only runtime dependencies. Multi-stage builds are "
            "the standard way to achieve that in Docker, and interviewers often ask why an image should not "
            "ship with compilers or source code."
        ),
        "real_world_example": (
            "A Go application needs a Go compiler to build, but the compiled binary runs on its own. A multi-stage "
            "Dockerfile builds the binary in a `golang:1.22` stage, then copies the single binary into an `alpine` "
            "stage. The final image is a few megabytes instead of hundreds, and it does not contain the Go toolchain."
        ),
        "common_mistake": (
            "Do not leave build-only tools such as compilers or dev dependencies in the final stage. Move those "
            "steps to a separate stage and copy only the runtime artifact."
        ),
        "worked_example": (
            "The example builds a small Go binary in one stage and copies only that binary into a minimal runtime image."
        ),
        "depth_note": "Canonical advanced content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": (
            "Examples use Dockerfile syntax compatible with Docker Engine 23+ and BuildKit. SkillBridge does not "
            "execute Docker commands."
        ),
        "grounding_sources": [
            {"title": "Multi-stage builds", "url": "https://docs.docker.com/build/building/multi-stage/", "source": "Docker documentation"},
            {"title": "Docker build overview", "url": "https://docs.docker.com/build/", "source": "Docker documentation"},
        ],
    },
    "example": {
        "title": "Build a Go binary in one stage and run it in a small image",
        "type": "bash",
        "content": (
            "# Dockerfile\n"
            "# Stage 1: build\n"
            "FROM golang:1.22 AS builder\n"
            "WORKDIR /src\n"
            "COPY . .\n"
            "RUN go build -o app .\n"
            "\n"
            "# Stage 2: runtime\n"
            "FROM alpine:3.19\n"
            "WORKDIR /app\n"
            "COPY --from=builder /src/app .\n"
            "CMD [\"./app\"]\n"
            "\n"
            "# Build and run\n"
            "docker build -t myapp:1.0 .\n"
            "docker run --rm myapp:1.0"
        ),
        "explanation": (
            "Only the compiled binary moves from the builder stage to the runtime stage. The Go compiler and "
            "source code stay behind, so the final image is much smaller. Worked example for reading — SkillBridge "
            "does not run these commands."
        ),
    },
    "practice": {
        "type": "practical",
        "title": "Shrink a Node.js image with a multi-stage build",
        "task": (
            "Your current Dockerfile installs `node_modules` and copies all source into the final image. Rewrite it "
            "as a multi-stage build. Requirements: (1) Stage 1 uses `node:20` to install dependencies and build the "
            "production bundle, (2) Stage 2 uses a smaller runtime image and copies only the built artifacts and "
            "the files needed to run, (3) the final container runs as a non-root user, (4) write the `docker build` "
            "and `docker run` commands. SkillBridge reviews your Dockerfile and commands as text only — it never "
            "executes them."
        ),
        "response_type": "configuration",
        "competency": "Multi-stage builds",
        "evaluation_note": (
            "Static text review only: SkillBridge checks for two `FROM` stages, `COPY --from` to move artifacts, "
            "a smaller runtime base image, a non-root `USER`, `docker build -t myapp:1.0 .`, and a `docker run` "
            "command. It does not run Docker, so the review cannot prove runtime results. A strong answer keeps "
            "build tools in the first stage only and explains why the final image is smaller. A weak answer copies "
            "`node_modules` from the build stage without pruning or omits the non-root user."
        ),
    },
    "mini_check": {
        "questions": [
            {"id": "m1", "type": "mcq", "question": "What is the main purpose of a multi-stage build?", "options": ["Keep build tools out of the final image", "Make the build run on multiple machines", "Increase the number of layers", "Allow containers to share networks"], "correct_answer": "Keep build tools out of the final image", "competency": "Multi-stage builds", "difficulty": "beginner", "misconception_hint": "Think about what stays in the published image versus what is only needed during build."},
            {"id": "m2", "type": "mcq", "question": "Which instruction copies a file from a previous build stage?", "options": ["COPY --from=builder", "COPY --stage=builder", "FROM --copy", "RUN --from=builder"], "correct_answer": "COPY --from=builder", "competency": "Multi-stage builds", "difficulty": "beginner", "misconception_hint": "The instruction is a normal COPY with an extra flag naming the source stage."},
            {"id": "m3", "type": "mcq", "question": "Which stage becomes the final Docker image?", "options": ["The last FROM stage", "The first FROM stage", "All stages combined", "The smallest stage automatically"], "correct_answer": "The last FROM stage", "competency": "Multi-stage builds", "difficulty": "beginner", "misconception_hint": "Docker keeps only one stage as the output image."},
        ]
    },
    "locales": {
        "ar": {
            "learn": {
                "title": "الـ Multi-stage Builds",
                "explanation": "الـ Dockerfile ممكن يكون فيه أكتر من تعليمة `FROM`. كل `FROM` بتبدأ **stage** جديد. بتستخدم stage كبير للـ build عشان تCompile الكود أو تنزّل الاعتماديات، وبعدين `COPY --from=BUILD_STAGE` بس للـ artifact المبني لمرحلة runtime صغيرة. الصورة النهائية بتحتوي بس على اللي محتاجه وقت التشغيل، فبتبقى أصغر وأسرع في النشر وأقل مخاطر أمنية.",
                "key_ideas": [
                    "كل `FROM` في Dockerfile بيبدأ stage جديد؛ بس آخر stage بيكون الصورة النهائية.",
                    "مرحلة الـ build ممكن تحتوي على compilers وأدوات تطوير وsource code مش محتاجينها في الـ runtime.",
                    "`COPY --from=builder /src/app /app/app` بينسخ ملف من stage `builder` للمرحلة الحالية.",
                    "صورة runtime صغيرة زي `alpine` أو `debian:slim` أو `distroless` بتقلل مساحة الهجوم.",
                    "الـ Multi-stage builds بتقلل حجم الصورة وبتتجنب شحن secrets كانت محتاجة بس وقت الـ build.",
                ],
                "key_terms": {"stage": "مرحلة build مسمّاة أو مرقّمة في Dockerfile، بتبدأ بتعليمة FROM.", "builder stage": "المرحلة اللي بتcompile أو بتpackage التطبيق.", "runtime stage": "المرحلة النهائية اللي بتبقى الصورة المنشورة.", "COPY --from": "تعليمة بتنسخ ملفات من stage سابق للمرحلة الحالية.", "artifact": "الـ binary المcompiled أو bundle أو ملف تاني انتجته مرحلة الـ build."},
                "job_relevance": "الصور الإنتاجية لازم تكون صغيرة وتحتوي بس على اعتماديات التشغيل. الـ Multi-stage builds هي الطريقة القياسية لتحقيق ده في Docker، والمقابلات بتسأل ليه الصورة مش لازم تشحن compilers أو source code.",
                "real_world_example": "تطبيق Go محتاج Go compiler عشان يتبنى، بس الـ binary المcompiled بيشتغل لوحده. Dockerfile multi-stage بيبني الـ binary في stage `golang:1.22`، وبعدين بينسخه لـ stage `alpine`. الصورة النهائية بقىت بضعة megabytes بدل مئات، ومش بتحتوي على Go toolchain.",
                "common_mistake": "ما تسيبش أدوات build زي compilers أو dev dependencies في المرحلة النهائية. حوّل الخطوات دي لـ stage منفصل وانسخ بس الـ artifact اللي محتاجه وقت التشغيل.",
                "worked_example": "المثال بيبني binary صغير بـ Go في مرحلة واحدة وبينسخه بس لصورة runtime صغيرة.",
                "depth_note": "محتوى متقدم ثابت من قاعدة المعرفة المراجَعة، مش محتوى مولّد حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صيغة Dockerfile متوافقة مع Docker Engine 23+ وBuildKit. SkillBridge ما بينفّذش أوامر Docker.",
                "grounding_sources": [
                    {"title": "الـ Multi-stage builds", "url": "https://docs.docker.com/build/building/multi-stage/", "source": "Docker documentation"},
                    {"title": "نظرة عامة على Docker build", "url": "https://docs.docker.com/build/", "source": "Docker documentation"},
                ],
            },
            "example": {
                "title": "ابنِ binary بـ Go في مرحلة وشغّله في صورة صغيرة",
                "type": "bash",
                "content": "# Dockerfile\n# Stage 1: build\nFROM golang:1.22 AS builder\nWORKDIR /src\nCOPY . .\nRUN go build -o app .\n\n# Stage 2: runtime\nFROM alpine:3.19\nWORKDIR /app\nCOPY --from=builder /src/app .\nCMD [\"./app\"]\n\n# Build and run\ndocker build -t myapp:1.0 .\ndocker run --rm myapp:1.0",
                "explanation": "بس الـ binary المcompiled بيتحوّل من مرحلة الـ builder لمرحلة الـ runtime. Go compiler وsource code بيفضلوا ورا، فالصورة النهائية أصغر بكتير. مثال للقراية — SkillBridge ما بينفّذش الأوامر دي.",
            },
            "practice": {
                "title": "صغّر صورة Node.js بـ multi-stage build",
                "task": "الـ Dockerfile الحالي عندك بينزّل `node_modules` وينسخ كل الـ source للصورة النهائية. اكتبه من جديد كـ multi-stage build. المتطلبات: (١) المرحلة الأولى تستخدم `node:20` لتنزيل الاعتماديات وتبني الـ production bundle، (٢) المرحلة التانية تستخدم صورة runtime أصغر وتنسخ بس الـ artifacts المبنية والملفات اللي محتاجة للتشغيل، (٣) الحاوية النهائية تشتغل بـ non-root user، (٤) اكتب أوامر `docker build` و`docker run`. SkillBridge بيراجع الـ Dockerfile والأوامر كنص بس — مش بينفّذهم.",
                "response_type": "configuration",
                "competency": "Multi-stage builds",
                "evaluation_note": "مراجعة نصية ثابتة فقط: SkillBridge بيتأكد من وجود مرحلتين `FROM`، و`COPY --from` لنقل الـ artifacts، وصورة runtime أصغر، و`USER` غير root، و`docker build -t myapp:1.0 .`، وأمر `docker run`. مش بيشغّل Docker، فالمراجعة ما بتثبتش نتيجة تشغيل. الإجابة القوية بتسبب أدوات الـ build في المرحلة الأولى بس وبتشرح ليه الصورة النهائية أصغر. الإجابة الضعيفة بتنسخ `node_modules` من مرحلة الـ build من غير ما تنضّفها أو تنسى الـ non-root user.",
            },
            "mini_check": {"questions": [
                {"id": "m1", "question": "إيه الغرض الرئيسي من multi-stage build؟", "options": ["إبقاء أدوات البناء برّا الصورة النهائية", "تشغيل الـ build على أكتر من جهاز", "زيادة عدد الطبقات", "خلّي الحاويات تشارك شبكات"], "misconception_hint": "فكّر إيه بيفضل في الصورة المنشورة مقارنة بإيه محتاجه بس وقت الـ build."},
                {"id": "m2", "question": "أي تعليمة بتنسخ ملف من مرحلة build سابقة؟", "options": ["COPY --from=builder", "COPY --stage=builder", "FROM --copy", "RUN --from=builder"], "misconception_hint": "التعليمة هي COPY عادية مع فلاغ إضافي بيسمّي الـ source stage."},
                {"id": "m3", "question": "أي مرحلة بتبقى الصورة النهائية بتاعة Docker؟", "options": ["آخر مرحلة FROM", "أول مرحلة FROM", "كل المراحل مجمعة", "أصغر مرحلة تلقائيًا"], "misconception_hint": "Docker بيحتفظ بمرحلة واحدة بس كصورة ناتجة."},
            ]},
        },
    },
}


DOCKER_SECURITY_SECRETS = {
    "status": "complete",
    "skill_aliases": ("docker", "docker & containers"),
    "competency": "Security & secrets",
    "objective": "Apply basic container security practices: run as non-root, avoid hardcoded secrets, and use Docker secrets appropriately.",
    "objectives": [
        "Explain why running containers as root increases risk.",
        "Use `USER` in a Dockerfile to drop privileges.",
        "Avoid baking credentials, tokens, or `.env` files into images.",
        "Distinguish between plain environment variables and Docker secrets.",
        "Choose minimal base images and keep images up to date.",
    ],
    "prerequisites": [],
    "roadmap_rationale": (
        "Security & secrets follows Dockerfile and Images because most security decisions are made when "
        "choosing a base image and writing the Dockerfile. It is the last advanced topic before orchestration."
    ),
    "learn": {
        "title": "Security & secrets",
        "explanation": (
            "A container is only as secure as its image and runtime settings. The two most common beginner "
            "mistakes are running everything as root and baking secrets into the image. A safer Dockerfile uses "
            "a minimal base image, creates an unprivileged user with `USER`, keeps credentials out of layers, "
            "and passes sensitive values at runtime through environment variables or Docker secrets."
        ),
        "key_ideas": [
            "By default many containers run as root; an attacker who escapes the container gains root on the host.",
            "`RUN useradd -m appuser` and `USER appuser` reduce the damage if the container is compromised.",
            "Never `COPY .env` or hardcode passwords into a Dockerfile; they become part of the image history.",
            "Environment variables are convenient but visible in `docker inspect`; Docker secrets (Swarm/Kubernetes) are better for clustered environments.",
            "Smaller, updated base images have fewer known vulnerabilities and a smaller attack surface.",
        ],
        "key_terms": {
            "rootless": "Running a container process as a non-root user.",
            "USER": "A Dockerfile instruction that sets the user for the rest of the build and for runtime.",
            "secret": "Sensitive data such as a password, API key, or certificate that must not be stored in an image.",
            "Docker secret": "A Swarm feature that mounts secrets into containers without storing them in environment variables.",
            "attack surface": "The number of ways an attacker could exploit a system; smaller images have a smaller surface.",
        },
        "job_relevance": (
            "Security audits, supply-chain reviews, and production deployments all expect containers to run as "
            "non-root and to keep secrets out of images. These practices are baseline expectations for backend "
            "and DevOps roles."
        ),
        "real_world_example": (
            "A team discovers their API image contains a `.env` file with a production database password. They "
            "rebuild the Dockerfile: remove the `.env` COPY, add an unprivileged user, pass `DATABASE_URL` at "
            "runtime, and switch from `node:20` to `node:20-alpine`. The image is smaller and no longer leaks credentials."
        ),
        "common_mistake": (
            "Do not put real passwords, API keys, or `.env` files in a Dockerfile or image layers. Even if you "
            "delete them in a later instruction, the earlier layer still contains them."
        ),
        "worked_example": (
            "The example shows a Dockerfile that creates a non-root user, avoids copying secrets, and uses a "
            "minimal base image."
        ),
        "depth_note": "Canonical advanced content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": (
            "Examples use Dockerfile syntax compatible with Docker Engine 23+ and BuildKit. SkillBridge does not "
            "execute Docker commands. No real credentials are used in any example."
        ),
        "grounding_sources": [
            {"title": "Dockerfile best practices", "url": "https://docs.docker.com/build/building/best-practices/", "source": "Docker documentation"},
            {"title": "Docker secrets", "url": "https://docs.docker.com/engine/swarm/secrets/", "source": "Docker documentation"},
        ],
    },
    "example": {
        "title": "Run a Node.js container as a non-root user without baked secrets",
        "type": "bash",
        "content": (
            "# Dockerfile\n"
            "FROM node:20-alpine\n"
            "RUN addgroup -S appgroup && adduser -S appuser -G appgroup\n"
            "WORKDIR /app\n"
            "COPY package*.json ./\n"
            "RUN npm install --omit=dev\n"
            "COPY . .\n"
            "USER appuser\n"
            "EXPOSE 3000\n"
            "CMD [\"node\", \"server.js\"]\n"
            "\n"
            "# Run, passing the secret at runtime, not in the image\n"
            "docker run -d --name api -e DATABASE_URL=\"REPLACE_AT_RUNTIME\" -p 3000:3000 myapi:1.0"
        ),
        "explanation": (
            "The image creates an unprivileged user, installs only production dependencies, and never copies a "
            "`.env` file. The real `DATABASE_URL` is provided when the container starts. Worked example for reading — "
            "SkillBridge does not run these commands."
        ),
    },
    "practice": {
        "type": "practical",
        "title": "Secure a Dockerfile that currently leaks a secret",
        "task": (
            "You are reviewing a Dockerfile that contains `COPY .env .` and the `.env` file has "
            "`DATABASE_URL=postgres://user:secret@db:5432/app`. Rewrite the approach to be secure: (1) explain "
            "why copying `.env` into the image is dangerous, (2) show a Dockerfile that creates a non-root user, "
            "does not copy secrets, uses a minimal base image, and (3) show the `docker run` command that passes "
            "the secret via an environment variable at runtime. Do not include real credentials. SkillBridge reviews "
            "your Dockerfile and commands as text only — it never executes them."
        ),
        "response_type": "configuration",
        "competency": "Security & secrets",
        "evaluation_note": (
            "Static text review only: SkillBridge checks for a clear warning about copying `.env`/secrets into "
            "the image, a non-root `USER` instruction, a minimal base image (e.g. alpine/slim), no secret literals "
            "in the Dockerfile, and a `docker run` command that passes the secret at runtime with `-e`. It does not "
            "run Docker, so the review cannot prove runtime results. A strong answer explains that image layers keep "
            "the secret forever. A weak answer leaves the secret in the Dockerfile or ignores the non-root user."
        ),
    },
    "mini_check": {
        "questions": [
            {"id": "s1", "type": "mcq", "question": "Why is `COPY .env .` in a Dockerfile dangerous?", "options": ["The secret becomes part of the image history", "It makes the container run slower", "It prevents the container from starting", "It disables networking"], "correct_answer": "The secret becomes part of the image history", "competency": "Security & secrets", "difficulty": "beginner", "misconception_hint": "Image layers are immutable; anything copied in stays visible in the image."},
            {"id": "s2", "type": "mcq", "question": "Which Dockerfile instruction sets the user the container runs as?", "options": ["USER", "RUNAS", "WHOAMI", "GROUP"], "correct_answer": "USER", "competency": "Security & secrets", "difficulty": "beginner", "misconception_hint": "This instruction drops privileges for the remaining build steps and for runtime."},
            {"id": "s3", "type": "mcq", "question": "Where should a production database password be provided?", "options": ["At runtime via an environment variable or secret manager", "Hardcoded in the Dockerfile", "Baked into the image as a config file", "Written in the source code"], "correct_answer": "At runtime via an environment variable or secret manager", "competency": "Security & secrets", "difficulty": "beginner", "misconception_hint": "Secrets belong outside the image so they can be rotated and are not stored in layers."},
        ]
    },
    "locales": {
        "ar": {
            "learn": {
                "title": "الأمان والـ Secrets",
                "explanation": "الحاوية أمنها بيعتمد على صورتها وإعدادات تشغيلها. أشهر غلطتين للمبتدئين هي تشغيل كل حاجة كـ root وخبز الـ secrets جوه الصورة. Dockerfile أكثر أمانًا بيستخدم صورة أساسية صغيرة، وبينشئ user غير privileged بـ `USER`، وبيبعد الاعتمادات عن الطبقات، وبمرّر القيم الحساسة وقت التشغيل عن طريق environment variables أو Docker secrets.",
                "key_ideas": [
                    "افتراضيًا كتير من الحاويات بتشتغل كـ root؛ لو مهاجم خرج من الحاوية يبقى root على الـ host.",
                    "`RUN useradd -m appuser` و`USER appuser` بيقللوا الضرر لو الحاوية ات compromized.",
                    "ما تعملش `COPY .env` أو تثبت كلمات سر في Dockerfile؛ هما بيبقوا جزء من تاريخ الصورة.",
                    "الـ Environment variables سهلة بس ظاهرة في `docker inspect`؛ Docker secrets (Swarm/Kubernetes) أحسن للـ clustered environments.",
                    "الصور الأساسية الصغيرة والمحدّثة عندها ثغرات معروفة أقل ومساحة هجوم أصغر.",
                ],
                "key_terms": {"rootless": "تشغيل عملية الحاوية كـ user غير root.", "USER": "تعليمة في Dockerfile بتحدد الـ user لباقي الـ build ولوقت التشغيل.", "secret": "بيانات حساسة زي باسورد أو API key أو certificate لازم ما تتخزّنش في الصورة.", "Docker secret": "ميزة في Swarm بتركّب secrets في الحاويات من غير ما تخزّنهم في environment variables.", "attack surface": "عدد الطرق اللي ممكن للمهاجم يستغلها؛ الصور الأصغر عندها مساحة هجوم أصغر."},
                "job_relevance": "التدقيقات الأمنية ومراجعات الـ supply-chain والنشرات الإنتاجية كلها بتتوقع إن الحاويات تشتغل غير root وإن الـ secrets تبقى برّا الصور. الممارسات دي توقعات أساسية لمهام backend وDevOps.",
                "real_world_example": "فريق اكتشف إن صورة الـ API تحتوي على ملف `.env` فيه باسورد قاعدة البيانات الإنتاجية. أعادوا بناء الـ Dockerfile: شالوا COPY بتاع `.env`، ضافوا unprivileged user، مرّروا `DATABASE_URL` وقت التشغيل، وغيّروا من `node:20` لـ `node:20-alpine`. الصورة بقت أصغر ولم تعد تسرب بيانات الاعتماد.",
                "common_mistake": "ما تحطش باسوردات حقيقية أو API keys أو ملفات `.env` في Dockerfile أو طبقات الصورة. حتى لو حذفتهم في خطوة لاحقة، الطبقة الأولى لسه بتحتوي عليهم.",
                "worked_example": "المثال بيوضّح Dockerfile بيعمل user غير root، ويتجنب نسخ secrets، ويستخدم صورة أساسية صغيرة.",
                "depth_note": "محتوى متقدم ثابت من قاعدة المعرفة المراجَعة، مش محتوى مولّد حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم صيغة Dockerfile متوافقة مع Docker Engine 23+ وBuildKit. SkillBridge ما بينفّذش أوامر Docker. مفيش بيانات اعتماد حقيقية مستخدمة في أي مثال.",
                "grounding_sources": [
                    {"title": "أفضل ممارسات Dockerfile", "url": "https://docs.docker.com/build/building/best-practices/", "source": "Docker documentation"},
                    {"title": "Docker secrets", "url": "https://docs.docker.com/engine/swarm/secrets/", "source": "Docker documentation"},
                ],
            },
            "example": {
                "title": "شغّل حاوية Node.js كـ non-root user من غير secrets مخبوزة",
                "type": "bash",
                "content": "# Dockerfile\nFROM node:20-alpine\nRUN addgroup -S appgroup && adduser -S appuser -G appgroup\nWORKDIR /app\nCOPY package*.json ./\nRUN npm install --omit=dev\nCOPY . .\nUSER appuser\nEXPOSE 3000\nCMD [\"node\", \"server.js\"]\n\n# Run, passing the secret at runtime, not in the image\ndocker run -d --name api -e DATABASE_URL=\"REPLACE_AT_RUNTIME\" -p 3000:3000 myapi:1.0",
                "explanation": "الصورة بتعمل user غير privileged، بتنزّل بس production dependencies، ومش بنسخ ملف `.env`. الـ `DATABASE_URL` الحقيقي بيتقدّم لما الحاوية تبدأ. مثال للقراية — SkillBridge ما بينفّذش الأوامر دي.",
            },
            "practice": {
                "title": "أأمن Dockerfile بيسرب secret",
                "task": "بت reviewing Dockerfile فيها `COPY .env .` والملف `.env` فيه `DATABASE_URL=postgres://user:secret@db:5432/app`. اكتب الطريقة الأكثر أمانًا: (١) اشرح ليه نسخ `.env` جوه الصورة خطير، (٢) ورّي Dockerfile بيعمل non-root user، ومينسخش secrets، ويستخدم صورة أساسية صغيرة، و(٣) اكتب أمر `docker run` اللي بيمرّر الـ secret عن طريق environment variable وقت التشغيل. متضمنش بيانات اعتماد حقيقية. SkillBridge بيراجع الـ Dockerfile والأوامر كنص بس — مش بينفّذها.",
                "response_type": "configuration",
                "competency": "Security & secrets",
                "evaluation_note": "مراجعة نصية ثابتة فقط: SkillBridge بيتأكد من تحذير واضح عن نسخ `.env`/secrets للصورة، وتعليمة `USER` غير root، وصورة أساسية صغيرة (مثلًا alpine/slim)، ومفيش secret literals في الـ Dockerfile، وأمر `docker run` بيمرّر الـ secret وقت التشغيل بـ `-e`. مش بيشغّل Docker، فالمراجعة ما بتثبتش نتيجة تشغيل. الإجابة القوية بتشرح إن طبقات الصورة بتحتفظ بالـ secret للأبد. الإجابة الضعيفة بتسيب الـ secret في Dockerfile أو تتجاهل الـ non-root user.",
            },
            "mini_check": {"questions": [
                {"id": "s1", "question": "ليه `COPY .env .` في Dockerfile خطير؟", "options": ["الـ Secret بيبقى جزء من تاريخ الصورة", "بيخلي الحاوية تشتغل أبطأ", "بيمنع الحاوية من البدء", "بيوقف الشبكة"], "misconception_hint": "طبقات الصورة immutable؛ أي حاجة اتنسخت فيها بتفضل ظاهرة في الصورة."},
                {"id": "s2", "question": "أي تعليمة في Dockerfile بتحدد الـ user اللي الحاوية بتشتغل بيه؟", "options": ["USER", "RUNAS", "WHOAMI", "GROUP"], "misconception_hint": "التعليمة دي بتقلّل الصلاحيات لباقي خطوات الـ build ولوقت التشغيل."},
                {"id": "s3", "question": "فين لازم يتقدّم باسورد قاعدة البيانات الإنتاجية؟", "options": ["وقت التشغيل عن طريق environment variable أو secret manager", "مثبت في Dockerfile", "مخبوز في الصورة كـ config file", "مكتوب في source code"], "misconception_hint": "الـ Secrets لازم تكون برّا الصورة عشان تتغيّر وما تتخزّنش في الطبقات."},
            ]},
        },
    },
}


DOCKER_ORCHESTRATION_BASICS = {
    "status": "complete",
    "skill_aliases": ("docker", "docker & containers"),
    "competency": "Orchestration basics",
    "objective": "Understand why container orchestration exists and compare Docker Swarm, Kubernetes, and Docker Compose.",
    "objectives": [
        "Explain why orchestration is needed for production multi-container systems.",
        "Describe scaling, self-healing, load balancing, and rolling updates.",
        "Create a simple Docker Swarm service with `docker service create`.",
        "Recognize Kubernetes as a more powerful, widely used orchestrator.",
        "Distinguish Docker Compose (single-host development) from orchestration (multi-host production).",
    ],
    "prerequisites": [],
    "roadmap_rationale": (
        "Orchestration basics is the final Docker topic. It assumes the learner already understands individual "
        "containers, images, networking, and Compose, and is ready to see how those concepts scale to production."
    ),
    "learn": {
        "title": "Orchestration basics",
        "explanation": (
            "Running one container on one machine is easy. Running tens or hundreds across many machines, keeping "
            "them healthy, balancing traffic, and updating them without downtime requires **orchestration**. "
            "Docker Swarm is Docker's built-in orchestrator; Kubernetes is the industry-standard platform. Both "
            "manage **services** — logical groups of identical containers — rather than individual containers."
        ),
        "key_ideas": [
            "Orchestrators place containers across a cluster, restart failed ones, and scale them up or down.",
            "A service in Swarm or Kubernetes is a desired state: 'run 3 replicas of this container'.",
            "Load balancing spreads traffic across replicas so no single container is overwhelmed.",
            "Self-healing means the orchestrator replaces containers that crash or become unhealthy.",
            "Docker Compose is great for local development on one machine; orchestrators manage production clusters.",
        ],
        "key_terms": {
            "orchestration": "Automated management of container deployment, scaling, networking, and health.",
            "cluster": "A group of machines (nodes) that run containers managed by an orchestrator.",
            "service": "A logical group of identical containers that share a name and scaling policy.",
            "replica": "One running instance of a service.",
            "self-healing": "The ability of an orchestrator to detect and replace failed containers automatically.",
            "rolling update": "Replacing old containers with new ones gradually to avoid downtime.",
        },
        "job_relevance": (
            "Production systems run on orchestrators. Understanding the basics of Swarm and Kubernetes, and the "
            "difference between Compose and orchestration, is essential for backend, DevOps, and platform engineering roles."
        ),
        "real_world_example": (
            "A web service needs three replicas for availability. In Docker Swarm you run `docker service create "
            "--replicas 3 --name web -p 8080:80 myweb:1.0`. Swarm keeps three instances running, routes traffic "
            "between them, and restarts any that fail. In Kubernetes you would write a Deployment and a Service YAML."
        ),
        "common_mistake": (
            "Do not use Docker Compose for production multi-host deployments. Compose is designed for single-host "
            "development and small deployments; orchestrators handle clustering, self-healing, and production scaling."
        ),
        "worked_example": (
            "The example initializes a Swarm, creates a replicated service, inspects it, and scales it from 3 to 5 replicas."
        ),
        "depth_note": "Canonical advanced content; it is fixed by the curated knowledge base, not generated for a target role.",
        "version_note": (
            "Examples use Docker Swarm commands from Docker Engine 23+. Kubernetes examples are conceptual only. "
            "SkillBridge does not execute Docker commands."
        ),
        "grounding_sources": [
            {"title": "Docker Swarm overview", "url": "https://docs.docker.com/engine/swarm/", "source": "Docker documentation"},
            {"title": "Kubernetes overview", "url": "https://kubernetes.io/docs/concepts/overview/", "source": "Kubernetes documentation"},
        ],
    },
    "example": {
        "title": "Create a replicated service in Docker Swarm",
        "type": "bash",
        "content": (
            "# Initialize a single-node swarm for learning\n"
            "docker swarm init\n"
            "\n"
            "# Create a service with 3 replicas\n"
            "docker service create --name web --replicas 3 -p 8080:80 nginx:1.27\n"
            "\n"
            "# List services and their replicas\n"
            "docker service ls\n"
            "docker service ps web\n"
            "\n"
            "# Scale to 5 replicas\n"
            "docker service scale web=5\n"
            "\n"
            "# Remove the service\n"
            "docker service rm web"
        ),
        "explanation": (
            "Swarm maintains the desired number of replicas, routes port 8080 to them, and replaces failed tasks. "
            "This is for learning and small setups; production clusters usually use Kubernetes. Worked example for "
            "reading — SkillBridge does not run these commands."
        ),
    },
    "practice": {
        "type": "practical",
        "title": "Choose between Compose and an orchestrator for production",
        "task": (
            "Your team currently runs a development stack with Docker Compose on one developer laptop. You need to "
            "deploy to production with three replicas, automatic restart on failure, and zero-downtime updates. "
            "Explain in two or three sentences whether Docker Compose or an orchestrator (Swarm or Kubernetes) is "
            "appropriate, and why. Then write the Docker Swarm command to create a service named `api` with 3 replicas, "
            "publishing host port 8080 to container port 3000, from image `myapi:1.0`. SkillBridge reviews your answer "
            "as text only — it never executes commands."
        ),
        "response_type": "command",
        "competency": "Orchestration basics",
        "evaluation_note": (
            "Static text review only: SkillBridge checks for an explanation that Compose is for single-host development "
            "while orchestrators handle clustering, self-healing, and rolling updates, plus the command "
            "`docker service create --name api --replicas 3 -p 8080:3000 myapi:1.0`. It does not run Docker, so the "
            "review cannot prove runtime results. A strong answer names Swarm or Kubernetes and explains replicas, "
            "self-healing, or load balancing. A weak answer recommends Compose for production clustering or omits the "
            "replicas flag."
        ),
    },
    "mini_check": {
        "questions": [
            {"id": "o1", "type": "mcq", "question": "What is the main job of a container orchestrator?", "options": ["Deploy, scale, and keep containers healthy across a cluster", "Build Docker images faster", "Replace Dockerfiles", "Run containers only on one machine"], "correct_answer": "Deploy, scale, and keep containers healthy across a cluster", "competency": "Orchestration basics", "difficulty": "beginner", "misconception_hint": "Orchestrators manage the lifecycle of containers at scale, not the build process."},
            {"id": "o2", "type": "mcq", "question": "Which command creates a Docker Swarm service with 3 replicas?", "options": ["docker service create --name web --replicas 3 ...", "docker compose up --replicas 3", "docker run --replicas 3", "docker swarm create --replicas 3"], "correct_answer": "docker service create --name web --replicas 3 ...", "competency": "Orchestration basics", "difficulty": "beginner", "misconception_hint": "Swarm services are created with docker service, not docker run or docker compose."},
            {"id": "o3", "type": "mcq", "question": "When should you move from Docker Compose to an orchestrator?", "options": ["When you need multi-host clustering, self-healing, and production scaling", "When you want to develop locally", "When you have only one container", "When you want to avoid YAML files"], "correct_answer": "When you need multi-host clustering, self-healing, and production scaling", "competency": "Orchestration basics", "difficulty": "beginner", "misconception_hint": "Compose and orchestrators serve different environments and scales."},
        ]
    },
    "locales": {
        "ar": {
            "learn": {
                "title": "أساسيات الـ Orchestration",
                "explanation": "تشغيل حاوية واحدة على جهاز واحد سهل. لكن تشغيل عشرات أو مئات الحاويات على أجهزة كتير، والحفاظ على صحتها، وتوزيع الترافيك، وتحديثها من غير downtime بيتطلب **orchestration**. Docker Swarm هو الـ orchestrator المدمج في Docker؛ Kubernetes هو المنصة القياسية في الصناعة. الاتنين بيديروا **services** — مجموعات منطقية من حاويات متطابقة — بدل الحاويات الفردية.",
                "key_ideas": [
                    "الـ Orchestrators بيحطوا الحاويات في cluster، يعيدوا تشغيل اللي بيفشلوا، ويعملوا scale up/down.",
                    "الـ Service في Swarm أو Kubernetes هو حالة مطلوبة: 'شغّل 3 replicas من الحاوية دي'.",
                    "الـ Load balancing بيوزّع الترافيك على الـ replicas عشان مفيش حاوية تتضغط لوحدها.",
                    "الـ Self-healing يعني الـ orchestrator بيستبدل الحاويات اللي بتcrash أو تبقى unhealthy.",
                    "Docker Compose رائع للتطوير المحلي على جهاز واحد؛ الـ Orchestrators بيديروا clusters الإنتاج.",
                ],
                "key_terms": {"orchestration": "الإدارة الآلية لنشر الحاويات وscaling وشبكاتها وصحتها.", "cluster": "مجموعة من الأجهزة (nodes) بتشغّل حاويات تحت إدارة orchestrator.", "service": "مجموعة منطقية من حاويات متطابقة بتشارك اسم وسياسة scaling.", "replica": "نسخة شغالة واحدة من service.", "self-healing": "قدرة الـ orchestrator على اكتشاف واستبدال الحاويات الفاشلة تلقائيًا.", "rolling update": "استبدال الحاويات القديمة بالجديدة تدريجيًا لتجنب downtime."},
                "job_relevance": "أنظمة الإنتاج بتشتغل على orchestrators. فهم أساسيات Swarm وKubernetes، والفرق بين Compose والـ orchestration، ضروري لمهام backend وDevOps وplatform engineering.",
                "real_world_example": "خدمة ويب محتاجة 3 replicas للتوفر. في Docker Swarm بتشغّل `docker service create --replicas 3 --name web -p 8080:80 myweb:1.0`. Swarm بيحافظ على 3 instances، يوجّه الترافيك بينهم، ويعيد تشغيل أي حاوية بتفشل. في Kubernetes هتكتب Deployment وService YAML.",
                "common_mistake": "ما تستخدمش Docker Compose للنشر الإنتاجي متعدد الأجهزة. Compose مصمم للتطوير المحلي على جهاز واحد والنشرات الصغيرة؛ الـ orchestrators بتتعامل مع clustering وself-healing وscaling الإنتاج.",
                "worked_example": "المثال بيعمل initialize لـ Swarm، ينشئ service مكرّر، يفحصه، ويعمل له scale من 3 لـ 5 replicas.",
                "depth_note": "محتوى متقدم ثابت من قاعدة المعرفة المراجَعة، مش محتوى مولّد حسب الوظيفة.",
                "version_note": "الأمثلة تستخدم أوامر Docker Swarm من Docker Engine 23+. أمثلة Kubernetes هي مفاهيمية فقط. SkillBridge ما بينفّذش أوامر Docker.",
                "grounding_sources": [
                    {"title": "نظرة عامة على Docker Swarm", "url": "https://docs.docker.com/engine/swarm/", "source": "Docker documentation"},
                    {"title": "نظرة عامة على Kubernetes", "url": "https://kubernetes.io/docs/concepts/overview/", "source": "Kubernetes documentation"},
                ],
            },
            "example": {
                "title": "اعمل service مكرّر في Docker Swarm",
                "type": "bash",
                "content": "# Initialize a single-node swarm for learning\ndocker swarm init\n\n# Create a service with 3 replicas\ndocker service create --name web --replicas 3 -p 8080:80 nginx:1.27\n\n# List services and their replicas\ndocker service ls\ndocker service ps web\n\n# Scale to 5 replicas\ndocker service scale web=5\n\n# Remove the service\ndocker service rm web",
                "explanation": "Swarm بيحافظ على العدد المطلوب من الـ replicas، يوجّه بورت 8080 ليهم، ويستبدل الـ tasks اللي بتفشل. ده للتعلم والإعدادات الصغيرة؛ clusters الإنتاج عادة بيستخدموا Kubernetes. مثال للقراية — SkillBridge ما بينفّذش الأوامر دي.",
            },
            "practice": {
                "title": "اختار بين Compose و orchestrator للإنتاج",
                "task": "فريقك حاليًا بيشغّل stack التطوير بـ Docker Compose على لابتوب مطوّر واحد. محتاج تنشر للإنتاج بـ 3 replicas، restart تلقائي لما يحصل فشل، وتحديثات من غير downtime. اشرح في جملتين أو تلاتة هل Docker Compose ولا orchestrator (Swarm أو Kubernetes) مناسب، وليه. وبعدين اكتب أمر Docker Swarm عشان تعمل service اسمها `api` بـ 3 replicas، تنشر بورت 8080 على الجهاز لبورت 3000، من صورة `myapi:1.0`. SkillBridge بيراجع إجابتك كنص بس — مش بينفّذ الأوامر.",
                "response_type": "command",
                "competency": "Orchestration basics",
                "evaluation_note": "مراجعة نصية ثابتة فقط: SkillBridge بيتأكد من شرح إن Compose للتطوير المحلي على جهاز واحد بينما الـ orchestrators بيديروا clustering وself-healing وrolling updates، بالإضافة للأمر `docker service create --name api --replicas 3 -p 8080:3000 myapi:1.0`. مش بيشغّل Docker، فالمراجعة ما بتثبتش نتيجة تشغيل. الإجابة القوية بتسمّي Swarm أو Kubernetes وتشرح replicas أو self-healing أو load balancing. الإجابة الضعيفة بتنصح بـ Compose للنشر الإنتاجي متعدد الأجهزة أو تنسى فلاغ الـ replicas.",
            },
            "mini_check": {"questions": [
                {"id": "o1", "question": "إيه الوظيفة الرئيسية لـ container orchestrator؟", "options": ["ينشر ويعمل scale ويحافظ على صحة الحاويات في cluster", "يبني صور Docker بسرعة", "يستبدل Dockerfiles", "يشغّل حاويات على جهاز واحد بس"], "misconception_hint": "الـ Orchestrators بيديروا lifecycle الحاويات على نطاق واسع، مش عملية الـ build."},
                {"id": "o2", "question": "أي أمر بيعمل Docker Swarm service بـ 3 replicas؟", "options": ["docker service create --name web --replicas 3 ...", "docker compose up --replicas 3", "docker run --replicas 3", "docker swarm create --replicas 3"], "misconception_hint": "خدمات Swarm بتتعمل بـ docker service، مش docker run أو docker compose."},
                {"id": "o3", "question": "إمتى لازم تنتقل من Docker Compose لـ orchestrator؟", "options": ["لما تحتاج multi-host clustering وself-healing وscaling إنتاجي", "لما عايز تطوّر محليًا", "لما عندك حاوية واحدة بس", "لما عايز تتجنب ملفات YAML"], "misconception_hint": "Compose والـ orchestrators بيخدموا environments وأحجام مختلفة."},
            ]},
        },
    },
}


def curated_diagnostic_questions(skill_name, competencies):
    """Return reviewed diagnostic questions for complete curated topics.

    Questions are authored against one canonical competency each.  This is
    intentionally narrower than the general skill-level bank: callers must
never tag a question about one Python topic as another merely for coverage.
    """
    requested = {_key(item) for item in (competencies or [])}
    skill_key = _key(skill_name)
    banks = {
        "python functions": [
            {"type": "mcq", "question": "In `def add(a, b): return a + b`, what does `return` do?", "options": ["Displays the sum only", "Sends the sum back to the caller", "Defines a parameter", "Stops Python forever"], "correct_answer": "Sends the sum back to the caller", "competency": "python_functions", "difficulty": "beginner"},
            {"type": "mcq", "question": "In `def greet(name):`, `name` is a:", "options": ["parameter", "argument", "module", "exception"], "correct_answer": "parameter", "competency": "python_functions", "difficulty": "beginner"},
            {"type": "mcq", "question": "Which call correctly supplies two arguments to `delivery_total(price, delivery_fee)`?", "options": ["delivery_total(20, 5)", "delivery_total(price)", "def delivery_total(20, 5)", "return delivery_total"], "correct_answer": "delivery_total(20, 5)", "competency": "python_functions", "difficulty": "beginner"},
        ],
        "python error handling": [
            {"type": "mcq", "question": "Which exception can `int(\"eighty\")` raise?", "options": ["ValueError", "KeyError", "ImportError", "No exception"], "correct_answer": "ValueError", "competency": "python_error_handling", "difficulty": "beginner"},
            {"type": "mcq", "question": "Where should `int(text)` go when it may fail because the text is not numeric?", "options": ["Inside `try`", "Only inside `except ValueError`", "After `return None`", "Inside a bare `except`"], "correct_answer": "Inside `try`", "competency": "python_error_handling", "difficulty": "beginner"},
            {"type": "mcq", "question": "Why catch `ValueError` rather than using bare `except:` in `parse_score`?", "options": ["It handles invalid numeric text without hiding unrelated bugs", "It converts every string", "It avoids using return", "It executes faster"], "correct_answer": "It handles invalid numeric text without hiding unrelated bugs", "competency": "python_error_handling", "difficulty": "beginner"},
        ],
        "queries & filtering": [
            {"type": "mcq", "question": "Which clause filters rows to customers in Cairo?", "options": ["WHERE city = 'Cairo'", "SELECT city", "FROM Cairo", "ORDER BY city"], "correct_answer": "WHERE city = 'Cairo'", "competency": "sql_queries_filtering", "difficulty": "beginner"},
            {"type": "mcq", "question": "What does `SELECT name, email` return?", "options": ["The name and email columns", "Every column", "Only rows with email", "A new table"], "correct_answer": "The name and email columns", "competency": "sql_queries_filtering", "difficulty": "beginner"},
            {"type": "mcq", "question": "Which query reads active Cairo customers without changing data?", "options": ["SELECT name, email FROM customers WHERE city = 'Cairo' AND status = 'active';", "DELETE FROM customers WHERE city = 'Cairo';", "UPDATE customers SET status = 'active';", "INSERT INTO customers (city) VALUES ('Cairo');"], "correct_answer": "SELECT name, email FROM customers WHERE city = 'Cairo' AND status = 'active';", "competency": "sql_queries_filtering", "difficulty": "beginner"},
        ],
        "sorting & limiting": [
            {"type": "mcq", "question": "Which clause sorts a result from the highest `total` down?", "options": ["ORDER BY total DESC", "LIMIT 3", "WHERE total > 0", "GROUP BY total"], "correct_answer": "ORDER BY total DESC", "competency": "sql_sorting_limiting", "difficulty": "beginner"},
            {"type": "mcq", "question": "What does `LIMIT 3` do?", "options": ["Keeps only the first three rows", "Sorts three columns", "Filters three cities", "Deletes three rows"], "correct_answer": "Keeps only the first three rows", "competency": "sql_sorting_limiting", "difficulty": "beginner"},
            {"type": "mcq", "question": "Which query previews the three highest totals without changing data?", "options": ["SELECT name, total FROM customers ORDER BY total DESC LIMIT 3;", "UPDATE customers SET total = 0;", "DELETE FROM customers ORDER BY total DESC LIMIT 3;", "SELECT name FROM customers ORDER BY city LIMIT 1;"], "correct_answer": "SELECT name, total FROM customers ORDER BY total DESC LIMIT 3;", "competency": "sql_sorting_limiting", "difficulty": "beginner"},
        ],
        "aggregation": [
            {"type": "mcq", "question": "Which clause creates one group per distinct city?", "options": ["GROUP BY city", "ORDER BY city", "LIMIT city", "HAVING city"], "correct_answer": "GROUP BY city", "competency": "sql_aggregation", "difficulty": "intermediate"},
            {"type": "mcq", "question": "What does `COUNT(*)` return for a group?", "options": ["The number of rows in the group", "The sum of a column", "The highest value", "A random row"], "correct_answer": "The number of rows in the group", "competency": "sql_aggregation", "difficulty": "intermediate"},
            {"type": "mcq", "question": "Which query lists each city with its customer count for cities with at least two customers?", "options": ["SELECT city, COUNT(*) FROM customers GROUP BY city HAVING COUNT(*) >= 2;", "SELECT city FROM customers WHERE COUNT(*) >= 2;", "DELETE FROM customers GROUP BY city;", "SELECT COUNT(*) FROM customers ORDER BY city;"], "correct_answer": "SELECT city, COUNT(*) FROM customers GROUP BY city HAVING COUNT(*) >= 2;", "competency": "sql_aggregation", "difficulty": "intermediate"},
        ],
        "joins": [
            {"type": "mcq", "question": "Which clause tells JOIN which columns to compare?", "options": ["ON customers.id = orders.customer_id", "WHERE orders = customers", "LIMIT orders", "GROUP BY customers"], "correct_answer": "ON customers.id = orders.customer_id", "competency": "sql_joins", "difficulty": "intermediate"},
            {"type": "mcq", "question": "Which JOIN keeps only rows that have a match in both tables?", "options": ["INNER JOIN", "LEFT JOIN", "CROSS JOIN", "FULL OUTER JOIN"], "correct_answer": "INNER JOIN", "competency": "sql_joins", "difficulty": "intermediate"},
            {"type": "mcq", "question": "Which query reads each customer's name alongside their order_date without changing data?", "options": ["SELECT customers.name, orders.order_date FROM customers INNER JOIN orders ON customers.id = orders.customer_id;", "DELETE FROM orders;", "UPDATE customers SET name = 'x';", "SELECT name FROM customers FULL OUTER JOIN orders;"], "correct_answer": "SELECT customers.name, orders.order_date FROM customers INNER JOIN orders ON customers.id = orders.customer_id;", "competency": "sql_joins", "difficulty": "intermediate"},
        ],
        "subqueries": [
            {"type": "mcq", "question": "What is a subquery?", "options": ["A SELECT statement written inside another statement", "A table stored inside a column", "An index on a column", "A command that deletes rows"], "correct_answer": "A SELECT statement written inside another statement", "competency": "sql_subqueries", "difficulty": "intermediate"},
            {"type": "mcq", "question": "What does `WHERE total > (SELECT AVG(total) FROM customers)` compare?", "options": ["Each row's total to the average total", "Every customer to the top total", "Two tables on the customer id", "No values at all"], "correct_answer": "Each row's total to the average total", "competency": "sql_subqueries", "difficulty": "intermediate"},
            {"type": "mcq", "question": "Which query reads customers above the average total without changing data?", "options": ["SELECT name FROM customers WHERE total > (SELECT AVG(total) FROM customers);", "SELECT name FROM customers WHERE total > AVG(total);", "DELETE FROM customers WHERE total > 100;", "SELECT name FROM customers ORDER BY total;"], "correct_answer": "SELECT name FROM customers WHERE total > (SELECT AVG(total) FROM customers);", "competency": "sql_subqueries", "difficulty": "intermediate"},
        ],
        "indexing basics": [
            {"type": "mcq", "question": "What does an index on a column give the database?", "options": ["A separate structure to find rows by that column faster", "Visible column headings", "An editable copy of the table", "A filter that deletes rows"], "correct_answer": "A separate structure to find rows by that column faster", "competency": "sql_indexing_basics", "difficulty": "intermediate"},
            {"type": "mcq", "question": "Which strategy does an index on the `email` column speed up?", "options": ["WHERE email = 'sara@example.com'", "ORDER BY total DESC", "LIMIT 3", "SELECT COUNT(*) FROM customers"], "correct_answer": "WHERE email = 'sara@example.com'", "competency": "sql_indexing_basics", "difficulty": "intermediate"},
            {"type": "mcq", "question": "Which statement is true of an index?", "options": ["It speeds up value lookups without changing the stored rows", "It deletes unused rows", "It permanently reorders the table", "It inserts new rows"], "correct_answer": "It speeds up value lookups without changing the stored rows", "competency": "sql_indexing_basics", "difficulty": "intermediate"},
        ],
        "window functions": [
            {"type": "mcq", "question": "What does `OVER (...)` keep in the result of a query?", "options": ["Every row, while the function is computed over a window", "Only one row per group", "Nothing; it deletes rows", "Only the first row"], "correct_answer": "Every row, while the function is computed over a window", "competency": "sql_window_functions", "difficulty": "advanced"},
            {"type": "mcq", "question": "Which fragment ranks customers by total from largest to smallest?", "options": ["ROW_NUMBER() OVER (ORDER BY total DESC)", "COUNT(*) GROUP BY total", "LIMIT total DESC", "WHERE total DESC"], "correct_answer": "ROW_NUMBER() OVER (ORDER BY total DESC)", "competency": "sql_window_functions", "difficulty": "advanced"},
            {"type": "mcq", "question": "Which query numbers each customer by total without changing data?", "options": ["SELECT name, total, ROW_NUMBER() OVER (ORDER BY total DESC) AS position FROM customers;", "UPDATE customers SET position = 1;", "DELETE FROM customers;", "SELECT name, total FROM customers GROUP BY total;"], "correct_answer": "SELECT name, total, ROW_NUMBER() OVER (ORDER BY total DESC) AS position FROM customers;", "competency": "sql_window_functions", "difficulty": "advanced"},
        ],
        "query optimization": [
            {"type": "mcq", "question": "What does a database optimizer do?", "options": ["Chooses how to execute a query, such as which index or scan to use", "Rewrites the stored tables automatically", "Deletes slow queries", "Adds columns to every table"], "correct_answer": "Chooses how to execute a query, such as which index or scan to use", "competency": "sql_query_optimization", "difficulty": "advanced"},
            {"type": "mcq", "question": "Which statement inspects the steps a database plans for a query?", "options": ["EXPLAIN", "SELECT * FROM users", "DELETE FROM users", "INSERT INTO users (id) VALUES (1)"], "correct_answer": "EXPLAIN", "competency": "sql_query_optimization", "difficulty": "advanced"},
            {"type": "mcq", "question": "Which statement about query performance is accurate?", "options": ["Actual performance can only be measured on a real database, not by reading the query text", "Reading the SQL proves exactly how fast it will run", "A longer query is always faster", "A static review measures execution time"], "correct_answer": "Actual performance can only be measured on a real database, not by reading the query text", "competency": "sql_query_optimization", "difficulty": "advanced"},
        ],
        "transactions": [
            {"type": "mcq", "question": "What does `BEGIN` do in SQL?", "options": ["Starts a transaction: a group of statements treated as one unit", "Deletes the current session's data", "Ends the connection", "Sorts the table permanently"], "correct_answer": "Starts a transaction: a group of statements treated as one unit", "competency": "sql_transactions", "difficulty": "advanced"},
            {"type": "mcq", "question": "Which property means all statements in a transaction take effect together or none do?", "options": ["Atomicity", "Normalization", "Indexing", "Partitioning"], "correct_answer": "Atomicity", "competency": "sql_transactions", "difficulty": "advanced"},
            {"type": "mcq", "question": "What can a static text review of a transaction script NOT prove?", "options": ["That commit, rollback, isolation, or atomicity actually happened at runtime", "That BEGIN and COMMIT appear in the script", "That a SELECT is present", "The order of statements"], "correct_answer": "That commit, rollback, isolation, or atomicity actually happened at runtime", "competency": "sql_transactions", "difficulty": "advanced"},
        ],
        "schema design": [
            {"type": "mcq", "question": "What does a `PRIMARY KEY` do for a table?", "options": ["Uniquely identifies each row in the table", "Sorts every column automatically", "Deletes duplicate rows", "Stores the query history"], "correct_answer": "Uniquely identifies each row in the table", "competency": "sql_schema_design", "difficulty": "advanced"},
            {"type": "mcq", "question": "Which constraint prevents two customers from sharing the same email?", "options": ["UNIQUE on the email column", "NOT NULL on the email column", "A DEFAULT email value", "ORDER BY email"], "correct_answer": "UNIQUE on the email column", "competency": "sql_schema_design", "difficulty": "advanced"},
            {"type": "mcq", "question": "What does a static review of a `CREATE TABLE` statement NOT prove?", "options": ["That the schema was deployed or validated against a running database", "That a PRIMARY KEY is declared", "That NOT NULL appears", "That the customers table is named"], "correct_answer": "That the schema was deployed or validated against a running database", "competency": "sql_schema_design", "difficulty": "advanced"},
        ],
        "local repositories": [
            {"type": "mcq", "question": "What does `git init` do for a folder?", "options": ["Creates a local Git repository and a `.git` directory that holds the project's history", "Uploads the folder to GitHub", "Deletes committed files", "Installs Git on your computer"], "correct_answer": "Creates a local Git repository and a `.git` directory that holds the project's history", "competency": "git_local_repositories", "difficulty": "beginner"},
            {"type": "mcq", "question": "Where does Git store a local repository's history?", "options": ["In a hidden `.git` directory inside the project", "Only on GitHub", "Inside each source file", "In the system's temporary folder"], "correct_answer": "In a hidden `.git` directory inside the project", "competency": "git_local_repositories", "difficulty": "beginner"},
            {"type": "mcq", "question": "What can a static text review of `git init` NOT prove?", "options": ["That the commands actually ran and created a repository on the learner's machine", "That `git init` appears in the answer", "That `git status` is listed", "That the folder is named my-project"], "correct_answer": "That the commands actually ran and created a repository on the learner's machine", "competency": "git_local_repositories", "difficulty": "beginner"},
        ],
        "committing": [
            {"type": "mcq", "question": "Which command stages a file so it is ready to be committed?", "options": ["git add README.md", "git commit -m \"text\"", "git init", "git log"], "correct_answer": "git add README.md", "competency": "git_committing", "difficulty": "beginner"},
            {"type": "mcq", "question": "What does `git commit -m \"Add the README\"` create?", "options": ["A snapshot of the staged files with the message Add the README", "A copy of the folder on GitHub", "A new branch", "A database table"], "correct_answer": "A snapshot of the staged files with the message Add the README", "competency": "git_committing", "difficulty": "beginner"},
            {"type": "mcq", "question": "What does a static review of a commit command NOT prove?", "options": ["That the commit actually happened in a repository", "That `git commit -m` appears in the answer", "That a message is present", "That `git add` is listed"], "correct_answer": "That the commit actually happened in a repository", "competency": "git_committing", "difficulty": "beginner"},
        ],
        "branching": [
            {"type": "mcq", "question": "Which command creates a new local branch named `feature-payment`?", "options": ["git branch feature-payment", "git switch feature-payment", "git commit -m \"feature-payment\"", "git status"], "correct_answer": "git branch feature-payment", "competency": "git_branching", "difficulty": "beginner"},
            {"type": "mcq", "question": "Which command makes `feature-payment` the current branch?", "options": ["git switch feature-payment", "git branch feature-payment", "git status", "git log"], "correct_answer": "git switch feature-payment", "competency": "git_branching", "difficulty": "beginner"},
            {"type": "mcq", "question": "What can a static text review of `git branch` NOT prove?", "options": ["That a branch was actually created on the learner's machine", "That `git branch feature-payment` appears in the answer", "That `git switch` is listed", "That `git status` is listed"], "correct_answer": "That a branch was actually created on the learner's machine", "competency": "git_branching", "difficulty": "beginner"},
        ],
        "merging": [
            {"type": "mcq", "question": "Which command integrates the commits of `feature-payment` into the current branch?", "options": ["git merge feature-payment", "git branch feature-payment", "git switch feature-payment", "git status"], "correct_answer": "git merge feature-payment", "competency": "git_merging", "difficulty": "intermediate"},
            {"type": "mcq", "question": "What do the `<<<<<<<`, `=======`, and `>>>>>>>` markers in a file indicate?", "options": ["A merge conflict that needs a deliberate resolution", "That a fast-forward completed", "That the file was committed", "That the file was deleted"], "correct_answer": "A merge conflict that needs a deliberate resolution", "competency": "git_merging", "difficulty": "intermediate"},
            {"type": "mcq", "question": "What does a static review of a merge command NOT prove?", "options": ["That a real merge ran or changed a repository", "That `git merge feature-payment` appears in the answer", "That `git switch main` is listed", "That `git log` is listed"], "correct_answer": "That a real merge ran or changed a repository", "competency": "git_merging", "difficulty": "intermediate"},
        ],
        "rebasing": [
            {"type": "mcq", "question": "What does `git rebase main` do?", "options": ["Replays the current branch's commits onto the tip of main", "Joins two histories with a merge commit", "Deletes the current branch", "Pushes the branch to the remote"], "correct_answer": "Replays the current branch's commits onto the tip of main", "competency": "git_rebasing", "difficulty": "intermediate"},
            {"type": "mcq", "question": "How does rebase differ from merge?", "options": ["Rebase rewrites the branch's commits for a linear history; merge joins histories with a merge commit", "Rebase only works on remotes; merge only works locally", "Merge rewrites commits; rebase never changes commits", "They are two names for the same operation"], "correct_answer": "Rebase rewrites the branch's commits for a linear history; merge joins histories with a merge commit", "competency": "git_rebasing", "difficulty": "intermediate"},
            {"type": "mcq", "question": "What does a static review of a rebase command NOT prove?", "options": ["That a rebase ran or that any repository's history was rewritten", "That `git rebase main` appears in the answer", "That `git switch` is listed", "That `git log` is listed"], "correct_answer": "That a rebase ran or that any repository's history was rewritten", "competency": "git_rebasing", "difficulty": "intermediate"},
        ],
        "remotes & collaboration": [
            {"type": "mcq", "question": "What does `git fetch origin` do?", "options": ["Downloads new commits from the remote without changing your working tree", "Uploads your commits to the remote", "Merges your branch into main", "Creates a Pull Request"], "correct_answer": "Downloads new commits from the remote without changing your working tree", "competency": "git_remotes_collaboration", "difficulty": "intermediate"},
            {"type": "mcq", "question": "Which command uploads your local `feature-payment` commits to the remote?", "options": ["git push origin feature-payment", "git fetch origin", "git pull", "git rebase main"], "correct_answer": "git push origin feature-payment", "competency": "git_remotes_collaboration", "difficulty": "intermediate"},
            {"type": "mcq", "question": "What does a static review of fetch/pull/push commands NOT prove?", "options": ["That any network operation contacted a remote", "That `git fetch origin` appears in the answer", "That `git pull` is listed", "That `git push` is listed"], "correct_answer": "That any network operation contacted a remote", "competency": "git_remotes_collaboration", "difficulty": "intermediate"},
        ],
        "history rewriting": [
            {"type": "mcq", "question": "What does `git commit --amend` do?", "options": ["Rewrites the most recent commit", "Deletes the most recent commit", "Pushes the most recent commit", "Creates a new branch"], "correct_answer": "Rewrites the most recent commit", "competency": "git_history_rewriting", "difficulty": "intermediate"},
            {"type": "mcq", "question": "Which command opens the branch's commits for reordering, squashing, or rewording?", "options": ["git rebase -i main", "git commit --amend", "git bisect start", "git push origin main"], "correct_answer": "git rebase -i main", "competency": "git_history_rewriting", "difficulty": "intermediate"},
            {"type": "mcq", "question": "What does a static review of history-rewriting commands NOT prove?", "options": ["That any commit was amended or rebased in a real repository", "That `git commit --amend` appears in the answer", "That `git rebase -i main` is listed", "That `git log` is listed"], "correct_answer": "That any commit was amended or rebased in a real repository", "competency": "git_history_rewriting", "difficulty": "intermediate"},
        ],
        "bisect & debugging": [
            {"type": "mcq", "question": "After `git bisect start`, which commands mark the broken and working states?", "options": ["git bisect bad and git bisect good <commit>", "git bisect start and git bisect stop", "git commit and git push", "git merge and git rebase"], "correct_answer": "git bisect bad and git bisect good <commit>", "competency": "git_bisect_debugging", "difficulty": "advanced"},
            {"type": "mcq", "question": "What does a finished bisect report?", "options": ["The first bad commit that introduced the regression", "A list of every commit in the repository", "The author with the most commits", "The files with the most lines"], "correct_answer": "The first bad commit that introduced the regression", "competency": "git_bisect_debugging", "difficulty": "advanced"},
            {"type": "mcq", "question": "What does a static review of bisect commands NOT prove?", "options": ["That a bisect session ran in any repository", "That `git bisect start` appears in the answer", "That `git bisect good` is listed", "That `git bisect reset` is listed"], "correct_answer": "That a bisect session ran in any repository", "competency": "git_bisect_debugging", "difficulty": "advanced"},
        ],
        "submodules": [
            {"type": "mcq", "question": "What is a submodule in Git?", "options": ["A repository embedded inside another repository at a pinned commit", "A copy of a single folder", "A remote branch", "An uncommitted change"], "correct_answer": "A repository embedded inside another repository at a pinned commit", "competency": "git_submodules", "difficulty": "advanced"},
            {"type": "mcq", "question": "Which command clones a project AND its submodules in one step?", "options": ["git clone --recurse-submodules <url>", "git clone --depth 1 <url>", "git submodule deinit --all", "git reset --hard"], "correct_answer": "git clone --recurse-submodules <url>", "competency": "git_submodules", "difficulty": "advanced"},
            {"type": "mcq", "question": "What does a static review of submodule commands NOT prove?", "options": ["That a submodule was cloned, initialized, updated, or modified in any repository", "That `git submodule init` appears in the answer", "That `git submodule update` is listed", "That `git clone` is listed"], "correct_answer": "That a submodule was cloned, initialized, updated, or modified in any repository", "competency": "git_submodules", "difficulty": "advanced"},
        ],
        "workflows & policy": [
            {"type": "mcq", "question": "Which command creates a feature branch and switches onto it?", "options": ["git switch -c feature-login", "git checkout main", "git push origin main", "git log --oneline"], "correct_answer": "git switch -c feature-login", "competency": "git_workflows_&_policy", "difficulty": "advanced"},
            {"type": "mcq", "question": "What is a Pull Request?", "options": ["A review step on the hosting service that proposes merging a branch", "A native Git command that merges branches locally", "A backup of the repository", "A command that rewrites history"], "correct_answer": "A review step on the hosting service that proposes merging a branch", "competency": "git_workflows_&_policy", "difficulty": "advanced"},
            {"type": "mcq", "question": "What does a static review of workflow commands NOT prove?", "options": ["That a branch was pushed or any repository policy was configured", "That `git switch -c` appears in the answer", "That `git push` is listed", "That `git merge` is listed"], "correct_answer": "That a branch was pushed or any repository policy was configured", "competency": "git_workflows_&_policy", "difficulty": "advanced"},
        ],
        "large-repo strategies": [
            {"type": "mcq", "question": "What does a shallow clone (`git clone --depth 1`) do?", "options": ["Copies only the latest commit history instead of the full history", "Copies every commit in full", "Deletes files over a size limit", "Converts the repository to a single file"], "correct_answer": "Copies only the latest commit history instead of the full history", "competency": "git_large-repo_strategies", "difficulty": "advanced"},
            {"type": "mcq", "question": "Which tool keeps very large binary files out of the repository?", "options": ["Git LFS (git lfs track)", "git commit --amend", "git rebase -i main", "git bisect reset"], "correct_answer": "Git LFS (git lfs track)", "competency": "git_large-repo_strategies", "difficulty": "advanced"},
            {"type": "mcq", "question": "What does a static review of large-repository commands NOT prove?", "options": ["That any clone, sparse checkout, LFS setup, or performance improvement occurred", "That `git clone --depth 1` appears in the answer", "That `git sparse-checkout set` is listed", "That `git lfs install` is listed"], "correct_answer": "That any clone, sparse checkout, LFS setup, or performance improvement occurred", "competency": "git_large-repo_strategies", "difficulty": "advanced"},
        ],
        # Docker Batch 1 — curated diagnostic banks for the topics that are complete.
        # These SUPPLEMENT the AI fallback; uncovered Docker competencies still get
        # AI-generated (or deterministic fallback) questions so all 11 blueprint
        # topics are represented.
        "containers": [
            {"type": "mcq", "question": "Which command lists containers that have already stopped?", "options": ["docker ps", "docker ps -a", "docker logs", "docker images"], "correct_answer": "docker ps -a", "competency": "containers", "difficulty": "beginner"},
            {"type": "mcq", "question": "What is true right after `docker stop web` finishes?", "options": ["It is deleted from disk immediately", "It still exists and can be started again with `docker start web`", "Its image is removed too", "It restarts automatically"], "correct_answer": "It still exists and can be started again with `docker start web`", "competency": "containers", "difficulty": "beginner"},
            {"type": "mcq", "question": "In `docker run -d --name web -p 8080:80 nginx:1.27`, what does `-d` do?", "options": ["Runs the container in the background (detached)", "Deletes the container when it exits", "Publishes port 8080", "Pins the image by digest"], "correct_answer": "Runs the container in the background (detached)", "competency": "containers", "difficulty": "beginner"},
        ],
        "images": [
            {"type": "mcq", "question": "What does `docker pull nginx` (no tag) actually download?", "options": ["The `nginx:latest` tag — whichever version it points to today", "Every tag in the repository", "Only the smallest layer", "A digest-pinned snapshot"], "correct_answer": "The `nginx:latest` tag — whichever version it points to today", "competency": "images", "difficulty": "beginner"},
            {"type": "mcq", "question": "Why can `docker rmi nginx:1.27` fail even when the command is typed correctly?", "options": ["A container — even a stopped one — still uses that image", "Images can never be removed", "`rmi` only works on dangling images", "Docker must be stopped first"], "correct_answer": "A container — even a stopped one — still uses that image", "competency": "images", "difficulty": "beginner"},
            {"type": "mcq", "question": "Two images stored locally share most of their layers. What does that mean for disk space?", "options": ["The shared layers are stored once, not duplicated per image", "Each image keeps a full private copy", "The layers are compressed twice", "Docker deletes the older image automatically"], "correct_answer": "The shared layers are stored once, not duplicated per image", "competency": "images", "difficulty": "beginner"},
        ],
        # Docker Batch 2 — one reviewed diagnostic question per newly complete topic.
        # Containers and Images keep their 3-question banks above.
        "basic commands": [
            {"type": "mcq", "question": "Which flag removes a container automatically after it exits?", "options": ["--rm", "-d", "-p", "--name"], "correct_answer": "--rm", "competency": "basic_commands", "difficulty": "beginner"},
        ],
        "dockerfile": [
            {"type": "mcq", "question": "Which Dockerfile instruction sets the base image?", "options": ["FROM", "COPY", "RUN", "CMD"], "correct_answer": "FROM", "competency": "dockerfile", "difficulty": "beginner"},
        ],
        "ports": [
            {"type": "mcq", "question": "Which `docker run` flag publishes a container port to the host?", "options": ["-p", "-d", "--name", "--rm"], "correct_answer": "-p", "competency": "ports", "difficulty": "beginner"},
        ],
        # Docker Batch 3 — one reviewed diagnostic question per newly complete topic.
        "volumes": [
            {"type": "mcq", "question": "What happens to data written in a container's writable layer when the container is removed?", "options": ["It is deleted", "It is copied into the image", "It moves to a volume automatically", "It stays forever"], "correct_answer": "It is deleted", "competency": "volumes", "difficulty": "beginner"},
        ],
        "networking": [
            {"type": "mcq", "question": "What is the main advantage of a user-defined bridge network over the default bridge?", "options": ["Containers can resolve each other by name (DNS)", "It makes containers run faster", "It removes the need for port publishing", "It gives containers direct host network access"], "correct_answer": "Containers can resolve each other by name (DNS)", "competency": "networking", "difficulty": "beginner"},
        ],
        "compose": [
            {"type": "mcq", "question": "Which command starts a Compose stack in the background using the modern plugin syntax?", "options": ["docker compose up -d", "docker-compose up -d", "docker compose start", "docker run compose up"], "correct_answer": "docker compose up -d", "competency": "compose", "difficulty": "beginner"},
        ],
        # Docker Batch 4 — one reviewed diagnostic question per newly complete topic.
        "multi-stage builds": [
            {"type": "mcq", "question": "What is the main purpose of a multi-stage build?", "options": ["Keep build tools out of the final image", "Make the build run on multiple machines", "Increase the number of layers", "Allow containers to share networks"], "correct_answer": "Keep build tools out of the final image", "competency": "multi-stage_builds", "difficulty": "beginner"},
        ],
        "security & secrets": [
            {"type": "mcq", "question": "Why is `COPY .env .` in a Dockerfile dangerous?", "options": ["The secret becomes part of the image history", "It makes the container run slower", "It prevents the container from starting", "It disables networking"], "correct_answer": "The secret becomes part of the image history", "competency": "security_&_secrets", "difficulty": "beginner"},
        ],
        "orchestration basics": [
            {"type": "mcq", "question": "What is the main job of a container orchestrator?", "options": ["Deploy, scale, and keep containers healthy across a cluster", "Build Docker images faster", "Replace Dockerfiles", "Run containers only on one machine"], "correct_answer": "Deploy, scale, and keep containers healthy across a cluster", "competency": "orchestration_basics", "difficulty": "beginner"},
        ],
    }
    if skill_key in PYTHON_FUNCTIONS["skill_aliases"]:
        out = []
        for key, questions in banks.items():
            if key in requested:
                out.extend(questions)
        return deepcopy(out)
    if skill_key in SQL_QUERIES_FILTERING["skill_aliases"]:
        out = []
        for key, questions in banks.items():
            if key in requested:
                out.extend(questions)
        return deepcopy(out)
    if skill_key in GIT_LOCAL_REPOSITORIES["skill_aliases"]:
        out = []
        for key, questions in banks.items():
            if key in requested:
                out.extend(questions)
        return deepcopy(out)
    if skill_key in DOCKER_CONTAINERS["skill_aliases"]:
        out = []
        for key, questions in banks.items():
            if key in requested:
                out.extend(questions)
        return deepcopy(out)
    return []


# These declarations reserve stable identifiers and schema for later curation.
# They are intentionally not served as lessons and must not be described as complete.
# All ten SQL blueprint topics are now complete curated content; nothing SQL is planned.
PLANNED_TOPICS = {
    ("machine learning", "evaluation basics"): {"status": "planned", "competency": "Evaluation basics", "prerequisites": ["Training a first model"], "content": None},
}


def complete_lesson(skill_name, competency):
    """Return a deep copy of canonical complete content, or ``None``."""
    if _key(skill_name) in PYTHON_FUNCTIONS["skill_aliases"] and _key(competency) == "python functions":
        return deepcopy(PYTHON_FUNCTIONS)
    if _key(skill_name) in PYTHON_ERROR_HANDLING["skill_aliases"] and _key(competency) in ("python error handling", "error handling"):
        return deepcopy(PYTHON_ERROR_HANDLING)
    if _key(skill_name) in SQL_QUERIES_FILTERING["skill_aliases"]:
        if _key(competency) in ("queries & filtering", "sql queries & filtering", "sql queries filtering"):
            return deepcopy(SQL_QUERIES_FILTERING)
        if _key(competency) in ("sorting & limiting", "sql sorting & limiting", "sql sorting limiting"):
            return deepcopy(SQL_SORTING_LIMITING)
        if _key(competency) in ("aggregation", "sql aggregation"):
            return deepcopy(SQL_AGGREGATION)
        if _key(competency) in ("joins", "sql joins"):
            return deepcopy(SQL_JOINS)
        if _key(competency) in ("subqueries", "sql subqueries"):
            return deepcopy(SQL_SUBQUERIES)
        if _key(competency) in ("indexing basics", "sql indexing basics"):
            return deepcopy(SQL_INDEXING_BASICS)
        if _key(competency) in ("window functions", "sql window functions"):
            return deepcopy(SQL_WINDOW_FUNCTIONS)
        if _key(competency) in ("query optimization", "sql query optimization"):
            return deepcopy(SQL_QUERY_OPTIMIZATION)
        if _key(competency) in ("transactions", "sql transactions"):
            return deepcopy(SQL_TRANSACTIONS)
        if _key(competency) in ("schema design", "sql schema design"):
            return deepcopy(SQL_SCHEMA_DESIGN)
    if _key(skill_name) in GIT_LOCAL_REPOSITORIES["skill_aliases"]:
        if _key(competency) in ("local repositories", "git local repositories"):
            return deepcopy(GIT_LOCAL_REPOSITORIES)
        if _key(competency) in ("committing", "git committing"):
            return deepcopy(GIT_COMMITTING)
        if _key(competency) in ("branching", "git branching"):
            return deepcopy(GIT_BRANCHING)
        if _key(competency) in ("merging", "git merging"):
            return deepcopy(GIT_MERGING)
        if _key(competency) in ("rebasing", "git rebasing"):
            return deepcopy(GIT_REBASING)
        if _key(competency) in ("remotes & collaboration", "git remotes & collaboration",
                                "remotes collaboration", "git remotes collaboration"):
            return deepcopy(GIT_REMOTES_COLLABORATION)
        if _key(competency) in ("history rewriting", "git history rewriting"):
            return deepcopy(GIT_HISTORY_REWRITING)
        if _key(competency) in ("bisect & debugging", "git bisect & debugging",
                                "bisect debugging", "git bisect debugging"):
            return deepcopy(GIT_BISECT_DEBUGGING)
        if _key(competency) in ("submodules", "git submodules"):
            return deepcopy(GIT_SUBMODULES)
        if _key(competency) in ("workflows & policy", "git workflows & policy",
                                "workflows policy", "git workflows policy",
                                "workflows and policy", "git workflows and policy"):
            return deepcopy(GIT_WORKFLOWS_POLICY)
        if _key(competency) in ("large-repo strategies", "git large-repo strategies",
                                "large repo strategies", "git large repo strategies"):
            return deepcopy(GIT_LARGE_REPO_STRATEGIES)
    if _key(skill_name) in DOCKER_CONTAINERS["skill_aliases"] and _key(competency) in ("containers", "docker containers"):
        return deepcopy(DOCKER_CONTAINERS)
    if _key(skill_name) in DOCKER_IMAGES["skill_aliases"] and _key(competency) in ("images", "docker images"):
        return deepcopy(DOCKER_IMAGES)
    if _key(skill_name) in DOCKER_BASIC_COMMANDS["skill_aliases"] and _key(competency) in ("basic commands", "basic commands"):
        return deepcopy(DOCKER_BASIC_COMMANDS)
    if _key(skill_name) in DOCKER_DOCKERFILE["skill_aliases"] and _key(competency) in ("dockerfile",):
        return deepcopy(DOCKER_DOCKERFILE)
    if _key(skill_name) in DOCKER_PORTS["skill_aliases"] and _key(competency) in ("ports",):
        return deepcopy(DOCKER_PORTS)
    if _key(skill_name) in DOCKER_VOLUMES["skill_aliases"] and _key(competency) in ("volumes",):
        return deepcopy(DOCKER_VOLUMES)
    if _key(skill_name) in DOCKER_NETWORKING["skill_aliases"] and _key(competency) in ("networking",):
        return deepcopy(DOCKER_NETWORKING)
    if _key(skill_name) in DOCKER_COMPOSE["skill_aliases"] and _key(competency) in ("compose",):
        return deepcopy(DOCKER_COMPOSE)
    if _key(skill_name) in DOCKER_MULTI_STAGE_BUILDS["skill_aliases"] and _key(competency) in ("multi-stage builds",):
        return deepcopy(DOCKER_MULTI_STAGE_BUILDS)
    if _key(skill_name) in DOCKER_SECURITY_SECRETS["skill_aliases"] and _key(competency) in ("security & secrets",):
        return deepcopy(DOCKER_SECURITY_SECRETS)
    if _key(skill_name) in DOCKER_ORCHESTRATION_BASICS["skill_aliases"] and _key(competency) in ("orchestration basics",):
        return deepcopy(DOCKER_ORCHESTRATION_BASICS)
    return None


def prerequisites_for(skill_name, competency):
    topic = complete_lesson(skill_name, competency)
    return topic["prerequisites"] if topic else []

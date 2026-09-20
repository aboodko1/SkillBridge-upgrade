"""Curated SQL topics: batches 1-4 across all ten blueprint competencies.

Batch 1: Sorting & Limiting, Aggregation. Batch 2: Joins, Subqueries.
Batch 3: Indexing basics, Window functions. Batch 4 (final): Query
optimization, Transactions, Schema design.

Dev A owns this file with backend/tests/test_curated_sql_foundations.py.  It
pins the bilingual complete content, the additive non-executing static review,
the curated diagnostic banks, and the full flows that persist progress without
ever verifying the skill.
"""
from urllib.parse import quote

import pytest

from app import genai, knowledge_base, lessons, models, practice
from app import skill_blueprint as sb


SORT_ANSWER = """SELECT name, total
FROM customers
ORDER BY total DESC
LIMIT 3;

ORDER BY sorts the result from the highest total down, and LIMIT keeps only three rows."""
AGG_ANSWER = """SELECT city, COUNT(*) AS customer_count
FROM customers
GROUP BY city
HAVING COUNT(*) >= 2;

GROUP BY creates one group per city, and HAVING keeps only groups with at least two customers."""
JOIN_ANSWER = """SELECT customers.name, orders.order_date
FROM customers
INNER JOIN orders
ON customers.id = orders.customer_id;

ON tells the join which columns to compare."""
SUB_ANSWER = """SELECT name
FROM customers
WHERE total >
  (SELECT AVG(total) FROM customers);

The inner query returns the average total."""
INDEX_ANSWER = """SELECT name, email
FROM customers
WHERE email = 'sara@example.com';

An index on the email column helps the database find the row directly instead of scanning the table."""
WINDOW_ANSWER = """SELECT name, total,
       ROW_NUMBER() OVER (ORDER BY total DESC) AS position
FROM customers;

OVER keeps every row while the row number is computed over the window."""
QOPT_ANSWER = """SELECT name, total
FROM customers
ORDER BY total DESC
LIMIT 3;

An index on total may help the optimizer, but a static review cannot measure query performance."""
TXN_ANSWER = """BEGIN;

SELECT name, total
FROM customers
WHERE name = 'amira';

COMMIT;

A transaction groups statements as one unit, but a static review cannot prove commit, rollback, isolation, or atomicity."""
SCHEMA_ANSWER = """CREATE TABLE customers (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  city TEXT,
  status TEXT
);

This defines the intended structure; a static review does not prove the schema was deployed or validated on a running database."""


@pytest.fixture(autouse=True)
def offline_reviewer(monkeypatch):
    monkeypatch.setattr(genai, "genai_enabled", lambda: False)


NEW_TOPICS = [
    ("sql_sorting_limiting", "sorting & limiting", "Sorting & limiting"),
    ("sql_aggregation", "aggregation", "Aggregation"),
    ("sql_joins", "joins", "Joins"),
    ("sql_subqueries", "subqueries", "Subqueries"),
    ("sql_indexing_basics", "indexing basics", "Indexing basics"),
    ("sql_window_functions", "window functions", "Window functions"),
    ("sql_query_optimization", "query optimization", "Query optimization"),
    ("sql_transactions", "transactions", "Transactions"),
    ("sql_schema_design", "schema design", "Schema design"),
]


def test_all_ten_sql_topics_complete_and_in_canonical_blueprint_order():
    blueprint_sql = []
    for level in ("Beginner", "Intermediate", "Advanced"):
        blueprint_sql.extend(sb.BLUEPRINT["sql"][level])
    assert blueprint_sql == [
        "Queries & filtering", "Sorting & limiting", "Aggregation", "Joins",
        "Subqueries", "Indexing basics", "Window functions",
        "Query optimization", "Transactions", "Schema design",
    ]
    for competency in blueprint_sql:
        topic = knowledge_base.complete_lesson("SQL", competency)
        assert topic and topic["status"] == "complete"
        if competency == "Queries & filtering":
            assert topic["competency"] == "SQL Queries & Filtering"
        else:
            assert topic["competency"] == competency
        assert knowledge_base.complete_lesson("SQL", sb.competency_slug(competency)) is not None


def test_curated_sql_topics_are_complete_and_resolved_by_every_key_form():
    expected = {
        "sql_sorting_limiting": ("Sorting & limiting", "SQL Sorting & Limiting"),
        "sql_aggregation": ("Aggregation", "SQL Aggregation"),
        "sql_joins": ("Joins", "SQL Joins"),
        "sql_subqueries": ("Subqueries", "SQL Subqueries"),
        "sql_indexing_basics": ("Indexing basics", "SQL Indexing Basics"),
        "sql_window_functions": ("Window functions", "SQL Window Functions"),
        "sql_query_optimization": ("Query optimization", "SQL Query Optimization"),
        "sql_transactions": ("Transactions", "SQL Transactions"),
        "sql_schema_design": ("Schema design", "SQL Schema Design"),
    }
    for slug, key_form, display in NEW_TOPICS:
        blue, learn_title = expected[slug]
        topic = knowledge_base.complete_lesson("SQL", slug)
        assert topic and topic["status"] == "complete"
        assert topic["competency"] == blue
        assert topic["learn"]["title"] == learn_title
        assert knowledge_base.complete_lesson("SQL", key_form)["competency"] == blue
        assert knowledge_base.complete_lesson("SQL", display)["competency"] == blue


def test_prerequisites_point_at_complete_sql_topics():
    sorting = knowledge_base.complete_lesson("SQL", "sql_sorting_limiting")
    aggregation = knowledge_base.complete_lesson("SQL", "sql_aggregation")
    joins = knowledge_base.complete_lesson("SQL", "sql_joins")
    subqueries = knowledge_base.complete_lesson("SQL", "sql_subqueries")
    indexing = knowledge_base.complete_lesson("SQL", "sql_indexing_basics")
    window = knowledge_base.complete_lesson("SQL", "sql_window_functions")
    qopt = knowledge_base.complete_lesson("SQL", "sql_query_optimization")
    transactions = knowledge_base.complete_lesson("SQL", "sql_transactions")
    schema = knowledge_base.complete_lesson("SQL", "sql_schema_design")
    sorting_prereqs = {p["competency"] for p in sorting["prerequisites"]}
    aggregation_prereqs = {p["competency"] for p in aggregation["prerequisites"]}
    joins_prereqs = {p["competency"] for p in joins["prerequisites"]}
    subqueries_prereqs = {p["competency"] for p in subqueries["prerequisites"]}
    indexing_prereqs = {p["competency"] for p in indexing["prerequisites"]}
    window_prereqs = {p["competency"] for p in window["prerequisites"]}
    qopt_prereqs = {p["competency"] for p in qopt["prerequisites"]}
    transactions_prereqs = {p["competency"] for p in transactions["prerequisites"]}
    schema_prereqs = {p["competency"] for p in schema["prerequisites"]}
    assert "sql_queries_filtering" in sorting_prereqs
    assert {"sql_queries_filtering", "sql_sorting_limiting"} <= aggregation_prereqs
    assert {"sql_queries_filtering", "sql_sorting_limiting", "sql_aggregation"} <= joins_prereqs
    assert {"sql_queries_filtering", "sql_sorting_limiting", "sql_aggregation", "sql_joins"} <= subqueries_prereqs
    assert {"sql_queries_filtering", "sql_sorting_limiting", "sql_aggregation", "sql_joins", "sql_subqueries"} <= indexing_prereqs
    assert {"sql_queries_filtering", "sql_sorting_limiting", "sql_aggregation", "sql_joins", "sql_subqueries", "sql_indexing_basics"} <= window_prereqs
    assert {"sql_queries_filtering", "sql_sorting_limiting", "sql_aggregation", "sql_joins", "sql_subqueries", "sql_indexing_basics", "sql_window_functions"} <= qopt_prereqs
    assert {"sql_queries_filtering", "sql_sorting_limiting", "sql_aggregation", "sql_joins", "sql_subqueries", "sql_indexing_basics", "sql_window_functions", "sql_query_optimization"} <= transactions_prereqs
    assert {"sql_queries_filtering", "sql_sorting_limiting", "sql_aggregation", "sql_joins", "sql_subqueries", "sql_indexing_basics", "sql_window_functions", "sql_query_optimization", "sql_transactions"} <= schema_prereqs
    # The orchestrator's canonical guard matches display-name prerequisites too.
    assert "SQL Queries & Filtering" in joins_prereqs
    assert {"SQL Queries & Filtering", "Sorting & limiting", "Aggregation", "Joins"} <= subqueries_prereqs
    assert {"SQL Queries & Filtering", "Sorting & limiting", "Aggregation", "Joins", "Subqueries"} <= indexing_prereqs
    assert {"SQL Queries & Filtering", "Sorting & limiting", "Aggregation", "Joins", "Subqueries", "Indexing basics"} <= window_prereqs
    assert {"SQL Queries & Filtering", "Sorting & limiting", "Aggregation", "Joins", "Subqueries", "Indexing basics", "Window functions"} <= qopt_prereqs
    assert {"SQL Queries & Filtering", "Sorting & limiting", "Aggregation", "Joins", "Subqueries", "Indexing basics", "Window functions", "Query optimization"} <= transactions_prereqs
    assert {"SQL Queries & Filtering", "Sorting & limiting", "Aggregation", "Joins", "Subqueries", "Indexing basics", "Window functions", "Query optimization", "Transactions"} <= schema_prereqs
    # Every slug prerequisite resolves to a complete curated lesson.
    for slug in (sorting_prereqs | aggregation_prereqs | joins_prereqs | subqueries_prereqs
                 | indexing_prereqs | window_prereqs | qopt_prereqs
                 | transactions_prereqs | schema_prereqs):
        assert knowledge_base.complete_lesson("SQL", slug) is not None


def test_new_topic_lessons_are_bilingual_and_mini_checks_pass():
    static_boundary = {
        "sql_query_optimization": "cannot claim actual performance",
        "sql_transactions": "cannot prove that any commit, rollback, isolation, or atomicity",
        "sql_schema_design": "cannot claim the schema was deployed or validated",
    }
    for slug, _, _ in NEW_TOPICS:
        content = lessons.generate_lesson("SQL", slug, "learn")
        assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
        assert len(content["learn"]["grounding_sources"]) == 2
        assert "does not provide a SQL database" in content["learn"]["version_note"]
        assert content["practice"]["language"] == "sql"
        assert static_boundary.get(slug, "cannot prove runtime results") in content["practice"]["evaluation_note"]
        assert content["locales"]["ar"]["learn"]["title"]
        assert content["locales"]["ar"]["practice"]["task"]
        assert len(content["locales"]["ar"]["mini_check"]["questions"]) == 3
        # Display translations never leak canonical English answers.
        assert all("correct_answer" not in q for q in content["locales"]["ar"]["mini_check"]["questions"])

        answers = [q["correct_answer"] for q in content["mini_check"]["questions"]]
        assert lessons.score_mini_check(content["mini_check"]["questions"], answers) == (3, 3, True)


def test_sorting_limiting_static_review_never_executes():
    lesson = {"content": lessons.generate_lesson("SQL", "sql_sorting_limiting", "learn")}
    good = practice.sql_sorting_limiting_static_check(lesson, SORT_ANSWER)
    assert good["kind"] == "sql_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not connect to a database or execute" in good["note"]

    for bad, expected in [
        ("UPDATE customers SET total = 0;", "Use one read-only SELECT"),
        ("SELECT name, total FROM customers ORDER BY total ASC LIMIT 3;", "Order by total descending"),
        ("SELECT name, total FROM customers ORDER BY total DESC;", "Keep the top three rows"),
    ]:
        result = practice.sql_sorting_limiting_static_check(lesson, bad)
        assert result["status"] == "needs_fix"
        assert any(expected in check for check in result["checks"])


def test_aggregation_static_review_never_executes():
    lesson = {"content": lessons.generate_lesson("SQL", "sql_aggregation", "learn")}
    good = practice.sql_aggregation_static_check(lesson, AGG_ANSWER)
    assert good["kind"] == "sql_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not connect to a database or execute" in good["note"]

    for bad, expected in [
        ("DELETE FROM customers WHERE city = 'Cairo';", "Use one read-only SELECT"),
        ("SELECT city, COUNT(*) FROM customers WHERE COUNT(*) >= 2 GROUP BY city;", "Filter the groups"),
        ("SELECT city, COUNT(*) FROM customers GROUP BY city;", "HAVING COUNT(*) >= 2"),
    ]:
        result = practice.sql_aggregation_static_check(lesson, bad)
        assert result["status"] == "needs_fix"
        assert any(expected in check for check in result["checks"])


def test_joins_static_review_never_executes():
    lesson = {"content": lessons.generate_lesson("SQL", "sql_joins", "learn")}
    good = practice.sql_joins_static_check(lesson, JOIN_ANSWER)
    assert good["kind"] == "sql_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not connect to a database or execute" in good["note"]

    for bad, expected in [
        ("DELETE FROM orders;", "Use one read-only SELECT"),
        ("SELECT customers.name, orders.order_date FROM customers FULL OUTER JOIN orders ON customers.id = orders.customer_id;", "INNER JOIN"),
        ("SELECT customers.name FROM customers INNER JOIN orders;", "ON customers.id = orders.customer_id"),
        ("UPDATE customers SET name = 'x';", "Use one read-only SELECT"),
    ]:
        result = practice.sql_joins_static_check(lesson, bad)
        assert result["status"] == "needs_fix"
        assert any(expected in check for check in result["checks"])


def test_subqueries_static_review_never_executes():
    lesson = {"content": lessons.generate_lesson("SQL", "sql_subqueries", "learn")}
    good = practice.sql_subqueries_static_check(lesson, SUB_ANSWER)
    assert good["kind"] == "sql_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not connect to a database or execute" in good["note"]

    for bad, expected in [
        ("DELETE FROM customers WHERE total > 100;", "Use one read-only SELECT"),
        ("SELECT name FROM customers WHERE total > AVG(total);", "inner query in parentheses"),
        ("SELECT name FROM customers ORDER BY total;", "Compare total to the average"),
        ("INSERT INTO customers (name) VALUES ('x');", "Use one read-only SELECT"),
    ]:
        result = practice.sql_subqueries_static_check(lesson, bad)
        assert result["status"] == "needs_fix"
        assert any(expected in check for check in result["checks"])


def test_indexing_basics_static_review_never_executes():
    lesson = {"content": lessons.generate_lesson("SQL", "sql_indexing_basics", "learn")}
    good = practice.sql_indexing_basics_static_check(lesson, INDEX_ANSWER)
    assert good["kind"] == "sql_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not connect to a database or execute" in good["note"]

    for bad, expected in [
        ("DELETE FROM customers WHERE email = 'sara@example.com';", "Use one read-only SELECT"),
        ("SELECT name FROM customers;", "WHERE email = 'sara@example.com'"),
        ("SELECT name, email FROM customers WHERE total > 100;", "WHERE email"),
        ("UPDATE customers SET name = 'x';", "Use one read-only SELECT"),
    ]:
        result = practice.sql_indexing_basics_static_check(lesson, bad)
        assert result["status"] == "needs_fix"
        assert any(expected in check for check in result["checks"])


def test_window_functions_static_review_never_executes():
    lesson = {"content": lessons.generate_lesson("SQL", "sql_window_functions", "learn")}
    good = practice.sql_window_functions_static_check(lesson, WINDOW_ANSWER)
    assert good["kind"] == "sql_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not connect to a database or execute" in good["note"]

    for bad, expected in [
        ("DELETE FROM customers;", "Use one read-only SELECT"),
        ("SELECT name, total FROM customers ORDER BY total DESC;", "ROW_NUMBER() with an OVER"),
        ("SELECT name, total, ROW_NUMBER() OVER (PARTITION BY city) AS position FROM customers;", "Order the window"),
        ("UPDATE customers SET position = 1;", "Use one read-only SELECT"),
    ]:
        result = practice.sql_window_functions_static_check(lesson, bad)
        assert result["status"] == "needs_fix"
        assert any(expected in check for check in result["checks"])


def test_query_optimization_static_review_never_executes_and_never_claims_speed():
    lesson = {"content": lessons.generate_lesson("SQL", "sql_query_optimization", "learn")}
    good = practice.sql_query_optimization_static_check(lesson, QOPT_ANSWER)
    assert good["kind"] == "sql_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not connect to a database or execute" in good["note"]
    assert "cannot measure query performance" in good["note"]

    for bad, expected in [
        ("DELETE FROM customers;", "Use one read-only SELECT"),
        ("SELECT name, total FROM customers ORDER BY total ASC LIMIT 3;\nIt is faster.", "Order by total descending"),
        ("SELECT name, total FROM customers ORDER BY total DESC;", "Keep the top three rows"),
        ("SELECT name, total FROM customers ORDER BY total DESC LIMIT 3;\nThis runs in 1ms.", "static review cannot measure query performance"),
    ]:
        result = practice.sql_query_optimization_static_check(lesson, bad)
        assert result["status"] == "needs_fix"
        assert any(expected in check for check in result["checks"])


def test_transactions_static_review_never_executes_and_never_proves_runtime_guarantees():
    lesson = {"content": lessons.generate_lesson("SQL", "sql_transactions", "learn")}
    good = practice.sql_transactions_static_check(lesson, TXN_ANSWER)
    assert good["kind"] == "sql_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not connect to a database or execute" in good["note"]
    assert "cannot prove that any commit, rollback, isolation, or atomicity" in good["note"]

    for bad, expected in [
        ("SELECT name, total FROM customers WHERE name = 'amira';", "Open the transaction with BEGIN"),
        ("BEGIN;\nSELECT name, total FROM customers;\nCOMMIT;\nCommit guarantees atomicity here.", "cannot prove commit, rollback, isolation, or atomicity"),
        ("BEGIN;\nUPDATE customers SET total = 0;\nCOMMIT;", "read-only SELECT"),
        ("BEGIN;\nSELECT name, total FROM customers WHERE name = 'amira';", "Close the transaction with COMMIT"),
    ]:
        result = practice.sql_transactions_static_check(lesson, bad)
        assert result["status"] == "needs_fix"
        assert any(expected in check for check in result["checks"])


def test_schema_design_static_review_never_executes_and_never_claims_deployment():
    lesson = {"content": lessons.generate_lesson("SQL", "sql_schema_design", "learn")}
    good = practice.sql_schema_design_static_check(lesson, SCHEMA_ANSWER)
    assert good["kind"] == "sql_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not create a table, connect to a database, or validate this schema" in good["note"]
    assert "cannot claim the schema was deployed or validated" in good["note"]

    for bad, expected in [
        ("CREATE TABLE customers (id INTEGER PRIMARY KEY);\nThis schema is live.", "static review does not prove the schema was deployed or validated"),
        ("CREATE TABLE orders (id INTEGER PRIMARY KEY, name TEXT NOT NULL);\nIntended structure only.", "Start the statement with CREATE TABLE customers"),
        ("CREATE TABLE customers (id INTEGER, name TEXT NOT NULL, email TEXT UNIQUE);\nIntended structure only.", "id column with PRIMARY KEY"),
        ("CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE);\nIntended structure only.", "name column with NOT NULL"),
        ("CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT);\nIntended structure only.", "email column with UNIQUE"),
        ("DROP TABLE customers;", "Start the statement with CREATE TABLE customers"),
    ]:
        result = practice.sql_schema_design_static_check(lesson, bad)
        assert result["status"] == "needs_fix"
        assert any(expected in check for check in result["checks"])


def test_static_reviews_are_scoped_to_their_own_lesson():
    sort_lesson = {"content": lessons.generate_lesson("SQL", "sql_sorting_limiting", "learn")}
    agg_lesson = {"content": lessons.generate_lesson("SQL", "sql_aggregation", "learn")}
    join_lesson = {"content": lessons.generate_lesson("SQL", "sql_joins", "learn")}
    sub_lesson = {"content": lessons.generate_lesson("SQL", "sql_subqueries", "learn")}
    index_lesson = {"content": lessons.generate_lesson("SQL", "sql_indexing_basics", "learn")}
    window_lesson = {"content": lessons.generate_lesson("SQL", "sql_window_functions", "learn")}
    qopt_lesson = {"content": lessons.generate_lesson("SQL", "sql_query_optimization", "learn")}
    txn_lesson = {"content": lessons.generate_lesson("SQL", "sql_transactions", "learn")}
    schema_lesson = {"content": lessons.generate_lesson("SQL", "sql_schema_design", "learn")}
    assert practice.sql_aggregation_static_check(sort_lesson, AGG_ANSWER) is None
    assert practice.sql_sorting_limiting_static_check(agg_lesson, SORT_ANSWER) is None
    assert practice.sql_joins_static_check(sub_lesson, JOIN_ANSWER) is None
    assert practice.sql_subqueries_static_check(join_lesson, SUB_ANSWER) is None
    assert practice.sql_joins_static_check(sort_lesson, JOIN_ANSWER) is None
    assert practice.sql_subqueries_static_check(agg_lesson, SUB_ANSWER) is None
    assert practice.sql_indexing_basics_static_check(window_lesson, INDEX_ANSWER) is None
    assert practice.sql_window_functions_static_check(index_lesson, WINDOW_ANSWER) is None
    assert practice.sql_indexing_basics_static_check(sub_lesson, INDEX_ANSWER) is None
    assert practice.sql_window_functions_static_check(join_lesson, WINDOW_ANSWER) is None
    assert practice.sql_query_optimization_static_check(window_lesson, QOPT_ANSWER) is None
    assert practice.sql_transactions_static_check(qopt_lesson, TXN_ANSWER) is None
    assert practice.sql_schema_design_static_check(txn_lesson, SCHEMA_ANSWER) is None
    assert practice.sql_query_optimization_static_check(txn_lesson, QOPT_ANSWER) is None
    assert practice.sql_transactions_static_check(schema_lesson, TXN_ANSWER) is None
    assert practice.sql_schema_design_static_check(qopt_lesson, SCHEMA_ANSWER) is None
    foreign = {"content": {"canonical": {"source": "generated"}, "practice": {"competency": "Joins"}}}
    assert practice.sql_joins_static_check(foreign, JOIN_ANSWER) is None


def test_curated_diagnostic_banks_are_served_only_for_requested_topics():
    only_new = knowledge_base.curated_diagnostic_questions(
        "SQL", ["Sorting & limiting", "Aggregation"])
    assert {q["competency"] for q in only_new} == {"sql_sorting_limiting", "sql_aggregation"}
    assert len(only_new) == 6
    all_sql = knowledge_base.curated_diagnostic_questions(
        "SQL", ["Queries & filtering", "Sorting & limiting", "Aggregation", "Joins", "Subqueries", "Indexing basics", "Window functions", "Query optimization", "Transactions", "Schema design"])
    assert [q["competency"] for q in all_sql].count("sql_queries_filtering") == 3
    assert [q["competency"] for q in all_sql].count("sql_sorting_limiting") == 3
    assert [q["competency"] for q in all_sql].count("sql_aggregation") == 3
    assert [q["competency"] for q in all_sql].count("sql_joins") == 3
    assert [q["competency"] for q in all_sql].count("sql_subqueries") == 3
    assert [q["competency"] for q in all_sql].count("sql_indexing_basics") == 3
    assert [q["competency"] for q in all_sql].count("sql_window_functions") == 3
    assert [q["competency"] for q in all_sql].count("sql_query_optimization") == 3
    assert [q["competency"] for q in all_sql].count("sql_transactions") == 3
    assert [q["competency"] for q in all_sql].count("sql_schema_design") == 3
    assert len(all_sql) == 30


def _make_sql_path(client, student_id, headers, sql):
    generated = client.post(
        f"/api/students/{student_id}/learning/{sql['id']}/diagnostic/generate",
        json={}, headers=headers)
    assert generated.status_code == 200, generated.text
    diagnostic = generated.json()
    submitted = client.post(
        f"/api/students/{student_id}/learning/{sql['id']}/diagnostic/submit",
        json={"diagnostic_id": diagnostic["diagnostic_id"], "answers": ["not this" for _ in diagnostic["questions"]]},
        headers=headers)
    assert submitted.status_code == 200, submitted.text
    path = client.post(
        f"/api/students/{student_id}/learning/{sql['id']}/personalized-path/generate",
        json={}, headers=headers)
    assert path.status_code == 200, path.text
    return diagnostic, path.json()


def test_aggregation_flow_persists_progress_without_verifying_skill(client, student_id, auth_headers):
    headers = auth_headers("aisha@student.edu")
    sql = models.get_skill_by_name("SQL")
    before = {(row["name"], row["level"]) for row in models.get_student(student_id).get("verified_skills") or []}
    diagnostic, path = _make_sql_path(client, student_id, headers, sql)

    assert len(diagnostic["questions"]) == 30
    aggregation_item = next(item for item in path["items"] if item["competency"] == "sql_aggregation")

    base = f"/api/students/{student_id}/learning/{sql['id']}/lessons/{quote('sql_aggregation', safe='')}"
    lesson_response = client.post(base + "/generate", json={}, headers=headers)
    assert lesson_response.status_code == 200, lesson_response.text
    lesson = lesson_response.json()
    assert lesson["content"]["canonical"]["source"] == "trusted_cs_knowledge_base"

    attempt = client.post(base + "/practice", json={"answer": AGG_ANSWER}, headers=headers)
    assert attempt.status_code == 200, attempt.text
    assert attempt.json()["attempt"]["competency"] == "sql_aggregation"

    questions = lesson["content"]["mini_check"]["questions"]
    completed = client.post(base + "/mini-check", json={"answers": [q["correct_answer"] for q in questions]}, headers=headers)
    assert completed.status_code == 200, completed.text
    assert completed.json()["lesson"]["state"] == "completed"

    persisted = client.get(
        f"/api/students/{student_id}/learning/{sql['id']}/personalized-path", headers=headers).json()
    assert aggregation_item["id"] in persisted["progress"]
    assert {(row["name"], row["level"]) for row in models.get_student(student_id).get("verified_skills") or []} == before


def test_preserved_topic_anchors_intact_after_final_batch():
    queries = knowledge_base.complete_lesson("SQL", "sql_queries_filtering")
    assert queries["example"]["content"] == "SELECT name, email\nFROM customers\nWHERE city = 'Cairo';"
    assert queries["learn"]["grounding_sources"][0]["url"] == (
        "https://www.postgresql.org/docs/current/tutorial-select.html")
    # Grounding differs per topic so no topic silently reuses another's claim.
    sorting = knowledge_base.complete_lesson("SQL", "sql_sorting_limiting")
    aggregation = knowledge_base.complete_lesson("SQL", "sql_aggregation")
    joins = knowledge_base.complete_lesson("SQL", "sql_joins")
    subqueries = knowledge_base.complete_lesson("SQL", "sql_subqueries")
    indexing = knowledge_base.complete_lesson("SQL", "sql_indexing_basics")
    window = knowledge_base.complete_lesson("SQL", "sql_window_functions")
    qopt = knowledge_base.complete_lesson("SQL", "sql_query_optimization")
    transactions = knowledge_base.complete_lesson("SQL", "sql_transactions")
    schema = knowledge_base.complete_lesson("SQL", "sql_schema_design")
    assert sorting["learn"]["grounding_sources"][0]["url"] == (
        "https://www.postgresql.org/docs/current/tutorial-select.html")
    assert aggregation["learn"]["grounding_sources"][0]["url"] == (
        "https://www.postgresql.org/docs/current/tutorial-agg.html")
    assert aggregation["learn"]["grounding_sources"][1]["url"] == (
        "https://sqlite.org/lang_aggfunc.html")
    assert joins["learn"]["grounding_sources"][0]["url"] == (
        "https://www.postgresql.org/docs/current/tutorial-join.html")
    assert joins["learn"]["grounding_sources"][1]["url"] == (
        "https://sqlite.org/lang_select.html")
    assert subqueries["learn"]["grounding_sources"][0]["url"] == (
        "https://www.postgresql.org/docs/current/functions-subquery.html")
    assert subqueries["learn"]["grounding_sources"][1]["url"] == (
        "https://sqlite.org/lang_select.html")
    assert indexing["learn"]["grounding_sources"][0]["url"] == (
        "https://www.postgresql.org/docs/current/indexes.html")
    assert indexing["learn"]["grounding_sources"][1]["url"] == (
        "https://sqlite.org/lang_createindex.html")
    assert window["learn"]["grounding_sources"][0]["url"] == (
        "https://www.postgresql.org/docs/current/tutorial-window.html")
    assert window["learn"]["grounding_sources"][1]["url"] == (
        "https://sqlite.org/windowfunctions.html")
    assert qopt["learn"]["grounding_sources"][0]["url"] == (
        "https://www.postgresql.org/docs/current/using-explain.html")
    assert qopt["learn"]["grounding_sources"][1]["url"] == (
        "https://sqlite.org/lang_explain.html")
    assert transactions["learn"]["grounding_sources"][0]["url"] == (
        "https://www.postgresql.org/docs/current/tutorial-transactions.html")
    assert transactions["learn"]["grounding_sources"][1]["url"] == (
        "https://sqlite.org/lang_transaction.html")
    assert schema["learn"]["grounding_sources"][0]["url"] == (
        "https://www.postgresql.org/docs/current/ddl-constraints.html")
    assert schema["learn"]["grounding_sources"][1]["url"] == (
        "https://sqlite.org/lang_createtable.html")


def _flow(slug, answer, expected_competency):
    def test_fn(client, student_id, auth_headers):
        headers = auth_headers("aisha@student.edu")
        sql = models.get_skill_by_name("SQL")
        before = {(row["name"], row["level"]) for row in models.get_student(student_id).get("verified_skills") or []}
        diagnostic, path = _make_sql_path(client, student_id, headers, sql)
        item = next(i for i in path["items"] if i["competency"] == slug)

        base = f"/api/students/{student_id}/learning/{sql['id']}/lessons/{quote(slug, safe='')}"
        lesson_response = client.post(base + "/generate", json={}, headers=headers)
        assert lesson_response.status_code == 200, lesson_response.text
        lesson = lesson_response.json()
        assert lesson["content"]["canonical"]["source"] == "trusted_cs_knowledge_base"

        attempt = client.post(base + "/practice", json={"answer": answer}, headers=headers)
        assert attempt.status_code == 200, attempt.text
        assert attempt.json()["attempt"]["competency"] == slug

        questions = lesson["content"]["mini_check"]["questions"]
        completed = client.post(base + "/mini-check", json={"answers": [q["correct_answer"] for q in questions]}, headers=headers)
        assert completed.status_code == 200, completed.text
        assert completed.json()["lesson"]["state"] == "completed"

        persisted = client.get(
            f"/api/students/{student_id}/learning/{sql['id']}/personalized-path", headers=headers).json()
        assert item["id"] in persisted["progress"]
        assert {(row["name"], row["level"]) for row in models.get_student(student_id).get("verified_skills") or []} == before

    test_fn.__name__ = f"test_{expected_competency}_flow_persists_progress_without_verifying_skill"
    return test_fn


test_joins_flow_persists_progress_without_verifying_skill = _flow(
    "sql_joins", JOIN_ANSWER, "joins")
test_subqueries_flow_persists_progress_without_verifying_skill = _flow(
    "sql_subqueries", SUB_ANSWER, "subqueries")
test_indexing_basics_flow_persists_progress_without_verifying_skill = _flow(
    "sql_indexing_basics", INDEX_ANSWER, "indexing_basics")
test_window_functions_flow_persists_progress_without_verifying_skill = _flow(
    "sql_window_functions", WINDOW_ANSWER, "window_functions")
test_query_optimization_flow_persists_progress_without_verifying_skill = _flow(
    "sql_query_optimization", QOPT_ANSWER, "query_optimization")
test_transactions_flow_persists_progress_without_verifying_skill = _flow(
    "sql_transactions", TXN_ANSWER, "transactions")
test_schema_design_flow_persists_progress_without_verifying_skill = _flow(
    "sql_schema_design", SCHEMA_ANSWER, "schema_design")
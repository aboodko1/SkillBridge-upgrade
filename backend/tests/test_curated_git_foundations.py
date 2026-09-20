"""Contracts for the curated Git foundation learning topics (batches 1-5).

Covers all eleven canonical Git blueprint topics — Local repositories,
Committing, Branching (Beginner), Merging, Rebasing, Remotes & collaboration,
History rewriting (Intermediate) and Bisect & debugging, Submodules,
Workflows & policy, Large-repo strategies (Advanced), in blueprint order:
bilingual complete lessons, reviewed Mini Checks, static `git` command review
that never executes (and never modifies a repository, runs a merge/rebase/
bisect, overwrites files, rewrites history, contacts any remote, or measures
performance), and the diagnostic -> path -> practice -> mini-check flow that
persists progress without ever verifying the skill.
"""
from urllib.parse import quote

import pytest

from app import genai, knowledge_base, lessons, models, practice
from app import skill_blueprint as sb

GIT_BLUEPRINT = {
    "Beginner": ["Local repositories", "Committing", "Branching"],
    "Intermediate": ["Merging", "Rebasing", "Remotes & collaboration", "History rewriting"],
    "Advanced": ["Bisect & debugging", "Submodules", "Workflows & policy", "Large-repo strategies"],
}

GIT_CANONICAL_ORDER = [
    "git_local_repositories", "git_committing", "git_branching", "git_merging",
    "git_rebasing", "git_remotes_collaboration", "git_history_rewriting",
    "git_bisect_debugging", "git_submodules", "git_workflows_&_policy",
    "git_large-repo_strategies",
]


LOCAL_ANSWER = """cd my-project
git init
git status

The .git directory is where Git keeps the repository's history. This is a written answer: SkillBridge does not run these commands."""


COMMIT_ANSWER = """git add README.md
git commit -m "Add the project README"
git log

A commit is a snapshot of the staged files, saved with a message. This is a written answer: SkillBridge does not run these commands."""


BRANCH_ANSWER = """git branch feature-payment
git switch feature-payment
git status
git branch --list

git branch creates the branch without switching onto it. This is a written answer: SkillBridge does not run these commands."""


MERGE_ANSWER = """git switch main
git merge feature-payment
git log

When both branches changed the same lines, Git reports a conflict: I read both sides, edit the file, stage with git add, then finish the commit. This is a written answer: SkillBridge does not run the merge or change any repository."""


REBASE_ANSWER = """git switch feature-payment
git rebase main
git log

Rebase rewrites the branch's commits for a linear history instead of joining histories with a merge commit, and you must never rebase commits that have already been shared. This is a written answer: SkillBridge does not run the rebase or rewrite any repository's history."""


REMOTES_ANSWER = """git fetch origin
git pull
git push origin feature-payment

git fetch only downloads the remote state while git pull also integrates it, and a Pull Request is a review step on the hosting service. This is a written answer: SkillBridge does not run these commands or contact any remote."""


HISTORY_ANSWER = """git commit --amend -m "Add the project README"
git rebase -i main
git log

Amend and interactive rebase rewrite commit hashes, so they are safe only for local commits that have not been pushed; published history is extended with new commits instead. This is a written answer: SkillBridge does not run these commands or rewrite any repository's history."""


BISECT_ANSWER = """git bisect start
git bisect bad
git bisect good v1.2
git bisect reset

Git checks out midpoint commits for me to test, and the finished bisect names the first bad commit that introduced the regression. This is a written answer: SkillBridge does not run these commands or start a bisect in any repository."""


SUBMODULES_ANSWER = """git clone https://example.com/team/library
git submodule init
git submodule update

A submodule references a pinned commit (a specific SHA) recorded in .gitmodules. This is a written answer: SkillBridge does not run these commands or modify any repository's submodules."""


WORKFLOWS_ANSWER = """git switch -c feature-login
git push origin feature-login
git merge feature-login

Feature branches isolate work until review; a Pull Request is a review step on the hosting service before protected main is merged. This is a written answer: SkillBridge does not run these commands or configure any repository policy."""


LARGE_REPO_ANSWER = """git clone --depth 1 https://example.com/big-project
git clone --filter=blob:none https://example.com/big-project
git sparse-checkout set src tests
git lfs install

Each of these strategies has limitations and trade-offs. This is a written answer: SkillBridge does not run these commands or measure any performance improvement."""


@pytest.fixture(autouse=True)
def offline_reviewer(monkeypatch):
    monkeypatch.setattr(genai, "genai_enabled", lambda: False)


def test_git_blueprint_topics_and_canonical_order_are_served_in_exact_order():
    for level, topics in GIT_BLUEPRINT.items():
        assert sb.BLUEPRINT["git"][level] == topics
    assert sb.required_competencies("Git", "Beginner", "Advanced") == [
        "Local repositories", "Committing", "Branching", "Merging", "Rebasing",
        "Remotes & collaboration", "History rewriting", "Bisect & debugging",
        "Submodules", "Workflows & policy", "Large-repo strategies",
    ]


def test_all_eleven_git_topics_are_complete_curated_content():
    # All eleven Git blueprint topics are complete in canonical order; their
    # display-name forms resolve too, and nothing Git stays reserved or planned
    # (the machine-learning topic keeps its booked slot).
    for competency in GIT_CANONICAL_ORDER:
        topic = knowledge_base.complete_lesson("Git", competency)
        assert topic and topic["status"] == "complete"
    for competency in GIT_BLUEPRINT["Beginner"] + GIT_BLUEPRINT["Intermediate"] + GIT_BLUEPRINT["Advanced"]:
        assert knowledge_base.complete_lesson("Git", competency) and \
            knowledge_base.complete_lesson("Git", competency)["status"] == "complete"
    assert all("git" not in str(key) or key[0] != "git" for key in knowledge_base.PLANNED_TOPICS)


def test_git_local_repositories_is_a_complete_bilingual_lesson():
    topic = knowledge_base.complete_lesson("Git", "git_local_repositories")
    assert topic and topic["status"] == "complete"
    assert topic["skill_aliases"] == ("git",)
    assert topic["prerequisites"][0]["competency"] == "Command line basics"
    assert topic["prerequisites"][0]["relationship"] == "required foundation"
    assert "roadmap" in topic["roadmap_rationale"].lower()

    content = lessons.generate_lesson("Git", "Local repositories", "learn")
    assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
    assert "git init" in content["example"]["content"]
    assert "git status" in content["example"]["content"]
    assert "does not run these commands" in content["learn"]["version_note"]
    assert len(content["learn"]["grounding_sources"]) >= 2
    assert all("git-scm.com" in source["url"] for source in content["learn"]["grounding_sources"])
    assert content["locales"]["ar"]["learn"]["title"] == "المستودعات المحلية"
    assert "مستودع" in content["locales"]["ar"]["learn"]["explanation"]
    assert content["practice"]["language"] == "bash"
    assert "does not run git" in content["practice"]["evaluation_note"]
    assert all(question["competency"] == "Local repositories" for question in content["mini_check"]["questions"])
    answers = [question["correct_answer"] for question in content["mini_check"]["questions"]]
    assert lessons.score_mini_check(content["mini_check"]["questions"], answers) == (3, 3, True)


def test_git_committing_is_a_complete_bilingual_lesson_with_local_repositories_prerequisite():
    topic = knowledge_base.complete_lesson("Git", "Committing")
    assert topic and topic["status"] == "complete"
    assert topic["prerequisites"][0]["competency"] == "Local repositories"
    assert topic["prerequisites"][0]["relationship"] == "required foundation"

    content = lessons.generate_lesson("Git", "Committing", "learn")
    assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
    assert "git add README.md" in content["example"]["content"]
    assert 'git commit -m "Add the project README"' in content["example"]["content"]
    assert "git log" in content["example"]["content"]
    assert len(content["learn"]["grounding_sources"]) >= 2
    assert all("git-scm.com" in source["url"] for source in content["learn"]["grounding_sources"])
    assert content["locales"]["ar"]["learn"]["title"] == "عمل الـ Commits"
    assert "لقطة" in content["locales"]["ar"]["learn"]["explanation"]
    assert "does not run these commands" in content["learn"]["version_note"]
    assert "cannot prove a commit exists" in content["practice"]["evaluation_note"]
    assert all(question["competency"] == "Committing" for question in content["mini_check"]["questions"])
    answers = [question["correct_answer"] for question in content["mini_check"]["questions"]]
    assert lessons.score_mini_check(content["mini_check"]["questions"], answers) == (3, 3, True)


def test_git_branching_is_a_complete_bilingual_lesson_with_committing_prerequisite():
    topic = knowledge_base.complete_lesson("Git", "git_branching")
    assert topic and topic["status"] == "complete"
    assert topic["prerequisites"][0]["competency"] == "Committing"
    assert topic["prerequisites"][0]["relationship"] == "required foundation"
    assert "roadmap" in topic["roadmap_rationale"].lower()

    content = lessons.generate_lesson("Git", "Branching", "learn")
    assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
    assert "git branch feature-payment" in content["example"]["content"]
    assert "git switch feature-payment" in content["example"]["content"]
    assert "git status" in content["example"]["content"]
    assert len(content["learn"]["grounding_sources"]) >= 2
    assert all("git-scm.com" in source["url"] for source in content["learn"]["grounding_sources"])
    assert content["locales"]["ar"]["learn"]["title"] == "الفروع (Branching)"
    assert "فرع" in content["locales"]["ar"]["learn"]["explanation"]
    assert "does not run these commands" in content["learn"]["version_note"]
    assert "cannot prove a branch exists" in content["practice"]["evaluation_note"]
    assert content["practice"]["language"] == "bash"
    assert all(question["competency"] == "Branching" for question in content["mini_check"]["questions"])
    assert not any("correct_answer" in question.get("misconception_hint", "") for question in content["mini_check"]["questions"])
    answers = [question["correct_answer"] for question in content["mini_check"]["questions"]]
    assert lessons.score_mini_check(content["mini_check"]["questions"], answers) == (3, 3, True)


def test_git_merging_is_a_complete_bilingual_lesson_with_branching_prerequisite_and_honest_merge_note():
    topic = knowledge_base.complete_lesson("Git", "Merging")
    assert topic and topic["status"] == "complete"
    assert topic["prerequisites"][0]["competency"] == "Branching"
    assert topic["prerequisites"][0]["relationship"] == "required foundation"
    assert "roadmap" in topic["roadmap_rationale"].lower()

    content = lessons.generate_lesson("Git", "Merging", "learn")
    assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
    assert "git switch main" in content["example"]["content"]
    assert "git merge feature-payment" in content["example"]["content"]
    assert "git log" in content["example"]["content"]
    assert "<<<<<<<" in content["learn"]["explanation"]
    assert len(content["learn"]["grounding_sources"]) >= 2
    assert all("git-scm.com" in source["url"] for source in content["learn"]["grounding_sources"])
    assert content["locales"]["ar"]["learn"]["title"] == "الدمج (Merging)"
    assert "تضارب" in content["locales"]["ar"]["learn"]["explanation"]
    assert "does not run these commands" in content["learn"]["version_note"]
    # The evaluation note is honest: whatever the learner wrote, the review
    # never performs a real merge or touches a repository.
    assert "does not run a merge" in content["practice"]["evaluation_note"]
    assert all(question["competency"] == "Merging" for question in content["mini_check"]["questions"])
    assert not any("correct_answer" in question.get("misconception_hint", "") for question in content["mini_check"]["questions"])
    answers = [question["correct_answer"] for question in content["mini_check"]["questions"]]
    assert lessons.score_mini_check(content["mini_check"]["questions"], answers) == (3, 3, True)


def test_git_rebasing_is_a_complete_bilingual_lesson_with_merging_prerequisite_and_honest_rebase_note():
    topic = knowledge_base.complete_lesson("Git", "git_rebasing")
    assert topic and topic["status"] == "complete"
    assert topic["prerequisites"][0]["competency"] == "Merging"
    assert topic["prerequisites"][0]["relationship"] == "required foundation"
    assert "roadmap" in topic["roadmap_rationale"].lower()

    content = lessons.generate_lesson("Git", "Rebasing", "learn")
    assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
    assert "git switch feature-payment" in content["example"]["content"]
    assert "git rebase main" in content["example"]["content"]
    assert "git log" in content["example"]["content"]
    assert "merge" in content["learn"]["explanation"].lower()
    assert "shared" in content["learn"]["explanation"].lower()
    assert len(content["learn"]["grounding_sources"]) >= 2
    assert all("git-scm.com" in source["url"] for source in content["learn"]["grounding_sources"])
    assert content["locales"]["ar"]["learn"]["title"] == "إعادة التأسيس (Rebasing)"
    assert "rebase" in content["locales"]["ar"]["learn"]["explanation"]
    assert "does not run these commands" in content["learn"]["version_note"]
    # The evaluation note is honest: the review never performs a rebase or
    # rewrites any repository's history.
    assert "does not run a rebase" in content["practice"]["evaluation_note"]
    assert content["practice"]["language"] == "bash"
    assert all(question["competency"] == "Rebasing" for question in content["mini_check"]["questions"])
    assert not any("correct_answer" in question.get("misconception_hint", "") for question in content["mini_check"]["questions"])
    answers = [question["correct_answer"] for question in content["mini_check"]["questions"]]
    assert lessons.score_mini_check(content["mini_check"]["questions"], answers) == (3, 3, True)


def test_git_remotes_collaboration_is_a_complete_bilingual_lesson_with_committing_prerequisite_and_honest_network_note():
    topic = knowledge_base.complete_lesson("Git", "git_remotes_collaboration")
    assert topic and topic["status"] == "complete"
    assert topic["competency"] == "Remotes & collaboration"
    assert topic["prerequisites"][0]["competency"] == "Committing"
    assert topic["prerequisites"][0]["relationship"] == "required foundation"
    assert "roadmap" in topic["roadmap_rationale"].lower()

    content = lessons.generate_lesson("Git", "Remotes & collaboration", "learn")
    assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
    assert "git fetch origin" in content["example"]["content"]
    assert "git pull" in content["example"]["content"]
    assert "git push origin feature-payment" in content["example"]["content"]
    assert "Pull Request" in content["learn"]["explanation"]
    assert len(content["learn"]["grounding_sources"]) >= 2
    assert all("git-scm.com" in source["url"] for source in content["learn"]["grounding_sources"])
    assert content["locales"]["ar"]["learn"]["title"] == "الـ Remotes والتعاون"
    assert "remote" in content["locales"]["ar"]["learn"]["explanation"]
    assert "does not run these commands" in content["learn"]["version_note"]
    # The evaluation note is honest: the review never contacts a remote or
    # performs any network Git operation.
    assert "does not run these commands or contact any remote" in content["practice"]["evaluation_note"]
    assert content["practice"]["language"] == "bash"
    assert all(question["competency"] == "Remotes & collaboration" for question in content["mini_check"]["questions"])
    assert not any("correct_answer" in question.get("misconception_hint", "") for question in content["mini_check"]["questions"])
    answers = [question["correct_answer"] for question in content["mini_check"]["questions"]]
    assert lessons.score_mini_check(content["mini_check"]["questions"], answers) == (3, 3, True)


def test_git_history_rewriting_is_a_complete_bilingual_lesson_with_rebasing_prerequisite_and_honest_rewrite_note():
    topic = knowledge_base.complete_lesson("Git", "git_history_rewriting")
    assert topic and topic["status"] == "complete"
    assert topic["competency"] == "History rewriting"
    assert topic["prerequisites"][0]["competency"] == "Rebasing"
    assert topic["prerequisites"][0]["relationship"] == "required foundation"
    assert "roadmap" in topic["roadmap_rationale"].lower()

    content = lessons.generate_lesson("Git", "History rewriting", "learn")
    assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
    assert "git commit --amend" in content["example"]["content"]
    assert "git rebase -i main" in content["example"]["content"]
    assert "git log" in content["example"]["content"]
    assert "local" in content["learn"]["explanation"].lower()
    assert "published" in content["learn"]["explanation"].lower()
    assert len(content["learn"]["grounding_sources"]) >= 2
    assert all("git-scm.com" in source["url"] for source in content["learn"]["grounding_sources"])
    assert content["locales"]["ar"]["learn"]["title"] == "إعادة كتابة التاريخ"
    assert "إعادة كتابة" in content["locales"]["ar"]["learn"]["explanation"]
    assert "does not run these commands" in content["learn"]["version_note"]
    # The evaluation note is honest: the review never rewrites any repository's
    # history, so it cannot prove any history was rewritten.
    assert "or rewrite any repository's history" in content["practice"]["evaluation_note"]
    assert "cannot prove any history was rewritten" in content["practice"]["evaluation_note"]
    assert content["practice"]["language"] == "bash"
    assert all(question["competency"] == "History rewriting" for question in content["mini_check"]["questions"])
    assert not any("correct_answer" in question.get("misconception_hint", "") for question in content["mini_check"]["questions"])
    answers = [question["correct_answer"] for question in content["mini_check"]["questions"]]
    assert lessons.score_mini_check(content["mini_check"]["questions"], answers) == (3, 3, True)


def test_git_bisect_debugging_is_a_complete_bilingual_lesson_with_committing_prerequisite_and_honest_bisect_note():
    topic = knowledge_base.complete_lesson("Git", "git_bisect_debugging")
    assert topic and topic["status"] == "complete"
    assert topic["competency"] == "Bisect & debugging"
    assert topic["prerequisites"][0]["competency"] == "Committing"
    assert topic["prerequisites"][0]["relationship"] == "required foundation"
    assert "roadmap" in topic["roadmap_rationale"].lower()

    content = lessons.generate_lesson("Git", "Bisect & debugging", "learn")
    assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
    assert "git bisect start" in content["example"]["content"]
    assert "git bisect bad" in content["example"]["content"]
    assert "git bisect good v1.2" in content["example"]["content"]
    assert "git bisect reset" in content["example"]["content"]
    assert "regression" in content["learn"]["explanation"].lower()
    assert "first bad" in content["learn"]["explanation"].lower()
    assert len(content["learn"]["grounding_sources"]) >= 2
    assert all("git-scm.com" in source["url"] for source in content["learn"]["grounding_sources"])
    assert content["locales"]["ar"]["learn"]["title"] == "الـ Bisect والتصحيح"
    assert "bisect" in content["locales"]["ar"]["learn"]["explanation"]
    assert "does not run these commands" in content["learn"]["version_note"]
    # The evaluation note is honest: the review never runs a bisect in any
    # repository, so it cannot prove a bisect happened.
    assert "or start a bisect in any repository" in content["practice"]["evaluation_note"]
    assert "cannot prove a bisect happened" in content["practice"]["evaluation_note"]
    assert content["practice"]["language"] == "bash"
    assert all(question["competency"] == "Bisect & debugging" for question in content["mini_check"]["questions"])
    assert not any("correct_answer" in question.get("misconception_hint", "") for question in content["mini_check"]["questions"])
    answers = [question["correct_answer"] for question in content["mini_check"]["questions"]]
    assert lessons.score_mini_check(content["mini_check"]["questions"], answers) == (3, 3, True)


def test_git_submodules_is_a_complete_bilingual_lesson_with_branching_prerequisite_and_honest_boundary():
    topic = knowledge_base.complete_lesson("Git", "git_submodules")
    assert topic and topic["status"] == "complete"
    assert topic["competency"] == "Submodules"
    assert topic["prerequisites"][0]["competency"] == "Branching"
    assert topic["prerequisites"][0]["relationship"] == "required foundation"
    assert "roadmap" in topic["roadmap_rationale"].lower()

    content = lessons.generate_lesson("Git", "Submodules", "learn")
    assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
    assert "git clone https://example.com/team/library" in content["example"]["content"]
    assert "git submodule init" in content["example"]["content"]
    assert "git submodule update" in content["example"]["content"]
    assert "pinned" in content["learn"]["explanation"].lower()
    assert len(content["learn"]["grounding_sources"]) >= 2
    assert all(("git-scm.com" in source["url"] or "git-lfs.com" in source["url"])
               for source in content["learn"]["grounding_sources"])
    assert content["locales"]["ar"]["learn"]["title"] == "الـ Submodules"
    assert "submodule" in content["locales"]["ar"]["learn"]["explanation"].lower()
    assert "does not run these commands" in content["learn"]["version_note"]
    # The evaluation note is honest: the review never clones, initializes,
    # updates, or modifies any repository's submodules.
    assert "modify any repository's submodules" in content["practice"]["evaluation_note"]
    assert "cannot prove any submodule was added" in content["practice"]["evaluation_note"]
    assert content["practice"]["language"] == "bash"
    assert all(question["competency"] == "Submodules" for question in content["mini_check"]["questions"])
    assert not any("correct_answer" in question.get("misconception_hint", "") for question in content["mini_check"]["questions"])
    answers = [question["correct_answer"] for question in content["mini_check"]["questions"]]
    assert lessons.score_mini_check(content["mini_check"]["questions"], answers) == (3, 3, True)


def test_git_workflows_policy_is_a_complete_bilingual_lesson_with_rebasing_prerequisite_and_honest_policy_boundary():
    topic = knowledge_base.complete_lesson("Git", "git_workflows_&_policy")
    assert topic and topic["status"] == "complete"
    assert topic["competency"] == "Workflows & policy"
    assert topic["prerequisites"][0]["competency"] == "Rebasing"
    assert topic["prerequisites"][0]["relationship"] == "required foundation"
    assert "roadmap" in topic["roadmap_rationale"].lower()

    content = lessons.generate_lesson("Git", "Workflows & policy", "learn")
    assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
    assert "git switch -c feature-login" in content["example"]["content"]
    assert "git push origin feature-login" in content["example"]["content"]
    assert "git merge feature-login" in content["example"]["content"]
    assert "Pull Request" in content["learn"]["explanation"]
    assert "protected" in content["learn"]["explanation"].lower()
    assert len(content["learn"]["grounding_sources"]) >= 2
    assert all("git-scm.com" in source["url"] for source in content["learn"]["grounding_sources"])
    assert content["locales"]["ar"]["learn"]["title"] == "الـ Workflows والسياسات"
    assert "Pull Request" in content["locales"]["ar"]["learn"]["explanation"]
    assert "does not run these commands" in content["learn"]["version_note"]
    # The evaluation note is honest: the review never pushes, creates a Pull
    # Request, or configures any repository policy.
    assert "does not run these commands" in content["practice"]["evaluation_note"]
    assert "cannot prove any branch was pushed or any policy was configured" in content["practice"]["evaluation_note"]
    assert content["practice"]["language"] == "bash"
    assert all(question["competency"] == "Workflows & policy" for question in content["mini_check"]["questions"])
    assert not any("correct_answer" in question.get("misconception_hint", "") for question in content["mini_check"]["questions"])
    answers = [question["correct_answer"] for question in content["mini_check"]["questions"]]
    assert lessons.score_mini_check(content["mini_check"]["questions"], answers) == (3, 3, True)


def test_git_large_repo_strategies_is_a_complete_bilingual_lesson_with_dual_prerequisite_and_honest_measurement_boundary():
    topic = knowledge_base.complete_lesson("Git", "git_large-repo_strategies")
    assert topic and topic["status"] == "complete"
    assert topic["competency"] == "Large-repo strategies"
    prereqs = [p["competency"] for p in topic["prerequisites"]]
    assert "History rewriting" in prereqs
    assert "Bisect & debugging" in prereqs
    assert all(p["relationship"] == "required foundation" for p in topic["prerequisites"])
    assert "roadmap" in topic["roadmap_rationale"].lower()

    content = lessons.generate_lesson("Git", "Large-repo strategies", "learn")
    assert content["canonical"]["source"] == "trusted_cs_knowledge_base"
    assert "git clone --depth 1" in content["example"]["content"]
    assert "git clone --filter=blob:none" in content["example"]["content"]
    assert "git sparse-checkout set src tests" in content["example"]["content"]
    assert "git lfs install" in content["example"]["content"]
    assert "shallow" in content["learn"]["explanation"].lower()
    assert len(content["learn"]["grounding_sources"]) >= 2
    assert all(("git-scm.com" in source["url"] or "git-lfs.com" in source["url"])
               for source in content["learn"]["grounding_sources"])
    assert content["locales"]["ar"]["learn"]["title"] == "استراتيجيات المستودعات الضخمة"
    assert "shallow" in content["locales"]["ar"]["learn"]["explanation"].lower()
    assert "does not run these commands" in content["learn"]["version_note"]
    # The evaluation note is honest: the review never runs the strategies or
    # measures any performance improvement.
    assert "does not run these commands" in content["practice"]["evaluation_note"]
    assert "cannot prove any performance improvement" in content["practice"]["evaluation_note"]
    assert content["practice"]["language"] == "bash"
    assert all(question["competency"] == "Large-repo strategies" for question in content["mini_check"]["questions"])
    assert not any("correct_answer" in question.get("misconception_hint", "") for question in content["mini_check"]["questions"])
    answers = [question["correct_answer"] for question in content["mini_check"]["questions"]]
    assert lessons.score_mini_check(content["mini_check"]["questions"], answers) == (3, 3, True)


def test_git_static_reviews_never_execute_and_require_the_requested_command_shapes():
    local_lesson = {"content": lessons.generate_lesson("Git", "Local repositories", "learn")}
    good = practice.git_local_repositories_static_check(local_lesson, LOCAL_ANSWER)
    assert good["kind"] == "git_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not run these commands" in good["note"]

    commit_lesson = {"content": lessons.generate_lesson("Git", "Committing", "learn")}
    good = practice.git_committing_static_check(commit_lesson, COMMIT_ANSWER)
    assert good["kind"] == "git_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not run these commands" in good["note"]

    branch_lesson = {"content": lessons.generate_lesson("Git", "Branching", "learn")}
    good = practice.git_branching_static_check(branch_lesson, BRANCH_ANSWER)
    assert good["kind"] == "git_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not run these commands" in good["note"]

    merge_lesson = {"content": lessons.generate_lesson("Git", "Merging", "learn")}
    good = practice.git_merging_static_check(merge_lesson, MERGE_ANSWER)
    assert good["kind"] == "git_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not run these commands" in good["note"]

    rebase_lesson = {"content": lessons.generate_lesson("Git", "Rebasing", "learn")}
    good = practice.git_rebasing_static_check(rebase_lesson, REBASE_ANSWER)
    assert good["kind"] == "git_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not run these commands" in good["note"]
    assert "rewrite any repository's history" in good["note"]

    remotes_lesson = {"content": lessons.generate_lesson("Git", "Remotes & collaboration", "learn")}
    good = practice.git_remotes_collaboration_static_check(remotes_lesson, REMOTES_ANSWER)
    assert good["kind"] == "git_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not run these commands or contact any remote" in good["note"]

    history_lesson = {"content": lessons.generate_lesson("Git", "History rewriting", "learn")}
    good = practice.git_history_rewriting_static_check(history_lesson, HISTORY_ANSWER)
    assert good["kind"] == "git_text"
    assert good["status"] == "looks_structurally_sound"
    assert "never amends, rebases, or rewrites" in good["note"].lower() or "did not run" in good["note"]
    assert "cannot prove any history was rewritten" in good["note"]

    bisect_lesson = {"content": lessons.generate_lesson("Git", "Bisect & debugging", "learn")}
    good = practice.git_bisect_debugging_static_check(bisect_lesson, BISECT_ANSWER)
    assert good["kind"] == "git_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not run" in good["note"]
    assert "cannot prove a bisect happened" in good["note"]

    # Missing pieces surface as targeted needs_fix guidance.
    local_bad, expected = "git init", "cd my-project"
    assert practice.git_local_repositories_static_check(local_lesson, local_bad)["status"] == "needs_fix"
    assert any(expected in c for c in practice.git_local_repositories_static_check(local_lesson, local_bad)["checks"])
    commit_bad = 'git add README.md\ngit commit'
    result = practice.git_committing_static_check(commit_lesson, commit_bad)
    assert result["status"] == "needs_fix"
    assert any("-m" in c for c in result["checks"])
    no_boundary = practice.git_committing_static_check(
        commit_lesson, "git add README.md\ngit commit -m \"Add the project README\"\ngit log")
    assert no_boundary["status"] == "needs_fix"
    assert any("written answer" in c for c in no_boundary["checks"])

    # Branching without switching or inspecting is not accepted as complete.
    branch_bad = "git branch feature-payment\nThis created the branch."
    result = practice.git_branching_static_check(branch_lesson, branch_bad)
    assert result["status"] == "needs_fix"
    assert any("git switch" in c for c in practice.git_branching_static_check(branch_lesson, branch_bad)["checks"])

    # Merging never runs or overwrites: missing conflict note AND boundary fail.
    merge_bad = "git switch main\ngit merge feature-payment"
    result = practice.git_merging_static_check(merge_lesson, merge_bad)
    assert result["status"] == "needs_fix"
    assert any("conflict" in c for c in result["checks"])
    merge_no_boundary = MERGE_ANSWER.replace(
        "This is a written answer: SkillBridge does not run the merge or change any repository.", "")
    assert practice.git_merging_static_check(merge_lesson, merge_no_boundary)["status"] == "needs_fix"

    # Rebasing without switching or the safety note is not accepted as complete.
    rebase_bad = "git rebase main"
    result = practice.git_rebasing_static_check(rebase_lesson, rebase_bad)
    assert result["status"] == "needs_fix"
    assert any("git switch" in c for c in result["checks"])
    assert any("never rebase" in c or "differs from merge" in c for c in result["checks"])
    rebase_no_boundary = REBASE_ANSWER.replace(
        "This is a written answer: SkillBridge does not run the rebase or rewrite any repository's history.", "")
    assert practice.git_rebasing_static_check(rebase_lesson, rebase_no_boundary)["status"] == "needs_fix"

    # Remotes without pull/push or the review note is not accepted as complete.
    remotes_bad = "git fetch origin"
    result = practice.git_remotes_collaboration_static_check(remotes_lesson, remotes_bad)
    assert result["status"] == "needs_fix"
    assert any("git push" in c for c in result["checks"])
    assert any("Pull Request" in c for c in result["checks"])
    remotes_no_boundary = REMOTES_ANSWER.replace(
        "This is a written answer: SkillBridge does not run these commands or contact any remote.", "")
    assert practice.git_remotes_collaboration_static_check(remotes_lesson, remotes_no_boundary)["status"] == "needs_fix"

    # History rewriting without the rebase/main, the log, or the safety note is
    # not accepted as complete.
    history_bad = "git commit --amend"
    result = practice.git_history_rewriting_static_check(history_lesson, history_bad)
    assert result["status"] == "needs_fix"
    assert any("git rebase -i" in c for c in result["checks"])
    assert any("git log" in c for c in result["checks"])
    history_no_boundary = HISTORY_ANSWER.replace(
        "This is a written answer: SkillBridge does not run these commands or rewrite any repository's history.", "")
    assert practice.git_history_rewriting_static_check(history_lesson, history_no_boundary)["status"] == "needs_fix"

    # Bisect without the good/reset markers or the safety note is not accepted
    # as complete.
    bisect_bad = "git bisect start"
    result = practice.git_bisect_debugging_static_check(bisect_lesson, bisect_bad)
    assert result["status"] == "needs_fix"
    assert any("git bisect good" in c for c in result["checks"])
    assert any("git bisect reset" in c for c in result["checks"])
    bisect_no_boundary = BISECT_ANSWER.replace(
        "This is a written answer: SkillBridge does not run these commands or start a bisect in any repository.", "")
    assert practice.git_bisect_debugging_static_check(bisect_lesson, bisect_no_boundary)["status"] == "needs_fix"

    submodules_lesson = {"content": lessons.generate_lesson("Git", "Submodules", "learn")}
    good = practice.git_submodules_static_check(submodules_lesson, SUBMODULES_ANSWER)
    assert good["kind"] == "git_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not run these commands" in good["note"]
    assert "cannot prove any submodule was added" in good["note"]

    workflows_lesson = {"content": lessons.generate_lesson("Git", "Workflows & policy", "learn")}
    good = practice.git_workflows_policy_static_check(workflows_lesson, WORKFLOWS_ANSWER)
    assert good["kind"] == "git_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not run these commands" in good["note"]

    large_repo_lesson = {"content": lessons.generate_lesson("Git", "Large-repo strategies", "learn")}
    good = practice.git_large_repo_strategies_static_check(large_repo_lesson, LARGE_REPO_ANSWER)
    assert good["kind"] == "git_text"
    assert good["status"] == "looks_structurally_sound"
    assert "did not run these commands" in good["note"]
    assert "cannot prove any performance improvement" in good["note"]

    # Submodules need init AND update AND the pinned-commit/boundary notes.
    submodules_bad = "git clone https://example.com/team/library"
    result = practice.git_submodules_static_check(submodules_lesson, submodules_bad)
    assert result["status"] == "needs_fix"
    assert any("git submodule init" in c for c in result["checks"])
    assert any("git submodule update" in c for c in result["checks"])
    submodules_no_boundary = SUBMODULES_ANSWER.replace(
        "This is a written answer: SkillBridge does not run these commands or modify any repository's submodules.", "")
    assert practice.git_submodules_static_check(submodules_lesson, submodules_no_boundary)["status"] == "needs_fix"

    # Workflows need the branch create, a push, a merge/PR, and a policy note.
    workflows_bad = "git switch -c feature-login"
    result = practice.git_workflows_policy_static_check(workflows_lesson, workflows_bad)
    assert result["status"] == "needs_fix"
    assert any("git push" in c for c in result["checks"])
    assert any("merge" in c for c in result["checks"])
    workflows_no_boundary = WORKFLOWS_ANSWER.replace(
        "This is a written answer: SkillBridge does not run these commands or configure any repository policy.", "")
    assert practice.git_workflows_policy_static_check(workflows_lesson, workflows_no_boundary)["status"] == "needs_fix"

    # Large-repo strategies need a shallow clone, a partial clone, a sparse
    # checkout, LFS, and a trade-offs note.
    large_repo_bad = "git clone --depth 1 https://example.com/big-project"
    result = practice.git_large_repo_strategies_static_check(large_repo_lesson, large_repo_bad)
    assert result["status"] == "needs_fix"
    assert any("--filter" in c for c in result["checks"])
    assert any("sparse-checkout" in c for c in result["checks"])
    assert any("git lfs" in c for c in result["checks"])
    large_repo_no_boundary = LARGE_REPO_ANSWER.replace(
        "This is a written answer: SkillBridge does not run these commands or measure any performance improvement.", "")
    assert practice.git_large_repo_strategies_static_check(large_repo_lesson, large_repo_no_boundary)["status"] == "needs_fix"


def test_git_static_reviews_are_scoped_to_their_own_lesson():
    local_lesson = {"content": lessons.generate_lesson("Git", "Local repositories", "learn")}
    commit_lesson = {"content": lessons.generate_lesson("Git", "Committing", "learn")}
    branch_lesson = {"content": lessons.generate_lesson("Git", "Branching", "learn")}
    merge_lesson = {"content": lessons.generate_lesson("Git", "Merging", "learn")}
    rebase_lesson = {"content": lessons.generate_lesson("Git", "Rebasing", "learn")}
    remotes_lesson = {"content": lessons.generate_lesson("Git", "Remotes & collaboration", "learn")}
    history_lesson = {"content": lessons.generate_lesson("Git", "History rewriting", "learn")}
    bisect_lesson = {"content": lessons.generate_lesson("Git", "Bisect & debugging", "learn")}
    submodules_lesson = {"content": lessons.generate_lesson("Git", "Submodules", "learn")}
    workflows_lesson = {"content": lessons.generate_lesson("Git", "Workflows & policy", "learn")}
    large_repo_lesson = {"content": lessons.generate_lesson("Git", "Large-repo strategies", "learn")}
    sql_lesson = {"content": lessons.generate_lesson("SQL", "Queries & filtering", "learn")}
    assert practice.git_local_repositories_static_check(commit_lesson, LOCAL_ANSWER) is None
    assert practice.git_committing_static_check(local_lesson, COMMIT_ANSWER) is None
    assert practice.git_branching_static_check(commit_lesson, BRANCH_ANSWER) is None
    assert practice.git_branching_static_check(local_lesson, BRANCH_ANSWER) is None
    assert practice.git_branching_static_check(sql_lesson, BRANCH_ANSWER) is None
    assert practice.git_merging_static_check(branch_lesson, MERGE_ANSWER) is None
    assert practice.git_merging_static_check(commit_lesson, MERGE_ANSWER) is None
    assert practice.git_merging_static_check(sql_lesson, MERGE_ANSWER) is None
    assert practice.git_rebasing_static_check(merge_lesson, REBASE_ANSWER) is None
    assert practice.git_rebasing_static_check(remotes_lesson, REBASE_ANSWER) is None
    assert practice.git_rebasing_static_check(sql_lesson, REBASE_ANSWER) is None
    assert practice.git_remotes_collaboration_static_check(rebase_lesson, REMOTES_ANSWER) is None
    assert practice.git_remotes_collaboration_static_check(merge_lesson, REMOTES_ANSWER) is None
    assert practice.git_remotes_collaboration_static_check(sql_lesson, REMOTES_ANSWER) is None
    assert practice.git_history_rewriting_static_check(bisect_lesson, HISTORY_ANSWER) is None
    assert practice.git_history_rewriting_static_check(rebase_lesson, HISTORY_ANSWER) is None
    assert practice.git_history_rewriting_static_check(sql_lesson, HISTORY_ANSWER) is None
    assert practice.git_bisect_debugging_static_check(history_lesson, BISECT_ANSWER) is None
    assert practice.git_bisect_debugging_static_check(commit_lesson, BISECT_ANSWER) is None
    assert practice.git_bisect_debugging_static_check(sql_lesson, BISECT_ANSWER) is None
    assert practice.git_submodules_static_check(bisect_lesson, SUBMODULES_ANSWER) is None
    assert practice.git_submodules_static_check(commit_lesson, SUBMODULES_ANSWER) is None
    assert practice.git_submodules_static_check(sql_lesson, SUBMODULES_ANSWER) is None
    assert practice.git_workflows_policy_static_check(submodules_lesson, WORKFLOWS_ANSWER) is None
    assert practice.git_workflows_policy_static_check(bisect_lesson, WORKFLOWS_ANSWER) is None
    assert practice.git_workflows_policy_static_check(sql_lesson, WORKFLOWS_ANSWER) is None
    assert practice.git_large_repo_strategies_static_check(workflows_lesson, LARGE_REPO_ANSWER) is None
    assert practice.git_large_repo_strategies_static_check(bisect_lesson, LARGE_REPO_ANSWER) is None
    assert practice.git_large_repo_strategies_static_check(sql_lesson, LARGE_REPO_ANSWER) is None
    assert practice.git_local_repositories_static_check(sql_lesson, LOCAL_ANSWER) is None
    assert practice.git_committing_static_check(sql_lesson, COMMIT_ANSWER) is None


def _git_skill():
    return models.get_skill_by_name("Git") or models.create_skill("Git", "DevOps")


def test_git_diagnostic_practice_mini_check_persist_without_verifying_skill(client, student_id, auth_headers):
    headers = auth_headers("aisha@student.edu")
    git = _git_skill()
    before = {(row["name"], row["level"]) for row in models.get_student(student_id).get("verified_skills") or []}

    generated = client.post(
        f"/api/students/{student_id}/learning/{git['id']}/diagnostic/generate",
        json={}, headers=headers)
    assert generated.status_code == 200, generated.text
    diagnostic = generated.json()
    # All eleven curated Git topics contribute 3 reviewed bank questions each.
    assert len(diagnostic["questions"]) == 33
    assert {question["competency"] for question in diagnostic["questions"]} == set(GIT_CANONICAL_ORDER)
    for name in GIT_CANONICAL_ORDER:
        assert sum(q["competency"] == name for q in diagnostic["questions"]) == 3
    assert all(question["options"] and question["correct_answer"] for question in diagnostic["questions"])

    submitted = client.post(
        f"/api/students/{student_id}/learning/{git['id']}/diagnostic/submit",
        json={"diagnostic_id": diagnostic["diagnostic_id"], "answers": ["not this" for _ in diagnostic["questions"]]},
        headers=headers)
    assert submitted.status_code == 200, submitted.text
    path = client.post(
        f"/api/students/{student_id}/learning/{git['id']}/personalized-path/generate",
        json={}, headers=headers).json()
    # Canonical blueprint order for all eleven curated topics (Local repositories
    # first ... Bisect & debugging, Submodules, Workflows & policy, Large-repo
    # strategies last).
    competencies = [item["competency"] for item in path["items"]]
    assert competencies == GIT_CANONICAL_ORDER
    local_item = next(item for item in path["items"] if item["competency"] == "git_local_repositories")

    base = f"/api/students/{student_id}/learning/{git['id']}/lessons/{quote('git_local_repositories', safe='')}"
    lesson_response = client.post(base + "/generate", json={}, headers=headers)
    assert lesson_response.status_code == 200, lesson_response.text
    lesson = lesson_response.json()
    assert lesson["content"]["canonical"]["source"] == "trusted_cs_knowledge_base"

    attempt = client.post(base + "/practice", json={"answer": LOCAL_ANSWER}, headers=headers)
    assert attempt.status_code == 200, attempt.text
    assert attempt.json()["attempt"]["competency"] == "git_local_repositories"

    questions = lesson["content"]["mini_check"]["questions"]
    completed = client.post(base + "/mini-check", json={"answers": [q["correct_answer"] for q in questions]}, headers=headers)
    assert completed.status_code == 200, completed.text
    assert completed.json()["lesson"]["state"] == "completed"

    # The Intermediate topic (Merging) is served and persists too.
    merge_base = f"/api/students/{student_id}/learning/{git['id']}/lessons/{quote('git_merging', safe='')}"
    merge_lesson = client.post(merge_base + "/generate", json={}, headers=headers)
    assert merge_lesson.status_code == 200, merge_lesson.text
    assert merge_lesson.json()["content"]["canonical"]["source"] == "trusted_cs_knowledge_base"
    merge_attempt = client.post(merge_base + "/practice", json={"answer": MERGE_ANSWER}, headers=headers)
    assert merge_attempt.status_code == 200, merge_attempt.text
    assert merge_attempt.json()["attempt"]["competency"] == "git_merging"
    merge_questions = merge_lesson.json()["content"]["mini_check"]["questions"]
    merge_done = client.post(merge_base + "/mini-check", json={"answers": [q["correct_answer"] for q in merge_questions]}, headers=headers)
    assert merge_done.status_code == 200, merge_done.text
    assert merge_done.json()["lesson"]["state"] == "completed"

    # The batch-4 Intermediate topic (History rewriting) is served and persists too.
    history_base = f"/api/students/{student_id}/learning/{git['id']}/lessons/{quote('git_history_rewriting', safe='')}"
    history_lesson = client.post(history_base + "/generate", json={}, headers=headers)
    assert history_lesson.status_code == 200, history_lesson.text
    assert history_lesson.json()["content"]["canonical"]["source"] == "trusted_cs_knowledge_base"
    history_attempt = client.post(history_base + "/practice", json={"answer": HISTORY_ANSWER}, headers=headers)
    assert history_attempt.status_code == 200, history_attempt.text
    assert history_attempt.json()["attempt"]["competency"] == "git_history_rewriting"
    history_questions = history_lesson.json()["content"]["mini_check"]["questions"]
    history_done = client.post(history_base + "/mini-check", json={"answers": [q["correct_answer"] for q in history_questions]}, headers=headers)
    assert history_done.status_code == 200, history_done.text
    assert history_done.json()["lesson"]["state"] == "completed"

    # The batch-5 Advanced topic (Submodules) is served and persists too.
    submodules_base = f"/api/students/{student_id}/learning/{git['id']}/lessons/{quote('git_submodules', safe='')}"
    submodules_lesson = client.post(submodules_base + "/generate", json={}, headers=headers)
    assert submodules_lesson.status_code == 200, submodules_lesson.text
    assert submodules_lesson.json()["content"]["canonical"]["source"] == "trusted_cs_knowledge_base"
    submodules_attempt = client.post(submodules_base + "/practice", json={"answer": SUBMODULES_ANSWER}, headers=headers)
    assert submodules_attempt.status_code == 200, submodules_attempt.text
    assert submodules_attempt.json()["attempt"]["competency"] == "git_submodules"
    submodules_questions = submodules_lesson.json()["content"]["mini_check"]["questions"]
    submodules_done = client.post(submodules_base + "/mini-check", json={"answers": [q["correct_answer"] for q in submodules_questions]}, headers=headers)
    assert submodules_done.status_code == 200, submodules_done.text
    assert submodules_done.json()["lesson"]["state"] == "completed"

    persisted = client.get(
        f"/api/students/{student_id}/learning/{git['id']}/personalized-path", headers=headers).json()
    # The topics actually attempted now persist on the path.
    assert local_item["id"] in persisted["progress"]
    merge_item = next(item for item in path["items"] if item["competency"] == "git_merging")
    assert merge_item["id"] in persisted["progress"]
    history_item = next(item for item in path["items"] if item["competency"] == "git_history_rewriting")
    assert history_item["id"] in persisted["progress"]
    submodules_item = next(item for item in path["items"] if item["competency"] == "git_submodules")
    assert submodules_item["id"] in persisted["progress"]
    # Mini Checks and practice never verify the skill.
    assert {(row["name"], row["level"]) for row in models.get_student(student_id).get("verified_skills") or []} == before
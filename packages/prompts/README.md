# StudyMateAI Prompts Package

This Python library contains system prompt configurations, educational instructions, and templates for StudyMateAI agents. Decoupling prompts into a dedicated package ensures consistent behavior across CLI, testing, and production runtime environments.

## ✍️ Available System Prompts

- **`physics_sme.md`**: Directives for Physics tutoring, focusing on clear conceptual breakdowns, problem-solving techniques, and KCET/NEET exam strategies.
- **`chemistry_sme.md`**: Directives for Chemistry tutoring, including chemical formula and equation formatting guidelines.
- **`quiz_generator.md`**: Instructions for outputting highly-aligned, curriculum-bounded multiple choice questions.
- **`evaluator.md`**: Directives for grading student answers, extracting errors, and formulating student revision tips.
- **`evaluator_review.md`**: Quality assessment guidelines for the Teacher Review workflow to validate correctness and safety before serving content.
- **`rag_agent.md`**: System constraints for textbook query processing and source formatting.
- **`global_system.md`**: Shared academic rules, tone specifications (teacher-like, exam-focused), and guardrails.

## 🚀 Usage

Install in editable mode for backend use:
```bash
# Install package from the root directory
pip install -e packages/prompts
```

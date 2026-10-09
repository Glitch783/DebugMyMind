from dataclasses import dataclass, field
from app.pipeline.ast_parser import analyze_ast
from app.pipeline.executor import execute_code
from app.pipeline.embedder import get_embedder
from app.pipeline.llm_analyser import analyze_misconception_with_llm

@dataclass
class AnalysisResult:
    misconception_id: str
    misconception_name: str
    confidence: float
    explanation: str
    micro_exercise: str
    error_trace: str
    ast_flags: list[str] = field(default_factory=list)

def analyze_student_submission(code: str) -> AnalysisResult:
    """
    Orchestrates the analysis pipeline:
    1. Runs the AST parser to detect static anti-patterns.
    2. Runs the executor to check for runtime errors/timeouts.
    3. Matches the submission to a misconception in the taxonomy (with AST override).
    4. Calls the LLM to get a customized explanation and micro-exercise.
    """
    # 1. Run static analysis
    ast_flags = analyze_ast(code)

    # 2. Run code execution
    exec_res = execute_code(code)
    error_type = exec_res["error_type"]
    error_msg = exec_res["error_message"]
    error_trace = exec_res["traceback"]

    # 3. Embedder & Taxonomy matching
    embedder_instance = get_embedder()
    
    matched_id = None
    misconception_name = "Unknown Misconception"
    misconception_desc = "No matching explanation available."
    example_fix = "# No fix available."
    confidence = 0.1

    # Check AST static analysis overrides (high-certainty matches)
    for flag in ast_flags:
        for entry in embedder_instance.taxonomy:
            if entry["id"] == flag:
                matched_id = entry["id"]
                misconception_name = entry["name"]
                misconception_desc = entry["description"]
                example_fix = entry["example_fix"]
                confidence = 0.95
                break
        if matched_id:
            break

    # If no AST override was triggered, search using embeddings similarity
    if not matched_id:
        matches = embedder_instance.find_top_matches(
            code=code,
            error_msg=error_msg or "",
            error_type=error_type or "",
            ast_flags=ast_flags,
            top_k=3
        )
        if matches:
            top_match = matches[0]
            matched_id = top_match["id"]
            misconception_name = top_match["name"]
            misconception_desc = top_match["description"]
            example_fix = top_match["example_fix"]
            confidence = top_match["confidence"]

    # 4. Generate explanation and micro-exercise using LLM or Fallback
    llm_res = analyze_misconception_with_llm(
        code=code,
        error=error_trace or f"{error_type}: {error_msg}" if error_type else "",
        misconception_name=misconception_name,
        misconception_description=misconception_desc,
        example_fix=example_fix
    )

    return AnalysisResult(
        misconception_id=matched_id or "unknown",
        misconception_name=misconception_name,
        confidence=confidence,
        explanation=llm_res.get("explanation", ""),
        micro_exercise=llm_res.get("micro_exercise", ""),
        error_trace=error_trace or "",
        ast_flags=ast_flags
    )

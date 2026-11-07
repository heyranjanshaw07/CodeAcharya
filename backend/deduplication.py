import re
import difflib
from typing import List, Optional, Tuple, Set, Dict, Any

STOP_WORDS: Set[str] = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of", "with", "by",
    "is", "are", "was", "were", "be", "been", "that", "this", "these", "those",
    "given", "write", "function", "return", "find", "determine", "calculate", "compute",
    "solve", "implement", "problem", "solution", "array", "string", "input", "output"
}

def normalize_text(text: str) -> str:
    """Normalize text by lowercasing, stripping punctuation, and removing extraneous spaces."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = [w for w in text.split() if w and w not in STOP_WORDS]
    return " ".join(tokens)

def compute_token_jaccard(str1: str, str2: str) -> float:
    """Compute Jaccard similarity over word tokens."""
    tokens1 = set(normalize_text(str1).split())
    tokens2 = set(normalize_text(str2).split())
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)

def compute_string_similarity(str1: str, str2: str) -> float:
    """Computes hybrid similarity combining token Jaccard and character sequence ratio."""
    norm1 = normalize_text(str1)
    norm2 = normalize_text(str2)
    if not norm1 or not norm2:
        return 0.0
    if norm1 == norm2:
        return 1.0

    jaccard = compute_token_jaccard(str1, str2)
    seq_ratio = difflib.SequenceMatcher(None, norm1, norm2).ratio()
    return max(jaccard, seq_ratio)

def is_duplicate_problem(
    candidate: Dict[str, Any],
    existing_titles: List[str],
    existing_ids: Optional[List[str]] = None,
    existing_descriptions: Optional[List[str]] = None,
    title_threshold: float = 0.75,
    desc_threshold: float = 0.85
) -> Tuple[bool, str]:
    """
    Evaluates whether candidate problem is a duplicate of previously seen or stored problems.
    Returns (is_duplicate: bool, reason: str).
    """
    cand_id = (candidate.get("id") or "").strip().lower()
    cand_title = (candidate.get("title") or "").strip()
    cand_desc = (candidate.get("description") or "").strip()

    # 1. Exact ID check
    existing_ids_set = {i.strip().lower() for i in (existing_ids or []) if i}
    if cand_id and cand_id in existing_ids_set:
        return True, f"Exact ID match '{cand_id}'"

    # 2. Title checks
    cand_norm_title = normalize_text(cand_title)
    for title in existing_titles:
        if not title:
            continue
        # Exact title match
        if cand_title.lower() == title.strip().lower():
            return True, f"Exact title match with '{title}'"

        # Normalized title match
        norm_t = normalize_text(title)
        if cand_norm_title and norm_t and cand_norm_title == norm_t:
            return True, f"Normalized title match with '{title}'"

        # Fuzzy title similarity
        sim = compute_string_similarity(cand_title, title)
        if sim >= title_threshold:
            return True, f"High title similarity ({sim:.2f}) with '{title}'"

    # 3. Description similarity check (to catch identical problems with rephrased titles)
    if cand_desc and existing_descriptions:
        for desc in existing_descriptions:
            if not desc:
                continue
            desc_sim = compute_token_jaccard(cand_desc, desc)
            if desc_sim >= desc_threshold:
                return True, f"High problem description similarity ({desc_sim:.2f})"

    return False, "Unique"

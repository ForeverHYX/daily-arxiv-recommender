"""Domain filtering and rule-based scoring for architecture paper candidates."""

from __future__ import annotations

from dataclasses import dataclass, field
import re


CORE_CATEGORIES = frozenset({"cs.AR", "cs.PF", "cs.DC", "cs.PL"})
EXPANSION_CATEGORIES = frozenset({"cs.AI", "cs.LG"})


@dataclass(frozen=True)
class Paper:
    paper_id: str
    title: str
    abstract: str
    authors: list[str]
    categories: list[str]


@dataclass(frozen=True)
class Classification:
    paper: Paper
    accepted: bool
    score: float
    sections: tuple[str, ...] = field(default_factory=tuple)
    positive_matches: tuple[str, ...] = field(default_factory=tuple)
    negative_matches: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SectionRule:
    name: str
    weight: float
    keywords: tuple[str, ...]


SECTION_RULES = (
    SectionRule(
        name="agentic_architecture",
        weight=4.0,
        keywords=(
            "agentic ai for computer architecture",
            "agentic ai-driven",
            "agentic ai driven",
            "llm-driven architecture",
            "llm driven architecture",
            "architecture idea factory",
            "architecture design space exploration",
            "microarchitecture design space exploration",
            "computer architecture discovery",
            "automated architecture discovery",
            "hardware design agent",
            "simulator-guided design space exploration",
        ),
    ),
    SectionRule(
        name="full_stack_codesign",
        weight=3.5,
        keywords=(
            "software hardware co-design",
            "hardware software co-optimization",
            "full-stack co-design",
            "compiler architecture co-design",
            "isa extension",
            "risc-v custom extension",
            "accelerator compiler",
            "domain-specific accelerator",
            "domain specific accelerator",
            "workload mapping",
            "hardware-aware",
            "mlir",
            "circt",
            "tvm",
            "triton",
            "xla",
        ),
    ),
    SectionRule(
        name="microarchitecture_simulators",
        weight=3.0,
        keywords=(
            "microarchitecture",
            "cache replacement",
            "data prefetcher",
            "branch predictor",
            "cycle-accurate simulation",
            "cycle accurate simulation",
            "cache hierarchy",
            "cache coherence",
            "memory hierarchy",
            "warp scheduling",
            "simt",
            "gem5",
            "champsim",
            "sniper",
            "sst",
            "gpgpu-sim",
            "accel-sim",
            "ramulator",
        ),
    ),
    SectionRule(
        name="hpc_cross_over",
        weight=2.0,
        keywords=(
            "high performance computing",
            "hpc",
            "exascale",
            "mpi",
            "openmp",
            "cuda",
            "rocm",
            "sycl",
            "kokkos",
            "performance portability",
            "roofline",
            "numa",
            "communication-avoiding",
            "sparse linear algebra",
            "memory bandwidth",
            "interconnect",
        ),
    ),
)

GENERIC_AI_AGENT_NOISE = (
    "rag agent",
    "web task",
    "browser task",
    "multi-agent software framework",
    "software framework",
    "retrieval augmented generation",
    "tool use",
)

NAS_NOISE = ("neural architecture search", " nas ")
NAS_RECOVERY_TERMS = (
    "hardware-aware",
    "hardware aware",
    "accelerator",
    "fpga",
    "compiler",
    "co-design",
    "codesign",
    "risc-v",
)


def classify_paper(paper: Paper) -> Classification:
    text = _paper_text(paper)
    positive_matches: list[str] = []
    negative_matches: list[str] = []
    section_scores: dict[str, float] = {}

    for rule in SECTION_RULES:
        matches = _matching_keywords(text, rule.keywords)
        if not matches:
            continue
        section_scores[rule.name] = len(matches) * rule.weight
        positive_matches.extend(f"{rule.name}:{match}" for match in matches)

    score = sum(section_scores.values())

    if _contains_any(text, GENERIC_AI_AGENT_NOISE):
        negative_matches.append("generic-ai-agent-noise")
        score -= 6.0

    if _contains_nas_noise(text) and not _contains_any(text, NAS_RECOVERY_TERMS):
        negative_matches.append("generic-nas-noise")
        score -= 5.0

    categories = set(paper.categories)
    in_core_category = bool(categories & CORE_CATEGORIES)
    in_expansion_category = bool(categories & EXPANSION_CATEGORIES)
    sections = tuple(
        name for name, value in sorted(section_scores.items(), key=lambda item: (-item[1], item[0]))
    )

    accepted = False
    if score > 0 and in_core_category:
        accepted = True
    elif score >= 4.0 and in_expansion_category and "generic-ai-agent-noise" not in negative_matches:
        accepted = True

    return Classification(
        paper=paper,
        accepted=accepted,
        score=score,
        sections=sections,
        positive_matches=tuple(positive_matches),
        negative_matches=tuple(negative_matches),
    )


def rank_papers(papers: list[Paper]) -> list[Classification]:
    accepted = [result for result in (classify_paper(paper) for paper in papers) if result.accepted]
    return sorted(accepted, key=lambda result: (-result.score, result.paper.paper_id))


def _paper_text(paper: Paper) -> str:
    return _normalize(" ".join([paper.title, paper.abstract, " ".join(paper.authors), " ".join(paper.categories)]))


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def _matching_keywords(text: str, keywords: tuple[str, ...]) -> list[str]:
    return [keyword for keyword in keywords if keyword.lower() in text]


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword.lower() in text for keyword in keywords)


def _contains_nas_noise(text: str) -> bool:
    return "neural architecture search" in text or re.search(r"\bnas\b", text) is not None


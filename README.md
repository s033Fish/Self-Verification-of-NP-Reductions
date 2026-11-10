# Self-verification of NP reductions

LLM agents write polynomial-time reductions between NP problems, sometimes
testing their own work. A hidden verifier checks whether each reduction is
actually correct, and we measure how often "the agent says verified" means
"correct".
"""OpenAI-compatible Modal endpoints for the three fixed generation models.

Deploy all three endpoints from the student release directory with:

    uv run modal deploy infrastructure/generation_models.py

Each class runs in its own GPU container and scales to zero independently.
"""

from __future__ import annotations

import modal
import serving

GLM_MODEL = "zai-org/GLM-4.7-Flash"
GLM_ALIAS = "glm-4.7"

MAX_NUM_SEQS = 16

app = modal.App("reductions-models")

# GLM-4.7 support currently requires vLLM and Transformers revisions newer than
# the stable shared image, so pin the exact pair exercised by the live smoke
# test rather than allowing either dependency to drift.
glm_image = (
    modal.Image.from_registry(serving.CUDA, add_python="3.12")
    .entrypoint([])
    .apt_install("git")
    .uv_pip_install(
        "https://wheels.vllm.ai/fcdc7c2e9c9b75c923751ea7d2dd79ef66572c81/"
        "vllm-0.26.1rc1.dev224%2Bgfcdc7c2e9-cp38-abi3-manylinux_2_28_x86_64.whl",
    )
    .uv_pip_install(
        "git+https://github.com/huggingface/transformers.git@4a2e450e601214024c8a37abdaca35df2a4a3ba3"
    )
    .env(serving.ENVIRONMENT)
    .add_local_python_source("serving")
)

@app.cls(
    image=glm_image,
    gpu="H100:1",
    max_containers=1,
    scaledown_window=5 * serving.MINUTES,
    timeout=15 * serving.MINUTES,
    volumes=serving.volumes(),
)
@modal.concurrent(max_inputs=MAX_NUM_SEQS)
class GlmServer:
    @modal.enter()
    def start(self) -> None:
        self.process = serving.start(GLM_MODEL, "glm-4.7", [
            "--tool-call-parser", "glm47",
            "--reasoning-parser", "glm45",
            "--enable-auto-tool-choice",
            "--max-num-seqs", str(MAX_NUM_SEQS),
            "--max-model-len", "32768",
            "--max-num-batched-tokens", "32768",
        ])

    @modal.web_server(port=serving.PORT, startup_timeout=15 * serving.MINUTES,
                      requires_proxy_auth=True)
    def serve(self) -> None:
        pass

    @modal.exit()
    def stop(self) -> None:
        serving.stop(self.process)

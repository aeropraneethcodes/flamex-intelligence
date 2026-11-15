# Optional model-backed language generation

FlameIQ's default **Evidence search · no model** works without any key, account or external network calls. It performs NASA-linked evidence retrieval and deterministic FLEX calculations; this is scientific search and analysis, not general-purpose generative AI.

For eligible use with parental authorization where required by the service, the optional hosted backends are Hugging Face Inference Providers and OpenAI. Each requires private credentials and may have a usage limit or fee. Do not add secrets to a public GitHub repository. The app's research-evidence restrictions remain in place in either case.

Live authentication, quota, provider output quality and production availability have **not** been tested. Provider code is covered only by mocked unit tests.

Hugging Face documentation: https://huggingface.co/docs/inference-providers/tasks/chat-completion
OpenAI API documentation: https://platform.openai.com/docs/overview

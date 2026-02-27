# AUREXIS Models Directory

Place your GGUF model files here.

## Default model: Phi-2

Download from HuggingFace:
```
# Option 1: huggingface-cli
pip install huggingface-hub
huggingface-cli download TheBloke/phi-2-GGUF phi-2.Q4_K_M.gguf --local-dir .

# Option 2: Direct download
wget https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf
```

## Other supported models
Any GGUF model works. Update `config/config.json` → `llm_configs.phi2_local.model_path`

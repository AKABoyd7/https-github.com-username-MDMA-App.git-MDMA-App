"""
Scan G:\Models_Organized for GGUF models and generate models_config.yaml entries
"""
import os
import json
from pathlib import Path
from typing import List, Dict

def scan_gguf_models(base_path: str = r"G:\Models_Organized\lmstudio-community") -> List[Dict]:
    """Scan for GGUF model files"""
    models = []

    base_path = Path(base_path)
    if not base_path.exists():
        print(f"❌ Path not found: {base_path}")
        return models

    print(f"🔍 Scanning: {base_path}\n")

    # Scan each model directory
    for model_dir in sorted(base_path.iterdir()):
        if not model_dir.is_dir():
            continue

        # Find GGUF files
        gguf_files = list(model_dir.rglob("*.gguf"))

        if gguf_files:
            print(f"📁 {model_dir.name}:")

            for gguf_file in sorted(gguf_files):
                # Get file size
                size_bytes = gguf_file.stat().st_size
                size_gb = size_bytes / (1024**3)

                # Determine model type from name
                model_name = gguf_file.stem.lower()

                # Categorize
                if any(x in model_name for x in ['q2', 'q3', 'q4']):
                    quant = 'small'
                elif any(x in model_name for x in ['q5', 'q6']):
                    quant = 'medium'
                elif any(x in model_name for x in ['q8', 'f16', 'f32']):
                    quant = 'large'
                else:
                    quant = 'unknown'

                models.append({
                    'family': model_dir.name,
                    'filename': gguf_file.name,
                    'path': str(gguf_file),
                    'size_gb': round(size_gb, 2),
                    'quantization': quant
                })

                print(f"  ✓ {gguf_file.name} ({size_gb:.2f} GB) [{quant}]")

    return models

def generate_model_config(models: List[Dict]) -> Dict:
    """Generate models_config.yaml entries"""
    config = {
        'local_models': {},
        'routing_suggestions': {}
    }

    # Group by family
    families = {}
    for model in models:
        family = model['family']
        if family not in families:
            families[family] = []
        families[family].append(model)

    # Create configs for each family
    for family, family_models in families.items():
        # Find best model (largest quantization)
        best = max(family_models, key=lambda x: x['size_gb'])

        # Create config entry
        model_id = f"{family.lower()}-local"

        config['local_models'][model_id] = {
            'model_path': best['path'],
            'model_type': 'gguf',
            'context_length': 8192,
            'max_tokens': 4096,
            'temperature': 0.7,
            'family': family
        }

        # Suggest routing based on model name
        if any(x in family.lower() for x in ['coder', 'code', 'deepseek']):
            if 'code' not in config['routing_suggestions']:
                config['routing_suggestions']['code'] = []
            config['routing_suggestions']['code'].append(model_id)

        if any(x in family.lower() for x in ['llama3.1', 'llama3.2', 'qwen2.5']):
            if 'reasoning' not in config['routing_suggestions']:
                config['routing_suggestions']['reasoning'] = []
            config['routing_suggestions']['reasoning'].append(model_id)

    return config

def main():
    print("=" * 80)
    print("🚀 AlphaEdge AINV - Model Scanner")
    print("=" * 80)
    print()

    # Scan models
    models = scan_gguf_models()

    if not models:
        print("\n❌ No GGUF models found!")
        return

    print(f"\n📊 Summary: Found {len(models)} GGUF models")
    print()

    # Sort by size
    models_sorted = sorted(models, key=lambda x: x['size_gb'], reverse=True)

    print("🏆 Top Models by Size:")
    print()
    for i, model in enumerate(models_sorted[:10], 1):
        print(f"{i:2}. {model['family']:25} - {model['filename']:50} ({model['size_gb']:6.2f} GB)")

    print()

    # Generate config
    config = generate_model_config(models)

    # Save to JSON for easy reading
    output_file = "local_models_config.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✅ Config saved to: {output_file}")
    print()
    print("=" * 80)
    print("📝 Recommended Models for TensorRT-LLM Conversion:")
    print("=" * 80)
    print()

    # Recommend top 5 for conversion
    recommended = []
    seen_families = set()

    for model in models_sorted:
        if model['family'] not in seen_families and len(recommended) < 5:
            recommended.append(model)
            seen_families.add(model['family'])

    for i, model in enumerate(recommended, 1):
        print(f"{i}. {model['family']}")
        print(f"   File: {model['filename']}")
        print(f"   Size: {model['size_gb']:.2f} GB")
        print(f"   Path: {model['path']}")
        print()

if __name__ == "__main__":
    main()

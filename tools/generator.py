import os
import logging
from pathlib import Path
import scipy.io.wavfile
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s')
logger = logging.getLogger("Tool-Generator-Local")

# 全局变量：用于缓存模型，避免每次调用都重新加载
_processor = None
_model = None

def _load_model():
    """懒加载模型，只在第一次生成音乐时加载权重到内存"""
    global _processor, _model
    if _model is None:
        logger.info("Downloading/Loading MusicGen-Small model... (This takes a moment on first run)")
        
        # 自动检测是否可以使用 Mac M2 的 Metal 硬件加速 (MPS)
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        logger.info(f"Hardware Acceleration: Using {device.upper()}")
        
        _processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
        _model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small").to(device)
        logger.info("Model loaded successfully into memory!")
        
    return _processor, _model

def generate_music(prompt: str, output_path: str = "workspace/outputs/generated_music.wav") -> dict:
    """
    Runs Meta's MusicGen locally on your Mac to generate audio from a text prompt.
    """
    logger.info(f"Starting local music generation for prompt: '{prompt}'")
    
    Path("workspace/outputs").mkdir(parents=True, exist_ok=True)

    try:
        # 1. 加载模型
        processor, model = _load_model()
        device = model.device
        
        # 2. 将文本提示词转换为模型能看懂的张量 (Tensors)
        logger.info("Synthesizing audio... (Please wait, your M2 chip is working hard!)")
        inputs = processor(
            text=[prompt],
            padding=True,
            return_tensors="pt",
        ).to(device)
        
        # 3. 生成音频波形 (设置生成大约 10 秒的音频，256 个 token 约等于 10 秒)
        audio_values = model.generate(**inputs, max_new_tokens=256)
        
        # 4. 将张量转换回 CPU 并保存为 .wav 文件
        audio_data = audio_values[0, 0].cpu().numpy()
        sampling_rate = model.config.audio_encoder.sampling_rate
        
        scipy.io.wavfile.write(output_path, rate=sampling_rate, data=audio_data)
        
        logger.info(f"✅ Local music generated successfully! Saved at: {output_path}")
        return {
            "status": "success",
            "audio_path": str(Path(output_path).absolute()),
            "description": f"New music locally generated based on: {prompt}"
        }

    except Exception as e:
        logger.error(f"Local generation failed: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # 本地直接测试生成！
    test_prompt = "Cyberpunk electronic style, heavy bass, futuristic synth, 120bpm"
    generate_music(test_prompt)
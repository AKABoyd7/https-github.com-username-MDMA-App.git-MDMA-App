#!/usr/bin/env python3
"""
TensorRT Optimizer Module
Optimize LLM models for faster inference with lower memory usage

Copyright © 2025 AlphaEdge AINV
"""
import os
import sys
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TensorRTOptimizer:
    """
    TensorRT Model Optimizer
    - Optimize PyTorch/ONNX models for inference
    - 2-5x faster inference
    - 30-50% less VRAM usage
    - FP16/INT8 quantization
    """

    def __init__(
        self,
        precision: str = "fp16",
        max_batch_size: int = 1,
        workspace_size: int = 4096
    ):
        """
        Initialize TensorRT optimizer

        Args:
            precision: Precision mode (fp32, fp16, int8)
            max_batch_size: Maximum batch size
            workspace_size: Workspace size in MB
        """
        self.precision = precision
        self.max_batch_size = max_batch_size
        self.workspace_size = workspace_size * 1024 * 1024  # Convert to bytes

        # Try to import TensorRT
        try:
            import tensorrt as trt
            self.trt = trt
            self.available = True
            logger.info(f"✓ TensorRT {trt.__version__} available")
        except ImportError:
            self.trt = None
            self.available = False
            logger.warning("TensorRT not available. Install with: pip install tensorrt")

    def is_available(self) -> bool:
        """Check if TensorRT is available"""
        return self.available

    def optimize_onnx_model(
        self,
        onnx_path: str,
        output_path: str,
        input_shapes: Dict[str, List[int]]
    ) -> bool:
        """
        Optimize ONNX model to TensorRT engine

        Args:
            onnx_path: Path to ONNX model
            output_path: Output path for TensorRT engine
            input_shapes: Input shapes dict {name: [dim1, dim2, ...]}

        Returns:
            Success boolean
        """
        if not self.available:
            logger.error("TensorRT not available")
            return False

        try:
            import tensorrt as trt

            # Create builder and network
            logger.info(f"Building TensorRT engine from {onnx_path}")

            TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
            builder = trt.Builder(TRT_LOGGER)
            network = builder.create_network(
                1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
            )
            parser = trt.OnnxParser(network, TRT_LOGGER)

            # Parse ONNX
            with open(onnx_path, 'rb') as model:
                if not parser.parse(model.read()):
                    logger.error("Failed to parse ONNX file")
                    for error in range(parser.num_errors):
                        logger.error(parser.get_error(error))
                    return False

            # Configure builder
            config = builder.create_builder_config()
            config.max_workspace_size = self.workspace_size

            # Set precision
            if self.precision == "fp16":
                if builder.platform_has_fast_fp16:
                    config.set_flag(trt.BuilderFlag.FP16)
                    logger.info("✓ FP16 mode enabled")
                else:
                    logger.warning("FP16 not supported on this GPU")
            elif self.precision == "int8":
                if builder.platform_has_fast_int8:
                    config.set_flag(trt.BuilderFlag.INT8)
                    logger.info("✓ INT8 mode enabled")
                else:
                    logger.warning("INT8 not supported on this GPU")

            # Build engine
            logger.info("Building TensorRT engine (this may take several minutes)...")
            engine = builder.build_engine(network, config)

            if engine is None:
                logger.error("Failed to build TensorRT engine")
                return False

            # Serialize and save
            with open(output_path, 'wb') as f:
                f.write(engine.serialize())

            logger.info(f"✓ TensorRT engine saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"TensorRT optimization failed: {e}")
            return False

    def optimize_pytorch_model(
        self,
        model,
        example_inputs: tuple,
        output_path: str
    ) -> bool:
        """
        Optimize PyTorch model via ONNX → TensorRT

        Args:
            model: PyTorch model
            example_inputs: Example inputs for tracing
            output_path: Output path for TensorRT engine

        Returns:
            Success boolean
        """
        if not self.available:
            logger.error("TensorRT not available")
            return False

        try:
            import torch
            import torch.onnx

            # Export to ONNX first
            onnx_path = output_path.replace('.trt', '.onnx')

            logger.info("Exporting PyTorch model to ONNX...")
            torch.onnx.export(
                model,
                example_inputs,
                onnx_path,
                export_params=True,
                opset_version=14,
                do_constant_folding=True,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes={
                    'input': {0: 'batch_size'},
                    'output': {0: 'batch_size'}
                }
            )

            # Get input shapes
            if isinstance(example_inputs, tuple):
                input_shape = list(example_inputs[0].shape)
            else:
                input_shape = list(example_inputs.shape)

            input_shapes = {'input': input_shape}

            # Convert ONNX to TensorRT
            success = self.optimize_onnx_model(onnx_path, output_path, input_shapes)

            # Clean up ONNX file
            if success:
                os.remove(onnx_path)

            return success

        except Exception as e:
            logger.error(f"PyTorch optimization failed: {e}")
            return False

    def load_engine(self, engine_path: str):
        """
        Load TensorRT engine

        Args:
            engine_path: Path to TensorRT engine

        Returns:
            TensorRT engine and context
        """
        if not self.available:
            raise RuntimeError("TensorRT not available")

        import tensorrt as trt

        TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
        runtime = trt.Runtime(TRT_LOGGER)

        with open(engine_path, 'rb') as f:
            engine = runtime.deserialize_cuda_engine(f.read())

        context = engine.create_execution_context()

        logger.info(f"✓ TensorRT engine loaded from {engine_path}")
        return engine, context

    def infer(
        self,
        engine,
        context,
        inputs: Dict[str, Any],
        stream=None
    ) -> Dict[str, Any]:
        """
        Run inference with TensorRT engine

        Args:
            engine: TensorRT engine
            context: TensorRT context
            inputs: Input tensors dict
            stream: CUDA stream (optional)

        Returns:
            Output tensors dict
        """
        import torch
        import pycuda.driver as cuda

        # Allocate device memory
        bindings = []
        outputs = {}

        for binding in engine:
            size = engine.get_binding_shape(binding)
            dtype = engine.get_binding_dtype(binding)

            # Convert TensorRT dtype to torch dtype
            if dtype == self.trt.DataType.FLOAT:
                torch_dtype = torch.float32
            elif dtype == self.trt.DataType.HALF:
                torch_dtype = torch.float16
            elif dtype == self.trt.DataType.INT8:
                torch_dtype = torch.int8
            else:
                torch_dtype = torch.float32

            # Allocate memory
            if engine.binding_is_input(binding):
                tensor = inputs[binding]
            else:
                tensor = torch.empty(size, dtype=torch_dtype, device='cuda')
                outputs[binding] = tensor

            bindings.append(int(tensor.data_ptr()))

        # Run inference
        if stream:
            context.execute_async_v2(bindings=bindings, stream_handle=stream)
        else:
            context.execute_v2(bindings=bindings)

        return outputs

    def benchmark(
        self,
        engine,
        context,
        example_inputs: Dict[str, Any],
        iterations: int = 100
    ) -> Dict[str, float]:
        """
        Benchmark TensorRT engine

        Args:
            engine: TensorRT engine
            context: TensorRT context
            example_inputs: Example inputs
            iterations: Number of iterations

        Returns:
            Benchmark results dict
        """
        import torch
        import time

        # Warmup
        for _ in range(10):
            self.infer(engine, context, example_inputs)

        # Benchmark
        torch.cuda.synchronize()
        start = time.time()

        for _ in range(iterations):
            self.infer(engine, context, example_inputs)

        torch.cuda.synchronize()
        end = time.time()

        total_time = end - start
        avg_time = total_time / iterations
        throughput = 1.0 / avg_time

        return {
            'total_time_seconds': total_time,
            'avg_time_ms': avg_time * 1000,
            'throughput_samples_per_second': throughput,
            'iterations': iterations
        }


class TensorRTModelWrapper:
    """
    Wrapper for TensorRT optimized models
    Drop-in replacement for PyTorch models
    """

    def __init__(self, engine_path: str):
        """Initialize with TensorRT engine"""
        self.optimizer = TensorRTOptimizer()
        self.engine, self.context = self.optimizer.load_engine(engine_path)
        self.engine_path = engine_path

    def __call__(self, *args, **kwargs):
        """Forward pass"""
        # Convert args to inputs dict
        if args:
            inputs = {'input': args[0]}
        else:
            inputs = kwargs

        # Run inference
        outputs = self.optimizer.infer(self.engine, self.context, inputs)

        # Return first output
        return list(outputs.values())[0]

    def eval(self):
        """Set to eval mode (no-op for TensorRT)"""
        return self

    def to(self, device):
        """Move to device (no-op for TensorRT)"""
        return self


# Convenience functions
def optimize_model(
    model,
    example_inputs,
    output_path: str,
    precision: str = "fp16"
) -> bool:
    """
    Quick optimize PyTorch model

    Args:
        model: PyTorch model
        example_inputs: Example inputs
        output_path: Output path
        precision: Precision mode

    Returns:
        Success boolean
    """
    optimizer = TensorRTOptimizer(precision=precision)
    return optimizer.optimize_pytorch_model(model, example_inputs, output_path)


def load_optimized_model(engine_path: str):
    """
    Quick load optimized model

    Args:
        engine_path: Path to TensorRT engine

    Returns:
        Model wrapper
    """
    return TensorRTModelWrapper(engine_path)


# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TensorRT Optimizer")
    parser.add_argument("--onnx", type=str, help="ONNX model path")
    parser.add_argument("--output", type=str, help="Output engine path")
    parser.add_argument("--precision", type=str, default="fp16", choices=["fp32", "fp16", "int8"])
    parser.add_argument("--batch-size", type=int, default=1)

    args = parser.parse_args()

    if args.onnx and args.output:
        optimizer = TensorRTOptimizer(precision=args.precision, max_batch_size=args.batch_size)

        # Example input shapes (modify as needed)
        input_shapes = {
            'input': [args.batch_size, 3, 224, 224]
        }

        success = optimizer.optimize_onnx_model(args.onnx, args.output, input_shapes)

        if success:
            print(f"✓ Optimization successful: {args.output}")
        else:
            print("✗ Optimization failed")
    else:
        parser.print_help()

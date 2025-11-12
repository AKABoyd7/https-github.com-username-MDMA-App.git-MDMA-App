#!/usr/bin/env python3
"""
Multi-GPU Support with NCCL
Distributed training and inference across multiple GPUs

Copyright © 2025 AlphaEdge AINV
"""
import os
import torch
import torch.distributed as dist
from typing import Optional, List, Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)


class MultiGPUManager:
    """
    Multi-GPU Manager with NCCL backend
    - Data parallelism
    - Model parallelism
    - Pipeline parallelism
    - Distributed inference
    """

    def __init__(
        self,
        backend: str = "nccl",
        init_method: str = "env://",
        world_size: Optional[int] = None,
        rank: Optional[int] = None
    ):
        """
        Initialize Multi-GPU manager

        Args:
            backend: Backend (nccl, gloo, mpi)
            init_method: Init method for process group
            world_size: Number of processes
            rank: Rank of current process
        """
        self.backend = backend
        self.init_method = init_method
        self.world_size = world_size or int(os.environ.get('WORLD_SIZE', '1'))
        self.rank = rank or int(os.environ.get('RANK', '0'))
        self.local_rank = int(os.environ.get('LOCAL_RANK', '0'))

        self.initialized = False
        self.num_gpus = torch.cuda.device_count()

    def is_available(self) -> bool:
        """Check if multi-GPU is available"""
        return self.num_gpus > 1

    def is_distributed(self) -> bool:
        """Check if distributed training is initialized"""
        return dist.is_initialized()

    def setup(self):
        """Setup distributed training"""
        if self.initialized:
            logger.warning("Already initialized")
            return

        if not torch.cuda.is_available():
            raise RuntimeError("CUDA not available")

        if self.num_gpus < 2:
            logger.warning(f"Only {self.num_gpus} GPU(s) available")
            return

        # Initialize process group
        if not dist.is_initialized():
            dist.init_process_group(
                backend=self.backend,
                init_method=self.init_method,
                world_size=self.world_size,
                rank=self.rank
            )

        # Set device
        torch.cuda.set_device(self.local_rank)

        self.initialized = True
        logger.info(f"✓ Multi-GPU initialized: {self.num_gpus} GPUs")
        logger.info(f"  Backend: {self.backend}")
        logger.info(f"  World size: {self.world_size}")
        logger.info(f"  Rank: {self.rank}")
        logger.info(f"  Local rank: {self.local_rank}")

    def cleanup(self):
        """Cleanup distributed training"""
        if self.is_distributed():
            dist.destroy_process_group()
            self.initialized = False
            logger.info("✓ Multi-GPU cleaned up")

    def get_device(self) -> torch.device:
        """Get current device"""
        if self.initialized:
            return torch.device(f'cuda:{self.local_rank}')
        else:
            return torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    def wrap_model_ddp(self, model: torch.nn.Module) -> torch.nn.Module:
        """
        Wrap model with DistributedDataParallel

        Args:
            model: PyTorch model

        Returns:
            DDP-wrapped model
        """
        if not self.is_distributed():
            logger.warning("Not in distributed mode, returning unwrapped model")
            return model

        model = model.to(self.get_device())

        ddp_model = torch.nn.parallel.DistributedDataParallel(
            model,
            device_ids=[self.local_rank],
            output_device=self.local_rank,
            find_unused_parameters=False
        )

        logger.info("✓ Model wrapped with DDP")
        return ddp_model

    def wrap_model_dp(self, model: torch.nn.Module, device_ids: Optional[List[int]] = None) -> torch.nn.Module:
        """
        Wrap model with DataParallel (simpler, single-node only)

        Args:
            model: PyTorch model
            device_ids: List of GPU IDs

        Returns:
            DP-wrapped model
        """
        if device_ids is None:
            device_ids = list(range(self.num_gpus))

        dp_model = torch.nn.DataParallel(model, device_ids=device_ids)

        logger.info(f"✓ Model wrapped with DataParallel on GPUs: {device_ids}")
        return dp_model

    def all_reduce(
        self,
        tensor: torch.Tensor,
        op: dist.ReduceOp = dist.ReduceOp.SUM
    ) -> torch.Tensor:
        """
        All-reduce tensor across all processes

        Args:
            tensor: Tensor to reduce
            op: Reduce operation

        Returns:
            Reduced tensor
        """
        if not self.is_distributed():
            return tensor

        dist.all_reduce(tensor, op=op)
        return tensor

    def all_gather(
        self,
        tensor: torch.Tensor
    ) -> List[torch.Tensor]:
        """
        All-gather tensor from all processes

        Args:
            tensor: Tensor to gather

        Returns:
            List of tensors from all processes
        """
        if not self.is_distributed():
            return [tensor]

        tensor_list = [torch.zeros_like(tensor) for _ in range(self.world_size)]
        dist.all_gather(tensor_list, tensor)
        return tensor_list

    def broadcast(
        self,
        tensor: torch.Tensor,
        src: int = 0
    ) -> torch.Tensor:
        """
        Broadcast tensor from source to all processes

        Args:
            tensor: Tensor to broadcast
            src: Source rank

        Returns:
            Broadcasted tensor
        """
        if not self.is_distributed():
            return tensor

        dist.broadcast(tensor, src=src)
        return tensor

    def barrier(self):
        """Synchronization barrier"""
        if self.is_distributed():
            dist.barrier()

    def print_once(self, *args, **kwargs):
        """Print only on rank 0"""
        if self.rank == 0:
            print(*args, **kwargs)

    def is_main_process(self) -> bool:
        """Check if this is the main process (rank 0)"""
        return self.rank == 0

    def get_world_size(self) -> int:
        """Get world size"""
        return self.world_size

    def get_rank(self) -> int:
        """Get current rank"""
        return self.rank


class DistributedSampler:
    """Custom distributed sampler"""

    def __init__(
        self,
        dataset,
        num_replicas: Optional[int] = None,
        rank: Optional[int] = None,
        shuffle: bool = True
    ):
        """
        Initialize distributed sampler

        Args:
            dataset: Dataset
            num_replicas: Number of processes
            rank: Current rank
            shuffle: Shuffle data
        """
        if num_replicas is None:
            num_replicas = dist.get_world_size() if dist.is_initialized() else 1

        if rank is None:
            rank = dist.get_rank() if dist.is_initialized() else 0

        self.dataset = dataset
        self.num_replicas = num_replicas
        self.rank = rank
        self.shuffle = shuffle
        self.epoch = 0

        self.num_samples = len(dataset) // num_replicas
        self.total_size = self.num_samples * num_replicas

    def __iter__(self):
        """Iterator"""
        import numpy as np

        if self.shuffle:
            # Deterministic shuffling based on epoch
            g = np.random.default_rng(self.epoch)
            indices = g.permutation(len(self.dataset)).tolist()
        else:
            indices = list(range(len(self.dataset)))

        # Subsample for this rank
        indices = indices[self.rank:self.total_size:self.num_replicas]

        return iter(indices)

    def __len__(self):
        """Length"""
        return self.num_samples

    def set_epoch(self, epoch: int):
        """Set epoch for shuffling"""
        self.epoch = epoch


# Global manager instance
_manager: Optional[MultiGPUManager] = None


def get_manager() -> MultiGPUManager:
    """Get global multi-GPU manager"""
    global _manager
    if _manager is None:
        _manager = MultiGPUManager()
    return _manager


def setup_distributed():
    """Setup distributed training"""
    manager = get_manager()
    manager.setup()


def cleanup_distributed():
    """Cleanup distributed training"""
    manager = get_manager()
    manager.cleanup()


def wrap_model(model: torch.nn.Module, use_ddp: bool = True) -> torch.nn.Module:
    """
    Wrap model for multi-GPU

    Args:
        model: PyTorch model
        use_ddp: Use DDP (True) or DP (False)

    Returns:
        Wrapped model
    """
    manager = get_manager()

    if use_ddp:
        return manager.wrap_model_ddp(model)
    else:
        return manager.wrap_model_dp(model)


# Utility functions
def all_reduce_mean(tensor: torch.Tensor) -> torch.Tensor:
    """All-reduce with mean"""
    manager = get_manager()

    if not manager.is_distributed():
        return tensor

    tensor = manager.all_reduce(tensor, op=dist.ReduceOp.SUM)
    tensor = tensor / manager.get_world_size()
    return tensor


def print_once(*args, **kwargs):
    """Print only on rank 0"""
    manager = get_manager()
    manager.print_once(*args, **kwargs)


# CLI
if __name__ == "__main__":
    # Example usage
    print("=== Multi-GPU Test ===\n")

    manager = MultiGPUManager()

    print(f"GPUs available: {manager.num_gpus}")
    print(f"Multi-GPU available: {manager.is_available()}")

    if manager.is_available():
        print("\nTo use multi-GPU, launch with:")
        print("  torchrun --nproc_per_node=2 multi_gpu.py")
        print("  or")
        print("  python -m torch.distributed.launch --nproc_per_node=2 multi_gpu.py")

    # Test simple tensor
    if torch.cuda.is_available():
        tensor = torch.randn(4, 4).cuda()
        print(f"\nTest tensor:\n{tensor}")

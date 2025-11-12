"""
Tests for GPU monitoring tools.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from mcp_server.tools import gpu_monitor


class TestGPUAvailability:
    """Test GPU availability detection."""

    @patch('mcp_server.tools.gpu_monitor.pynvml')
    def test_gpu_available(self, mock_pynvml):
        """Test when GPU is available."""
        mock_pynvml.nvmlInit.return_value = None
        mock_pynvml.nvmlDeviceGetCount.return_value = 1

        assert gpu_monitor.is_gpu_available() is True

    @patch('mcp_server.tools.gpu_monitor.pynvml')
    def test_gpu_not_available(self, mock_pynvml):
        """Test when GPU is not available."""
        mock_pynvml.nvmlInit.side_effect = Exception("NVML not found")

        assert gpu_monitor.is_gpu_available() is False


class TestGPUStatus:
    """Test GPU status retrieval."""

    @patch('mcp_server.tools.gpu_monitor.is_gpu_available')
    def test_gpu_status_no_gpu(self, mock_available):
        """Test GPU status when no GPU available."""
        mock_available.return_value = False

        result = gpu_monitor.gpu_status()

        assert result["success"] is False
        assert "error" in result

    @patch('mcp_server.tools.gpu_monitor.is_gpu_available')
    @patch('mcp_server.tools.gpu_monitor.get_gpu_handle')
    @patch('mcp_server.tools.gpu_monitor.pynvml')
    def test_gpu_status_success(self, mock_pynvml, mock_handle, mock_available):
        """Test successful GPU status retrieval."""
        mock_available.return_value = True
        mock_handle.return_value = Mock()

        # Mock GPU info
        mock_pynvml.nvmlDeviceGetName.return_value = b"NVIDIA GeForce RTX 3090"
        mock_pynvml.nvmlSystemGetDriverVersion.return_value = b"560.94"
        mock_pynvml.nvmlSystemGetCudaDriverVersion.return_value = 12060

        # Mock utilization
        mock_util = Mock()
        mock_util.gpu = 75
        mock_util.memory = 85
        mock_pynvml.nvmlDeviceGetUtilizationRates.return_value = mock_util

        # Mock memory
        mock_mem = Mock()
        mock_mem.total = 24 * 1024 ** 3  # 24GB
        mock_mem.used = 20 * 1024 ** 3   # 20GB
        mock_mem.free = 4 * 1024 ** 3    # 4GB
        mock_pynvml.nvmlDeviceGetMemoryInfo.return_value = mock_mem

        # Mock temperature and power
        mock_pynvml.nvmlDeviceGetTemperature.return_value = 72
        mock_pynvml.nvmlDeviceGetPowerUsage.return_value = 350000  # mW
        mock_pynvml.nvmlDeviceGetFanSpeed.return_value = 65

        # Mock clocks
        mock_pynvml.nvmlDeviceGetClockInfo.side_effect = [1950, 9751]

        result = gpu_monitor.gpu_status()

        assert result["success"] is True
        assert result["gpu_name"] == "NVIDIA GeForce RTX 3090"
        assert result["utilization"]["gpu"] == 75
        assert result["memory"]["total_gb"] == 24.0
        assert result["temperature"] == 72


class TestVRAMMonitoring:
    """Test VRAM monitoring."""

    @patch('mcp_server.tools.gpu_monitor.is_gpu_available')
    def test_vram_monitor_no_gpu(self, mock_available):
        """Test VRAM monitor when no GPU available."""
        mock_available.return_value = False

        result = gpu_monitor.vram_monitor()

        assert result["success"] is False

    @patch('mcp_server.tools.gpu_monitor.is_gpu_available')
    @patch('mcp_server.tools.gpu_monitor.get_gpu_handle')
    @patch('mcp_server.tools.gpu_monitor.pynvml')
    def test_vram_monitor_ok_level(self, mock_pynvml, mock_handle, mock_available):
        """Test VRAM monitor with OK alert level."""
        mock_available.return_value = True
        mock_handle.return_value = Mock()

        # Mock memory - 50% usage (OK level)
        mock_mem = Mock()
        mock_mem.total = 24 * 1024 ** 3
        mock_mem.used = 12 * 1024 ** 3
        mock_mem.free = 12 * 1024 ** 3
        mock_pynvml.nvmlDeviceGetMemoryInfo.return_value = mock_mem

        result = gpu_monitor.vram_monitor()

        assert result["success"] is True
        assert result["alert_level"] == "ok"
        assert result["utilization_percent"] == 50.0

    @patch('mcp_server.tools.gpu_monitor.is_gpu_available')
    @patch('mcp_server.tools.gpu_monitor.get_gpu_handle')
    @patch('mcp_server.tools.gpu_monitor.pynvml')
    def test_vram_monitor_warning_level(self, mock_pynvml, mock_handle, mock_available):
        """Test VRAM monitor with warning alert level."""
        mock_available.return_value = True
        mock_handle.return_value = Mock()

        # Mock memory - 92% usage (warning level)
        mock_mem = Mock()
        mock_mem.total = 24 * 1024 ** 3
        mock_mem.used = 22 * 1024 ** 3
        mock_mem.free = 2 * 1024 ** 3
        mock_pynvml.nvmlDeviceGetMemoryInfo.return_value = mock_mem

        result = gpu_monitor.vram_monitor()

        assert result["success"] is True
        assert result["alert_level"] == "warning"
        assert "WARNING" in result["recommendation"]


class TestCUDAInfo:
    """Test CUDA information retrieval."""

    @patch('mcp_server.tools.gpu_monitor.is_gpu_available')
    def test_cuda_info_no_gpu(self, mock_available):
        """Test CUDA info when no GPU available."""
        mock_available.return_value = False

        result = gpu_monitor.cuda_info()

        assert result["success"] is False

    @patch('mcp_server.tools.gpu_monitor.is_gpu_available')
    @patch('mcp_server.tools.gpu_monitor.get_gpu_handle')
    @patch('mcp_server.tools.gpu_monitor.pynvml')
    def test_cuda_info_success(self, mock_pynvml, mock_handle, mock_available):
        """Test successful CUDA info retrieval."""
        mock_available.return_value = True
        mock_handle.return_value = Mock()

        mock_pynvml.nvmlInit.return_value = None
        mock_pynvml.nvmlSystemGetCudaDriverVersion.return_value = 12060
        mock_pynvml.nvmlDeviceGetCount.return_value = 1
        mock_pynvml.nvmlDeviceGetName.return_value = b"NVIDIA GeForce RTX 3090"
        mock_pynvml.nvmlDeviceGetCudaComputeCapability.return_value = (8, 6)

        result = gpu_monitor.cuda_info()

        assert result["success"] is True
        assert result["cuda_version"] == "12.6"
        assert result["num_gpus"] == 1
        assert result["architecture"] == "Ampere"
        assert result["compute_capability"] == "8.6"


class TestGPUProcesses:
    """Test GPU process monitoring."""

    @patch('mcp_server.tools.gpu_monitor.is_gpu_available')
    @patch('mcp_server.tools.gpu_monitor.get_gpu_handle')
    @patch('mcp_server.tools.gpu_monitor.pynvml')
    @patch('mcp_server.tools.gpu_monitor.psutil')
    def test_gpu_processes_list(self, mock_psutil, mock_pynvml, mock_handle, mock_available):
        """Test listing GPU processes."""
        mock_available.return_value = True
        mock_handle.return_value = Mock()

        # Mock processes
        mock_proc1 = Mock()
        mock_proc1.pid = 1234
        mock_proc1.usedGpuMemory = 8 * 1024 ** 3  # 8GB in bytes

        mock_proc2 = Mock()
        mock_proc2.pid = 5678
        mock_proc2.usedGpuMemory = 4 * 1024 ** 3  # 4GB in bytes

        mock_pynvml.nvmlDeviceGetComputeRunningProcesses.return_value = [mock_proc1, mock_proc2]
        mock_pynvml.nvmlDeviceGetGraphicsRunningProcesses.return_value = []

        # Mock psutil process info
        mock_ps_proc1 = Mock()
        mock_ps_proc1.name.return_value = "python.exe"

        mock_ps_proc2 = Mock()
        mock_ps_proc2.name.return_value = "lmstudio.exe"

        mock_psutil.Process.side_effect = [mock_ps_proc1, mock_ps_proc2]

        result = gpu_monitor.gpu_processes()

        assert result["success"] is True
        assert result["total_processes"] == 2
        assert len(result["processes"]) == 2
        # Should be sorted by memory usage (descending)
        assert result["processes"][0]["gpu_memory_mb"] >= result["processes"][1]["gpu_memory_mb"]


class TestToolRegistration:
    """Test tool registration."""

    def test_get_tools_count(self):
        """Test that correct number of GPU tools are registered."""
        tools = gpu_monitor.get_tools()

        assert isinstance(tools, list)
        assert len(tools) == 5  # Should have 5 GPU monitoring tools

    def test_all_tools_have_handlers(self):
        """Test that all tools have callable handlers."""
        tools = gpu_monitor.get_tools()

        for tool in tools:
            assert callable(tool["handler"])
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool


@pytest.mark.integration
class TestGPUIntegration:
    """Integration tests requiring actual GPU."""

    @pytest.mark.skip(reason="Requires NVIDIA GPU")
    def test_actual_gpu_status(self):
        """Test actual GPU status retrieval (requires GPU)."""
        result = gpu_monitor.gpu_status()

        if result["success"]:
            assert "gpu_name" in result
            assert "memory" in result
            assert "temperature" in result

    @pytest.mark.skip(reason="Requires NVIDIA GPU")
    def test_actual_vram_monitor(self):
        """Test actual VRAM monitoring (requires GPU)."""
        result = gpu_monitor.vram_monitor()

        if result["success"]:
            assert result["alert_level"] in ["ok", "warning", "critical"]
            assert 0 <= result["utilization_percent"] <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

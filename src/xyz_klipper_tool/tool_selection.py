"""Bounded dynamic tool discovery and reference selection."""

from xyz_klipper_tool.domain.models import ToolId
from xyz_klipper_tool.ports import ToolchangerAdapter


def discover_tools(
    adapter: ToolchangerAdapter, reference: ToolId | None = None, max_tools: int = 64
) -> tuple[ToolId, ...]:
    """Return deterministic dynamic tools; reject duplicates, ambiguity, mismatch, and bounds."""
    if type(max_tools) is not int or max_tools <= 0:
        raise ValueError("max_tools must be positive")
    found = tuple(adapter.discover_tools())
    if not found or len(found) > max_tools:
        raise ValueError("tool discovery is empty or exceeds bound")
    if any(type(tool) is not ToolId for tool in found) or len(set(found)) != len(found):
        raise ValueError("tool discovery contains invalid or duplicate IDs")
    active = adapter.active_tool()
    detected = adapter.detected_tool()
    if (active is None) != (detected is None) or (
        active is not None and active != detected
    ):
        raise ValueError("active and detected tool state mismatch")
    if reference is None:
        raise ValueError("reference tool must be explicitly configured")
    if active is not None and (type(active) is not ToolId or active not in found):
        raise ValueError("active tool is not discovered or is not typed")
    if detected is not None and (type(detected) is not ToolId or detected not in found):
        raise ValueError("detected tool is not discovered or is not typed")
    if type(reference) is not ToolId or reference not in found:
        raise ValueError("reference tool is missing")
    return (reference,) + tuple(
        sorted(
            (tool for tool in found if tool != reference), key=lambda item: item.value
        )
    )

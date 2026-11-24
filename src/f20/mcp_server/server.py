"""Lokaler MCP-Server (stdio) für Claude Code – ausschließlich lesend.

Registrieren (im Projektordner):
    claude mcp add f20 -- ./scripts/f20-mcp
oder über die mitgelieferte .mcp.json.
"""

from __future__ import annotations

import functools
import inspect
import json

from .. import APP_NAME, __version__
from .tools import TOOL_NAMES, F20Tools

INSTRUCTIONS = (
    "F20 Intelligence: lesender Zugriff auf Fahrzeugprofil, Steuergeräte, Codierungskatalog (mit Quellen, "
    "Risiko, Rechtslage), aktuelle Codierung im Klartext, Backup-Historie, gespeicherte Diagnosen und "
    "Messwerte eines BMW 116i F20 (01/2012). Nachweisstufen beachten: verified/documented/likely/"
    "experimental/incompatible/unknown – nie als 'getestet' darstellen, was nur dokumentiert ist. "
    "Sicherheitskritische Steuergeräte (DME, DSC, EPS, ICM, ACSM) nur dokumentieren, nicht zur Änderung raten. "
    "Codierungen setzt der Besitzer selbst in BimmerCode um; dieser Server schreibt nichts."
)


def _make_server():
    try:
        from mcp.server.mcpserver import MCPServer as Server  # mcp >= 2
    except ImportError:  # pragma: no cover - mcp 1.x
        from mcp.server.fastmcp import FastMCP as Server
    try:
        from mcp.types import ToolAnnotations
        ro = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    except Exception:  # noqa: BLE001
        ro = None
    server = Server(name="f20-intelligence", instructions=INSTRUCTIONS)
    tools = F20Tools()
    for name in TOOL_NAMES:
        method = getattr(tools, name)

        @functools.wraps(method)
        def wrapper(*args, __m=method, **kwargs):
            try:
                return json.dumps(__m(*args, **kwargs), ensure_ascii=False, default=str)
            except PermissionError as exc:
                return json.dumps({"error": str(exc)}, ensure_ascii=False)
        wrapper.__signature__ = inspect.signature(method).replace(return_annotation=str)  # type: ignore[attr-defined]
        wrapper.__annotations__ = {**{k: v for k, v in getattr(method, "__annotations__", {}).items() if k != "return"},
                                   "return": str}
        kwargs = {"name": name, "description": (method.__doc__ or name).strip()}
        if ro is not None:
            kwargs["annotations"] = ro
        server.tool(**kwargs)(wrapper)
    return server


def main() -> None:
    server = _make_server()
    server.run("stdio")


if __name__ == "__main__":  # pragma: no cover
    main()

__all__ = ["main", "_make_server", "APP_NAME", "__version__"]

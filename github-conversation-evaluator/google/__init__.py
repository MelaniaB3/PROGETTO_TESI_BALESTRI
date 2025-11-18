"""Local `google` package used only as a development shim.

This file ensures `import google.generativeai` works when a local
`google/generativeai.py` stub is present. In real deployments, remove this
package and install the official `google-generativeai` client.
"""

from . import generativeai  # re-export the local stub

__all__ = ["generativeai"]

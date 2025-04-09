"""
This module provides custom implementations of BaseDoc and DocList for compatibility
with GenAIComps when the correct docarray version is not available.
"""

from typing import TypeVar, Generic, List, Dict, Any, Optional, Union
import json
import numpy as np
from pydantic import BaseModel  # Ensure compatibility with pydantic>=2.0.0

T = TypeVar("T")

# Try importing from docarray v0.21+ first
try:
    from docarray import BaseDoc, DocList

    DOCARRAY_VERSION = "0.30+"
    print(f"Using docarray {DOCARRAY_VERSION} with native BaseDoc and DocList")
except ImportError:
    print("docarray not found, falling back to compatibility wrappers")
    # Fall back to older docarray with Document and DocumentArray
    try:
        from docarray import Document, DocumentArray

        DOCARRAY_VERSION = "legacy"
        print(
            f"Using legacy docarray {DOCARRAY_VERSION}, creating compatibility wrappers"
        )

        # Create compatibility wrappers
        class BaseDoc(Document):
            """Compatibility wrapper for BaseDoc using Document"""

            pass

        class DocList(DocumentArray, Generic[T]):
            """Compatibility wrapper for DocList using DocumentArray"""

            pass

    except ImportError:
        # Create our own implementations if docarray isn't available at all
        DOCARRAY_VERSION = "shim"

        # Create compatibility wrappers
        class BaseDoc(BaseModel):
            """Compatibility wrapper for BaseDoc using pydantic>=2.0.0"""

            def dict(self):
                """Convert to dict representation"""
                return {
                    k: v
                    for k, v in self.__dict__.items()
                    if not k.startswith("_")
                }

            def json(self):
                """Convert to JSON string"""
                return json.dumps(self.dict())

        class DocList(Generic[T]):
            """Compatibility wrapper for DocList"""

            def __init__(self, items=None):
                self._items = items or []

            def append(self, item):
                self._items.append(item)

            def extend(self, items):
                self._items.extend(items)

            def __iter__(self):
                return iter(self._items)

            def __getitem__(self, idx):
                return self._items[idx]

            def __len__(self):
                return len(self._items)

            def __repr__(self):
                return f"DocList({repr(self._items)})"


# Add compatibility class for AudioDoc
class AudioDoc(BaseDoc):
    """Audio document for GenAIComps compatibility"""

    def __init__(self, audio_values=None, sample_rate=None, **kwargs):
        super().__init__(**kwargs)
        self.audio_values = audio_values or []
        self.sample_rate = sample_rate or 44100


# Add module patch function for emergency use
def patch_docarray():
    """
    Patch the docarray module with our custom implementations if needed
    """
    import sys
    import importlib.util

    # Check if docarray is available
    if importlib.util.find_spec("docarray"):
        try:
            import docarray

            # Check if we need to patch DocList and BaseDoc
            needs_patch = not (
                hasattr(docarray, "BaseDoc") and hasattr(docarray, "DocList")
            )

            if (
                needs_patch
                and hasattr(docarray, "Document")
                and hasattr(docarray, "DocumentArray")
            ):
                # It's an older version with Document/DocumentArray - patch it
                print(
                    f"Patching docarray {docarray.__version__} with BaseDoc and DocList compatibility"
                )
                docarray.BaseDoc = BaseDoc
                docarray.DocList = DocList
                docarray.documents.AudioDoc = AudioDoc
                docarray.typing = importlib.util.find_spec(
                    "docarray.typing"
                ) or types.ModuleType("docarray.typing")
                docarray.typing.AudioUrl = str
                docarray.typing.ImageUrl = str
                return True
            elif not needs_patch:
                print(
                    f"docarray {docarray.__version__} already has BaseDoc and DocList"
                )
                return False
        except ImportError:
            pass

    # Create a fake docarray module
    import types

    fake_docarray = types.ModuleType("docarray")
    fake_docarray.BaseDoc = BaseDoc
    fake_docarray.DocList = DocList
    fake_docarray.__version__ = "0.21.0-shim"
    fake_docarray.documents = types.ModuleType("docarray.documents")
    fake_docarray.documents.AudioDoc = AudioDoc
    fake_docarray.typing = types.ModuleType("docarray.typing")
    fake_docarray.typing.AudioUrl = str
    fake_docarray.typing.ImageUrl = str

    # Register the fake module
    sys.modules["docarray"] = fake_docarray
    sys.modules["docarray.documents"] = fake_docarray.documents
    sys.modules["docarray.typing"] = fake_docarray.typing

    print("✅ docarray fully patched with custom implementations")
    return True

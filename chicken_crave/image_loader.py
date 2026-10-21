"""Asynchronous image loading with caching and fallbacks."""

from __future__ import annotations

import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple
from urllib.request import Request, urlopen

from PIL import Image, ImageOps, ImageTk


class AsyncImageLoader:
    def __init__(self, root, cache_dir: str = ".image_cache", max_workers: int = 4):
        self.root = root
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="img-loader")
        self.memory_cache: Dict[Tuple[str, Tuple[int, int]], ImageTk.PhotoImage] = {}
        self.pending: Dict[Tuple[str, Tuple[int, int]], bool] = {}
        self.lock = threading.Lock()

    def load(self, image_url: str, fallback_path: str, size: Tuple[int, int], callback: Callable):
        key = (image_url, size)
        cached = self.memory_cache.get(key)
        if cached is not None:
            self.root.after(0, lambda: callback(cached))
            return

        with self.lock:
            if self.pending.get(key):
                return
            self.pending[key] = True

        self.executor.submit(self._download_and_prepare, image_url, fallback_path, size, key, callback)

    def _download_and_prepare(self, image_url: str, fallback_path: str, size, key, callback):
        data = self._read_remote_or_cache(image_url)
        if data is None:
            data = Path(fallback_path).read_bytes()

        def on_main_thread():
            try:
                with Image.open(BytesIO(data)) as raw:
                    prepared = ImageOps.fit(raw.convert("RGB"), size, method=Image.Resampling.LANCZOS)
                image = ImageTk.PhotoImage(prepared)
                self.memory_cache[key] = image
                callback(image)
            finally:
                with self.lock:
                    self.pending.pop(key, None)

        self.root.after(0, on_main_thread)

    def _read_remote_or_cache(self, image_url: str) -> Optional[bytes]:
        digest = hashlib.sha256(image_url.encode("utf-8")).hexdigest()
        cache_path = self.cache_dir / f"{digest}.bin"
        if cache_path.exists():
            try:
                return cache_path.read_bytes()
            except OSError:
                pass

        request = Request(image_url, headers={"User-Agent": "ChickenCrave/1.0"})
        try:
            with urlopen(request, timeout=8) as response:
                payload = response.read()
            cache_path.write_bytes(payload)
            return payload
        except Exception:
            return None

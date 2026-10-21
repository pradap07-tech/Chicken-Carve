const cache = new Map();
const queue = [];
const inFlight = new Set();
const MAX_CONCURRENT = 4;

self.onmessage = (event) => {
  const { id, url } = event.data;
  queue.push({ id, url });
  pump();
};

function pump() {
  while (inFlight.size < MAX_CONCURRENT && queue.length > 0) {
    const task = queue.shift();
    inFlight.add(task.id);
    fetchImage(task)
      .catch(() => undefined)
      .finally(() => {
        inFlight.delete(task.id);
        pump();
      });
  }
}

async function fetchImage(task) {
  if (cache.has(task.url)) {
    self.postMessage({ id: task.id, status: "ok", src: cache.get(task.url) });
    return;
  }

  try {
    const response = await fetch(task.url, { cache: "force-cache" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const blob = await response.blob();
    if (!blob.type.startsWith("image/") || blob.size === 0) {
      throw new Error("Invalid image blob");
    }

    const objectUrl = URL.createObjectURL(blob);
    cache.set(task.url, objectUrl);
    self.postMessage({ id: task.id, status: "ok", src: objectUrl });
  } catch (error) {
    self.postMessage({ id: task.id, status: "error", message: error.message });
  }
}

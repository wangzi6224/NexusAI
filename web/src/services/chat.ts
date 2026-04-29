// 统一从 api.ts 导出所有后端接口函数和类型
export * from './api';

/** 流式问答（SSE） */
export function streamChat (
  params: {
    session_id: number;
    question: string;
    enable_web_search?: boolean;
    sector?: string;
  },
  callbacks: StreamCallbacks,
): () => void {
  const abortController = new AbortController();
  const tokenData = getToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'text/event-stream',
  };

  if (tokenData) {
    headers['xtoken'] = tokenData.token;
    headers['sign'] = tokenData.sign;
    headers['token'] = tokenData.token;
  }

  let accumulated = '';

  (async () => {
    try {
      const response = await fetch('/api/announce/qa/chat/stream', {
        method: 'POST',
        headers,
        body: JSON.stringify(params),
        signal: abortController.signal,
      });

      if (!response.ok) {
        let errMsg = `HTTP ${response.status}`;
        try {
          const errBody = await response.json();
          errMsg = errBody?.msg || errMsg;
        } catch {
          // ignore parse error
        }
        callbacks.onError?.(new Error(errMsg));
        return;
      }

      if (!response.body) {
        callbacks.onError?.(new Error('响应体为空'));
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let doneCalled = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const jsonStr = line.slice(6).trim();
          if (!jsonStr) continue;

          try {
            const event = JSON.parse(jsonStr);
            const payload = event.data ?? event;
            if (payload.type === 'answer') {
              accumulated += payload.content;
              callbacks.onChunk(accumulated);
            } else if (payload.type === 'done') {
              doneCalled = true;
              callbacks.onDone(payload.message_id ?? 0);
              return;
            }
          } catch {
            // 跳过格式错误的数据块
          }
        }
      }

      // 流正常结束但未收到 done 事件
      if (!doneCalled) {
        callbacks.onDone(0);
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        callbacks.onError?.(err as Error);
      }
    }
  })();

  return () => {
    abortController.abort();
    stopChat({ session_id: params.session_id }).catch(() => { });
  };
}

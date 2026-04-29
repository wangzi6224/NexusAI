/**
 * 后端统一响应结构
 */
export interface ApiResponse<T = any> {
  code: number;
  msg: string;
  data: T;
}

/**
 * HTTP 请求方法
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

/**
 * 请求类型
 */
export type RequestType = 'json' | 'formdata';

/**
 * 响应类型
 */
export type ResponseType = 'json' | 'blob' | 'arraybuffer' | 'text';

/**
 * 请求配置选项
 */
export interface RequestOptions<Req = any> {
  /** 请求路径 */
  path: string;
  
  /** 请求方法 */
  method: HttpMethod;
  
  /** 请求数据（统一使用 data，内部根据 method 自动转换） */
  data?: Req;
  
  /** 自定义请求头 */
  headers?: Record<string, string>;
  
  /** 请求类型，默认 'json' */
  requestType?: RequestType;
  
  /** 响应类型，默认 'json' */
  responseType?: ResponseType;
  
  /** 请求超时时间（毫秒），默认 10000 */
  timeout?: number;
  
  /** AbortController 信号 */
  signal?: AbortSignal;
  
  /** 是否静默处理错误（不显示错误提示） */
  silent?: boolean;
}

/**
 * HTTP 错误
 */
export class HttpError extends Error {
  public status: number;
  public statusText: string;
  public url: string;

  constructor(status: number, statusText: string, url: string, message?: string) {
    super(message || `HTTP Error ${status}: ${statusText}`);
    this.name = 'HttpError';
    this.status = status;
    this.statusText = statusText;
    this.url = url;
  }
}

/**
 * 业务错误
 */
export class BizError extends Error {
  public code: number;
  public url: string;

  constructor(code: number, msg: string, url: string) {
    super(msg || `Business Error ${code}`);
    this.name = 'BizError';
    this.code = code;
    this.url = url;
  }
}

/**
 * 响应格式错误
 */
export class ResponseFormatError extends Error {
  public response: any;

  constructor(response: any, message?: string) {
    super(message || '响应数据格式不符合约定：缺少 code、msg 或 data 字段');
    this.name = 'ResponseFormatError';
    this.response = response;
  }
}

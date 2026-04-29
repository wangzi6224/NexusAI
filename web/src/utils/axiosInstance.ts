import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse, BizError, HttpError, ResponseFormatError } from './types';

/**
 * 创建 axios 实例
 */
const axiosInstance: AxiosInstance = axios.create({
  baseURL: process.env.API_BASE_URL || '',
  timeout: 10000,
  withCredentials: true, // 支持跨域携带凭证（cookie）
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 生成唯一的 trace-id（用于请求追踪）
 */
function generateTraceId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 获取 token（从 localStorage 或其他存储中）
 */
function getAuthToken(): string | null {
  // 根据实际项目调整 token 存储方式
  return localStorage.getItem('token') || sessionStorage.getItem('token');
}

/**
 * 请求拦截器
 */
axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 合并默认 headers
    if (!config.headers) {
      config.headers = {} as any;
    }

    // 注入 trace-id（请求追踪）
    if (!config.headers['X-Trace-Id']) {
      config.headers['X-Trace-Id'] = generateTraceId();
    }

    // 注入 token
    const token = getAuthToken();
    if (token && !config.headers['Authorization']) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * 响应拦截器
 */
axiosInstance.interceptors.response.use(
  (response: AxiosResponse<ApiResponse<any>>) => {
    const { data, config } = response;
    const url = config.url || '';

    // 如果响应类型不是 json，直接返回原始数据
    const responseType = config.responseType || 'json';
    if (responseType !== 'json') {
      return response;
    }

    // 验证响应结构是否符合约定
    if (typeof data !== 'object' || data === null) {
      throw new ResponseFormatError(data, '响应数据不是有效的对象');
    }

    if (!('code' in data) || !('msg' in data) || !('data' in data)) {
      throw new ResponseFormatError(
        data,
        '响应数据格式不符合约定：缺少 code、msg 或 data 字段'
      );
    }

    // 检查业务状态码
    if (data.code !== 0) {
      throw new BizError(data.code, data.msg, url);
    }

    // 成功：返回完整的响应结构
    return response;
  },
  (error) => {
    // HTTP 错误处理
    if (error.response) {
      const { status, statusText, config } = error.response;
      const url = config?.url || '';
      throw new HttpError(status, statusText, url);
    }

    // 网络错误或其他错误
    if (error.request) {
      throw new HttpError(0, 'Network Error', error.config?.url || '', '网络异常，请检查网络连接');
    }

    // 其他错误（如请求配置错误）
    return Promise.reject(error);
  }
);

export default axiosInstance;

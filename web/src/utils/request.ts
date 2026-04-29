import { message } from 'antd';
import { AxiosRequestConfig } from 'axios';
import axiosInstance from './axiosInstance';
import { toFormData } from './formData';
import { getToken } from './token';
import {
  ApiResponse,
  BizError,
  HttpError,
  RequestOptions,
  ResponseFormatError,
} from './types';

/**
 * 统一错误提示（可接入 antd message 或其他 UI 组件）
 */
function showErrorMessage(msg: string) {
  message.error(msg);
  console.error('[Request Error]:', msg);
}

/**
 * 统一请求方法
 * @template Req 请求入参类型
 * @template Res 响应 data 的类型
 * @param options 请求配置
 * @returns Promise<ApiResponse<Res>>
 */
export async function request<Req = any, Res = any>(
  options: RequestOptions<Req>,
): Promise<ApiResponse<Res>> {
  const {
    path,
    method,
    data,
    headers = {},
    requestType = 'json',
    responseType = 'json',
    timeout = 10000,
    signal,
    silent = false,
  } = options;

  const tokenData = getToken();

  try {
    // 构建 axios 请求配置
    const config: AxiosRequestConfig = {
      url: path,
      method,
      timeout,
      signal,
      responseType,
      headers: {
        ...headers,
        sign: tokenData?.sign,
        ['Xtoken']: tokenData?.token,
      },
    };

    // 根据 method 和 requestType 处理 data
    if (data) {
      if (method === 'GET' || method === 'DELETE') {
        // GET 和 DELETE 请求：data 转为 params
        config.params = data;
      } else {
        // POST、PUT、PATCH 请求：根据 requestType 处理
        if (requestType === 'formdata') {
          // FormData 格式
          config.data = toFormData(data as Record<string, any>);
          config.headers!['Content-Type'] = 'multipart/form-data';
        } else {
          // JSON 格式（默认）
          config.data = data;
          config.headers!['Content-Type'] = 'application/json';
        }
      }
    }

    // 发送请求
    const response = await axiosInstance.request<ApiResponse<Res>>(config);

    // 如果响应类型不是 json，直接返回包装后的数据
    if (responseType !== 'json') {
      return {
        code: 0,
        msg: 'success',
        data: response.data as any,
      };
    }

    // 返回完整的 ApiResponse<Res>
    return response.data;
  } catch (error: any) {
    // 错误处理
    if (!silent) {
      if (error instanceof HttpError) {
        showErrorMessage(`网络错误 ${error.status}: ${error.statusText}`);
      } else if (error instanceof BizError) {
        showErrorMessage(`业务错误 ${error.code}: ${error.message}`);
      } else if (error instanceof ResponseFormatError) {
        showErrorMessage(error.message);
      } else if (error.name === 'AbortError') {
        showErrorMessage('请求已取消');
      } else if (error.name === 'TimeoutError') {
        showErrorMessage('请求超时');
      } else {
        showErrorMessage(error.message || '请求失败');
      }
    }

    // 抛出错误，让调用方可以进一步处理
    throw error;
  }
}

/**
 * 便捷方法：GET 请求
 */
export function get<Req = any, Res = any>(
  path: string,
  data?: Req,
  options?: Omit<RequestOptions<Req>, 'path' | 'method' | 'data'>,
): Promise<ApiResponse<Res>> {
  return request<Req, Res>({ path, method: 'GET', data, ...options });
}

/**
 * 便捷方法：POST 请求
 */
export function post<Req = any, Res = any>(
  path: string,
  data?: Req,
  options?: Omit<RequestOptions<Req>, 'path' | 'method' | 'data'>,
): Promise<ApiResponse<Res>> {
  return request<Req, Res>({ path, method: 'POST', data, ...options });
}

/**
 * 便捷方法：PUT 请求
 */
export function put<Req = any, Res = any>(
  path: string,
  data?: Req,
  options?: Omit<RequestOptions<Req>, 'path' | 'method' | 'data'>,
): Promise<ApiResponse<Res>> {
  return request<Req, Res>({ path, method: 'PUT', data, ...options });
}

/**
 * 便捷方法：DELETE 请求
 */
export function del<Req = any, Res = any>(
  path: string,
  data?: Req,
  options?: Omit<RequestOptions<Req>, 'path' | 'method' | 'data'>,
): Promise<ApiResponse<Res>> {
  return request<Req, Res>({ path, method: 'DELETE', data, ...options });
}

/**
 * 便捷方法：PATCH 请求
 */
export function patch<Req = any, Res = any>(
  path: string,
  data?: Req,
  options?: Omit<RequestOptions<Req>, 'path' | 'method' | 'data'>,
): Promise<ApiResponse<Res>> {
  return request<Req, Res>({ path, method: 'PATCH', data, ...options });
}

export default request;

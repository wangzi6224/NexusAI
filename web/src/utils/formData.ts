/**
 * 将 JSON 对象转换为 FormData
 * 支持：File、Blob、数组、嵌套对象
 */
export function toFormData(data: Record<string, any>, formData?: FormData, parentKey?: string): FormData {
  const fd = formData || new FormData();

  if (!data || typeof data !== 'object') {
    return fd;
  }

  Object.keys(data).forEach((key) => {
    const value = data[key];
    const formKey = parentKey ? `${parentKey}[${key}]` : key;

    if (value === null || value === undefined) {
      // 跳过 null 和 undefined
      return;
    }

    if (value instanceof File || value instanceof Blob) {
      // File 或 Blob 直接添加
      fd.append(formKey, value);
    } else if (Array.isArray(value)) {
      // 数组处理
      value.forEach((item, index) => {
        if (item instanceof File || item instanceof Blob) {
          // 文件数组
          fd.append(formKey, item);
        } else if (typeof item === 'object' && item !== null) {
          // 对象数组：递归处理
          toFormData({ [index]: item }, fd, formKey);
        } else {
          // 基本类型数组
          fd.append(`${formKey}[]`, String(item));
        }
      });
    } else if (typeof value === 'object' && !(value instanceof Date)) {
      // 嵌套对象：使用 JSON.stringify
      // 根据后端需求，可以选择递归展开或序列化
      // 这里使用序列化方式，更通用
      fd.append(formKey, JSON.stringify(value));
    } else {
      // 基本类型（string, number, boolean, Date）
      fd.append(formKey, String(value));
    }
  });

  return fd;
}

/**
 * 判断对象中是否包含 File 或 Blob
 */
export function hasFileOrBlob(data: any): boolean {
  if (!data || typeof data !== 'object') {
    return false;
  }

  if (data instanceof File || data instanceof Blob) {
    return true;
  }

  if (Array.isArray(data)) {
    return data.some((item) => hasFileOrBlob(item));
  }

  return Object.values(data).some((value) => hasFileOrBlob(value));
}

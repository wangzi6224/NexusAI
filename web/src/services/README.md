# Services 接口定义规范

## 📁 文件结构

```
src/services/
├── demo/
│   ├── types.ts       # 类型定义（命名空间）
│   ├── api.ts         # API 方法
│   └── README.md      # 使用说明
└── user/
    ├── types.ts
    └── api.ts
```

## 📝 定义接口步骤

### 1️⃣ 定义类型（types.ts）

使用命名空间，数组格式：`[请求参数, 响应数据]`

```typescript
// types.ts
export namespace UserAPI {
  export type GetList = [
    { page: number; pageSize: number }, // 入参
    { list: User[]; total: number }, // 出参
  ];
}
```

### 2️⃣ 定义 API 方法（api.ts）

```typescript
// api.ts
import { request } from '@/utils/request';
import { UserAPI } from './types';

export function getUserList(params: UserData.GetList[0]) {
  return request<UserData.GetList[0], UserData.GetList[1]>({
    path: '/api/users',
    method: 'GET',
    data: params,
  });
}
```

### 3️⃣ 使用

```typescript
import { getUserList } from '@/services/demo/api';

const { data } = await getUserList({ page: 1, pageSize: 10 });
console.log(data.list); // 类型安全
```

## 🎯 请求配置示例

### GET 请求

```typescript
// types.ts
export namespace UserAPI {
  export type GetInfo = [{ userId: number }, UserInfo];
}

// api.ts
export function getUserInfo(params: UserAPI.GetInfo[0]) {
  return request<UserAPI.GetInfo[0], UserAPI.GetInfo[1]>({
    path: '/api/user/info',
    method: 'GET',
    data: params, // 自动转为 ?userId=123
  });
}
```

### POST 请求

```typescript
// types.ts
export namespace UserAPI {
  export type Create = [{ name: string; email: string }, { userId: number }];
}

// api.ts
export function createUser(data: UserAPI.Create[0]) {
  return request<UserAPI.Create[0], UserAPI.Create[1]>({
    path: '/api/users',
    method: 'POST',
    data, // JSON body
  });
}
```

### FormData 上传

```typescript
// types.ts
export namespace UploadAPI {
  export type Avatar = [{ file: File; userId: number }, { url: string }];
}

// api.ts
export function uploadAvatar(data: UploadAPI.Avatar[0]) {
  return request<UploadAPI.Avatar[0], UploadAPI.Avatar[1]>({
    path: '/api/upload',
    method: 'POST',
    data,
    requestType: 'formdata', // 自动转换
  });
}
```

### 自定义 Header

```typescript
export function createUser(data: UserData.Create[0]) {
  return request<UserData.Create[0], UserData.Create[1]>({
    path: '/api/users',
    method: 'POST',
    data,
    headers: {
      'X-Trace-Id': '123',
      'X-Custom': 'value',
    },
  });
}
```

### 设置超时

```typescript
export function uploadFile(data: UploadAPI.File[0]) {
  return request<UploadAPI.File[0], UploadAPI.File[1]>({
    path: '/api/upload',
    method: 'POST',
    data,
    requestType: 'formdata',
    timeout: 60000, // 60秒
  });
}
```

### 取消请求

```typescript
export function search(params: SearchAPI.Global[0], signal?: AbortSignal) {
  return request<SearchAPI.Global[0], SearchAPI.Global[1]>({
    path: '/api/search',
    method: 'GET',
    data: params,
    signal, // AbortController.signal
  });
}

// 使用
const controller = new AbortController();
search({ keyword: 'test' }, controller.signal);
controller.abort(); // 取消
```

### 静默请求（不显示错误提示）

```typescript
export function checkUsername(username: string) {
  return request<UserData.CheckUsername[0], UserData.CheckUsername[1]>({
    path: '/api/check/username',
    method: 'GET',
    data: { username },
    silent: true, // 不显示错误提示
  });
}
```

### 下载文件（Blob）

```typescript
// types.ts
export namespace FileAPI {
  export type Download = [{ fileId: string }, Blob];
}

// api.ts
export function downloadFile(fileId: string) {
  return request<FileAPI.Download[0], FileAPI.Download[1]>({
    path: '/api/files/download',
    method: 'GET',
    data: { fileId },
    responseType: 'blob',
  });
}
```

### PUT / PATCH / DELETE

```typescript
// PUT
export function updateUser(data: UserData.Update[0]) {
  return request<UserData.Update[0], UserData.Update[1]>({
    path: '/api/users/123',
    method: 'PUT',
    data,
  });
}

// PATCH
export function patchUser(data: UserData.Patch[0]) {
  return request<UserData.Patch[0], UserData.Patch[1]>({
    path: '/api/users/123',
    method: 'PATCH',
    data,
  });
}

// DELETE
export function deleteUser(params: UserData.Delete[0]) {
  return request<UserData.Delete[0], UserData.Delete[1]>({
    path: '/api/users/123',
    method: 'DELETE',
    data: params, // 自动转为 query
  });
}
```

## 📌 命名空间组织

### 按模块分类

```typescript
// types.ts
export namespace UserAPI {
  export type GetList = [/* ... */];
  export type Create = [/* ... */];
  export type Update = [/* ... */];
}

export namespace OrderAPI {
  export type GetList = [/* ... */];
  export type Create = [/* ... */];
}

export namespace ProductAPI {
  export type GetList = [/* ... */];
  export type GetDetail = [/* ... */];
}
```

### 共享类型

```typescript
// 公共类型定义在命名空间外部
interface User {
  id: number;
  name: string;
}

interface Pagination {
  page: number;
  pageSize: number;
}

// 在命名空间中使用
export namespace UserAPI {
  export type GetList = [
    Pagination & { keyword?: string },
    { list: User[]; total: number },
  ];
}
```

## ✅ 最佳实践

```typescript
// ❌ 不推荐：直接定义接口
export async function getUser(userId: number): Promise<UserInfo> {
  const res = await request({...});
  return res.data;
}

// ✅ 推荐：使用命名空间
export namespace UserAPI {
  export type GetInfo = [{ userId: number }, UserInfo];
}

export function getUserInfo(params: UserAPI.GetInfo[0]) {
  return request<UserAPI.GetInfo[0], UserAPI.GetInfo[1]>({...});
}
```

## 🎨 完整示例

```typescript
// types.ts
interface User {
  id: number;
  name: string;
  email: string;
}

export namespace UserAPI {
  export type GetList = [
    { page: number; pageSize: number; keyword?: string },
    { list: User[]; total: number },
  ];

  export type Create = [
    { name: string; email: string; password: string },
    { userId: number; createdAt: string },
  ];

  export type Update = [
    { userId: number; name?: string; email?: string },
    void,
  ];

  export type Delete = [{ userId: number }, void];
}

// api.ts
import { request } from '@/utils/request';
import { UserAPI } from './types';

export function getUserList(params: UserAPI.GetList[0]) {
  return request<UserAPI.GetList[0], UserAPI.GetList[1]>({
    path: '/api/users',
    method: 'GET',
    data: params,
  });
}

export function createUser(data: UserAPI.Create[0]) {
  return request<UserAPI.Create[0], UserAPI.Create[1]>({
    path: '/api/users',
    method: 'POST',
    data,
  });
}

export function updateUser(data: UserAPI.Update[0]) {
  return request<UserAPI.Update[0], UserAPI.Update[1]>({
    path: `/api/users/${data.userId}`,
    method: 'PUT',
    data,
  });
}

export function deleteUser(params: UserAPI.Delete[0]) {
  return request<UserAPI.Delete[0], UserAPI.Delete[1]>({
    path: `/api/users/${params.userId}`,
    method: 'DELETE',
    data: params,
  });
}

// 页面使用
import { getUserList, createUser } from '@/services/demo/api';

// 获取列表
const { data } = await getUserList({ page: 1, pageSize: 10 });
console.log(data.list, data.total);

// 创建用户
const { data: result } = await createUser({
  name: 'John',
  email: 'john@example.com',
  password: '123456',
});
console.log(result.userId);
```

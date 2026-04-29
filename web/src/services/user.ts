import { request } from '@/utils/request';

export const getUserInfo = () => {
  return request<UserData.UserInfo[0], UserData.UserInfo[1]>({
    path: '/api/pluginv4/userinfo',
    method: 'GET',
  });
};

export function getInitData() {
  return request<UserData.InitInfo[0], UserData.InitInfo[1]>({
    path: '/api/announce/qa/init',
    method: 'GET',
  });
}

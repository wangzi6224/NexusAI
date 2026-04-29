// 运行时配置
import { getInitData, getUserInfo } from '@/services/user';
import '../tailwind.css';
import './styles/init.css';
import './styles/variables.css';
import { getToken, getTokenAndSignFromQuery, setToken } from './utils/token';

// 全局初始化数据配置，用于 Layout 用户信息和权限初始化
// 更多信息见文档：https://umijs.org/docs/api/runtime-config#getinitialstate
export async function getInitialState(): Promise<
  (UserData.UserInfo[1] & UserData.InitInfo[1]) | null
> {
  try {
    const resToken = getTokenAndSignFromQuery();
    if (resToken) {
      setToken({ value: resToken });
    } else {
      const localToken = getToken();
      if (!localToken) {
        location.href = '/';
      }
    }

    const useInfo = await getUserInfo();
    const setting = await getInitData();

    return {
      ...(useInfo?.data || {}),
      ...(setting?.data || {}),
    };
  } catch (err) {
    console.error(err);
    location.href = '/';
    return null;
  }
}

export const layout = () => {
  return {
    menu: {
      locale: false,
    },
    contentStyle: {
      padding: 0,
      display: 'block',
    },
    menuRender: false,
  };
};

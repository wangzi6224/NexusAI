import { TOKEN_KEY } from '@/constants';

export type Token = {
  value: {
    token: string;
    sign: string;
  };
};

const getToken = (): Token['value'] | null | undefined => {
  const tokenString = localStorage.getItem(TOKEN_KEY);
  if (!tokenString) {
    return null;
  }
  try {
    return JSON.parse(tokenString)?.value as Token['value'];
  } catch (error) {
    return null;
  }
};

const setToken = (token: Token) => {
  // 从query中获取然后设置到localStorage
  localStorage.setItem(TOKEN_KEY, JSON.stringify(token));
};

const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY);
};

const getTokenAndSignFromQuery = (): Token['value'] | null => {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('xtoken');
  const sign = urlParams.get('sign');
  if (token && sign) {
    return { token, sign };
  }
  return null;
};

export { getToken, getTokenAndSignFromQuery, removeToken, setToken };

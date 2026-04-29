// 运行时配置
import '../tailwind.css';
import './styles/init.css';
import './styles/variables.css';

export async function getInitialState(): Promise<Record<string, never>> {
  return {};
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

import { COLOR_PRIMARY } from '@/constants';
import { ChatProvider } from '@/contexts/ChatContext';
import { XProvider } from '@ant-design/x';
import xZhCN from '@ant-design/x/locale/zh_CN';
import { ConfigProvider, theme } from 'antd';
import React from 'react';
import ChatLayout from '../../components/ChatLayout';

const HomePage: React.FC = () => {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          borderRadius: 4,
          colorPrimary: COLOR_PRIMARY,
          colorBgContainer: 'rgba(255,255,255, 0.2)',
        },
        components: {
          Select: {
            colorBorder: COLOR_PRIMARY,
            colorBgContainer: 'rgba(255,61,154,0.12)',
            optionSelectedColor: COLOR_PRIMARY,
          },
          Button: {},
        },
      }}
    >
      <XProvider
        locale={{
          ...xZhCN,
          Actions: {
            ...xZhCN.Actions,
            feedbackLike: '有帮助',
            feedbackDislike: '无帮助',
          },
        }}
      >
        <ChatProvider>
          <ChatLayout />
        </ChatProvider>
      </XProvider>
    </ConfigProvider>
  );
};

export default HomePage;

import { useChatContext } from '@/contexts/ChatContext';
import { useModel } from '@@/exports';
import { Typography } from 'antd';
import React, { useEffect, useState } from 'react';
import icon1 from '../../assets/images/icon.png';
import ChatSenderInput from '../ChatSenderInput';
import styles from './index.module.less';

const { Text } = Typography;

const TITLE_BEFORE = 'Hi~\u00a0\u00a0我是你的';
const TITLE_HIGHLIGHT = '专属AI合规助手';
const FULL_TITLE_LEN = TITLE_BEFORE.length + TITLE_HIGHLIGHT.length;

const WelcomeScreen: React.FC = () => {
  const { sendMessage } = useChatContext();
  const { initialState } = useModel('@@initialState');
  const [visibleCount, setVisibleCount] = useState(0);

  useEffect(() => {
    if (visibleCount >= FULL_TITLE_LEN) return;
    const timer = setTimeout(() => {
      setVisibleCount((prev) => prev + 1);
    }, 80);
    return () => clearTimeout(timer);
  }, [visibleCount]);

  const visibleBefore = TITLE_BEFORE.slice(
    0,
    Math.min(visibleCount, TITLE_BEFORE.length),
  );
  const visibleHighlight =
    visibleCount > TITLE_BEFORE.length
      ? TITLE_HIGHLIGHT.slice(0, visibleCount - TITLE_BEFORE.length)
      : '';

  return (
    <div className={styles.container}>
      <div className={styles.bgPattern} />

      <div className={styles.content}>
        <div className={styles.titleWrapper}>
          <Text className={styles.title}>
            {visibleBefore}
            {visibleHighlight && (
              <span className={styles.titleHighlight}>{visibleHighlight}</span>
            )}
          </Text>
          <Text className={styles.subtitle}>
            任何法律法规相关问题，都可以问我哦
          </Text>
        </div>

        <div className={styles.inputWrapper}>
          <ChatSenderInput autoSize={{ minRows: 7, maxRows: 7 }} />
        </div>

        <div className={styles.promptsWrapper}>
          {initialState?.quick_questions.map((p) => (
            <div
              key={p}
              className={styles.promptCard}
              onClick={() => sendMessage(p)}
            >
              <img src={icon1} alt="" className={styles.promptIcon} />
              <Text className={styles.promptText} ellipsis>
                {p}
              </Text>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;

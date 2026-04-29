import type { ActionsFeedbackProps } from '@ant-design/x';
import { Actions } from '@ant-design/x';
import React from 'react';
import styles from './index.module.less';

interface FeedbackFooterProps {
  messageId?: number;
  helpful?: boolean;
}

const FeedbackFooter: React.FC<FeedbackFooterProps> = ({ helpful }) => {
  const value: ActionsFeedbackProps['value'] =
    helpful === true ? 'like' : helpful === false ? 'dislike' : 'default';

  const actionItems = [
    {
      key: 'feedback',
      actionRender: () => (
        <Actions.Feedback key="feedback" value={value} onChange={() => {}} />
      ),
    },
  ];

  return (
    <div className={styles.feedbackSection}>
      <div className={styles.feedbackActions}>
        <Actions items={actionItems} onClick={() => {}} />
      </div>
    </div>
  );
};

export default FeedbackFooter;

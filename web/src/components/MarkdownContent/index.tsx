import { Typography } from 'antd';
import React from 'react';
import styles from './index.module.less';

const { Title, Paragraph } = Typography;

interface MarkdownContentProps {
  content: string;
}

/**
 * Simple markdown renderer that handles headings and paragraphs.
 * Supports: # h1, ## h2, ### h3, #### h4, and plain paragraph text.
 */
const MarkdownContent: React.FC<MarkdownContentProps> = ({ content }) => {
  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];
  let paragraphBuffer: string[] = [];

  const flushParagraph = (key: string) => {
    if (paragraphBuffer.length > 0) {
      const text = paragraphBuffer.join(' ').trim();
      if (text) {
        elements.push(
          <Paragraph key={key} className={styles.paragraph}>
            {text}
          </Paragraph>,
        );
      }
      paragraphBuffer = [];
    }
  };

  lines.forEach((line, index) => {
    const trimmed = line.trim();

    if (trimmed.startsWith('#### ')) {
      flushParagraph(`p-before-${index}`);
      elements.push(
        <Title key={`h4-${index}`} level={5} className={styles.h4}>
          {trimmed.slice(5)}
        </Title>,
      );
    } else if (trimmed.startsWith('### ')) {
      flushParagraph(`p-before-${index}`);
      elements.push(
        <Title key={`h3-${index}`} level={4} className={styles.h3}>
          {trimmed.slice(4)}
        </Title>,
      );
    } else if (trimmed.startsWith('## ')) {
      flushParagraph(`p-before-${index}`);
      elements.push(
        <Title key={`h2-${index}`} level={3} className={styles.h2}>
          {trimmed.slice(3)}
        </Title>,
      );
    } else if (trimmed.startsWith('# ')) {
      flushParagraph(`p-before-${index}`);
      elements.push(
        <Title key={`h1-${index}`} level={2} className={styles.h1}>
          {trimmed.slice(2)}
        </Title>,
      );
    } else if (trimmed === '') {
      flushParagraph(`p-empty-${index}`);
    } else {
      paragraphBuffer.push(trimmed);
    }
  });

  flushParagraph('p-final');

  return <div className={styles.container}>{elements}</div>;
};

export default MarkdownContent;

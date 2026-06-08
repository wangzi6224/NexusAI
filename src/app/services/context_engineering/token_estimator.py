class TokenEstimator:
    """轻量 token 估算器。

    中文按 1 字约 1 token。
    英文按 4 字符约 1 token。
    这是估算，不是精确计费。
    """

    def estimate(self, text: str) -> int:
        if not text:
            return 0

        chinese_chars = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
        other_chars = len(text) - chinese_chars
        return chinese_chars + max(1, other_chars // 4)

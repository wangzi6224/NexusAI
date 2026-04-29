declare namespace UserData {
  /**
   * 用户设置类型定义
   */
  type Settings = {
    /**
     * 是否启用网络搜索功能
     */
    enable_web_search: boolean;
    /**
     * 默认交易所
     */
    sector: string;
  };

  type UserInfo = [
    null,
    {
      is_password?: boolean;
      /**
       * 用户ID
       */
      uid: int;
      /**
       * 用户手机号
       */
      phone: string;
      /**
       * 用户昵称
       */
      nickname: string;
      /**
       * 状态
       */
      status: int;
      /**
       * 用户创建时间戳
       */
      createdAt: int;
      /**
       * 用户头像
       */
      avatar: string;
      is_bind_wechat?: boolean;
      wechat_nickname?: string;
      corp?: string;
      duty?: string;
      source?: 'yunnanexpo' | string;

      /**
       * 用于登陆 xtoken sign
       */
      xtoken: string;
      sign: string;
      /**
       * 用户过期时间
       */
      expiration_date: string;
      account_type: AccountType;
      old_url?: string;
    },
  ];

  type InitInfo = [
    null,
    {
      /**
       * 快速提问列表
       */
      quick_questions: string[];
      /**
       * 可选的交易所列表
       */
      sectors: string[];
      /**
       * 服务器时间戳
       */
      server_time: number;
      /**
       * 用户会话列表
       */
      sessions: Array<{
        session_id: number;
        title: string;
        updated_at: number;
      }>;
      /**
       * 用户设置
       */
      settings: Settings;
    },
  ];
}

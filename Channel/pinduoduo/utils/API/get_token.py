from ..base_request import BaseRequest


class ChatNotEnabledError(RuntimeError):
    """The merchant platform hasn't enabled this shop's chat service."""


class GetToken(BaseRequest):
    def __init__(self, shop_id, user_id, channel_name="pinduoduo"):
        super().__init__(shop_id, user_id, channel_name)

    def get_token(self):
        """
        根据提供的店铺名获取对应的token
        Returns:
            str: 成功返回token字符串
            None: 获取失败返回None
        """
        url = "https://mms.pinduoduo.com/chats/getToken"
        payload = {'version': '3'}

        result = self.post(url, data=payload)
        
        if isinstance(result, dict):
            token = result.get('token')
            if isinstance(token, str) and token:
                return token

            nested = result.get('result')
            if isinstance(nested, dict):
                token = nested.get('token')
                if isinstance(token, str) and token:
                    return token

            if nested is False and result.get('enableByCs') is False:
                raise ChatNotEnabledError(
                    "店铺聊天尚未开启，请在拼多多商家后台查看开通条件；"
                    "新店需等待首件商品审核通过。"
                )

            self.logger.error(
                f"账号 {self.account_name} 无法从响应中获取token; "
                f"response_keys={sorted(result.keys())}"
            )
        elif result is not None:
            self.logger.error(
                f"账号 {self.account_name} 获取token的响应类型异常: "
                f"{type(result).__name__}"
            )
        
        return None




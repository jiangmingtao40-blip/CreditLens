package com.zbkj.common.service.credit;

import cn.hutool.http.HttpUtil;
import com.alibaba.fastjson.JSONObject;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/**
 * 微信小程序服务端 API 调用
 */
@Slf4j
@Service
public class WechatMiniAppService {

    private static final String CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session";

    @Value("${wechat.mini-app.app-id:}")
    private String appId;

    @Value("${wechat.mini-app.app-secret:}")
    private String appSecret;

    /**
     * 用 code 换取 openid 和 session_key
     * @param code 前端 wx.login() 返回的临时凭证
     * @return { openid, session_key, unionid }，失败返回 null
     */
    public JSONObject code2session(String code) {
        if (isMockMode()) {
            return mockCode2session(code);
        }

        String url = CODE2SESSION_URL
                + "?appid=" + appId
                + "&secret=" + appSecret
                + "&js_code=" + code
                + "&grant_type=authorization_code";

        log.info("调用 jscode2session: appId={}, code={}", appId, code);

        try {
            String response = HttpUtil.get(url, 10000);
            log.info("微信返回: {}", response);

            JSONObject result = JSONObject.parseObject(response);

            if (result.containsKey("errcode") && result.getInteger("errcode") != 0) {
                log.error("jscode2session 失败: errcode={}, errmsg={}",
                        result.getInteger("errcode"), result.getString("errmsg"));
                return null;
            }

            return result;
        } catch (Exception e) {
            log.error("调用微信 jscode2session 异常", e);
            return null;
        }
    }

    /**
     * 未配置真实 AppId 时的 Mock 模式
     */
    private boolean isMockMode() {
        return appId == null || appId.isEmpty() || appId.startsWith("your_");
    }

    /**
     * Mock 登录：用 code 的 hash 生成一个模拟 openid
     */
    private JSONObject mockCode2session(String code) {
        log.warn("使用 Mock 模式登录（未配置真实微信 AppId）");
        // 用 code 哈希生成确定的 mock openid
        String mockOpenid = "mock_" + Integer.toHexString(code.hashCode());
        JSONObject result = new JSONObject();
        result.put("openid", mockOpenid);
        result.put("session_key", "mock_session_key");
        return result;
    }
}

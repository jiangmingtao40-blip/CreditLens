package com.zbkj.admin.filter;

import cn.hutool.core.util.ObjectUtil;
import cn.hutool.core.util.StrUtil;
import com.zbkj.common.constants.Constants;
import com.zbkj.common.vo.LoginUserVo;
import org.springframework.stereotype.Component;

import javax.servlet.http.HttpServletRequest;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class TokenComponent {

    private static final Long MILLIS_MINUTE_TEN = 20 * 60 * 1000L;

    private static final Long MILLIS_MINUTE = 60 * 1000L;

    private static final int expireTime = 5 * 60;

    private static final String TOKEN_REDIS = "TOKEN:ADMIN:";

    private static final ConcurrentHashMap<String, LoginUserVo> tokenMap = new ConcurrentHashMap<>();

    public LoginUserVo getLoginUser(HttpServletRequest request) {
        String token = getToken(request);
        if (StrUtil.isNotEmpty(token)) {
            String userKey = getTokenKey(token);
            LoginUserVo loginUser = tokenMap.get(userKey);
            if (loginUser != null) {
                long currentTime = System.currentTimeMillis();
                if (currentTime > loginUser.getExpireTime()) {
                    tokenMap.remove(userKey);
                    return null;
                }
                return loginUser;
            }
        }
        return null;
    }

    public void setLoginUser(LoginUserVo loginUser) {
        if (ObjectUtil.isNotNull(loginUser) && StrUtil.isNotEmpty(loginUser.getToken())) {
            refreshToken(loginUser);
        }
    }

    public void delLoginUser(String token) {
        if (StrUtil.isNotEmpty(token)) {
            String userKey = getTokenKey(token);
            tokenMap.remove(userKey);
        }
    }

    public String createToken(LoginUserVo loginUser) {
        String token = UUID.randomUUID().toString().replace("-", "");
        loginUser.setToken(token);
        refreshToken(loginUser);
        return token;
    }

    public void verifyToken(LoginUserVo loginUser) {
        long expireTime = loginUser.getExpireTime();
        long currentTime = System.currentTimeMillis();
        if (expireTime - currentTime <= MILLIS_MINUTE_TEN) {
            refreshToken(loginUser);
        }
    }

    public void refreshToken(LoginUserVo loginUser) {
        loginUser.setLoginTime(System.currentTimeMillis());
        loginUser.setExpireTime(loginUser.getLoginTime() + expireTime * MILLIS_MINUTE);
        String userKey = getTokenKey(loginUser.getToken());
        tokenMap.put(userKey, loginUser);
    }

    private String getToken(HttpServletRequest request) {
        String token = request.getHeader(Constants.HEADER_AUTHORIZATION_KEY);
        if (StrUtil.isNotEmpty(token) && token.startsWith(TOKEN_REDIS)) {
            token = token.replace(TOKEN_REDIS, "");
        }
        return token;
    }

    private String getTokenKey(String uuid) {
        return TOKEN_REDIS + uuid;
    }
}

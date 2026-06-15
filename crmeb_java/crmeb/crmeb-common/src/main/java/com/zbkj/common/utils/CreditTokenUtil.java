package com.zbkj.common.utils;

import cn.hutool.core.util.StrUtil;
import com.zbkj.common.model.credit.CreditUser;
import com.zbkj.common.service.credit.CreditUserService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;

/**
 * 征信模块 Token 工具类
 * 统一处理 Token 生成、存储、解析，供所有 Controller 使用
 */
@Slf4j
@Component
public class CreditTokenUtil {

    private static final String TOKEN_PREFIX = "credit_token:";
    private static final long TOKEN_EXPIRE_SECONDS = 30L * 24 * 3600; // 30天

    private static CreditTokenUtil instance;

    @Autowired
    private RedisUtil redisUtil;

    @Autowired
    private CreditUserService creditUserService;

    @PostConstruct
    public void init() {
        instance = this;
    }

    /**
     * 存储 Token → userId 映射到 Redis
     */
    public void storeToken(String token, Long userId) {
        String key = TOKEN_PREFIX + token;
        redisUtil.set(key, userId.toString(), TOKEN_EXPIRE_SECONDS);
        log.debug("Token存储: token={}, userId={}", token, userId);
    }

    /**
     * 从 Redis 中解析 Token → userId
     * @param token 完整的 Authorization header 值（含 "Bearer " 前缀或纯 token）
     * @return userId，解析失败返回 null
     */
    public Long resolveUserId(String token) {
        if (StrUtil.isBlank(token)) {
            return null;
        }

        // 去掉 "Bearer " 前缀
        String pureToken = token.startsWith("Bearer ") ? token.substring(7) : token;

        String key = TOKEN_PREFIX + pureToken;
        String userIdStr = redisUtil.get(key);
        if (StrUtil.isBlank(userIdStr)) {
            log.warn("Token无效或已过期: {}", pureToken);
            return null;
        }

        try {
            return Long.parseLong(userIdStr);
        } catch (NumberFormatException e) {
            log.error("Token对应的userId格式异常: {}", userIdStr);
            return null;
        }
    }

    /**
     * 从 Token 获取用户实体
     */
    public CreditUser resolveUser(String token) {
        Long userId = resolveUserId(token);
        if (userId == null) {
            return null;
        }
        return creditUserService.getById(userId);
    }

    /**
     * 从 Token 获取 userId，失败抛异常
     */
    public Long requireUserId(String token) {
        Long userId = resolveUserId(token);
        if (userId == null) {
            throw new RuntimeException("登录已过期，请重新登录");
        }
        return userId;
    }

    /**
     * 删除 Token（退出登录）
     */
    public void removeToken(String token) {
        String pureToken = token.startsWith("Bearer ") ? token.substring(7) : token;
        redisUtil.delete(TOKEN_PREFIX + pureToken);
        log.debug("Token已删除: {}", pureToken);
    }

    // ─── 静态方法（供非 Spring Bean 使用）───

    public static Long getUserId(String token) {
        if (instance == null) {
            log.error("CreditTokenUtil 未初始化");
            return null;
        }
        return instance.resolveUserId(token);
    }

    public static CreditUser getUser(String token) {
        if (instance == null) {
            log.error("CreditTokenUtil 未初始化");
            return null;
        }
        return instance.resolveUser(token);
    }

    public static void saveToken(String token, Long userId) {
        if (instance != null) {
            instance.storeToken(token, userId);
        }
    }

    public static void deleteToken(String token) {
        if (instance != null) {
            instance.removeToken(token);
        }
    }
}

package com.zbkj.common.service.credit;

import cn.hutool.core.util.IdUtil;
import cn.hutool.core.util.StrUtil;
import cn.hutool.crypto.SecureUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.zbkj.common.dao.credit.CreditUserDao;
import com.zbkj.common.model.credit.CreditUser;
import com.zbkj.common.response.credit.LoginResponse;
import com.zbkj.common.response.credit.UserInfoResponse;
import com.zbkj.common.utils.CreditTokenUtil;
import com.zbkj.common.utils.RedisUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.Date;

/**
 * 征信用户服务
 */
@Slf4j
@Service
public class CreditUserService extends ServiceImpl<CreditUserDao, CreditUser> {

    private static final String TOKEN_PREFIX = "credit_token:";
    private static final long TOKEN_EXPIRE_SECONDS = 30L * 24 * 3600; // 30天

    @Autowired
    private RedisUtil redisUtil;

    /**
     * 微信登录
     */
    @Transactional(rollbackFor = Exception.class)
    public LoginResponse wxLogin(String openid, String nickname, String avatar, String inviteCode) {
        log.info("微信登录: openid={}, nickname={}, inviteCode={}", openid, nickname, inviteCode);

        // 查询用户是否存在
        CreditUser user = getOne(new LambdaQueryWrapper<CreditUser>()
                .eq(CreditUser::getOpenid, openid)
                .eq(CreditUser::getIsDeleted, 0));

        boolean isNew = false;
        if (user == null) {
            // 新用户注册
            user = registerUser(openid, nickname, avatar, inviteCode);
            isNew = true;
            log.info("新用户注册: userId={}", user.getId());
        } else {
            // 老用户更新信息
            user.setNickname(nickname);
            user.setAvatar(avatar);
            user.setLastLoginTime(new Date());
            updateById(user);
            log.info("老用户登录: userId={}", user.getId());
        }

        // 生成Token
        String token = generateToken(user.getId());

        // 存储 Token → userId 到 Redis（30天有效）
        redisUtil.set(TOKEN_PREFIX + token, user.getId().toString(), TOKEN_EXPIRE_SECONDS);

        // 构建响应
        LoginResponse response = new LoginResponse();
        response.setUserId(user.getId());
        response.setToken(token);
        response.setNickname(user.getNickname());
        response.setAvatar(user.getAvatar());
        response.setPhone(user.getPhone());
        response.setFreeCount(user.getFreeCount());
        response.setIsVip(user.getIsVip() == 1);
        response.setVipExpireTime(user.getVipExpireTime());
        response.setInviteCode(user.getInviteCode());
        response.setTotalCommission(user.getTotalCommission());
        response.setAvailableCommission(user.getAvailableCommission());
        response.setIsNew(isNew);

        return response;
    }

    /**
     * 注册新用户
     */
    private CreditUser registerUser(String openid, String nickname, String avatar, String inviteCode) {
        CreditUser user = new CreditUser();
        user.setOpenid(openid);
        user.setNickname(nickname);
        user.setAvatar(avatar);
        user.setFreeCount(3); // 默认3次免费
        user.setIsVip(0);
        user.setTotalCommission(BigDecimal.ZERO);
        user.setAvailableCommission(BigDecimal.ZERO);
        user.setFrozenCommission(BigDecimal.ZERO);
        user.setStatus(1);
        user.setLastLoginTime(new Date());
        user.setCreateTime(new Date());
        user.setUpdateTime(new Date());
        user.setIsDeleted(0);

        // 生成邀请码
        user.setInviteCode(generateInviteCode(openid));

        // 处理邀请关系
        if (StrUtil.isNotBlank(inviteCode)) {
            CreditUser inviter = getOne(new LambdaQueryWrapper<CreditUser>()
                    .eq(CreditUser::getInviteCode, inviteCode)
                    .eq(CreditUser::getIsDeleted, 0));
            if (inviter != null) {
                user.setInvitedBy(inviter.getId());
                // TODO: 创建邀请记录
            }
        }

        save(user);
        return user;
    }

    /**
     * 生成邀请码
     */
    private String generateInviteCode(String openid) {
        return "INV" + SecureUtil.md5(openid + System.currentTimeMillis()).substring(0, 8).toUpperCase();
    }

    /**
     * 生成Token
     */
    private String generateToken(Long userId) {
        return SecureUtil.md5(userId + "_" + System.currentTimeMillis() + "_" + IdUtil.simpleUUID());
    }

    /**
     * 根据Token获取用户
     */
    public CreditUser getUserByToken(String token) {
        if (StrUtil.isBlank(token)) {
            return null;
        }
        // 去掉 "Bearer " 前缀
        String pureToken = token.startsWith("Bearer ") ? token.substring(7) : token;

        String userIdStr = redisUtil.get(TOKEN_PREFIX + pureToken);
        if (StrUtil.isBlank(userIdStr)) {
            return null;
        }

        try {
            Long userId = Long.parseLong(userIdStr);
            return getById(userId);
        } catch (NumberFormatException e) {
            log.error("Token对应的userId格式异常: {}", userIdStr);
            return null;
        }
    }

    /**
     * 根据用户ID获取用户信息
     */
    public UserInfoResponse getUserInfo(Long userId) {
        CreditUser user = getById(userId);
        if (user == null || user.getIsDeleted() == 1) {
            return null;
        }

        UserInfoResponse response = new UserInfoResponse();
        response.setUserId(user.getId());
        response.setNickname(user.getNickname());
        response.setAvatar(user.getAvatar());
        response.setPhone(user.getPhone());
        response.setFreeCount(user.getFreeCount());
        response.setIsVip(user.getIsVip() == 1);
        response.setVipExpireTime(user.getVipExpireTime());
        response.setInviteCode(user.getInviteCode());
        response.setTotalCommission(user.getTotalCommission());
        response.setAvailableCommission(user.getAvailableCommission());
        response.setFrozenCommission(user.getFrozenCommission());

        // TODO: 查询统计数据
        response.setTotalReports(0);
        response.setCompletedReports(0);
        response.setTotalCost(BigDecimal.ZERO);

        return response;
    }

    /**
     * 扣减免费次数
     */
    @Transactional(rollbackFor = Exception.class)
    public boolean deductFreeCount(Long userId) {
        CreditUser user = getById(userId);
        if (user == null || user.getFreeCount() <= 0) {
            return false;
        }

        user.setFreeCount(user.getFreeCount() - 1);
        return updateById(user);
    }
}

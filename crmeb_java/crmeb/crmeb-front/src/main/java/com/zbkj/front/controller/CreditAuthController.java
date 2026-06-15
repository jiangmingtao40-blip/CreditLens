package com.zbkj.front.controller;

import com.zbkj.common.result.CommonResult;
import com.zbkj.common.response.credit.LoginResponse;
import com.zbkj.common.response.credit.UserInfoResponse;
import com.zbkj.common.service.credit.CreditUserService;
import com.zbkj.common.service.credit.WechatMiniAppService;
import com.zbkj.common.utils.CreditTokenUtil;
import com.alibaba.fastjson.JSONObject;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 征信用户认证控制器
 */
@Slf4j
@RestController("CreditAuthFrontController")
@RequestMapping("api/credit/auth")
@Api(tags = "征信用户认证")
public class CreditAuthController {

    @Autowired
    private CreditUserService creditUserService;

    @Autowired
    private WechatMiniAppService wechatMiniAppService;

    /**
     * 微信登录
     */
    @ApiOperation(value = "微信登录")
    @RequestMapping(value = "/wxLogin", method = RequestMethod.POST)
    public CommonResult<LoginResponse> wxLogin(
            @RequestParam String code,
            @RequestParam(required = false) String nickname,
            @RequestParam(required = false) String avatar,
            @RequestParam(required = false) String inviteCode) {
        
        log.info("微信登录请求: code={}, nickname={}, inviteCode={}", code, nickname, inviteCode);
        
        try {
            // 调用微信 API 换取 openid
            JSONObject wxResult = wechatMiniAppService.code2session(code);
            if (wxResult == null) {
                return CommonResult.failed("微信登录失败，请重试");
            }

            String openid = wxResult.getString("openid");
            if (openid == null || openid.isEmpty()) {
                return CommonResult.failed("获取用户openid失败");
            }
            
            // 默认昵称和头像
            if (nickname == null || nickname.isEmpty()) {
                nickname = "用户" + System.currentTimeMillis() % 10000;
            }
            if (avatar == null || avatar.isEmpty()) {
                avatar = "";
            }
            
            LoginResponse response = creditUserService.wxLogin(openid, nickname, avatar, inviteCode);
            return CommonResult.success(response);
        } catch (Exception e) {
            log.error("微信登录失败", e);
            return CommonResult.failed("登录失败: " + e.getMessage());
        }
    }

    /**
     * 获取用户信息
     */
    @ApiOperation(value = "获取用户信息")
    @RequestMapping(value = "/userInfo", method = RequestMethod.GET)
    public CommonResult<UserInfoResponse> getUserInfo(@RequestHeader("Authorization") String token) {
        log.info("获取用户信息: token={}", token);
        
        try {
            Long userId = CreditTokenUtil.getUserId(token);
            if (userId == null) {
                return CommonResult.failed("登录已过期，请重新登录");
            }

            UserInfoResponse response = creditUserService.getUserInfo(userId);
            if (response == null) {
                return CommonResult.failed("用户不存在");
            }
            return CommonResult.success(response);
        } catch (Exception e) {
            log.error("获取用户信息失败", e);
            return CommonResult.failed("获取失败: " + e.getMessage());
        }
    }

    /**
     * 更新用户信息
     */
    @ApiOperation(value = "更新用户信息")
    @RequestMapping(value = "/updateUserInfo", method = RequestMethod.POST)
    public CommonResult<String> updateUserInfo(
            @RequestHeader("Authorization") String token,
            @RequestParam(required = false) String nickname,
            @RequestParam(required = false) String avatar,
            @RequestParam(required = false) String phone) {
        
        log.info("更新用户信息: nickname={}, phone={}", nickname, phone);
        
        try {
            // TODO: 实现更新逻辑
            return CommonResult.success("更新成功");
        } catch (Exception e) {
            log.error("更新用户信息失败", e);
            return CommonResult.failed("更新失败: " + e.getMessage());
        }
    }

    /**
     * 退出登录
     */
    @ApiOperation(value = "退出登录")
    @RequestMapping(value = "/logout", method = RequestMethod.POST)
    public CommonResult<String> logout(@RequestHeader("Authorization") String token) {
        log.info("退出登录: token={}", token);
        
        try {
            CreditTokenUtil.deleteToken(token);
            return CommonResult.success("退出成功");
        } catch (Exception e) {
            log.error("退出登录失败", e);
            return CommonResult.failed("退出失败: " + e.getMessage());
        }
    }
}

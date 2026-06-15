package com.zbkj.front.controller;

import com.zbkj.common.result.CommonResult;
import com.zbkj.common.service.credit.CreditWithdrawService;
import com.zbkj.common.utils.CreditTokenUtil;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Map;

/**
 * 征信提现控制器
 */
@Slf4j
@RestController("CreditWithdrawFrontController")
@RequestMapping("api/credit/withdraw")
@Api(tags = "征信提现")
public class CreditWithdrawController {

    @Autowired
    private CreditWithdrawService creditWithdrawService;

    /**
     * 申请提现
     */
    @ApiOperation(value = "申请提现")
    @RequestMapping(value = "/apply", method = RequestMethod.POST)
    public CommonResult<String> applyWithdraw(
            @RequestHeader("Authorization") String token,
            @RequestBody Map<String, Object> accountInfo) {
        
        BigDecimal amount = new BigDecimal(accountInfo.get("amount").toString());
        log.info("申请提现: amount={}", amount);
        
        try {
            Long userId = CreditTokenUtil.getUserId(token);
            if (userId == null) {
                return CommonResult.failed("登录已过期，请重新登录");
            }
            boolean success = creditWithdrawService.applyWithdraw(userId, amount, accountInfo);
            if (success) {
                return CommonResult.success("申请成功");
            } else {
                return CommonResult.failed("申请失败");
            }
        } catch (Exception e) {
            log.error("申请提现失败", e);
            return CommonResult.failed("申请失败: " + e.getMessage());
        }
    }

    /**
     * 获取提现记录
     */
    @ApiOperation(value = "获取提现记录")
    @RequestMapping(value = "/list", method = RequestMethod.GET)
    public CommonResult<String> getWithdrawList(
            @RequestHeader("Authorization") String token,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer limit) {
        
        log.info("获取提现记录: page={}, limit={}", page, limit);
        
        try {
            // TODO: 实现提现记录查询
            return CommonResult.success("");
        } catch (Exception e) {
            log.error("获取提现记录失败", e);
            return CommonResult.failed("获取失败: " + e.getMessage());
        }
    }
}

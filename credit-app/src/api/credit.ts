// API配置
const AI_SERVICE_URL = 'http://localhost:8081'
const JAVA_SERVICE_URL = 'http://localhost:20510'

// Token管理
let TOKEN = ''

export function setToken(token: string) {
	TOKEN = token
	uni.setStorageSync('credit_token', token)
}

export function getToken(): string {
	if (!TOKEN) {
		TOKEN = uni.getStorageSync('credit_token') || ''
	}
	return TOKEN
}

export function clearToken() {
	TOKEN = ''
	uni.removeStorageSync('credit_token')
}

// 通用请求函数
function request(url: string, method: string, data?: any) {
	return new Promise((resolve, reject) => {
		uni.request({
			url,
			method,
			data,
			header: {
				'Accept': 'application/json',
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${getToken()}`
			},
			success: (res) => {
				if (res.statusCode === 200) {
					resolve(res.data)
				} else if (res.statusCode === 401) {
					// Token过期，清除登录状态
					clearToken()
					uni.showToast({
						title: '请先登录',
						icon: 'none'
					})
					reject(new Error('未登录'))
				} else {
					reject(new Error(`请求失败: ${res.statusCode}`))
				}
			},
			fail: (err) => {
				reject(err)
			}
		})
	})
}

// 上传征信报告
export function uploadCreditReport(filePath: string) {
	return new Promise((resolve, reject) => {
		uni.uploadFile({
			url: `${AI_SERVICE_URL}/api/ocr/upload`,
			filePath: filePath,
			name: 'file',
			header: {
				'Accept': 'application/json'
			},
			success: (res) => {
				if (res.statusCode === 200) {
					try {
						const data = JSON.parse(res.data)
						resolve(data)
					} catch (e) {
						reject(new Error('解析响应失败'))
					}
				} else {
					reject(new Error(`上传失败: ${res.statusCode}`))
				}
			},
			fail: (err) => {
				reject(err)
			}
		})
	})
}

// 开始分析
export function startAnalysis(taskId: string) {
	return new Promise((resolve, reject) => {
		uni.request({
			url: `${AI_SERVICE_URL}/api/ocr/analyze/${taskId}`,
			method: 'POST',
			header: {
				'Accept': 'application/json'
			},
			success: (res) => {
				if (res.statusCode === 200) {
					resolve(res.data)
				} else {
					reject(new Error(`分析失败: ${res.statusCode}`))
				}
			},
			fail: (err) => {
				reject(err)
			}
		})
	})
}

// 获取分析结果
export function getAnalysisResult(taskId: string) {
	return new Promise((resolve, reject) => {
		uni.request({
			url: `${AI_SERVICE_URL}/api/ocr/result/${taskId}`,
			method: 'GET',
			header: {
				'Accept': 'application/json'
			},
			success: (res) => {
				if (res.statusCode === 200) {
					resolve(res.data)
				} else {
					reject(new Error(`获取结果失败: ${res.statusCode}`))
				}
			},
			fail: (err) => {
				reject(err)
			}
		})
	})
}

// 获取用户额度
export function getUserQuota() {
	return request(`${JAVA_SERVICE_URL}/api/credit/quota`, 'GET')
}

// ========== 用户认证相关 ==========

// 微信登录
export function wxLogin(code: string, nickname?: string, avatar?: string, inviteCode?: string) {
	return request(`${JAVA_SERVICE_URL}/api/credit/auth/wxLogin`, 'POST', {
		code,
		nickname,
		avatar,
		inviteCode
	})
}

// 获取用户信息
export function getUserInfo() {
	return request(`${JAVA_SERVICE_URL}/api/credit/auth/userInfo`, 'GET')
}

// 更新用户信息
export function updateUserInfo(data: { nickname?: string; avatar?: string; phone?: string }) {
	return request(`${JAVA_SERVICE_URL}/api/credit/auth/updateUserInfo`, 'POST', data)
}

// 退出登录
export function logout() {
	return request(`${JAVA_SERVICE_URL}/api/credit/auth/logout`, 'POST')
}

// ========== VIP会员相关 ==========

// 获取VIP套餐列表
export function getVipPackages() {
	return request(`${JAVA_SERVICE_URL}/api/credit/vip/packages`, 'GET')
}

// 购买VIP
export function purchaseVip(packageId: number) {
	return request(`${JAVA_SERVICE_URL}/api/credit/vip/purchase`, 'POST', { packageId })
}

// 检查VIP状态
export function checkVipStatus() {
	return request(`${JAVA_SERVICE_URL}/api/credit/vip/check`, 'GET')
}

// ========== 报告相关 ==========

// 获取报告列表
export function getReportList(page: number = 1, limit: number = 10) {
	return request(`${JAVA_SERVICE_URL}/api/credit/report/list?page=${page}&limit=${limit}`, 'GET')
}

// 获取报告详情
export function getReportDetail(taskId: string) {
	return request(`${JAVA_SERVICE_URL}/api/credit/report/detail/${taskId}`, 'GET')
}

// 删除报告
export function deleteReport(taskId: string) {
	return request(`${JAVA_SERVICE_URL}/api/credit/report/delete/${taskId}`, 'DELETE')
}

// ========== 消费记录相关 ==========

// 获取消费记录列表
export function getConsumeList(page: number = 1, limit: number = 10) {
	return request(`${JAVA_SERVICE_URL}/api/credit/consume/list?page=${page}&limit=${limit}`, 'GET')
}

// ========== 支付相关 ==========

// 创建支付订单
export function createPayOrder(type: string, amount: number) {
	return request(`${JAVA_SERVICE_URL}/api/credit/pay/create`, 'POST', { type, amount })
}

// 查询支付状态
export function getPayStatus(orderId: string) {
	return request(`${JAVA_SERVICE_URL}/api/credit/pay/status/${orderId}`, 'GET')
}

// ========== 邀请相关 ==========

// 获取邀请统计
export function getInviteStats() {
	return request(`${JAVA_SERVICE_URL}/api/credit/invite/stats`, 'GET')
}

// 获取邀请列表
export function getInviteList(page: number = 1, limit: number = 10) {
	return request(`${JAVA_SERVICE_URL}/api/credit/invite/list?page=${page}&limit=${limit}`, 'GET')
}

// 申请提现
export function applyWithdraw(amount: number, accountInfo: any) {
	return request(`${JAVA_SERVICE_URL}/api/credit/withdraw/apply`, 'POST', { amount, accountInfo })
}

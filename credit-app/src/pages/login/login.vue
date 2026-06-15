<template>
	<view class="page">
		<!-- Nav Bar -->
		<view class="nav-bar">
			<view class="nav-back" @click="goBack">
				<svg viewBox="0 0 24 24" width="44rpx" height="44rpx">
					<path d="M15 19l-7-7 7-7" stroke="#1E293B" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</view>
			<text class="nav-title">登录</text>
			<view class="nav-placeholder"></view>
		</view>

		<view class="content">
			<!-- Logo & Slogan -->
			<view class="login-header">
				<view class="login-logo">
					<svg viewBox="0 0 100 100" width="160rpx" height="160rpx">
						<defs>
							<linearGradient id="logoGradLogin" x1="0%" y1="0%" x2="100%" y2="100%">
								<stop offset="0%" style="stop-color:#6366F1"/>
								<stop offset="100%" style="stop-color:#A855F7"/>
							</linearGradient>
						</defs>
						<rect width="100" height="100" rx="24" fill="url(#logoGradLogin)"/>
						<text x="50" y="65" text-anchor="middle" fill="#FFFFFF" font-size="48" font-weight="bold">征</text>
					</svg>
				</view>
				<view class="login-slogan">征信报告AI分析</view>
				<view class="login-desc">登录后享受完整功能服务</view>
			</view>

			<!-- WeChat Login Button -->
			<button
				class="wechat-btn"
				:class="{ loading: isLogging }"
				:disabled="isLogging"
				@click="handleWechatLogin"
			>
				<svg v-if="!isLogging" viewBox="0 0 24 24" width="40rpx" height="40rpx">
					<path d="M8.5 11a1.5 1.5 0 110-3 1.5 1.5 0 010 3zm5 0a1.5 1.5 0 110-3 1.5 1.5 0 010 3zM5.5 16.5c0 1.5 1.5 2.5 3.5 2.5h.5l2 1.5v-1.5h1c2 0 3.5-1 3.5-2.5S14 14 12 14H9c-2 0-3.5 1-3.5 2.5z" fill="#FFFFFF"/>
					<path d="M3 6c0-1.5 1.5-3 3-3h12c1.5 0 3 1.5 3 3v7c0 1.5-1.5 3-3 3h-3l-3 2.5V16H6c-1.5 0-3-1.5-3-3V6z" fill="#07C160"/>
					<path d="M8.5 11a1.5 1.5 0 110-3 1.5 1.5 0 010 3zm5 0a1.5 1.5 0 110-3 1.5 1.5 0 010 3zM5.5 16.5c0 1.5 1.5 2.5 3.5 2.5h.5l2 1.5v-1.5h1c2 0 3.5-1 3.5-2.5S14 14 12 14H9c-2 0-3.5 1-3.5 2.5z" fill="#FFFFFF"/>
				</svg>
				<text v-if="isLogging">登录中...</text>
				<text v-else>微信一键登录</text>
			</button>

			<!-- H5 备用：手动输入手机号登录 -->
			<view class="divider" v-if="isH5">
				<view class="divider-line"></view>
				<text class="divider-text">其他登录方式</text>
				<view class="divider-line"></view>
			</view>

			<view class="phone-form" v-if="isH5">
				<view class="input-group">
					<text class="input-label">手机号</text>
					<input
						class="input-field"
						v-model="phone"
						type="number"
						maxlength="11"
						placeholder="请输入手机号"
					/>
				</view>
				<button class="phone-btn" :disabled="phone.length < 11 || isLogging" @click="handlePhoneLogin">
					获取验证码登录
				</button>
			</view>

			<!-- 协议勾选 -->
			<view class="agreement">
				<view class="checkbox" :class="{ checked: agreed }" @click="agreed = !agreed"></view>
				<text class="agreement-text">
					登录即表示同意
					<text class="link" @click="goToAgreement('service')">《服务协议》</text>
					和
					<text class="link" @click="goToAgreement('privacy')">《隐私政策》</text>
				</text>
			</view>

			<!-- 底部间距 -->
			<view class="bottom-spacing"></view>
		</view>
	</view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { wxLogin } from '@/api/credit'

const isLogging = ref(false)
const agreed = ref(false)
const phone = ref('')
const isH5 = ref(false)

onMounted(() => {
	// 判断是否为 H5 环境
	// #ifdef H5
	isH5.value = true
	// #endif

	// H5端：处理微信 OAuth 回跳（URL 中携带 code）
	// #ifdef H5
	if (typeof window !== 'undefined') {
		try {
			const params = new URLSearchParams(window.location.search)
			const code = params.get('code')
			const state = params.get('state')
			if (code) {
				// 验证 state 防 CSRF
				const savedState = uni.getStorageSync('wx_oauth_state')
				if (state !== savedState) {
					uni.showToast({ title: '登录验证失败', icon: 'none' })
					return
				}
				uni.removeStorageSync('wx_oauth_state')
				// 调用后端登录接口
				handleOAuthCallback(code)
			}
		} catch (e) {}
	}
	// #endif
})

const goBack = () => {
	const pages = getCurrentPages()
	if (pages.length > 1) {
		uni.navigateBack()
	} else {
		uni.switchTab({ url: '/pages/profile/profile' })
	}
}

const validateAgreement = (): boolean => {
	if (!agreed.value) {
		uni.showToast({ title: '请先阅读并同意协议', icon: 'none' })
		return false
	}
	return true
}

const handleWechatLogin = async () => {
	if (!validateAgreement()) return

	isLogging.value = true
	try {
		let code = ''

		// #ifdef MP-WEIXIN
		const loginRes: any = await new Promise((resolve, reject) => {
			uni.login({
				provider: 'weixin',
				success: resolve,
				fail: reject
			})
		})
		code = loginRes.code
		// #endif

		// #ifdef APP-PLUS
		const loginRes: any = await new Promise((resolve, reject) => {
			uni.login({
				provider: 'weixin',
				success: resolve,
				fail: reject
			})
		})
		code = loginRes.code
		// #endif

		// #ifdef H5
		// H5 端微信登录：需要公众号 appId（配置后启用）
		const appId = '' // 填入微信公众号 appId 后生效
		if (!appId) {
			uni.showToast({ title: 'H5端需配置公众号AppID', icon: 'none', duration: 2000 })
			isLogging.value = false
			return
		}
		const redirectUri = encodeURIComponent(window.location.origin + '/#/pages/login/login')
		const state = Math.random().toString(36).substring(2)
		uni.setStorageSync('wx_oauth_state', state)
		window.location.href = `https://open.weixin.qq.com/connect/oauth2/authorize?appid=${appId}&redirect_uri=${redirectUri}&response_type=code&scope=snsapi_userinfo&state=${state}#wechat_redirect`
		return
		// #endif

		if (!code) {
			throw new Error('获取微信code失败')
		}

		// 调用后端登录接口
		const res: any = await wxLogin(code)
		if (res.code === 0 && res.data) {
			// 保存 token 和用户信息
			const token = res.data.token
			if (token) {
				const tokenData = { token, expires: Date.now() + 7 * 24 * 60 * 60 * 1000 }
				uni.setStorageSync('credit_token', tokenData)
			}
			const userData = res.data.userInfo || { id: res.data.userId }
			uni.setStorageSync('user_info', userData)

			uni.showToast({ title: '登录成功', icon: 'success' })
			setTimeout(() => {
				const pages = getCurrentPages()
				if (pages.length > 1) {
					uni.navigateBack()
				} else {
					uni.switchTab({ url: '/pages/profile/profile' })
				}
			}, 1200)
		} else {
			throw new Error(res.msg || '登录失败')
		}
	} catch (error: any) {
		console.error('微信登录失败:', error)
		uni.showToast({
			title: error.message || error.errMsg || '登录失败，请重试',
			icon: 'none',
			duration: 2000
		})
	} finally {
		isLogging.value = false
	}
}

const handlePhoneLogin = async () => {
	if (!validateAgreement()) return
	if (phone.value.length < 11) {
		uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
		return
	}

	isLogging.value = true
	try {
		// TODO: 调用后端发送验证码接口
		uni.showToast({ title: '验证码已发送', icon: 'success' })
	} catch (error: any) {
		uni.showToast({ title: '发送失败，请重试', icon: 'none' })
	} finally {
		isLogging.value = false
	}
}

const goToAgreement = (tab: string) => {
	uni.navigateTo({ url: `/pages/about/about?tab=${tab}` })
}

// H5 端 OAuth 回跳处理
const handleOAuthCallback = async (code: string) => {
	isLogging.value = true
	try {
		const res: any = await wxLogin(code)
		if (res.code === 0 && res.data) {
			const token = res.data.token
			if (token) {
				const tokenData = { token, expires: Date.now() + 7 * 24 * 60 * 60 * 1000 }
				uni.setStorageSync('credit_token', tokenData)
			}
			const userData = res.data.userInfo || { id: res.data.userId }
			uni.setStorageSync('user_info', userData)

			uni.showToast({ title: '登录成功', icon: 'success' })
			// H5端清除 URL 中的 code 参数避免重复处理
			if (typeof window !== 'undefined') {
				window.history.replaceState({}, document.title, window.location.pathname + '#/pages/profile/profile')
			}
			setTimeout(() => {
				uni.switchTab({ url: '/pages/profile/profile' })
			}, 1200)
		} else {
			throw new Error(res.msg || '登录失败')
		}
	} catch (error: any) {
		console.error('OAuth登录失败:', error)
		uni.showToast({ title: '登录失败，请重试', icon: 'none' })
	} finally {
		isLogging.value = false
	}
}
</script>

<style lang="scss" scoped>
.page {
	display: flex;
	flex-direction: column;
	height: 100vh;
	background: #FFFFFF;
}

.nav-bar {
	display: flex;
	align-items: center;
	justify-content: space-between;
	height: 96rpx;
	padding: 0 20rpx;
	border-bottom: 1rpx solid #F1F5F9;
	flex-shrink: 0;

	.nav-back {
		width: 68rpx;
		height: 68rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.nav-title {
		font-size: 34rpx;
		font-weight: 700;
		color: #1E293B;
	}

	.nav-placeholder {
		width: 68rpx;
	}
}

.content {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 60rpx 48rpx 0;
}

.login-header {
	display: flex;
	flex-direction: column;
	align-items: center;
	margin-bottom: 80rpx;

	.login-logo {
		margin-bottom: 28rpx;
	}

	.login-slogan {
		font-size: 36rpx;
		font-weight: 700;
		color: #1E293B;
		margin-bottom: 12rpx;
	}

	.login-desc {
		font-size: 26rpx;
		color: #94A3B8;
	}
}

.wechat-btn {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 16rpx;
	width: 100%;
	height: 100rpx;
	background: #07C160;
	border-radius: 50rpx;
	border: none;
	color: #FFFFFF;
	font-size: 32rpx;
	font-weight: 600;

	&::after {
		border: none;
	}

	&.loading {
		opacity: 0.7;
	}

	&[disabled] {
		opacity: 0.6;
	}
}

.divider {
	display: flex;
	align-items: center;
	gap: 20rpx;
	margin: 48rpx 0 32rpx;
	width: 100%;

	.divider-line {
		flex: 1;
		height: 1rpx;
		background: #E2E8F0;
	}

	.divider-text {
		font-size: 24rpx;
		color: #94A3B8;
		flex-shrink: 0;
	}
}

.phone-form {
	width: 100%;

	.input-group {
		background: #F8FAFC;
		border-radius: 20rpx;
		padding: 24rpx 28rpx;
		margin-bottom: 24rpx;

		.input-label {
			font-size: 24rpx;
			color: #64748B;
			margin-bottom: 12rpx;
			display: block;
		}

		.input-field {
			font-size: 32rpx;
			color: #1E293B;
			height: 48rpx;
			background: transparent;
		}
	}

	.phone-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 100%;
		height: 92rpx;
		background: linear-gradient(135deg, #6366F1, #A855F7);
		border-radius: 46rpx;
		border: none;
		color: #FFFFFF;
		font-size: 28rpx;
		font-weight: 600;

		&::after {
			border: none;
		}

		&[disabled] {
			opacity: 0.5;
		}
	}
}

.agreement {
	display: flex;
	align-items: center;
	gap: 12rpx;
	margin-top: 36rpx;

	.checkbox {
		width: 32rpx;
		height: 32rpx;
		border: 2rpx solid #CBD5E1;
		border-radius: 50%;
		flex-shrink: 0;
		transition: all 0.2s;

		&.checked {
			background: #6366F1;
			border-color: #6366F1;
			position: relative;

			&::after {
				content: '';
				position: absolute;
				left: 8rpx;
				top: 4rpx;
				width: 12rpx;
				height: 20rpx;
				border: solid #FFFFFF;
				border-width: 0 3rpx 3rpx 0;
				transform: rotate(45deg);
			}
		}
	}

	.agreement-text {
		font-size: 22rpx;
		color: #94A3B8;

		.link {
			color: #6366F1;
		}
	}
}

.bottom-spacing {
	height: 60rpx;
}
</style>

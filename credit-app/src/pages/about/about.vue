<template>
	<view class="page">
		<!-- Nav Bar -->
		<view class="nav-bar">
			<view class="nav-back" @click="goBack">
				<svg viewBox="0 0 24 24" width="44rpx" height="44rpx">
					<path d="M15 19l-7-7 7-7" stroke="#1E293B" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</view>
			<text class="nav-title">关于我们</text>
			<view class="nav-placeholder"></view>
		</view>

		<scroll-view class="content" scroll-y>
			<!-- App Logo & Info -->
			<view class="app-header">
				<view class="app-logo">
					<svg viewBox="0 0 80 80" width="120rpx" height="120rpx">
						<defs>
							<linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
								<stop offset="0%" style="stop-color:#6366F1"/>
								<stop offset="100%" style="stop-color:#A855F7"/>
							</linearGradient>
						</defs>
						<rect width="80" height="80" rx="20" fill="url(#logoGrad)"/>
						<text x="40" y="52" text-anchor="middle" fill="#FFFFFF" font-size="36" font-weight="bold">征</text>
					</svg>
				</view>
				<view class="app-name">征信报告AI分析</view>
				<view class="app-version">Version {{ version }}</view>
			</view>

			<!-- Tab 切换 -->
			<view class="tab-bar">
				<view class="tab-item" :class="{ active: activeTab === 'about' }" @click="activeTab = 'about'">关于我们</view>
				<view class="tab-item" :class="{ active: activeTab === 'service' }" @click="activeTab = 'service'">服务协议</view>
				<view class="tab-item" :class="{ active: activeTab === 'privacy' }" @click="activeTab = 'privacy'">隐私政策</view>
			</view>

			<!-- 关于我们 -->
			<view v-if="activeTab === 'about'" class="tab-content">
				<view class="card">
					<view class="card-title">产品介绍</view>
					<view class="card-text">
						征信报告AI分析是一款基于人工智能技术的征信报告解读工具。通过OCR识别和DeepSeek大模型分析，帮助用户快速理解征信报告内容，发现潜在风险，提供专业的信用管理建议。
					</view>
				</view>

				<view class="card">
					<view class="card-title">核心功能</view>
					<view class="feature-list">
						<view class="feature-item">
							<view class="feature-dot"></view>
							<text>AI智能解读征信报告</text>
						</view>
						<view class="feature-item">
							<view class="feature-dot"></view>
							<text>信用风险评分与预警</text>
						</view>
						<view class="feature-item">
							<view class="feature-dot"></view>
							<text>个性化信用优化建议</text>
						</view>
						<view class="feature-item">
							<view class="feature-dot"></view>
							<text>历史报告对比分析</text>
						</view>
					</view>
				</view>

				<view class="card">
					<view class="card-title">联系我们</view>
					<view class="contact-list">
						<view class="contact-item" @click="copyEmail">
							<text class="contact-label">客服邮箱</text>
							<view class="contact-value-row">
								<text class="contact-value">support@credit-ai.com</text>
								<svg viewBox="0 0 16 16" width="24rpx" height="24rpx">
									<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
								</svg>
							</view>
						</view>
						<view class="contact-item" @click="callService">
							<text class="contact-label">客服电话</text>
							<view class="contact-value-row">
								<text class="contact-value">400-888-9999</text>
								<svg viewBox="0 0 16 16" width="24rpx" height="24rpx">
									<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
								</svg>
							</view>
						</view>
						<view class="contact-item" @click="copyWechat">
							<text class="contact-label">微信公众号</text>
							<view class="contact-value-row">
								<text class="contact-value">CreditAI_Official</text>
								<svg viewBox="0 0 16 16" width="24rpx" height="24rpx">
									<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
								</svg>
							</view>
						</view>
					</view>
				</view>

				<view class="copyright">
					<text>(c) 2024 征信报告AI分析 版权所有</text>
				</view>
			</view>

			<!-- 服务协议 -->
			<view v-else-if="activeTab === 'service'" class="tab-content">
				<view class="legal-content">
					<view class="legal-title">服务协议</view>
					<view class="legal-section">
						<view class="legal-h3">一、协议范围</view>
						<view class="legal-p">本协议是您与征信报告AI分析平台之间关于使用本平台服务所订立的契约。</view>
					</view>
					<view class="legal-section">
						<view class="legal-h3">二、服务内容</view>
						<view class="legal-p">本平台提供征信报告智能解读、信用风险分析、信用优化建议等服务。</view>
					</view>
					<view class="legal-section">
						<view class="legal-h3">三、用户义务</view>
						<view class="legal-p">用户应确保上传的征信报告为本人真实报告，不得上传他人征信报告或虚假文件。</view>
					</view>
					<view class="legal-section">
						<view class="legal-h3">四、免责声明</view>
						<view class="legal-p">本平台提供的分析结果仅供参考，不构成任何金融建议。</view>
					</view>
					<view class="legal-section">
						<view class="legal-h3">五、协议修改</view>
						<view class="legal-p">本平台有权在必要时修改本协议条款，修改后将通过平台公告通知您。</view>
					</view>
					<view class="legal-date">最后更新日期：2024年1月1日</view>
				</view>
			</view>

			<!-- 隐私政策 -->
			<view v-else class="tab-content">
				<view class="legal-content">
					<view class="legal-title">隐私政策</view>
					<view class="legal-section">
						<view class="legal-h3">一、信息收集</view>
						<view class="legal-p">我们收集的信息包括：手机号码、微信OpenID、上传的征信报告文件、使用日志。</view>
					</view>
					<view class="legal-section">
						<view class="legal-h3">二、信息使用</view>
						<view class="legal-p">您上传的征信报告仅用于AI分析，不会被用于其他目的。</view>
					</view>
					<view class="legal-section">
						<view class="legal-h3">三、信息存储</view>
						<view class="legal-p">您的征信报告和分析结果存储于安全的云服务器，采用加密传输和存储。</view>
					</view>
					<view class="legal-section">
						<view class="legal-h3">四、信息删除</view>
						<view class="legal-p">您有权随时删除您的征信报告和历史分析记录。</view>
					</view>
					<view class="legal-section">
						<view class="legal-h3">五、联系我们</view>
						<view class="legal-p">如对本隐私政策有任何疑问，请联系我们：support@credit-ai.com。</view>
					</view>
					<view class="legal-date">最后更新日期：2024年1月1日</view>
				</view>
			</view>

			<view class="bottom-spacing"></view>
		</scroll-view>
	</view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const activeTab = ref('about')
const version = ref('1.0.0')

onMounted(() => {
	// 获取 App 版本号
	try {
		const sysInfo = uni.getSystemInfoSync()
		version.value = sysInfo.appVersion || '1.0.0'
	} catch (e) {
		version.value = '1.0.0'
	}

	// 解析 tab 参数
	try {
		let tab = ''
		// 页面栈方式（小程序/App）
		const pages = getCurrentPages()
		const currentPage = pages[pages.length - 1]
		if (currentPage && currentPage.options) {
			tab = currentPage.options.tab || ''
		}
		// H5 从 URL 解析
		if (typeof window !== 'undefined') {
			try {
				const params = new URLSearchParams(window.location.search)
				const urlTab = params.get('tab')
				if (urlTab) tab = urlTab
			} catch (e) {}
		}
		if (tab === 'privacy') activeTab.value = 'privacy'
		if (tab === 'service') activeTab.value = 'service'
	} catch (e) {}
})

const goBack = () => {
	const pages = getCurrentPages()
	if (pages.length > 1) {
		uni.navigateBack()
	} else {
		uni.switchTab({ url: '/pages/profile/profile' })
	}
}

const copyEmail = () => {
	uni.setClipboardData({
		data: 'support@credit-ai.com',
		success: () => uni.showToast({ title: '邮箱已复制', icon: 'success' })
	})
}

const callService = () => {
	uni.makePhoneCall({
		phoneNumber: '4008889999',
		fail: () => uni.showToast({ title: '拨号失败', icon: 'none' })
	})
}

const copyWechat = () => {
	uni.setClipboardData({
		data: 'CreditAI_Official',
		success: () => uni.showToast({ title: '公众号已复制', icon: 'success' })
	})
}
</script>

<style lang="scss" scoped>
.page {
	display: flex;
	flex-direction: column;
	height: 100vh;
	background: #F8FAFC;
}

.nav-bar {
	display: flex;
	align-items: center;
	justify-content: space-between;
	height: 96rpx;
	padding: 0 20rpx;
	background: #FFFFFF;
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
	overflow-y: auto;
}

.app-header {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 48rpx 32rpx 32rpx;

	.app-logo {
		margin-bottom: 20rpx;
	}

	.app-name {
		font-size: 36rpx;
		font-weight: 700;
		color: #1E293B;
		margin-bottom: 8rpx;
	}

	.app-version {
		font-size: 24rpx;
		color: #94A3B8;
	}
}

.tab-bar {
	display: flex;
	margin: 0 24rpx;
	background: #F1F5F9;
	border-radius: 20rpx;
	padding: 6rpx;

	.tab-item {
		flex: 1;
		text-align: center;
		padding: 16rpx 0;
		font-size: 24rpx;
		color: #64748B;
		border-radius: 16rpx;
		transition: all 0.2s;

		&.active {
			background: #FFFFFF;
			color: #6366F1;
			font-weight: 600;
			box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.06);
		}
	}
}

.tab-content {
	padding: 24rpx;
}

.card {
	background: #FFFFFF;
	border-radius: 28rpx;
	padding: 28rpx;
	margin-top: 20rpx;
	box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.04);

	.card-title {
		font-size: 30rpx;
		font-weight: 700;
		color: #1E293B;
		margin-bottom: 16rpx;
	}

	.card-text {
		font-size: 26rpx;
		color: #64748B;
		line-height: 1.8;
	}
}

.feature-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;

	.feature-item {
		display: flex;
		align-items: center;
		gap: 16rpx;
		font-size: 26rpx;
		color: #334155;

		.feature-dot {
			width: 12rpx;
			height: 12rpx;
			border-radius: 50%;
			background: linear-gradient(135deg, #6366F1, #A855F7);
			flex-shrink: 0;
		}
	}
}

.contact-list {
	display: flex;
	flex-direction: column;

	.contact-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 20rpx 0;
		border-bottom: 1rpx solid #F1F5F9;

		&:last-child {
			border-bottom: none;
		}

		.contact-label {
			font-size: 26rpx;
			color: #64748B;
		}

		.contact-value-row {
			display: flex;
			align-items: center;
			gap: 8rpx;

			.contact-value {
				font-size: 26rpx;
				color: #1E293B;
			}
		}
	}
}

.copyright {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 32rpx 0 16rpx;
	font-size: 20rpx;
	color: #94A3B8;
}

.legal-content {
	background: #FFFFFF;
	border-radius: 28rpx;
	padding: 32rpx;
	margin-top: 20rpx;
	box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.04);

	.legal-title {
		font-size: 34rpx;
		font-weight: 700;
		color: #1E293B;
		text-align: center;
		margin-bottom: 28rpx;
	}

	.legal-section {
		margin-bottom: 24rpx;

		.legal-h3 {
			font-size: 28rpx;
			font-weight: 600;
			color: #334155;
			margin-bottom: 8rpx;
		}

		.legal-p {
			font-size: 24rpx;
			color: #64748B;
			line-height: 1.8;
		}
	}

	.legal-date {
		font-size: 22rpx;
		color: #94A3B8;
		text-align: center;
		margin-top: 24rpx;
	}
}

.bottom-spacing {
	height: 140rpx;
}
</style>

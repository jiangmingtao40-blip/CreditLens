<template>
	<view class="page">
		<!-- Status Bar -->
		<view class="status-bar">
			<text class="time">9:41</text>
			<view class="spacer"></view>
			<view class="battery"></view>
		</view>
		
		<!-- Content -->
		<scroll-view class="content" scroll-y>
			<!-- Page Header -->
			<view class="page-header">
				<text class="back-arrow" @click="goBack">←</text>
				<view class="page-title">分析结果</view>
				<view class="header-spacer"></view>
			</view>
			
			<!-- Loading State -->
			<view v-if="isLoading" class="loading-state">
				<view class="loading-ring"></view>
				<text class="loading-text">正在加载分析结果...</text>
			</view>
			
			<!-- Result Content -->
			<template v-else>
				<!-- Score Card -->
				<view class="score-card">
					<view class="score-label">信用评分</view>
					<view class="score-value">{{ creditScore }}</view>
					<view class="grade-badge"><text>{{ gradeText }}</text></view>
				</view>
				
				<!-- Risk Card -->
				<view class="risk-card" :class="riskLevelClass">
					<view class="risk-icon" :style="{ background: riskIconBgColor }">
						<svg v-if="riskIcon === 'check'" viewBox="0 0 16 16">
							<path d="M4 8l3 3 5-6" stroke="white" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
						<svg v-else-if="riskIcon === 'warning'" viewBox="0 0 16 16">
							<path d="M8 3l6 10H2L8 3z" stroke="white" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
							<path d="M8 7v3M8 11.5v.5" stroke="white" stroke-width="1.5" fill="none" stroke-linecap="round"/>
						</svg>
						<svg v-else viewBox="0 0 16 16">
							<path d="M4 4l8 8M12 4l-8 8" stroke="white" stroke-width="2" fill="none" stroke-linecap="round"/>
						</svg>
					</view>
					<view class="risk-info">
						<view class="risk-title">风险等级：{{ riskLevel }}</view>
						<view class="risk-desc">{{ riskDesc }}</view>
					</view>
				</view>
				
				<!-- Section Title -->
				<view class="section-title">详细分析</view>
				
				<!-- Detail Cards -->
				<view class="detail-card" @click="goToDetail('personal')">
					<view class="left">
						<view class="detail-title">个人信息</view>
						<view class="detail-value green">{{ personalInfoStatus }}</view>
					</view>
					<svg class="detail-arrow" viewBox="0 0 16 16">
						<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
					</svg>
				</view>
				
				<view class="detail-card" @click="goToDetail('credit')">
					<view class="left">
						<view class="detail-title">信贷记录</view>
						<view class="detail-value muted">{{ creditRecordsCount }}</view>
					</view>
					<svg class="detail-arrow" viewBox="0 0 16 16">
						<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
					</svg>
				</view>
				
				<view class="detail-card" @click="goToDetail('overdue')">
					<view class="left">
						<view class="detail-title">逾期记录</view>
						<view class="detail-value" :class="overdueClass">{{ overdueStatus }}</view>
					</view>
					<svg class="detail-arrow" viewBox="0 0 16 16">
						<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
					</svg>
				</view>
				
				<view class="detail-card" :class="{ warn: hasRiskWarning }" @click="goToDetail('risk')">
					<view class="left">
						<view class="detail-title">风险预警</view>
						<view class="detail-value" :class="riskWarningClass">{{ riskWarningStatus }}</view>
					</view>
					<svg class="detail-arrow" viewBox="0 0 16 16">
						<path d="M6 4l4 4-4 4" stroke="#94A3B8" stroke-width="2" fill="none" stroke-linecap="round"/>
					</svg>
				</view>
				
				<!-- Suggestions -->
				<view v-if="suggestions.length > 0" class="suggestions-card">
					<view class="suggestions-title">优化建议</view>
					<view v-for="(suggestion, index) in suggestions" :key="index" class="suggestion-item">
						<text class="suggestion-num">{{ index + 1 }}</text>
						<text class="suggestion-text">{{ suggestion }}</text>
					</view>
				</view>
			</template>
			
			<!-- Bottom Spacing -->
			<view class="bottom-spacing"></view>
		</scroll-view>
		
		<!-- Tab Bar -->
		<TabBar :current="3" @change="onTabChange"></TabBar>
	</view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import TabBar from '@/components/TabBar/index.vue'
import { getAnalysisResult } from '@/api/credit'

const isLoading = ref(true)
const taskId = ref('')

// 分析结果数据
const creditScore = ref(782)
const gradeText = ref('良好')
const riskLevel = ref('低风险')
const riskLevelClass = ref('low')
const riskIcon = ref('check')  // check: 绿色勾, warning: 黄色警告, danger: 红色叉
const riskIconBgColor = ref('#10B981')
const riskDesc = ref('信用状况良好，无重大风险项')
const personalInfoStatus = ref('已识别')
const creditRecordsCount = ref('共 5 笔，无异常')
const overdueStatus = ref('无逾期记录')
const overdueClass = ref('green')
const riskWarningStatus = ref('1 项需关注')
const riskWarningClass = ref('warning')
const hasRiskWarning = ref(true)
const suggestions = ref<string[]>([])

// 详细数据
const personalData = ref<any>(null)
const creditData = ref<any>(null)
const overdueData = ref<any>(null)
const riskData = ref<any>(null)
const showDetail = ref(false)
const currentDetailType = ref('')

const goBack = () => {
	uni.navigateBack()
}

const goToDetail = (type: string) => {
	// 直接显示详情模态框
	currentDetailType.value = type
	showDetail.value = true
	
	// 根据类型加载对应数据
	const resultData = {
		personal: personalData.value,
		credit: creditData.value,
		overdue: overdueData.value,
		risk: riskData.value
	}
	
	// 显示详情
	showDetailModal(type, resultData[type])
}

const showDetailModal = (type: string, data: any) => {
	const titles: Record<string, string> = {
		personal: '个人信息',
		credit: '信贷记录',
		overdue: '逾期记录',
		risk: '风险预警'
	}
	
	const content = formatDetailContent(type, data)
	uni.showModal({
		title: titles[type] || '详情',
		content: content,
		showCancel: false,
		confirmText: '关闭'
	})
}

const formatDetailContent = (type: string, data: any): string => {
	if (!data) return '暂无数据'
	
	switch (type) {
		case 'personal':
			return `姓名：${data.name || '未知'}\n身份证：${data.id_number || '未知'}\n婚姻：${data.marriage || '未知'}\n学历：${data.education || '未知'}`
		case 'credit':
			return `信用卡：${data.credit_cards || 0} 张\n贷款：${data.loans || 0} 笔\n还款状态：${data.repayment_status || '未知'}`
		case 'overdue':
			return `逾期状态：${data.has_overdue ? '有' : '无'}\n详情：${data.details || '无'}`
		case 'risk':
			if (data.warnings && data.warnings.length > 0) {
				return data.warnings.join('\n')
			}
			return '无风险项'
		default:
			return JSON.stringify(data)
	}
}

onMounted(() => {
	// 获取taskId
	const pages = getCurrentPages()
	const currentPage = pages[pages.length - 1]
	const options = currentPage.options || currentPage.$route?.query || {}
	
	if (!options.taskId) {
		// 没有taskId，使用默认数据
		isLoading.value = false
		return
	}
	
	taskId.value = options.taskId
	fetchResult()
})

const fetchResult = async () => {
	try {
		const result: any = await getAnalysisResult(taskId.value)
		
		if (result.status === 'completed') {
			// 解析真实数据
			parseResult(result)
		} else if (result.status === 'failed') {
			uni.showToast({ title: '分析失败', icon: 'none' })
		} else {
			// 还在分析中，稍后重试
			setTimeout(fetchResult, 2000)
			return
		}
	} catch (error) {
		console.error('获取结果失败:', error)
		uni.showToast({ title: '获取结果失败', icon: 'none' })
	} finally {
		isLoading.value = false
	}
}

const parseResult = (data: any) => {
	// 信用评分
	if (data.credit_score !== undefined) {
		creditScore.value = data.credit_score
	}
	
	// 评分等级
	if (data.credit_score >= 800) {
		gradeText.value = '优秀'
	} else if (data.credit_score >= 700) {
		gradeText.value = '良好'
	} else if (data.credit_score >= 600) {
		gradeText.value = '一般'
	} else {
		gradeText.value = '较差'
	}
	
	// 风险等级（支持中文和英文）
	if (data.risk_level) {
		riskLevel.value = data.risk_level
		const level = data.risk_level.toLowerCase()
		if (level.includes('低') || level.includes('优') || level === 'low') {
			riskLevelClass.value = 'low'
			riskIcon.value = 'check'
			riskIconBgColor.value = '#10B981'
			riskDesc.value = '信用状况良好，无重大风险项'
		} else if (level.includes('中') || level === 'medium') {
			riskLevelClass.value = 'medium'
			riskIcon.value = 'warning'
			riskIconBgColor.value = '#F59E0B'
			riskDesc.value = '存在一定风险，建议关注'
		} else {
			riskLevelClass.value = 'high'
			riskIcon.value = 'danger'
			riskIconBgColor.value = '#EF4444'
			riskDesc.value = '风险较高，建议及时处理'
		}
	}
	
	// 个人信息
	if (data.personal_info) {
		personalInfoStatus.value = '已识别'
		personalData.value = data.personal_info
	} else if (data.personal) {
		personalInfoStatus.value = '已识别'
		personalData.value = data.personal
	}
	
	// 信贷记录
	if (data.credit_records) {
		const count = data.credit_records.count || 0
		creditRecordsCount.value = `共 ${count} 笔，无异常`
		creditData.value = data.credit_records
	} else if (data.credit) {
		const count = (data.credit.credit_cards || 0) + (data.credit.loans || 0)
		creditRecordsCount.value = `共 ${count} 笔，无异常`
		creditData.value = data.credit
	}
	
	// 逾期记录
	if (data.overdue_records) {
		const count = data.overdue_records.count || 0
		if (count === 0) {
			overdueStatus.value = '无逾期记录'
			overdueClass.value = 'green'
		} else {
			overdueStatus.value = `${count} 笔逾期`
			overdueClass.value = 'warning'
		}
		overdueData.value = data.overdue_records
	} else if (data.overdue) {
		const count = data.overdue.has_overdue ? 1 : 0
		if (count === 0) {
			overdueStatus.value = '无逾期记录'
			overdueClass.value = 'green'
		} else {
			overdueStatus.value = '有逾期'
			overdueClass.value = 'warning'
		}
		overdueData.value = data.overdue
	}
	
	// 风险预警
	if (data.risk_tips && data.risk_tips.length > 0) {
		hasRiskWarning.value = true
		riskWarningStatus.value = `${data.risk_tips.length} 项需关注`
		riskWarningClass.value = 'warning'
		riskData.value = { warnings: data.risk_tips }
	} else if (data.risk_warnings && data.risk_warnings.length > 0) {
		hasRiskWarning.value = true
		riskWarningStatus.value = `${data.risk_warnings.length} 项需关注`
		riskWarningClass.value = 'warning'
		riskData.value = { warnings: data.risk_warnings }
	} else {
		hasRiskWarning.value = false
		riskWarningStatus.value = '无风险项'
		riskWarningClass.value = 'green'
		riskData.value = { warnings: [] }
	}
	
	// 优化建议
	if (data.suggestions) {
		suggestions.value = data.suggestions
	}
}

const onTabChange = (index: number) => {
	const routes = [
		'/pages/index/index',
		'/pages/records/records',
		'/pages/upload/upload',
		'/pages/result/result',
		'/pages/profile/profile'
	]
	if (routes[index]) {
		uni.navigateTo({ url: routes[index] })
	}
}
</script>

<style lang="scss" scoped>
.page {
	display: flex;
	flex-direction: column;
	height: 100vh;
	background: #F8FAFC;
}

/* Status Bar */
.status-bar {
	display: flex;
	align-items: center;
	height: 62rpx;
	padding: 0 48rpx;
	background: #F8FAFC;
	
	.time {
		font-size: 28rpx;
		font-weight: 600;
		color: #1E293B;
	}
	
	.spacer {
		flex: 1;
	}
	
	.battery {
		width: 48rpx;
		height: 24rpx;
		background: #CBD5E1;
		border-radius: 6rpx;
	}
}

/* Content */
.content {
	flex: 1;
	padding: 20rpx;
	overflow-y: auto;
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

/* Page Header */
.page-header {
	display: flex;
	align-items: center;
	height: 88rpx;
	gap: 24rpx;
	
	.back-arrow {
		font-size: 44rpx;
		font-weight: 600;
		color: #1E293B;
		font-family: 'IBM Plex Sans', sans-serif;
		line-height: 1;
	}
	
	.page-title {
		flex: 1;
		text-align: center;
		font-size: 36rpx;
		font-weight: 700;
		color: #1E293B;
	}
	
	.header-spacer {
		width: 48rpx;
	}
}

/* Loading State */
.loading-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 120rpx 40rpx;
	gap: 24rpx;
	
	.loading-ring {
		width: 80rpx;
		height: 80rpx;
		border: 4rpx solid #E2E8F0;
		border-top-color: #6366F1;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}
	
	.loading-text {
		font-size: 28rpx;
		color: #64748B;
	}
}

@keyframes spin {
	to {
		transform: rotate(360deg);
	}
}

/* Score Card */
.score-card {
	background: linear-gradient(135deg, #6366F1, #A855F7);
	border-radius: 40rpx;
	padding: 48rpx;
	text-align: center;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 8rpx;
	
	.score-label {
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.7);
	}
	
	.score-value {
		font-family: 'IBM Plex Sans', sans-serif;
		font-size: 112rpx;
		font-weight: 700;
		color: #FFFFFF;
	}
	
	.grade-badge {
		background: rgba(255, 255, 255, 0.2);
		border-radius: 26rpx;
		padding: 8rpx 24rpx;
		
		text {
			font-size: 26rpx;
			font-weight: 700;
			color: #FFFFFF;
		}
	}
}

/* Risk Card */
.risk-card {
	display: flex;
	align-items: center;
	border-radius: 28rpx;
	padding: 28rpx 32rpx;
	gap: 24rpx;
	
	&.low {
		background: #F0FDF4;
		
		.risk-icon {
			background: #10B981;
		}
		
		.risk-title {
			color: #10B981;
		}
	}
	
	&.medium {
		background: #FFF7ED;
		
		.risk-icon {
			background: #F59E0B;
		}
		
		.risk-title {
			color: #F59E0B;
		}
	}
	
	&.high {
		background: #FEF2F2;
		
		.risk-icon {
			background: #EF4444;
		}
		
		.risk-title {
			color: #EF4444;
		}
	}
	
	.risk-icon {
		width: 72rpx;
		height: 72rpx;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
		
		svg {
			width: 32rpx;
			height: 32rpx;
		}
	}
	
	.risk-info {
		display: flex;
		flex-direction: column;
		gap: 4rpx;
		
		.risk-title {
			font-size: 28rpx;
			font-weight: 600;
		}
		
		.risk-desc {
			font-size: 22rpx;
			color: #64748B;
		}
	}
}

/* Section Title */
.section-title {
	font-size: 34rpx;
	font-weight: 700;
	color: #1E293B;
}

/* Detail Cards */
.detail-card {
	display: flex;
	align-items: center;
	background: #FFFFFF;
	border-radius: 24rpx;
	padding: 28rpx;
	gap: 24rpx;
	box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.04);
	transition: all 0.2s ease;
	
	&:active {
		opacity: 0.8;
		transform: scale(0.98);
	}
	
	&.warn {
		background: #FFF7ED;
	}
	
	.left {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 4rpx;
		
		.detail-title {
			font-size: 26rpx;
			font-weight: 600;
			color: #1E293B;
		}
		
		.detail-value {
			font-size: 24rpx;
			
			&.green {
				color: #10B981;
			}
			
			&.warning {
				color: #F59E0B;
			}
			
			&.muted {
				color: #64748B;
			}
		}
	}
	
	.detail-arrow {
		width: 32rpx;
		height: 32rpx;
		flex-shrink: 0;
	}
}

/* Suggestions Card */
.suggestions-card {
	background: #FFFFFF;
	border-radius: 28rpx;
	padding: 32rpx;
	box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.04);
	
	.suggestions-title {
		font-size: 30rpx;
		font-weight: 700;
		color: #1E293B;
		margin-bottom: 20rpx;
	}
	
	.suggestion-item {
		display: flex;
		align-items: flex-start;
		gap: 16rpx;
		padding: 16rpx 0;
		border-bottom: 1rpx solid #F1F5F9;
		
		&:last-child {
			border-bottom: none;
		}
		
		.suggestion-num {
			width: 36rpx;
			height: 36rpx;
			border-radius: 50%;
			background: #6366F1;
			color: #FFFFFF;
			font-size: 20rpx;
			font-weight: 600;
			display: flex;
			align-items: center;
			justify-content: center;
			flex-shrink: 0;
		}
		
		.suggestion-text {
			flex: 1;
			font-size: 26rpx;
			color: #64748B;
			line-height: 1.5;
		}
	}
}

/* Bottom Spacing */
.bottom-spacing {
	height: 140rpx;
}
</style>

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
				<view class="page-title">报告解析中</view>
				<view class="header-spacer"></view>
			</view>
			
			<!-- Progress Section -->
			<view class="progress-section">
				<view class="progress-ring">
					<text class="percent">{{ progressPercent }}%</text>
				</view>
				<view class="progress-status">{{ statusText }}</view>
				<view class="progress-time">已用时 {{ elapsedTime }}</view>
			</view>
			
			<!-- Step List -->
			<view class="step-list">
				<view class="step-item-progress">
					<text class="icon" :class="getStepIconClass(0)">{{ getStepIcon(0) }}</text>
					<text :class="getStepTextClass(0)">{{ steps[0] }}</text>
				</view>
				<view class="step-item-progress">
					<text class="icon" :class="getStepIconClass(1)">{{ getStepIcon(1) }}</text>
					<text :class="getStepTextClass(1)">{{ steps[1] }}</text>
				</view>
				<view class="step-item-progress">
					<text class="icon" :class="getStepIconClass(2)">{{ getStepIcon(2) }}</text>
					<text :class="getStepTextClass(2)">{{ steps[2] }}</text>
				</view>
				<view class="step-item-progress">
					<text class="icon" :class="getStepIconClass(3)">{{ getStepIcon(3) }}</text>
					<text :class="getStepTextClass(3)">{{ steps[3] }}</text>
				</view>
			</view>
			
			<!-- Cancel Button -->
			<button class="btn-outline" @click="goBack">取消解析</button>
		</scroll-view>
	</view>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { startAnalysis, getAnalysisResult } from '@/api/credit'

const taskId = ref('')
const progressPercent = ref(0)
const elapsedTime = ref('00:00')
const statusText = ref('正在初始化...')
const currentStep = ref(0)

const steps = [
	'文件上传完成',
	'OCR文字识别中...',
	'AI智能解析',
	'生成分析报告'
]

let timer: number | null = null
let elapsedTimer: number | null = null
let pollTimer: number | null = null
let seconds = 0

const getStepIcon = (index: number) => {
	if (index < currentStep.value) return '✓'
	if (index === currentStep.value) return '⟳'
	return '○'
}

const getStepIconClass = (index: number) => {
	if (index < currentStep.value) return 'done'
	if (index === currentStep.value) return 'active'
	return 'pending'
}

const getStepTextClass = (index: number) => {
	if (index < currentStep.value) return 'step-done'
	if (index === currentStep.value) return 'step-active'
	return 'step-pending'
}

const goBack = () => {
	clearAllTimers()
	uni.navigateBack()
}

const clearAllTimers = () => {
	if (timer) clearInterval(timer)
	if (elapsedTimer) clearInterval(elapsedTimer)
	if (pollTimer) clearInterval(pollTimer)
}

const startElapsedTimer = () => {
	elapsedTimer = setInterval(() => {
		seconds++
		const mins = Math.floor(seconds / 60).toString().padStart(2, '0')
		const secs = (seconds % 60).toString().padStart(2, '0')
		elapsedTime.value = `${mins}:${secs}`
	}, 1000) as unknown as number
}

const pollResult = async () => {
	try {
		const result: any = await getAnalysisResult(taskId.value)
		
		if (result.status === 'completed') {
			// 分析完成，跳转到结果页
			clearAllTimers()
			progressPercent.value = 100
			currentStep.value = 3
			statusText.value = '分析完成'
			
			setTimeout(() => {
				uni.navigateTo({
					url: `/pages/result/result?taskId=${taskId.value}`
				})
			}, 800)
			return
		} else if (result.status === 'failed') {
			clearAllTimers()
			statusText.value = '分析失败'
			uni.showToast({ title: '分析失败，请重试', icon: 'none' })
			return
		}
		
		// 更新进度
		if (result.status === 'processing') {
			if (progressPercent.value < 90) {
				progressPercent.value += Math.floor(Math.random() * 8) + 3
				if (progressPercent.value > 90) progressPercent.value = 90
			}
			
			// 更新步骤
			if (progressPercent.value > 20 && currentStep.value < 1) {
				currentStep.value = 1
				statusText.value = '正在识别报告内容...'
			} else if (progressPercent.value > 50 && currentStep.value < 2) {
				currentStep.value = 2
				statusText.value = 'AI正在分析中...'
			} else if (progressPercent.value > 80 && currentStep.value < 3) {
				currentStep.value = 3
				statusText.value = '正在生成分析报告...'
			}
		}
	} catch (error) {
		console.error('查询进度失败:', error)
	}
}

onMounted(() => {
	// 获取taskId
	const pages = getCurrentPages()
	const currentPage = pages[pages.length - 1]
	const options = currentPage.options || currentPage.$route?.query || {}
	
	if (!options.taskId) {
		uni.showToast({ title: '缺少任务ID', icon: 'none' })
		return
	}
	
	taskId.value = options.taskId
	currentStep.value = 0
	progressPercent.value = 5
	statusText.value = '正在识别报告内容...'
	
	// 启动分析
	startElapsedTimer()
	
	// 开始分析流程
	startAnalysis(taskId.value).then(() => {
		// 开始轮询结果
		pollTimer = setInterval(pollResult, 2000) as unknown as number
	}).catch((error) => {
		console.error('启动分析失败:', error)
		statusText.value = '启动分析失败'
		uni.showToast({ title: '启动分析失败', icon: 'none' })
	})
})

onUnmounted(() => {
	clearAllTimers()
})
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
	gap: 48rpx;
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

/* Progress Section */
.progress-section {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 32rpx;
	padding: 40rpx 0;
	
	.progress-ring {
		width: 300rpx;
		height: 300rpx;
		border-radius: 50%;
		background: linear-gradient(135deg, #6366F1, #A855F7);
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 16rpx 48rpx rgba(99, 102, 241, 0.25);
		
		.percent {
			font-family: 'IBM Plex Sans', sans-serif;
			font-size: 80rpx;
			font-weight: 700;
			color: #FFFFFF;
		}
	}
	
	.progress-status {
		font-size: 30rpx;
		font-weight: 600;
		color: #6366F1;
	}
	
	.progress-time {
		font-size: 24rpx;
		color: #94A3B8;
	}
}

/* Step List */
.step-list {
	background: #FFFFFF;
	border-radius: 32rpx;
	padding: 40rpx;
	display: flex;
	flex-direction: column;
	gap: 32rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
	
	.step-item-progress {
		display: flex;
		align-items: center;
		gap: 16rpx;
		font-size: 28rpx;
		
		.icon {
			width: 36rpx;
			text-align: center;
			flex-shrink: 0;
			
			&.done {
				color: #10B981;
			}
			&.active {
				color: #6366F1;
			}
			&.pending {
				color: #94A3B8;
			}
		}
		
		.step-done {
			font-weight: 600;
			color: #10B981;
		}
		
		.step-active {
			font-weight: 600;
			color: #6366F1;
		}
		
		.step-pending {
			color: #94A3B8;
		}
	}
}

/* Cancel Button */
.btn-outline {
	margin-top: auto;
	height: 96rpx;
	background: #FFFFFF;
	border: 2rpx solid #E2E8F0;
	border-radius: 48rpx;
	font-size: 32rpx;
	font-weight: 600;
	color: #64748B;
}
</style>

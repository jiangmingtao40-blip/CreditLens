<template>
	<view class="page">
		<!-- Status Bar -->
		<view class="status-bar">
			<text class="time">9:41</text>
			<view class="spacer"></view>
			<view class="battery"></view>
		</view>
		
		<!-- Header -->
		<view class="page-header">
			<text class="back-arrow" @click="goBack">←</text>
			<view class="page-title">报告分析中</view>
			<view class="header-spacer"></view>
		</view>
		
		<!-- Content -->
		<view class="content">
			<!-- Progress Section -->
			<view class="progress-section">
				<view class="progress-ring">
					<view class="percent">{{ progress }}%</view>
				</view>
				<view class="progress-status">{{ statusText }}</view>
				<view class="progress-time">预计剩余 {{ remainingTime }} 秒</view>
			</view>
			
			<!-- Step List -->
			<view class="step-list">
				<view class="step-item-progress">
					<view class="step-icon" :class="getStepClass(1)">
						<template v-if="currentStep > 1">✓</template>
						<template v-else-if="currentStep === 1">{{ currentStep }}</template>
						<template v-else>1</template>
					</view>
					<text :class="getStepTextClass(1)">上传报告</text>
				</view>
				
				<view class="step-item-progress">
					<view class="step-icon" :class="getStepClass(2)">
						<template v-if="currentStep > 2">✓</template>
						<template v-else-if="currentStep === 2">{{ currentStep }}</template>
						<template v-else>2</template>
					</view>
					<text :class="getStepTextClass(2)">OCR文字识别</text>
				</view>
				
				<view class="step-item-progress">
					<view class="step-icon" :class="getStepClass(3)">
						<template v-if="currentStep > 3">✓</template>
						<template v-else-if="currentStep === 3">{{ currentStep }}</template>
						<template v-else>3</template>
					</view>
					<text :class="getStepTextClass(3)">AI智能分析</text>
				</view>
				
				<view class="step-item-progress">
					<view class="step-icon" :class="getStepClass(4)">
						<template v-if="currentStep > 4">✓</template>
						<template v-else-if="currentStep === 4">{{ currentStep }}</template>
						<template v-else>4</template>
					</view>
					<text :class="getStepTextClass(4)">生成报告</text>
				</view>
			</view>
			
			<!-- Current Step Description -->
			<view class="step-desc-card">
				<view class="step-desc-title">{{ currentStepInfo.title }}</view>
				<view class="step-desc-text">{{ currentStepInfo.desc }}</view>
			</view>
		</view>
	</view>
</template>

<script>
	import { analyzeCreditReport, pollUntilComplete, cacheResult } from '@/api/credit.js';

	export default {
		data() {
			return {
				progress: 0,
				currentStep: 1,
				remainingTime: 30,
				taskId: '',
				pollTimer: null
			}
		},
		computed: {
			statusText() {
				const texts = ['处理中', 'OCR识别中', 'AI分析中', '生成报告'];
				return texts[this.currentStep - 1] || '处理中';
			},
			currentStepInfo() {
				const infos = [
					{ title: '准备分析', desc: '正在准备分析您的征信报告' },
					{ title: 'OCR文字识别', desc: '使用PaddleOCR提取报告中的文字信息' },
					{ title: 'AI深度分析', desc: '基于DeepSeek大模型进行信用评估' },
					{ title: '生成分析报告', desc: '整理分析结果，生成结构化报告' }
				];
				return infos[this.currentStep - 1] || infos[0];
			}
		},
		onLoad(options) {
			this.taskId = options.taskId || '';
			if (this.taskId) {
				this.startAnalysis();
			} else {
				this.startMockProgress();
			}
		},
		onUnload() {
			if (this.pollTimer) {
				clearInterval(this.pollTimer);
			}
		},
		methods: {
			goBack() {
				uni.navigateBack();
			},
			startMockProgress() {
				// 模拟进度（用于演示）
				this.pollTimer = setInterval(() => {
					this.progress += Math.random() * 8;
					
					if (this.progress >= 100) {
						this.progress = 100;
						clearInterval(this.pollTimer);
						
						setTimeout(() => {
							uni.redirectTo({
								url: '/pages/credit/result'
							});
						}, 500);
						return;
					}
					
					if (this.progress >= 75) {
						this.currentStep = 4;
						this.remainingTime = Math.ceil((100 - this.progress) * 0.3);
					} else if (this.progress >= 50) {
						this.currentStep = 3;
						this.remainingTime = Math.ceil((75 - this.progress) * 0.5);
					} else if (this.progress >= 25) {
						this.currentStep = 2;
						this.remainingTime = Math.ceil((50 - this.progress) * 0.3);
					} else {
						this.currentStep = 1;
						this.remainingTime = Math.ceil((25 - this.progress) * 0.4);
					}
				}, 200);
			},
			startAnalysis() {
				this.currentStep = 2; // 开始OCR识别

				analyzeCreditReport(this.taskId).then((res) => {
					if (res.status === 'completed') {
						this.handleAnalysisComplete(res);
					} else {
						// 进入轮询等待
						this.startPolling();
					}
				}).catch((err) => {
					console.error('分析启动失败:', err);
					uni.showToast({ title: '分析启动失败', icon: 'none' });
				});
			},
			startPolling() {
				pollUntilComplete(this.taskId, (status, detail) => {
					// 更新步骤显示
					const progress = Math.min(95, Math.floor((detail.attempt / detail.max) * 100));
					this.progress = progress;
					if (progress >= 75) {
						this.currentStep = 4;
					} else if (progress >= 50) {
						this.currentStep = 3;
					}
				}).then((res) => {
					this.progress = 100;
					this.handleAnalysisComplete(res);
				}).catch((err) => {
					uni.showToast({ title: err.message || '分析失败', icon: 'none' });
				});
			},
			handleAnalysisComplete(result) {
				cacheResult(this.taskId, result);

				setTimeout(() => {
					uni.redirectTo({
						url: '/pages/credit/result?taskId=' + this.taskId
					});
				}, 500);
			},
			getStepClass(step) {
				if (this.currentStep > step) return 'done';
				if (this.currentStep === step) return 'active';
				return 'pending';
			},
			getStepTextClass(step) {
				if (this.currentStep > step) return 'step-done';
				if (this.currentStep === step) return 'step-active';
				return 'step-pending';
			}
		}
	}
</script>

<style lang="scss" scoped>
page {
	background: #F8FAFC;
}

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
	flex-shrink: 0;
	
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

/* Page Header */
.page-header {
	display: flex;
	align-items: center;
	height: 88rpx;
	padding: 0 24rpx;
	gap: 24rpx;
}

.back-arrow {
	font-size: 44rpx;
	font-weight: 600;
	color: #1E293B;
	font-family: 'IBM Plex Sans', sans-serif;
	line-height: 1;
}

.page-title {
	flex: 1;
	font-size: 36rpx;
	font-weight: 700;
	color: #1E293B;
	text-align: center;
}

.header-spacer {
	width: 48rpx;
}

/* Content */
.content {
	flex: 1;
	padding: 40rpx 20rpx;
	display: flex;
	flex-direction: column;
	gap: 40rpx;
}

/* Progress Section */
.progress-section {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 24rpx;
	padding: 40rpx 0;
}

.progress-ring {
	width: 300rpx;
	height: 300rpx;
	border-radius: 50%;
	background: linear-gradient(135deg, #6366F1, #A855F7);
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 16rpx 48rpx rgba(99,102,241,0.25);
	
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

/* Step List */
.step-list {
	background: #FFFFFF;
	border-radius: 32rpx;
	padding: 40rpx;
	display: flex;
	flex-direction: column;
	gap: 32rpx;
	box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.04);
}

.step-item-progress {
	display: flex;
	align-items: center;
	gap: 16rpx;
}

.step-icon {
	width: 36rpx;
	height: 36rpx;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 22rpx;
	font-weight: 700;
	flex-shrink: 0;
	
	&.done {
		background: #10B981;
		color: #FFFFFF;
	}
	
	&.active {
		background: #6366F1;
		color: #FFFFFF;
	}
	
	&.pending {
		background: #E2E8F0;
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

/* Step Description */
.step-desc-card {
	background: #FFFFFF;
	border-radius: 24rpx;
	padding: 32rpx;
	box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.04);
}

.step-desc-title {
	font-size: 28rpx;
	font-weight: 600;
	color: #1E293B;
	margin-bottom: 12rpx;
}

.step-desc-text {
	font-size: 24rpx;
	color: #64748B;
	line-height: 1.5;
}
</style>

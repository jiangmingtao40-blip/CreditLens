<template>
	<view class="tab-bar-container">
		<view class="tab-pill">
			<view 
				class="tab-item" 
				:class="{ active: currentIndex === 0 }"
				@click="switchTab(0)"
			>
				<view class="tab-icon home-icon"></view>
				<text class="tab-label">首页</text>
			</view>
			<view 
				class="tab-item" 
				:class="{ active: currentIndex === 1 }"
				@click="switchTab(1)"
			>
				<view class="tab-icon records-icon"></view>
				<text class="tab-label">历史</text>
			</view>
			<view 
				class="tab-item" 
				:class="{ active: currentIndex === 2 }"
				@click="switchTab(2)"
			>
				<view class="tab-icon upload-icon"></view>
				<text class="tab-label">上传</text>
			</view>
			<view 
				class="tab-item" 
				:class="{ active: currentIndex === 3 }"
				@click="switchTab(3)"
			>
				<view class="tab-icon result-icon"></view>
				<text class="tab-label">结果</text>
			</view>
			<view 
				class="tab-item" 
				:class="{ active: currentIndex === 4 }"
				@click="switchTab(4)"
			>
				<view class="tab-icon profile-icon"></view>
				<text class="tab-label">我的</text>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		name: 'TabBar',
		props: {
			current: {
				type: Number,
				default: 0
			}
		},
		data() {
			return {
				currentIndex: 0
			}
		},
		watch: {
			current(val) {
				this.currentIndex = val;
			}
		},
		created() {
			this.currentIndex = this.current;
			this.updateCurrentIndex();
		},
		methods: {
			updateCurrentIndex() {
				const pages = getCurrentPages();
				if (pages.length > 0) {
					const currentPage = pages[pages.length - 1];
					const route = '/' + currentPage.route;
					
					if (route.indexOf('pages/credit/index') !== -1) {
						this.currentIndex = 0;
					} else if (route.indexOf('pages/credit/records') !== -1) {
						this.currentIndex = 1;
					} else if (route.indexOf('pages/credit/upload') !== -1) {
						this.currentIndex = 2;
					} else if (route.indexOf('pages/credit/result') !== -1) {
						this.currentIndex = 3;
					} else if (route.indexOf('pages/user/index') !== -1) {
						this.currentIndex = 4;
					}
				}
			},
			switchTab(index) {
				if (this.currentIndex === index) return;
				
				this.currentIndex = index;
				this.$emit('change', index);
				
				const routes = {
					0: '/pages/credit/index',
					1: '/pages/credit/records',
					2: '/pages/credit/upload',
					3: '/pages/credit/result',
					4: '/pages/user/index'
				};
				
				const url = routes[index];
				if (!url) return;
				
				// 获取当前页面栈
				const pages = getCurrentPages();
				const currentPage = pages[pages.length - 1];
				const currentRoute = '/' + currentPage.route;
				
				// 如果是tabBar页面，使用switchTab
				if (index === 0 || index === 4) {
					uni.switchTab({ url });
				} else {
					// 检查页面是否已经存在
					const pageExists = pages.some(p => '/' + p.route === url);
					if (pageExists) {
						uni.navigateBack({
							delta: pages.length - pages.findIndex(p => '/' + p.route === url) - 1
						});
					} else {
						uni.navigateTo({ url });
					}
				}
			}
		}
	}
</script>

<style lang="scss" scoped>
.tab-bar-container {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	height: 88rpx;
	padding-bottom: env(safe-area-inset-bottom);
	display: flex;
	align-items: center;
	justify-content: center;
	background: #F8FAFC;
	z-index: 1000;
}

.tab-pill {
	display: flex;
	align-items: center;
	background: #FFFFFF;
	border-radius: 72rpx;
	padding: 8rpx;
	box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.06);
	gap: 4rpx;
}

.tab-item {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	width: 124rpx;
	height: 108rpx;
	border-radius: 52rpx;
	gap: 4rpx;
	transition: all 0.25s ease;
	
	&.active {
		background: linear-gradient(135deg, #6366F1, #A855F7);
		
		.tab-label {
			color: #FFFFFF;
			font-weight: 600;
		}
		
		.tab-icon {
			background: #FFFFFF;
			
			&.home-icon { background: #FFFFFF; }
			&.records-icon { background: #FFFFFF; }
			&.upload-icon { background: #FFFFFF; }
			&.result-icon { background: #FFFFFF; }
			&.profile-icon { background: #FFFFFF; }
		}
	}
}

.tab-icon {
	width: 36rpx;
	height: 36rpx;
	border-radius: 50%;
	background: #94A3B8;
}

.home-icon {
	background: #94A3B8;
}

.records-icon {
	background: #94A3B8;
	border-radius: 50%;
}

.upload-icon {
	background: #94A3B8;
	border-radius: 8rpx;
}

.result-icon {
	background: #94A3B8;
	border-radius: 50%;
	position: relative;
	
	&::after {
		content: '';
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 16rpx;
		height: 16rpx;
		border-radius: 50%;
		background: #94A3B8;
	}
}

.profile-icon {
	background: #94A3B8;
	border-radius: 50%;
}

.tab-label {
	font-size: 20rpx;
	color: #94A3B8;
	font-weight: 500;
}
</style>

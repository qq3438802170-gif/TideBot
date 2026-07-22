// Connect APP Page Component (Dedicated Page, Not a Modal)
const AppConnectView = {
    template: `
        <div class="h-full overflow-y-auto p-6 max-w-4xl mx-auto space-y-6">
            <!-- Back Navigation & Title Header -->
            <div class="flex items-center space-x-3">
                <button @click="goBack" class="p-2 rounded-xl bg-slate-200/70 dark:bg-slate-800/80 text-slate-700 dark:text-slate-200 hover:bg-slate-300 dark:hover:bg-slate-700 transition-all spring-btn">
                    <i data-lucide="arrow-left" class="w-4 h-4"></i>
                </button>
                <div>
                    <h1 class="text-xl font-bold tracking-tight">移动端 App 连接与公网密钥管理</h1>
                    <p class="text-xs text-slate-500 dark:text-slate-400">通过 Cloudflare 内网穿透服务，将本地 TideBot 部署映射至移动客户端。</p>
                </div>
            </div>

            <!-- Notice Banner -->
            <div class="p-4 rounded-2xl bg-ios-amber/10 border border-ios-amber/30 text-amber-700 dark:text-amber-300 text-xs flex items-start space-x-3">
                <i data-lucide="alert-triangle" class="w-5 h-5 shrink-0 text-amber-500 mt-0.5"></i>
                <div>
                    <span class="font-bold">安全提示：</span>
                    API 地址与 API Key 均为单次会话临时凭证。服务端停止运行或重新启动后，先前获取的地址与密钥将自动失效，需重新点击获取。
                </div>
            </div>

            <!-- Main Connection Configuration Cards -->
            <div class="space-y-6">
                <!-- Section 1: API Address Card -->
                <div class="glass-card p-6 rounded-3xl space-y-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <div class="p-2 rounded-xl bg-ios-blue/10 text-ios-blue">
                                <i data-lucide="globe" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <h3 class="font-bold text-sm">Cloudflare 公网 API 地址</h3>
                                <p class="text-[11px] text-slate-400">用于移动端连接后端 RESTful / WebSocket 通信总线</p>
                            </div>
                        </div>
                    </div>

                    <div class="flex flex-col sm:flex-row items-center gap-3">
                        <div class="flex-1 w-full px-4 py-3 rounded-2xl bg-slate-100 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700 text-xs font-mono text-slate-800 dark:text-slate-200 truncate select-all">
                            {{ store.apiAddress || '未获取到API地址' }}
                        </div>

                        <div class="flex items-center space-x-2 w-full sm:w-auto shrink-0">
                            <button 
                                @click="store.fetchApiAddress()" 
                                :disabled="store.isGeneratingTunnel"
                                class="flex-1 sm:flex-initial px-4 py-2.5 rounded-2xl bg-ios-blue text-white text-xs font-semibold hover:bg-blue-600 spring-btn flex items-center justify-center space-x-1.5 shadow-ios-active disabled:opacity-50">
                                <i data-lucide="link" class="w-3.5 h-3.5"></i>
                                <span>{{ store.isGeneratingTunnel ? '穿透建立中...' : '获取API地址' }}</span>
                            </button>

                            <button 
                                @click="store.copyToClipboard(store.apiAddress, 'API地址')" 
                                :disabled="!store.apiAddress"
                                class="px-4 py-2.5 rounded-2xl bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-100 text-xs font-semibold hover:bg-slate-300 dark:hover:bg-slate-600 spring-btn flex items-center space-x-1 disabled:opacity-40">
                                <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                                <span>复制</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Section 2: API Key Card -->
                <div class="glass-card p-6 rounded-3xl space-y-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <div class="p-2 rounded-xl bg-ios-indigo/10 text-ios-indigo">
                                <i data-lucide="key" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <h3 class="font-bold text-sm">单次 API Key 访问密钥</h3>
                                <p class="text-[11px] text-slate-400">App 鉴权令牌（Session Scope）</p>
                            </div>
                        </div>
                    </div>

                    <div class="flex flex-col sm:flex-row items-center gap-3">
                        <div class="flex-1 w-full px-4 py-3 rounded-2xl bg-slate-100 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700 text-xs font-mono text-slate-800 dark:text-slate-200 truncate select-all">
                            {{ store.apiKey || '还未获取APIkey' }}
                        </div>

                        <div class="flex items-center space-x-2 w-full sm:w-auto shrink-0">
                            <button 
                                @click="store.fetchApiKey()" 
                                :disabled="store.isGeneratingKey"
                                class="flex-1 sm:flex-initial px-4 py-2.5 rounded-2xl bg-ios-indigo text-white text-xs font-semibold hover:bg-indigo-600 spring-btn flex items-center justify-center space-x-1.5 shadow-md disabled:opacity-50">
                                <i data-lucide="shield-check" class="w-3.5 h-3.5"></i>
                                <span>{{ store.isGeneratingKey ? '密钥生成中...' : '获取APIkey' }}</span>
                            </button>

                            <button 
                                @click="store.copyToClipboard(store.apiKey, 'API Key')" 
                                :disabled="!store.apiKey"
                                class="px-4 py-2.5 rounded-2xl bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-100 text-xs font-semibold hover:bg-slate-300 dark:hover:bg-slate-600 spring-btn flex items-center space-x-1 disabled:opacity-40">
                                <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                                <span>复制</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Section 3: Mobile App Download Area -->
                <div class="glass-card p-6 rounded-3xl flex flex-col md:flex-row items-center justify-between gap-4">
                    <div class="space-y-1 text-center md:text-left">
                        <div class="flex items-center justify-center md:justify-start space-x-2">
                            <h3 class="font-bold text-sm">TideBot 移动端客户端</h3>
                            <span class="px-2 py-0.5 rounded-full bg-ios-blue/10 text-ios-blue text-[10px] font-bold">Flutter 跨端版</span>
                        </div>
                        <p class="text-xs text-slate-400">目前移动端 iOS/Android 客户端正处于内测封装阶段，敬请期待。</p>
                    </div>

                    <button @click="downloadAppPlaceholder" class="px-5 py-3 rounded-2xl bg-slate-200/80 dark:bg-slate-800/80 hover:bg-slate-300 dark:hover:bg-slate-700 text-xs font-bold spring-btn flex items-center space-x-2 shrink-0">
                        <i data-lucide="download" class="w-4 h-4 text-ios-blue"></i>
                        <span>获取手机 APP (预留)</span>
                    </button>
                </div>
            </div>
        </div>
    `,
    setup() {
        const goBack = () => {
            store.currentView = 'main';
        };

        const downloadAppPlaceholder = () => {
            store.showAlert('手机 APP 预留', 'TideBot Flutter App 目前正在内部打包测试，正式构建包发布后将开启一键安装下载通道。');
        };

        Vue.onMounted(() => {
            if (window.lucide) window.lucide.createIcons();
        });

        Vue.onUpdated(() => {
            if (window.lucide) window.lucide.createIcons();
        });

        return { store, goBack, downloadAppPlaceholder };
    }
};

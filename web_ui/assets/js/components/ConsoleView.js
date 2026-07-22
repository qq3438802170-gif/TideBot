// Console View Component with Rich Settings & Cards
const ConsoleView = {
    template: `
        <div class="h-full overflow-y-auto p-6 space-y-6 max-w-7xl mx-auto">
            <!-- Top Status Banner -->
            <div class="glass-card p-6 rounded-3xl relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-6 border-l-4 border-l-ios-blue">
                <div class="space-y-1 text-center md:text-left z-10">
                    <div class="flex items-center justify-center md:justify-start space-x-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-ios-green animate-ping"></span>
                        <h2 class="text-xl font-bold tracking-tight">TideBot 核心引擎运行正常</h2>
                    </div>
                    <p class="text-sm text-slate-500 dark:text-slate-400">事件总线、Agent 调度中心与 LLM Gateway 网关已就绪，保持高可靠响应。</p>
                </div>
                <div class="flex items-center space-x-4 z-10">
                    <div class="px-4 py-2 rounded-2xl bg-slate-100 dark:bg-slate-800/80 text-xs font-medium flex flex-col items-center">
                        <span class="text-slate-400">活跃 Adapters</span>
                        <span class="text-base font-bold text-ios-blue">2 个</span>
                    </div>
                    <div class="px-4 py-2 rounded-2xl bg-slate-100 dark:bg-slate-800/80 text-xs font-medium flex flex-col items-center">
                        <span class="text-slate-400">启用的插件</span>
                        <span class="text-base font-bold text-ios-green">2 个</span>
                    </div>
                    <button @click="reloadEngine" class="px-4 py-2 rounded-2xl bg-ios-blue text-white text-xs font-medium hover:bg-blue-600 spring-btn flex items-center space-x-1.5 shadow-ios-active">
                        <i data-lucide="refresh-cw" class="w-3.5 h-3.5"></i>
                        <span>热重载系统</span>
                    </button>
                </div>
            </div>

            <!-- Dashboard Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Card 1: Agent 人设与模型调度设置 -->
                <div class="glass-card p-6 rounded-3xl space-y-4">
                    <div class="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-700/60">
                        <div class="flex items-center space-x-2">
                            <div class="p-2 rounded-xl bg-ios-blue/10 text-ios-blue">
                                <i data-lucide="bot" class="w-5 h-5"></i>
                            </div>
                            <h3 class="font-bold text-base">Agent 人设与路由</h3>
                        </div>
                        <span class="text-xs px-2 py-0.5 rounded-full bg-ios-blue/10 text-ios-blue font-medium">ReAct 模式</span>
                    </div>

                    <div class="space-y-3 text-sm">
                        <div>
                            <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">智能体名称</label>
                            <input v-model="store.systemConfig.agentName" type="text" class="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700 text-xs focus:outline-none focus:ring-2 focus:ring-ios-blue">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">主 LLM 路由 (Primary)</label>
                            <select v-model="store.systemConfig.model" class="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700 text-xs focus:outline-none focus:ring-2 focus:ring-ios-blue">
                                <option>GPT-4o (Primary Router)</option>
                                <option>Claude 3.5 Sonnet</option>
                                <option>DeepSeek-V3 / R1</option>
                                <option>Gemini 1.5 Pro</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">兜底模型 (Fallback Router)</label>
                            <select v-model="store.systemConfig.fallbackModel" class="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700 text-xs focus:outline-none focus:ring-2 focus:ring-ios-blue">
                                <option>Claude 3.5 Sonnet</option>
                                <option>GPT-4o Mini</option>
                                <option>DeepSeek-Coder</option>
                            </select>
                        </div>
                        <div>
                            <div class="flex justify-between text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">
                                <span>生成随机度 (Temperature)</span>
                                <span class="text-ios-blue">{{ store.systemConfig.temperature }}</span>
                            </div>
                            <input v-model.number="store.systemConfig.temperature" type="range" min="0" max="1" step="0.1" class="w-full accent-ios-blue">
                        </div>
                    </div>
                </div>

                <!-- Card 2: 社交平台 Adapter 管理 -->
                <div class="glass-card p-6 rounded-3xl space-y-4">
                    <div class="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-700/60">
                        <div class="flex items-center space-x-2">
                            <div class="p-2 rounded-xl bg-ios-green/10 text-ios-green">
                                <i data-lucide="share-2" class="w-5 h-5"></i>
                            </div>
                            <h3 class="font-bold text-base">社交平台 Adapters</h3>
                        </div>
                        <span class="text-xs px-2 py-0.5 rounded-full bg-ios-green/10 text-ios-green font-medium">多网关监听</span>
                    </div>

                    <div class="space-y-3">
                        <!-- WeChat Adapter -->
                        <div class="flex items-center justify-between p-3 rounded-2xl bg-slate-100/70 dark:bg-slate-800/50 border border-slate-200/50 dark:border-slate-700/40">
                            <div class="flex items-center space-x-3">
                                <div class="w-8 h-8 rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center font-bold text-xs">
                                    WX
                                </div>
                                <div>
                                    <div class="text-xs font-bold">微信平台</div>
                                    <div class="text-[10px] text-slate-400">{{ store.systemConfig.adapters.wechat.account }}</div>
                                </div>
                            </div>
                            <div class="flex items-center space-x-2">
                                <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 font-medium">已连接</span>
                                <input type="checkbox" v-model="store.systemConfig.adapters.wechat.enabled" class="toggle accent-ios-blue">
                            </div>
                        </div>

                        <!-- Telegram Adapter -->
                        <div class="flex items-center justify-between p-3 rounded-2xl bg-slate-100/70 dark:bg-slate-800/50 border border-slate-200/50 dark:border-slate-700/40">
                            <div class="flex items-center space-x-3">
                                <div class="w-8 h-8 rounded-xl bg-sky-500/10 text-sky-500 flex items-center justify-center font-bold text-xs">
                                    TG
                                </div>
                                <div>
                                    <div class="text-xs font-bold">Telegram Bot</div>
                                    <div class="text-[10px] text-slate-400">{{ store.systemConfig.adapters.telegram.botName }}</div>
                                </div>
                            </div>
                            <div class="flex items-center space-x-2">
                                <span class="text-[10px] px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-500 font-medium">在线</span>
                                <input type="checkbox" v-model="store.systemConfig.adapters.telegram.enabled" class="toggle accent-ios-blue">
                            </div>
                        </div>

                        <!-- QQ Adapter -->
                        <div class="flex items-center justify-between p-3 rounded-2xl bg-slate-100/70 dark:bg-slate-800/50 border border-slate-200/50 dark:border-slate-700/40 opacity-75">
                            <div class="flex items-center space-x-3">
                                <div class="w-8 h-8 rounded-xl bg-blue-500/10 text-blue-500 flex items-center justify-center font-bold text-xs">
                                    QQ
                                </div>
                                <div>
                                    <div class="text-xs font-bold">QQ 机器人</div>
                                    <div class="text-[10px] text-slate-400">未绑定账号</div>
                                </div>
                            </div>
                            <div class="flex items-center space-x-2">
                                <span class="text-[10px] px-2 py-0.5 rounded-full bg-slate-500/10 text-slate-400 font-medium">未启用</span>
                                <input type="checkbox" v-model="store.systemConfig.adapters.qq.enabled" class="toggle accent-ios-blue">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Card 3: 系统高级参数与穿透 -->
                <div class="glass-card p-6 rounded-3xl space-y-4">
                    <div class="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-700/60">
                        <div class="flex items-center space-x-2">
                            <div class="p-2 rounded-xl bg-ios-orange/10 text-ios-orange">
                                <i data-lucide="sliders" class="w-5 h-5"></i>
                            </div>
                            <h3 class="font-bold text-base">系统核心设置</h3>
                        </div>
                        <span class="text-xs px-2 py-0.5 rounded-full bg-ios-orange/10 text-ios-orange font-medium">全局引擎</span>
                    </div>

                    <div class="space-y-4 text-xs">
                        <div class="flex items-center justify-between p-3 rounded-2xl bg-slate-100/70 dark:bg-slate-800/50">
                            <div>
                                <div class="font-bold">WebSocket 流式响应</div>
                                <div class="text-[10px] text-slate-400">开启打字机高帧率数据流推送</div>
                            </div>
                            <input type="checkbox" v-model="store.systemConfig.streamResponse" class="toggle accent-ios-blue">
                        </div>

                        <div class="flex items-center justify-between p-3 rounded-2xl bg-slate-100/70 dark:bg-slate-800/50">
                            <div>
                                <div class="font-bold">Cloudflare 穿透自启</div>
                                <div class="text-[10px] text-slate-400">启动服务端时自动建立公网 Tunnel</div>
                            </div>
                            <input type="checkbox" v-model="store.systemConfig.cfTunnelAutoStart" class="toggle accent-ios-blue">
                        </div>

                        <button @click="saveSettings" class="w-full py-2.5 rounded-xl bg-slate-900 dark:bg-slate-100 dark:text-slate-900 text-white font-semibold text-xs hover:opacity-90 spring-btn">
                            保存全局配置变更
                        </button>
                    </div>
                </div>
            </div>

            <!-- Card 4: 扩展插件中心 Capability Registry (Full Width) -->
            <div class="glass-card p-6 rounded-3xl space-y-4">
                <div class="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-700/60">
                    <div class="flex items-center space-x-2">
                        <div class="p-2 rounded-xl bg-ios-indigo/10 text-ios-indigo">
                            <i data-lucide="puzzle" class="w-5 h-5"></i>
                        </div>
                        <h3 class="font-bold text-base">能力注册中心与插件库 (TideBot-Plugins)</h3>
                    </div>
                    <button @click="installNewPlugin" class="px-3 py-1.5 rounded-xl bg-ios-blue/10 text-ios-blue hover:bg-ios-blue/20 text-xs font-semibold spring-btn flex items-center space-x-1">
                        <i data-lucide="plus" class="w-3.5 h-3.5"></i>
                        <span>安装外部插件</span>
                    </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div v-for="plugin in store.systemConfig.plugins" :key="plugin.id" class="p-4 rounded-2xl bg-slate-100/80 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/50 flex flex-col justify-between space-y-3">
                        <div>
                            <div class="flex items-center justify-between">
                                <span class="font-bold text-sm text-slate-900 dark:text-white">{{ plugin.name }}</span>
                                <span class="text-[10px] px-2 py-0.5 rounded-md bg-slate-200 dark:bg-slate-700 text-slate-500 font-mono">{{ plugin.version }}</span>
                            </div>
                            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">{{ plugin.desc }}</p>
                        </div>
                        <div class="flex items-center justify-between pt-2 border-t border-slate-200/50 dark:border-slate-700/40">
                            <span :class="['text-[10px] font-semibold px-2 py-0.5 rounded-full', plugin.status === 'active' ? 'bg-ios-green/10 text-ios-green' : 'bg-slate-500/10 text-slate-400']">
                                {{ plugin.status === 'active' ? '运行中' : '未开启' }}
                            </span>
                            <button @click="togglePlugin(plugin)" class="text-xs text-ios-blue hover:underline font-medium">
                                {{ plugin.status === 'active' ? '停用' : '启用' }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    setup() {
        const reloadEngine = () => {
            store.showToast('系统引擎与事件总线已完成热重载！', 'success');
        };

        const saveSettings = () => {
            store.showToast('全局系统配置已修改并保存', 'success');
        };

        const installNewPlugin = () => {
            store.showAlert('安装插件', '请使用 TideBot-SDK CLI 提交插件仓库 Git 链接，或将 .tbplugin 包直接解压放入 plugins/ 目录。');
        };

        const togglePlugin = (plugin) => {
            plugin.status = plugin.status === 'active' ? 'disabled' : 'active';
            store.showToast(`插件 ${plugin.name} 状态更新成功`, 'info');
        };

        Vue.onMounted(() => {
            if (window.lucide) window.lucide.createIcons();
        });

        return { store, reloadEngine, saveSettings, installNewPlugin, togglePlugin };
    }
};

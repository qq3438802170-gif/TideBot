// Top Navigation Bar Component
const NavbarComponent = {
    template: `
        <header class="h-16 px-5 flex items-center justify-between glass-panel sticky top-0 z-40 shadow-sm border-b transition-all duration-300">
            <!-- Left Side Title -->
            <div class="flex items-center space-x-3 cursor-pointer" @click="goHome">
                <div class="w-9 h-9 rounded-2xl bg-gradient-to-tr from-ios-blue to-indigo-500 flex items-center justify-center text-white shadow-ios-active">
                    <i data-lucide="waves" class="w-5 h-5"></i>
                </div>
                <div class="flex items-baseline select-none">
                    <span class="text-xl font-bold tracking-tight text-slate-900 dark:text-white">TideBot</span>
                    <!-- Dynamic Subtitle based on mode/view -->
                    <span v-if="store.currentView === 'app-connect'" class="text-xs font-medium text-ios-blue dark:text-ios-teal ml-1.5 px-2 py-0.5 rounded-full bg-ios-blue/10">
                        APP连接设置
                    </span>
                    <span v-else-if="store.currentMode === 'console'" class="text-xs font-normal text-slate-500 dark:text-slate-400 ml-1">
                        控制台
                    </span>
                    <span v-else-if="store.currentMode === 'chat'" class="text-xs font-normal text-slate-500 dark:text-slate-400 ml-1">
                        chat
                    </span>
                </div>
            </div>

            <!-- Right Side Controls -->
            <div class="flex items-center space-x-3">
                <!-- Connect App Button -->
                <button 
                    @click="store.openAppConnect()" 
                    :class="[
                        'px-3.5 py-1.5 rounded-xl text-xs font-medium flex items-center space-x-1.5 spring-btn border transition-all',
                        store.currentView === 'app-connect' 
                            ? 'bg-ios-blue text-white border-ios-blue shadow-md' 
                            : 'bg-white/80 dark:bg-slate-800/80 text-slate-700 dark:text-slate-200 border-slate-200 dark:border-slate-700/80 hover:bg-slate-100 dark:hover:bg-slate-700'
                    ]">
                    <i data-lucide="smartphone" class="w-3.5 h-3.5"></i>
                    <span>连接APP</span>
                </button>

                <!-- Day/Night Mode Switch -->
                <button 
                    @click="store.toggleTheme()" 
                    class="p-2 rounded-xl bg-slate-200/60 dark:bg-slate-800/80 text-slate-700 dark:text-amber-400 hover:bg-slate-300/60 dark:hover:bg-slate-700/80 transition-all spring-btn"
                    title="切换主题模式">
                    <i v-if="store.isDarkMode" data-lucide="moon" class="w-4 h-4"></i>
                    <i v-else data-lucide="sun" class="w-4 h-4 text-amber-500"></i>
                </button>

                <!-- Console / Chat Mode Toggle Switch -->
                <div class="p-1 bg-slate-200/80 dark:bg-slate-800/90 rounded-2xl flex items-center relative w-40 h-9 border border-slate-300/40 dark:border-slate-700/50">
                    <!-- Sliding Pill background -->
                    <div 
                        class="absolute top-1 bottom-1 rounded-xl bg-white dark:bg-ios-blue shadow-sm transition-all duration-300 ease-out"
                        :style="{
                            left: store.currentMode === 'console' ? '4px' : 'calc(50% + 2px)',
                            width: 'calc(50% - 6px)'
                        }">
                    </div>

                    <!-- Toggle Options -->
                    <button 
                        @click="store.setMode('console')" 
                        :class="[
                            'flex-1 text-center text-xs font-semibold z-10 transition-colors duration-200 flex items-center justify-center space-x-1',
                            store.currentMode === 'console' 
                                ? 'text-slate-900 dark:text-white' 
                                : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
                        ]">
                        <i data-lucide="layout-dashboard" class="w-3.5 h-3.5"></i>
                        <span>控制台</span>
                    </button>

                    <button 
                        @click="store.setMode('chat')" 
                        :class="[
                            'flex-1 text-center text-xs font-semibold z-10 transition-colors duration-200 flex items-center justify-center space-x-1',
                            store.currentMode === 'chat' 
                                ? 'text-slate-900 dark:text-white' 
                                : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
                        ]">
                        <i data-lucide="message-square" class="w-3.5 h-3.5"></i>
                        <span>Chat</span>
                    </button>
                </div>
            </div>
        </header>
    `,
    setup() {
        const goHome = () => {
            store.currentView = 'main';
        };
        Vue.onMounted(() => {
            if (window.lucide) window.lucide.createIcons();
        });
        Vue.onUpdated(() => {
            if (window.lucide) window.lucide.createIcons();
        });
        return { store, goHome };
    }
};

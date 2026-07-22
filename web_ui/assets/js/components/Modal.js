// Custom iOS Glass Modal & Toast Dialog Component (NO Native Alert)
const ModalComponent = {
    template: `
        <div>
            <!-- Custom Modal Backdrop & Dialog -->
            <transition name="fade-slide">
                <div v-if="store.modal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-md">
                    <div class="glass-card w-full max-w-sm rounded-3xl p-6 shadow-2xl space-y-4 border border-white/30 dark:border-slate-700/60 transform transition-all">
                        <div class="space-y-2 text-center">
                            <h3 class="text-base font-bold text-slate-900 dark:text-white">{{ store.modal.title }}</h3>
                            <p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{{ store.modal.message }}</p>
                        </div>

                        <div class="flex items-center space-x-3 pt-2">
                            <button 
                                v-if="store.modal.cancelText"
                                @click="store.modal.show = false" 
                                class="flex-1 py-2.5 rounded-2xl bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-semibold hover:bg-slate-300 dark:hover:bg-slate-700 spring-btn">
                                {{ store.modal.cancelText }}
                            </button>
                            <button 
                                @click="confirmModal" 
                                class="flex-1 py-2.5 rounded-2xl bg-ios-blue text-white text-xs font-semibold hover:bg-blue-600 spring-btn shadow-ios-active">
                                {{ store.modal.confirmText }}
                            </button>
                        </div>
                    </div>
                </div>
            </transition>

            <!-- Custom Toast Floating Capsule -->
            <transition name="fade-slide">
                <div v-if="store.toast.show" class="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 px-5 py-2.5 rounded-full glass-panel shadow-glass-md flex items-center space-x-2 border border-white/40 dark:border-slate-700/80">
                    <i v-if="store.toast.type === 'success'" data-lucide="check-circle-2" class="w-4 h-4 text-ios-green"></i>
                    <i v-else-if="store.toast.type === 'error'" data-lucide="x-circle" class="w-4 h-4 text-ios-red"></i>
                    <i v-else data-lucide="info" class="w-4 h-4 text-ios-blue"></i>
                    <span class="text-xs font-semibold text-slate-800 dark:text-slate-100">{{ store.toast.message }}</span>
                </div>
            </transition>
        </div>
    `,
    setup() {
        const confirmModal = () => {
            if (store.modal.onConfirm) {
                store.modal.onConfirm();
            } else {
                store.modal.show = false;
            }
        };

        Vue.onUpdated(() => {
            if (window.lucide) window.lucide.createIcons();
        });

        return { store, confirmModal };
    }
};

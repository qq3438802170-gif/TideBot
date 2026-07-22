// Chat View Component with Glassmorphism Bubbles & Interactive Agent
const ChatView = {
    template: `
        <div class="h-full flex overflow-hidden">
            <!-- Sidebar Conversation List -->
            <aside class="w-72 glass-panel border-r border-slate-200/60 dark:border-slate-800/80 flex flex-col hidden md:flex">
                <div class="p-4 border-b border-slate-200/60 dark:border-slate-800/80 flex items-center justify-between">
                    <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">对话历史</span>
                    <button @click="createNewChat" class="p-1.5 rounded-xl bg-ios-blue text-white spring-btn shadow-ios-active" title="新建对话">
                        <i data-lucide="plus" class="w-4 h-4"></i>
                    </button>
                </div>

                <div class="flex-1 overflow-y-auto p-3 space-y-2">
                    <div 
                        v-for="chat in store.conversations" 
                        :key="chat.id"
                        @click="store.activeConversationId = chat.id"
                        :class="[
                            'p-3 rounded-2xl cursor-pointer transition-all duration-200 flex flex-col space-y-1',
                            store.activeConversationId === chat.id 
                                ? 'bg-ios-blue/10 border border-ios-blue/30 text-ios-blue dark:text-white font-medium shadow-sm' 
                                : 'hover:bg-slate-200/50 dark:hover:bg-slate-800/50 text-slate-600 dark:text-slate-300'
                        ]">
                        <div class="flex items-center justify-between text-xs">
                            <span class="truncate font-semibold max-w-[140px]">{{ chat.title }}</span>
                            <span class="text-[10px] text-slate-400">{{ chat.time }}</span>
                        </div>
                        <p class="text-[11px] text-slate-400 truncate">
                            {{ chat.messages[chat.messages.length - 1]?.text || '无消息' }}
                        </p>
                    </div>
                </div>
            </aside>

            <!-- Main Chat Conversation Window -->
            <section class="flex-1 flex flex-col h-full bg-slate-50/50 dark:bg-ios-bgDark/50 relative">
                <!-- Chat Window Header -->
                <div class="h-12 px-6 glass-panel border-b border-slate-200/60 dark:border-slate-800/80 flex items-center justify-between z-10">
                    <div class="flex items-center space-x-2">
                        <span class="w-2 h-2 rounded-full bg-ios-green"></span>
                        <span class="text-xs font-bold">{{ currentChat?.title || '新对话' }}</span>
                        <span class="text-[10px] px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-500 font-mono">GPT-4o Agent</span>
                    </div>
                    <button @click="clearChat" class="text-slate-400 hover:text-ios-red text-xs transition-colors">
                        清空此会话
                    </button>
                </div>

                <!-- Chat Messages Stream Area -->
                <div ref="msgContainer" class="flex-1 overflow-y-auto p-6 space-y-6">
                    <div v-for="msg in currentChat?.messages" :key="msg.id" :class="['flex flex-col', msg.sender === 'user' ? 'items-end' : 'items-start']">
                        <!-- Bot Thought / Tool Execution Badge -->
                        <div v-if="msg.thoughts" class="mb-2 text-[10px] px-3 py-1 rounded-xl bg-ios-indigo/10 text-ios-indigo border border-ios-indigo/20 flex items-center space-x-1.5 animate-pulse">
                            <i data-lucide="cpu" class="w-3 h-3"></i>
                            <span>{{ msg.thoughts }}</span>
                        </div>

                        <div class="flex items-end space-x-2 max-w-[85%] md:max-w-[70%]">
                            <!-- Bot Avatar -->
                            <div v-if="msg.sender === 'bot'" class="w-8 h-8 rounded-2xl bg-gradient-to-tr from-ios-blue to-indigo-500 text-white flex items-center justify-center shrink-0 shadow-sm text-xs font-bold">
                                TB
                            </div>

                            <!-- Message Content Box -->
                            <div :class="[
                                'p-4 rounded-3xl text-xs leading-relaxed space-y-1',
                                msg.sender === 'user' 
                                    ? 'chat-bubble-user text-white rounded-br-none' 
                                    : 'chat-bubble-bot text-slate-800 dark:text-slate-100 rounded-bl-none'
                            ]">
                                <div class="whitespace-pre-wrap">{{ msg.text }}</div>
                                <div :class="['text-[9px] text-right mt-1', msg.sender === 'user' ? 'text-blue-100' : 'text-slate-400']">
                                    {{ msg.time }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Chat Input Dock (iOS Floating Glass Style) -->
                <div class="p-4 glass-panel border-t border-slate-200/60 dark:border-slate-800/80">
                    <div class="max-w-4xl mx-auto flex items-center space-x-3 bg-white/80 dark:bg-slate-800/80 p-2 rounded-2xl border border-slate-200/80 dark:border-slate-700/80 shadow-lg">
                        <button @click="triggerAttachment" class="p-2 rounded-xl text-slate-400 hover:text-ios-blue hover:bg-slate-100 dark:hover:bg-slate-700 spring-btn">
                            <i data-lucide="paperclip" class="w-4 h-4"></i>
                        </button>

                        <textarea 
                            v-model="inputQuery" 
                            @keydown.enter.prevent="sendMessage"
                            rows="1" 
                            placeholder="发送消息给 TideBot Agent... (Press Enter)" 
                            class="flex-1 bg-transparent border-none text-xs focus:outline-none resize-none px-2 py-1.5 text-slate-800 dark:text-slate-100 placeholder-slate-400">
                        </textarea>

                        <button 
                            @click="sendMessage" 
                            :disabled="!inputQuery.trim()"
                            :class="[
                                'p-2 rounded-xl transition-all spring-btn text-white',
                                inputQuery.trim() ? 'bg-ios-blue shadow-ios-active cursor-pointer' : 'bg-slate-300 dark:bg-slate-700 cursor-not-allowed opacity-50'
                            ]">
                            <i data-lucide="send" class="w-4 h-4"></i>
                        </button>
                    </div>
                </div>
            </section>
        </div>
    `,
    setup() {
        const inputQuery = Vue.ref('');
        const msgContainer = Vue.ref(null);

        const currentChat = Vue.computed(() => {
            return store.conversations.find(c => c.id === store.activeConversationId);
        });

        const scrollToBottom = () => {
            Vue.nextTick(() => {
                if (msgContainer.value) {
                    msgContainer.value.scrollTop = msgContainer.value.scrollHeight;
                }
            });
        };

        const sendMessage = () => {
            const text = inputQuery.value.trim();
            if (!text || !currentChat.value) return;

            const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            // User Message
            currentChat.value.messages.push({
                id: 'm_' + Date.now(),
                sender: 'user',
                text: text,
                time: timeNow
            });

            inputQuery.value = '';
            scrollToBottom();

            // Simulate Agent Pipeline Processing
            setTimeout(() => {
                const botMsgId = 'm_' + (Date.now() + 1);
                currentChat.value.messages.push({
                    id: botMsgId,
                    sender: 'bot',
                    text: 'Thinking...',
                    time: timeNow,
                    thoughts: 'Agent Workflow: 正在调用底层插件并生成打字流...'
                });
                scrollToBottom();

                // Mock streaming response
                let i = 0;
                const fullReply = `收到指令：“${text}”。TideBot Agent 已成功通过事件总线处理您的输入，当前响应流正常。`;
                const targetMsg = currentChat.value.messages.find(m => m.id === botMsgId);
                targetMsg.text = '';

                const interval = setInterval(() => {
                    if (i < fullReply.length) {
                        targetMsg.text += fullReply[i];
                        i++;
                        scrollToBottom();
                    } else {
                        clearInterval(interval);
                        targetMsg.thoughts = null; // Clear active thought indicator when done
                    }
                }, 40);
            }, 600);
        };

        const createNewChat = () => {
            const newId = 'c_' + Date.now();
            store.conversations.unshift({
                id: newId,
                title: '全新对话 ' + (store.conversations.length + 1),
                time: '刚刚',
                messages: [
                    { id: 'm1', sender: 'bot', text: '你好！我是 TideBot。开启新的智能探索吧！', time: '刚刚' }
                ]
            });
            store.activeConversationId = newId;
        };

        const clearChat = () => {
            if (currentChat.value) {
                store.showConfirm('清空消息', '确定要清空此对话的所有消息记录吗？', () => {
                    currentChat.value.messages = [];
                    store.showToast('对话已清空', 'info');
                });
            }
        };

        const triggerAttachment = () => {
            store.showAlert('文件上传', '可以通过插件选择或直接拖拽文件/图片至窗口发送给 Agent 解析。');
        };

        Vue.onMounted(() => {
            scrollToBottom();
            if (window.lucide) window.lucide.createIcons();
        });

        Vue.onUpdated(() => {
            if (window.lucide) window.lucide.createIcons();
        });

        return { store, inputQuery, currentChat, msgContainer, sendMessage, createNewChat, clearChat, triggerAttachment };
    }
};

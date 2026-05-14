// 卫星遥感智能问答系统 - 修复白屏问题并优化支持格式显示

document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const loadingTemplate = document.getElementById('loading-template');
    
    // 附件相关元素
    const attachmentInput = document.getElementById('attachment-input');
    const attachmentBtn = document.getElementById('attachment-btn');
    const attachmentPreview = document.getElementById('attachment-preview');
    const attachmentPreviewContainer = document.getElementById('attachment-preview-container');
    const inputContainer = document.querySelector('.input-container');
    
    // 右键菜单
    const contextMenu = document.getElementById('context-menu');
    
    // 当前选中的文件用于右键删除
    let selectedFileForDeletion = null;
    
    // 对话历史数组
    let chatHistory = [];
    
    // 文件类型图标映射 - 使用更专业的SVG图标类名
    const fileTypeIcons = {
        'pdf': 'pdf',
        'txt': 'txt', 
        'doc': 'doc',
        'docx': 'docx',
        'md': 'txt',
        'csv': 'csv',
        'json': 'json',
        'tif': 'tif',
        'tiff': 'tiff',
        'img': 'img',
        'hdr': 'tif',
        'bil': 'tif',
        'bsq': 'tif',
        'bip': 'tif',
        'nc': 'tif',
        'hdf': 'tif',
        'h5': 'tif',
        'shp': 'shp',
        'geojson': 'geojson',
        'kml': 'shp',
        'kmz': 'shp',
        'gpx': 'shp',
        'jpg': 'jpg',
        'jpeg': 'jpg',
        'png': 'png',
        'bmp': 'img',
        'gif': 'img',
        'default': 'txt'
    };
    
    // 支持的文件格式
    const SUPPORTED_FORMATS = ['.pdf', '.txt', '.doc', '.docx', '.md', '.csv', '.json', '.tif', '.tiff', '.img', '.hdr', '.bil', '.bsq', '.bip', '.nc', '.hdf', '.h5', '.shp', '.geojson', '.kml', '.kmz', '.gpx', '.jpg', '.jpeg', '.png', '.bmp', '.gif'];
    
    // 自动调整文本区域高度
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
    
    // 初始化时清空输入框，确保新会话
    userInput.value = '';
    userInput.style.height = 'auto';
    
    // 设置欢迎消息的时间
    const welcomeTimeElement = document.getElementById('welcome-message-time');
    if (welcomeTimeElement) {
        const now = new Date();
        const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
        welcomeTimeElement.textContent = timeString;
    }
    
    // 添加模型状态监测
    checkModelStatus();
    setInterval(checkModelStatus, 30000); // 每30秒检查一次
    
    // 处理文件选择
    attachmentInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        handleFileSelection(files);
    });

    // 拖拽文件处理
    inputContainer.addEventListener('drop', function(e) {
        e.preventDefault();
        inputContainer.classList.remove('drag-over');
        const files = Array.from(e.dataTransfer.files);
        handleFileSelection(files);
        
        // 确保焦点返回到输入框
        setTimeout(() => {
            userInput.focus();
        }, 10);
    });

    // 处理文件选择的通用函数
    function handleFileSelection(files) {
        let hasDocFiles = false;
        let validFiles = [];
        
        files.forEach(file => {
            // 修正：file.filename 应该是 file.name
            if (!file.name) {
                return;
            }
            
            const fileExt = file.name.split('.').pop().toLowerCase();
            
            // 检查是否为DOC文件
            if (fileExt === 'doc') {
                hasDocFiles = true;
            }
            
            // 检查文件类型是否支持
            if (!SUPPORTED_FORMATS.includes('.' + fileExt)) {
                alert(`不支持的文件格式: ${file.name}\n支持的格式: ${SUPPORTED_FORMATS.join(', ')}`);
                return;
            }
            
            validFiles.push(file);
        });
        
        // 如果有有效的文件，更新文件输入
        if (validFiles.length > 0) {
            const dataTransfer = new DataTransfer();
            validFiles.forEach(file => dataTransfer.items.add(file));
            attachmentInput.files = dataTransfer.files;
            updateAttachmentPreview();
        }
        
        // 如果有DOC文件，显示提示
        if (hasDocFiles) {
            const docHint = document.createElement('div');
            docHint.className = 'doc-hint';
            docHint.style.cssText = `
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 4px;
                padding: 8px 12px;
                margin: 8px 0;
                font-size: 12px;
                color: #856404;
            `;
            docHint.innerHTML = '💡 提示: .doc文件仅支持基本信息提取，建议转换为.docx格式以获得完整内容支持。';
            
            // 在输入框上方显示提示
            const inputContainer = document.querySelector('.input-container');
            if (inputContainer && !document.querySelector('.doc-hint')) {
                inputContainer.parentNode.insertBefore(docHint, inputContainer);
                
                // 3秒后自动移除提示
                setTimeout(() => {
                    if (docHint.parentNode) {
                        docHint.parentNode.removeChild(docHint);
                    }
                }, 3000);
            }
        }
        
        updatePreviewVisibility();
        
        // 如果有有效文件，确保焦点返回到输入框
        if (validFiles.length > 0) {
            setTimeout(() => {
                userInput.focus();
            }, 10);
        }
    }
    
    // 打开文件选择对话框
    attachmentBtn.addEventListener('click', function() {
        attachmentInput.click();
    });
    
    // 获取文件扩展名
    function getFileExtension(filename) {
        return filename.split('.').pop().toLowerCase();
    }
    
    // 获取文件图标类名（修复未定义函数问题）
    function getFileIconClass(filename) {
        const ext = getFileExtension(filename);
        const iconMap = {
            'pdf': '📄',
            'txt': '📄',
            'doc': '📄',
            'docx': '📄',
            'md': '📄',
            'csv': '📊',
            'json': '📋',
            'tif': '🛰️',
            'tiff': '🛰️',
            'img': '🛰️',
            'hdr': '🛰️',
            'bil': '🛰️',
            'bsq': '🛰️',
            'bip': '🛰️',
            'nc': '🛰️',
            'hdf': '🛰️',
            'h5': '🛰️',
            'shp': '🗺️',
            'geojson': '🗺️',
            'kml': '🗺️',
            'kmz': '🗺️',
            'gpx': '🗺️',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'png': '🖼️',
            'bmp': '🖼️',
            'gif': '🖼️',
            'default': '📄'
        };
        return iconMap[ext] || iconMap['default'];
    }
    
    // 获取文件图标SVG
    function getFileIconSVG(ext) {
        const iconMap = {
            'pdf': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
            </svg>`,
            'doc': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
            </svg>`,
            'docx': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
            </svg>`,
            'txt': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
            </svg>`,
            'md': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
            </svg>`,
            'csv': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
            </svg>`,
            'json': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
            </svg>`,
            'tif': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
            </svg>`,
            'tiff': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
            </svg>`,
            'shp': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="12,2 20,8 20,16 12,22 4,16 4,8 12,2"></polygon>
                <line x1="12" y1="2" x2="12" y2="22"></line>
                <line x1="4" y1="8" x2="20" y2="8"></line>
                <line x1="4" y1="16" x2="20" y2="16"></line>
            </svg>`,
            'geojson': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="12,2 20,8 20,16 12,22 4,16 4,8 12,2"></polygon>
                <line x1="12" y1="2" x2="12" y2="22"></line>
                <line x1="4" y1="8" x2="20" y2="8"></line>
                <line x1="4" y1="16" x2="20" y2="16"></line>
            </svg>`,
            'jpg': '', // 图片文件使用实际缩略图，不需要SVG
            'jpeg': '', // 图片文件使用实际缩略图，不需要SVG  
            'png': '', // 图片文件使用实际缩略图，不需要SVG
            'bmp': '', // 图片文件使用实际缩略图，不需要SVG
            'gif': '', // 图片文件使用实际缩略图，不需要SVG
            'default': `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
            </svg>`
        };
        
        return iconMap[ext] || iconMap['default'];
    }

    // 为图片文件创建缩略图（其他文件返回 null）
    function createThumbnailForFile(file) {
        return new Promise((resolve) => {
            const ext = getFileExtension(file.name);
            if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext)) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    resolve(e.target.result);
                };
                reader.onerror = function() {
                    resolve(null);
                };
                reader.readAsDataURL(file);
            } else {
                resolve(null);
            }
        });
    }
    
    // 更新附件预览
    function updateAttachmentPreview() {
        attachmentPreview.innerHTML = '';
        const files = attachmentInput.files;
        if (files && files.length > 0) {
            // 为每个文件创建预览项
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                const fileItem = document.createElement('div');
                fileItem.className = 'attachment-item';
                fileItem.dataset.index = i;
                
                // 检查是否为图片文件以显示缩略图
                const ext = getFileExtension(file.name);
                const isImage = ['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext);
                
                const thumbnailContainer = document.createElement('div');
                thumbnailContainer.className = 'attachment-thumbnail';
                
                if (isImage) {
                    // 创建图片缩略图
                    const img = document.createElement('img');
                    img.src = URL.createObjectURL(file);
                    img.alt = '缩略图';
                    img.style.width = '32px';
                    img.style.height = '32px';
                    img.style.objectFit = 'cover';
                    img.style.borderRadius = '4px';
                    thumbnailContainer.appendChild(img);
                } else {
                    // 显示SVG图标
                    const iconSVG = getFileIconSVG(ext);
                    if (iconSVG) {
                        thumbnailContainer.innerHTML = iconSVG;
                    } else {
                        // 如果没有SVG，显示默认图标
                        thumbnailContainer.innerHTML = getFileIconSVG('default');
                    }
                }
                
                fileItem.appendChild(thumbnailContainer);
                
                // 文件名
                const filenameDiv = document.createElement('div');
                filenameDiv.className = 'attachment-filename';
                filenameDiv.title = file.name;
                // 截断长文件名
                const displayFilename = file.name.length > 20 ? file.name.substring(0, 17) + '...' : file.name;
                filenameDiv.textContent = displayFilename;
                fileItem.appendChild(filenameDiv);
                
                // 删除按钮
                const removeBtn = document.createElement('button');
                removeBtn.className = 'remove-attachment';
                removeBtn.type = 'button';
                removeBtn.textContent = '×';
                removeBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    removeFileFromInput(i);
                });
                fileItem.appendChild(removeBtn);
                
                attachmentPreview.appendChild(fileItem);
            }
            attachmentPreviewContainer.classList.add('show');
        } else {
            attachmentPreviewContainer.classList.remove('show');
        }
        
        // 绑定右键菜单事件
        bindRemoveEvents();
    }
    
    // 绑定删除事件
    function bindRemoveEvents() {
        // 右键菜单事件绑定到附件项
        document.querySelectorAll('.attachment-item').forEach((item, index) => {
            item.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                selectedFileForDeletion = index;
                contextMenu.style.left = e.pageX + 'px';
                contextMenu.style.top = e.pageY + 'px';
                contextMenu.style.display = 'block';
            });
        });
    }
    
    // 从输入中移除指定索引的文件
    function removeFileFromInput(indexToRemove) {
        const files = Array.from(attachmentInput.files);
        files.splice(indexToRemove, 1);
        const dataTransfer = new DataTransfer();
        files.forEach(file => dataTransfer.items.add(file));
        attachmentInput.files = dataTransfer.files;
        updateAttachmentPreview();
        if (dataTransfer.files.length === 0) {
            localStorage.removeItem('attachments');
        }
    }
    
    // 发送消息函数
    async function sendMessageWithFiles() {
        const query = userInput.value.trim();
        if (!query) return;
        
        // 获取当前附件信息用于显示在用户消息上方（包含图片缩略图）
        const currentFiles = attachmentInput.files;
        let attachmentInfo = null;
        let filesToUpload = [];
        
        if (currentFiles && currentFiles.length > 0) {
            // 创建文件的副本用于上传，避免清除预览后文件丢失
            filesToUpload = Array.from(currentFiles);
            
            const thumbPromises = filesToUpload.map(f => createThumbnailForFile(f));
            const thumbs = await Promise.all(thumbPromises);
            attachmentInfo = {
                files: filesToUpload.map((f, idx) => ({
                    name: f.name,
                    icon: getFileIconClass(f.name),
                    thumbnail: thumbs[idx] // dataURL 或 null
                }))
            };
        }
        
        // 添加用户消息（包含附件预览）
        addMessageToChat(query, 'user', attachmentInfo);
        
        // 将用户消息添加到对话历史
        chatHistory.push({
            role: 'user',
            content: query
        });
        
        // 立即清除对话框上方的文件预览（在发送请求前就清除）
        attachmentInput.value = '';
        updateAttachmentPreview();
        
        const currentInput = userInput.value;
        userInput.value = '';
        userInput.style.height = 'auto';
        
        // 显示加载指示器
        const loadingElement = loadingTemplate.cloneNode(true);
        loadingElement.style.display = 'flex';
        loadingElement.id = 'loading-indicator';
        chatMessages.appendChild(loadingElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // 显示文件上传进度条（如果有文件）
        let uploadProgressElement = null;
        if (filesToUpload && filesToUpload.length > 0) {
            const progressTemplate = document.getElementById('upload-progress-template');
            if (progressTemplate) {
                uploadProgressElement = progressTemplate.cloneNode(true);
                uploadProgressElement.style.display = 'flex';
                uploadProgressElement.id = 'upload-progress-indicator';
                chatMessages.insertBefore(uploadProgressElement, loadingElement);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
        
        try {
            const formData = new FormData();
            formData.append('query', query);
            formData.append('chat_history', JSON.stringify(chatHistory));  // 添加对话历史
            
            if (filesToUpload && filesToUpload.length > 0) {
                // 移除50MB文件大小限制，支持更大的遥感数据文件
                // 只保留基本的文件验证
                
                for (let i = 0; i < filesToUpload.length; i++) {
                    formData.append('files', filesToUpload[i]);
                }
            }
            
            // 使用XMLHttpRequest以支持上传进度
            const xhr = new XMLHttpRequest();
            
            // 监听上传进度
            if (uploadProgressElement) {
                xhr.upload.addEventListener('progress', function(e) {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        const progressFill = uploadProgressElement.querySelector('.upload-progress-fill');
                        if (progressFill) {
                            progressFill.style.width = percentComplete + '%';
                        }
                        const timeElement = uploadProgressElement.querySelector('.message-time');
                        if (timeElement) {
                            timeElement.textContent = `文件上传中... ${Math.round(percentComplete)}%`;
                        }
                    }
                });
            }
            
            // 监听完成事件
            xhr.addEventListener('load', function() {
                // 移除上传进度条
                if (uploadProgressElement) {
                    const progressIndicator = document.getElementById('upload-progress-indicator');
                    if (progressIndicator) {
                        progressIndicator.remove();
                    }
                }
                
                const loadingIndicator = document.getElementById('loading-indicator');
                if (loadingIndicator) {
                    loadingIndicator.remove();
                }
                
                if (xhr.status === 200) {
                    const data = JSON.parse(xhr.responseText);
                    // 添加助手回复
                    addMessageToChat(data.answer, 'assistant', null, data.processing_time);
                    
                    // 将助手回复添加到对话历史
                    chatHistory.push({
                        role: 'assistant',
                        content: data.answer
                    });
                } else {
                    addMessageToChat('抱歉，服务暂时不可用。请确保Ollama正在运行。', 'assistant');
                }
            });
            
            // 监听错误事件
            xhr.addEventListener('error', function() {
                // 移除上传进度条
                if (uploadProgressElement) {
                    const progressIndicator = document.getElementById('upload-progress-indicator');
                    if (progressIndicator) {
                        progressIndicator.remove();
                    }
                }
                
                const loadingIndicator = document.getElementById('loading-indicator');
                if (loadingIndicator) {
                    loadingIndicator.remove();
                }
                
                addMessageToChat('抱歉，服务暂时不可用。请确保Ollama正在运行。', 'assistant');
            });
            
            // 发送请求
            xhr.open('POST', '/api/v1/query');
            xhr.timeout = 90000; // 90秒超时
            xhr.send(formData);
            
        } catch (error) {
            console.error('Error:', error);
            
            // 移除上传进度条
            if (uploadProgressElement) {
                const progressIndicator = document.getElementById('upload-progress-indicator');
                if (progressIndicator) {
                    progressIndicator.remove();
                }
            }
            
            const loadingIndicator = document.getElementById('loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.remove();
            }
            
            if (error.name === 'AbortError') {
                addMessageToChat('⏰ 请求超时，请稍后重试。', 'assistant');
                userInput.value = currentInput;
                userInput.style.height = 'auto';
                userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
            } else {
                addMessageToChat('抱歉，服务暂时不可用。请确保Ollama正在运行。', 'assistant');
            }
        }
    }
    
    // 添加用户消息到聊天界面（修改参数以支持处理时间显示）
    function addMessageToChat(text, sender, attachmentInfo = null, processingTime = null) {
        const messageElement = document.createElement('div');
        messageElement.className = sender === 'user' ? 'message user-message' : 'message assistant-message';
        
        const now = new Date();
        const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
        
        let escapedText = text.replace(/&/g, '&amp;')
                                .replace(/</g, '&lt;')
                                .replace(/>/g, '&gt;');
            
        if (sender === 'user') {
            let messageContent = `<div class="message-content"><div class="message-text">${escapedText}</div>`;
                
            // 添加附件信息显示
            if (attachmentInfo && attachmentInfo.files && attachmentInfo.files.length > 0) {
                messageContent += `<div class="message-attachments">`;
                attachmentInfo.files.forEach(file => {
                    messageContent += `
                            <div class="message-attachment-item">
                                <span class="message-attachment-icon">${file.icon}</span>
                                <span class="message-attachment-name" title="${file.name}">${file.name}</span>
                            </div>`;
                });
                messageContent += `</div>`;
            }
                
            messageContent += `</div>`;
            messageContent += `<div class="message-time">${timeString}</div>`;
            messageElement.innerHTML = messageContent;
        } else {
            // 助手消息 - 添加处理时间显示
            let messageContent = '';
            if (processingTime && processingTime > 0) {
                messageContent += `<div class="message-processing-time">已思考 ${processingTime.toFixed(1)} 秒</div>`;
            }
            messageContent += `<div class="message-content"><div class="message-text">${escapedText}</div></div>`;
            messageContent += `<div class="message-time">${timeString}</div>`;
            messageElement.innerHTML = messageContent;
        }
        
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // 添加右键菜单事件监听器
        if (sender === 'user' && attachmentInfo && attachmentInfo.files && attachmentInfo.files.length > 0) {
            const attachmentItems = messageElement.querySelectorAll('.message-attachment-item');
            attachmentItems.forEach(item => {
                item.addEventListener('contextmenu', function(e) {
                    e.preventDefault();
                    selectedFileForDeletion = {
                        element: item,
                        filename: item.querySelector('.message-attachment-name').textContent.trim()
                    };
                    
                    contextMenu.style.display = 'block';
                    contextMenu.style.left = e.pageX + 'px';
                    contextMenu.style.top = e.pageY + 'px';
                });
            });
        }
    }

    // 发送按钮点击处理
    sendButton.addEventListener('click', function() {
        sendMessageWithFiles();
    });
    
    // 键盘快捷键处理 - 使用更可靠的事件处理方式
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            // 触发发送按钮点击事件，确保与按钮行为一致
            sendButton.click();
        }
    });
    
    // 拖拽上传支持
    inputContainer.addEventListener('dragover', function(e) {
        e.preventDefault();
        inputContainer.classList.add('drag-over');
    });
    
    inputContainer.addEventListener('dragleave', function() {
        inputContainer.classList.remove('drag-over');
    });
    
    inputContainer.addEventListener('drop', function(e) {
        e.preventDefault();
        inputContainer.classList.remove('drag-over');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const existingFiles = Array.from(attachmentInput.files);
            const newFiles = Array.from(e.dataTransfer.files);
            const allFiles = [...existingFiles, ...newFiles];
            
            const dataTransfer = new DataTransfer();
            allFiles.forEach(file => dataTransfer.items.add(file));
            attachmentInput.files = dataTransfer.files;
            
            updateAttachmentPreview();
        }
    });
    
    // 右键菜单处理
    document.addEventListener('contextmenu', function(e) {
        if (!e.target.closest('.attachment-item')) {
            contextMenu.style.display = 'none';
        }
    });
    
    document.addEventListener('click', function(e) {
        if (e.target !== contextMenu && !contextMenu.contains(e.target)) {
            contextMenu.style.display = 'none';
        }
    });
    
    document.querySelector('.delete-context-item').addEventListener('click', function() {
        if (selectedFileForDeletion !== null) {
            removeFileFromInput(selectedFileForDeletion);
            selectedFileForDeletion = null;
            contextMenu.style.display = 'none';
        }
    });
    
    // 初始化时滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // 确保页面加载完成后焦点在输入框
    setTimeout(() => {
        userInput.focus();
    }, 100);
});

// 在文件末尾添加模型状态检查函数
function checkModelStatus() {
    fetch('/api/v1/status')
        .then(response => response.json())
        .then(data => {
            const statusElement = document.getElementById('modelStatus');
            if (statusElement) {
                const statusDot = statusElement.querySelector('.status-dot');
                const statusText = statusElement.querySelector('span');
                
                if (data.status === 'online') {
                    statusElement.className = 'status online';
                    statusDot.className = 'status-dot';
                    statusText.textContent = '在线';
                } else if (data.status === 'offline') {
                    statusElement.className = 'status offline';
                    statusDot.className = 'status-dot';
                    statusText.textContent = '离线';
                } else {
                    statusElement.className = 'status unknown';
                    statusDot.className = 'status-dot';
                    statusText.textContent = '未知';
                }
            }
        })
        .catch(error => {
            const statusElement = document.getElementById('modelStatus');
            if (statusElement) {
                statusElement.className = 'status offline';
                const statusDot = statusElement.querySelector('.status-dot');
                const statusText = statusElement.querySelector('span');
                statusDot.className = 'status-dot';
                statusText.textContent = '离线';
            }
        });
}

// 初始化时立即检查一次状态，然后每10秒检查一次
checkModelStatus();
setInterval(checkModelStatus, 10000);

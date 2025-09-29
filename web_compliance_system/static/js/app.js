// Spes合规审查系统 - JavaScript文件

// 全局变量
let loadingModal = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化Bootstrap模态框
    loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    
    // 检查系统状态
    checkStatus();
    
    // 设置图片预览功能
    setupImagePreview();
    
    // 设置文件上传功能
    setupFileUpload();
});

// 检查系统状态
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (response.ok) {
            updateSystemStatus(data);
        } else {
            showError('系统状态检查失败: ' + data.error);
        }
    } catch (error) {
        console.error('状态检查错误:', error);
        showError('无法连接到服务器');
    }
}

// 更新系统状态显示
function updateSystemStatus(status) {
    const statusElement = document.getElementById('system-status');
    const kbStatusElement = document.getElementById('kb-status');
    const docCountElement = document.getElementById('doc-count');
    
    if (status.status === '已初始化') {
        statusElement.innerHTML = '<i class="fas fa-circle text-success me-1"></i>系统运行正常';
        kbStatusElement.textContent = '已初始化';
        docCountElement.textContent = status.document_count || '未知';
    } else {
        statusElement.innerHTML = '<i class="fas fa-circle text-danger me-1"></i>系统异常';
        kbStatusElement.textContent = status.status || '未知';
        docCountElement.textContent = '-';
    }
}

// 设置图片预览功能
function setupImagePreview() {
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImg.src = e.target.result;
                imagePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
}

// 设置文件上传功能
function setupFileUpload() {
    const fileInput = document.getElementById('fileInput');
    
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // 自动上传文件
            uploadFile(file);
        }
    });
}

// 清空图片
function clearImage() {
    document.getElementById('imageInput').value = '';
    document.getElementById('imagePreview').style.display = 'none';
}

// 清空所有内容
function clearAll() {
    document.getElementById('textInput').value = '';
    document.getElementById('imageInput').value = '';
    document.getElementById('fileInput').value = '';
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('resultArea').innerHTML = `
        <div class="text-center text-muted">
            <i class="fas fa-clipboard-list fa-3x mb-3"></i>
            <p>请输入内容并点击"开始审查"查看结果</p>
        </div>
    `;
}

// 执行审查
async function performReview() {
    const text = document.getElementById('textInput').value.trim();
    const imageInput = document.getElementById('imageInput');
    
    if (!text && !imageInput.files[0]) {
        showError('请输入文本内容或上传图片');
        return;
    }
    
    showLoading('正在分析内容...');
    
    try {
        let imageData = '';
        
        // 处理图片
        if (imageInput.files[0]) {
            imageData = await fileToBase64(imageInput.files[0]);
        }
        
        const response = await fetch('/api/review', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                image: imageData
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResult(data);
        } else {
            showError('审查失败: ' + data.error);
        }
    } catch (error) {
        console.error('审查错误:', error);
        showError('网络错误，请检查连接');
    } finally {
        hideLoading();
    }
}

// 上传文件
async function uploadFile(file) {
    showLoading('正在上传文件...');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResult(data);
            // 清空文件输入
            document.getElementById('fileInput').value = '';
        } else {
            showError('文件上传失败: ' + data.error);
        }
    } catch (error) {
        console.error('上传错误:', error);
        showError('文件上传失败');
    } finally {
        hideLoading();
    }
}

// 文件转Base64
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

// 显示结果
function displayResult(data) {
    const resultArea = document.getElementById('resultArea');
    
    let resultHtml = `
        <div class="fade-in">
            <div class="mb-3">
                <h6><i class="fas fa-info-circle me-2"></i>输入信息</h6>
                <p class="mb-1"><strong>文本:</strong> ${data.input_text || '无'}</p>
                <p class="mb-0"><strong>图片:</strong> ${data.has_image ? '已上传' : '无'}</p>
            </div>
            <hr>
            <h6><i class="fas fa-clipboard-check me-2"></i>审查结果</h6>
    `;
    
    // 解析Markdown表格结果
    if (data.result) {
        const tableHtml = parseMarkdownTable(data.result);
        resultHtml += tableHtml;
    } else {
        resultHtml += '<p class="text-muted">无结果</p>';
    }
    
    resultHtml += '</div>';
    resultArea.innerHTML = resultHtml;
}

// 解析Markdown表格
function parseMarkdownTable(markdown) {
    const lines = markdown.split('\n');
    let tableHtml = '<div class="table-responsive"><table class="table table-striped result-table">';
    let inTable = false;
    
    for (let line of lines) {
        line = line.trim();
        
        if (line.startsWith('|') && line.endsWith('|')) {
            if (!inTable) {
                inTable = true;
                tableHtml += '<thead><tr>';
            }
            
            const cells = line.split('|').slice(1, -1).map(cell => cell.trim());
            
            if (cells[0].includes('---')) {
                // 这是分隔行，跳过
                continue;
            }
            
            if (inTable && cells.length > 1) {
                if (tableHtml.includes('<thead>')) {
                    // 表头
                    cells.forEach(cell => {
                        tableHtml += `<th>${cell}</th>`;
                    });
                    tableHtml += '</tr></thead><tbody>';
                } else {
                    // 数据行
                    tableHtml += '<tr>';
                    cells.forEach(cell => {
                        // 根据内容添加样式
                        let cellClass = '';
                        if (cell.includes('拒绝')) {
                            cellClass = 'text-danger fw-bold';
                        } else if (cell.includes('安全通过')) {
                            cellClass = 'text-success fw-bold';
                        } else if (cell.includes('警告')) {
                            cellClass = 'text-warning fw-bold';
                        }
                        tableHtml += `<td class="${cellClass}">${cell}</td>`;
                    });
                    tableHtml += '</tr>';
                }
            }
        } else if (inTable) {
            tableHtml += '</tbody></table></div>';
            inTable = false;
        }
    }
    
    if (inTable) {
        tableHtml += '</tbody></table></div>';
    }
    
    return tableHtml;
}

// 重新加载文档
async function reloadDocument() {
    showLoading('正在重新加载文档...');
    
    try {
        const response = await fetch('/api/reload');
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(data.message);
            checkStatus(); // 刷新状态
        } else {
            showError('重新加载失败: ' + data.error);
        }
    } catch (error) {
        console.error('重新加载错误:', error);
        showError('重新加载失败');
    } finally {
        hideLoading();
    }
}

// 添加自定义规则
async function addCustomRules() {
    const rules = document.getElementById('customRules').value.trim();
    
    if (!rules) {
        showError('请输入规则内容');
        return;
    }
    
    showLoading('正在添加规则...');
    
    try {
        const response = await fetch('/api/add_rules', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                rules: rules
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(data.message);
            document.getElementById('customRules').value = '';
        } else {
            showError('添加规则失败: ' + data.error);
        }
    } catch (error) {
        console.error('添加规则错误:', error);
        showError('添加规则失败');
    } finally {
        hideLoading();
    }
}

// 显示加载提示
function showLoading(text = '正在处理中，请稍候...') {
    document.getElementById('loadingText').textContent = text;
    loadingModal.show();
}

// 隐藏加载提示
function hideLoading() {
    loadingModal.hide();
}

// 显示成功消息
function showSuccess(message) {
    showAlert(message, 'success');
}

// 显示错误消息
function showError(message) {
    showAlert(message, 'danger');
}

// 显示警告消息
function showWarning(message) {
    showAlert(message, 'warning');
}

// 显示信息消息
function showInfo(message) {
    showAlert(message, 'info');
}

// 显示警告框
function showAlert(message, type) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // 在页面顶部显示警告
    const container = document.querySelector('.container');
    container.insertAdjacentHTML('afterbegin', alertHtml);
    
    // 3秒后自动消失
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            alert.remove();
        }
    }, 3000);
}

// 获取警告图标
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

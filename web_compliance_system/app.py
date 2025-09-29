# Spes合规审查系统 - Web版本
# Flask Web应用主文件

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import json
from werkzeug.utils import secure_filename
from shenhe import ComplianceAgent
import base64
from PIL import Image
import io

app = Flask(__name__)
app.secret_key = 'spes_compliance_2024'

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 全局Agent实例
agent = None

def init_agent():
    """初始化合规审查Agent"""
    global agent
    try:
        agent = ComplianceAgent()
        return True
    except Exception as e:
        print(f"Agent初始化失败: {e}")
        return False

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_image_file(filename):
    """检查是否为图片文件"""
    image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in image_extensions

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    if not agent:
        return jsonify({"error": "系统未初始化"}), 500
    
    try:
        status = agent.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/review', methods=['POST'])
def review_content():
    """合规审查API"""
    if not agent:
        return jsonify({"error": "系统未初始化"}), 500
    
    try:
        data = request.get_json()
        text = data.get('text', '')
        image_data = data.get('image', '')  # base64编码的图片
        
        if not text and not image_data:
            return jsonify({"error": "请提供文本或图片"}), 400
        
        # 处理图片
        image_path = None
        if image_data:
            # 解码base64图片
            try:
                image_data = image_data.split(',')[1] if ',' in image_data else image_data
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # 保存临时图片
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_image.jpg')
                image.save(image_path)
            except Exception as e:
                return jsonify({"error": f"图片处理失败: {str(e)}"}), 400
        
        # 执行审查
        result = agent.review_with_image(text=text, image_path=image_path)
        
        # 清理临时文件
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        
        return jsonify({
            "success": True,
            "result": result,
            "input_text": text,
            "has_image": bool(image_data)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传API"""
    if not agent:
        return jsonify({"error": "系统未初始化"}), 500
    
    try:
        if 'file' not in request.files:
            return jsonify({"error": "没有选择文件"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "没有选择文件"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # 根据文件类型处理
            if is_image_file(filename):
                # 图片文件，直接审查
                result = agent.review_with_image(image_path=filepath)
                file_type = "图片"
            else:
                # 文档文件，读取内容后审查
                if filename.endswith('.txt'):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                elif filename.endswith('.docx'):
                    from docx import Document
                    doc = Document(filepath)
                    content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                else:
                    return jsonify({"error": "暂不支持此文件格式"}), 400
                
                result = agent.review_with_image(text=content)
                file_type = "文档"
            
            # 清理上传的文件
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({
                "success": True,
                "result": result,
                "filename": filename,
                "file_type": file_type
            })
        else:
            return jsonify({"error": "不支持的文件格式"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reload')
def reload_document():
    """重新加载合规文档"""
    if not agent:
        return jsonify({"error": "系统未初始化"}), 500
    
    try:
        result = agent.reload_document()
        return jsonify({"success": True, "message": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/add_rules', methods=['POST'])
def add_custom_rules():
    """添加自定义规则"""
    if not agent:
        return jsonify({"error": "系统未初始化"}), 500
    
    try:
        data = request.get_json()
        custom_rules = data.get('rules', '')
        
        if not custom_rules:
            return jsonify({"error": "请提供规则内容"}), 400
        
        # 通过Agent工具添加规则
        result = agent.agent_executor.invoke({
            "input": f"请添加自定义规则: {custom_rules}"
        })
        
        return jsonify({
            "success": True,
            "message": result["output"]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({"error": "文件过大，请选择小于16MB的文件"}), 413

@app.errorhandler(404)
def not_found(e):
    """404错误处理"""
    return jsonify({"error": "页面不存在"}), 404

@app.errorhandler(500)
def internal_error(e):
    """500错误处理"""
    return jsonify({"error": "服务器内部错误"}), 500

if __name__ == '__main__':
    print("🚀 启动Spes合规审查Web系统...")
    
    # 初始化Agent
    if init_agent():
        print("✅ Agent初始化成功")
        print("🌐 启动Web服务器...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Agent初始化失败，请检查环境配置")
